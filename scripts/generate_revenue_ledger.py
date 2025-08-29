#!/usr/bin/env python3
"""
Revenue Ledger Generator
Refactored from user-provided one-liner for maintainability and automation.
Usage:
  python scripts/generate_revenue_ledger.py
Environment variables:
  OUTDIR, SEG, CPS, SEED
"""
import datetime as dt
import hashlib
import io
import json
import os
import random
import uuid


def U():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def H(s):
    return hashlib.sha256(s.encode()).hexdigest()


g = os.getenv
B = g("OUTDIR", "./ledger")
os.makedirs(B, exist_ok=True)
SEG = int(g("SEG", "20"))
CPS = int(g("CPS", "15"))
SEED = g("SEED", "TrueNorth")

ROOT = H("genesis:" + SEED)
LED = f"{B}/revenue_ledger.jsonl"
open(LED, "a").close()
CAS = f"{B}/cas"
os.makedirs(CAS, exist_ok=True)

CH = [
    ("Website", 0.00, 0.0),
    ("Ads", 1.2, 0.0),
    ("Newsletter", 0.2, 0.0),
    ("Partners", 0.0, 0.15),
    ("Marketplace", 0.0, 0.10),
]
PL = [("Free", 0.0), ("Starter", 19.0), ("Pro", 79.0), ("Enterprise", 399.0)]
bandit = {c: {p: 0 for _, p in PL} for c, _, _ in CH}
wins = {c: {p: 1 for _, p in PL} for c, _, _ in CH}


def pick_price(ch):
    import random

    if random.random() < 0.1:
        return random.choice(PL)[1]
    return max(PL, key=lambda x: wins[ch][x[1]] / (bandit[ch][x[1]] + 1))[1]


def conv(ch, price):
    base = {
        "Website": 0.06,
        "Ads": 0.03,
        "Newsletter": 0.08,
        "Partners": 0.05,
        "Marketplace": 0.04,
    }[ch]
    mult = 1.15 if price in (19.0, 79.0) else (0.75 if price >= 399.0 else 1.0)
    import random

    return max(0.002, min(0.2, base * mult + random.uniform(-0.01, 0.01)))


def put(p):
    b = open(p, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    out_path = f"{CAS}/{h}.bin"
    if not os.path.exists(out_path):
        open(out_path, "wb").write(b)
    return h


state = {"root": ROOT, "last": "genesis", "segs": []}

revT = costT = gmT = 0.0
links = []
for s in range(1, SEG + 1):
    cycles = []
    segR = segC = 0.0
    users = 0
    for c in range(1, CPS + 1):
        ch, cpc, take = random.choice(CH)
        price = pick_price(ch)

        traffic = random.randint(800, 3000)
        clicks = int(traffic * (0.05 if cpc > 0 else 0.02) + random.randint(0, 40))
        signups = int(clicks * conv(ch, price))
        arpu = price * 0.9 if price > 0 else 0.0
        churn = max(
            0.02, 0.15 - 0.05 * (price > 0) - 0.03 * (ch in ("Newsletter", "Website"))
        ) + random.uniform(-0.01, 0.01)
        ltv = arpu / max(0.02, min(0.3, churn))
        rev = signups * price + signups * ltv * 0.20
        cost = clicks * cpc + rev * take
        gm = max(0.0, rev - cost)
        bandit[ch][price] += 1
        wins[ch][price] += signups
        segR += rev
        segC += cost
        users += signups
        cycles.append(
            {
                "c": c,
                "ch": ch,
                "price": price,
                "signups": signups,
                "rev": round(rev, 2),
                "cost": round(cost, 2),
                "gm": round(gm, 2),
                "ltv": round(ltv, 2),
            }
        )
    exf = f"{B}/rev_seg_{s}.json"
    open(exf, "w").write(
        json.dumps(
            {
                "ts": U(),
                "cycles": cycles,
                "seg_rev": round(segR, 2),
                "seg_cost": round(segC, 2),
                "users": users,
            },
            separators=(",", ":"),
        )
    )
    mh = put(exf)
    cap = {
        "capsule_id": f"REV-SEG{s}-{uuid.uuid4().hex[:6]}",
        "ts": U(),
        "prov": {
            "prev": (state["segs"][-1]["sha"] if state["segs"] else "genesis"),
            "cas": mh,
        },
        "payload": os.path.basename(exf),
    }
    raw = json.dumps(cap, separators=(",", ":")).encode()
    sha = hashlib.sha256(raw).hexdigest()
    open(f'{B}/{cap["capsule_id"]}.json', "wb").write(raw)

    state["last"] = hashlib.sha256((state["last"] + ":" + sha).encode()).hexdigest()
    state["segs"].append({"sha": sha, "cid": cap["capsule_id"], "chain": state["last"]})
    links.append({"prev": cap["prov"]["prev"], "curr": sha})
    revT += segR
    costT += segC
    gmT += max(0.0, segR - segC)
    line = {
        "ts": U(),
        "event": "revenue",
        "cid": cap["capsule_id"],
        "sha": sha,
        "seg": s,
        "line_sha": None,
    }
    base = json.dumps(
        {k: v for k, v in line.items() if k != "line_sha"}, separators=(",", ":")
    )
    line["line_sha"] = hashlib.sha256(base.encode()).hexdigest()
    io.open(LED, "a", encoding="utf-8").write(
        json.dumps(line, separators=(",", ":")) + "\n"
    )
summary = {
    "ts": U(),
    "segments": SEG,
    "rev_total": round(revT, 2),
    "cost_total": round(costT, 2),
    "gross_margin": round(gmT, 2),
    "roi": round((revT - costT) / max(1.0, costT), 3),
    "chain_last": state["last"],
}
open(f"{B}/revenue_summary.json", "w").write(json.dumps(summary, separators=(",", ":")))
print(json.dumps(summary, separators=(",", ":")))
