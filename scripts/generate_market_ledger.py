#!/usr/bin/env python3
"""
Market Ledger Generator
Refactored from user-provided one-liner for maintainability and automation.
Usage:
  python scripts/generate_market_ledger.py
Environment variables:
  OUTDIR, SEG, CPS
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import io
import json
import os
import random
import uuid


def U():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


g = os.getenv
B = g("OUTDIR", "./ledger")
os.makedirs(B, exist_ok=True)
SEG = int(g("SEG", "24"))
CPS = int(g("CPS", "20"))
LED = f"{B}/market_ledger.jsonl"
open(LED, "a").close()
agents = [("alpha", 0.94), ("bravo", 0.91), ("gamma", 0.90), ("delta", 0.92)]
caps = ["discover", "plan", "execute", "review", "publish"]


def run_seg(s):
    random.seed(1000 + s)
    rev = cost = 0.0
    cycles = []
    for c in range(1, CPS + 1):
        tR = tC = 0.0
        for i, cap in enumerate(caps):
            base = 0.02 + 0.03 * i
            bids = [
                (aid, round(base * (1.2 - random.random() * 0.4) / w, 4))
                for (aid, w) in agents
            ]
            aid, price = min(bids, key=lambda x: x[1])
            demand = random.randint(4, 30)
            take = 0.12 + 0.03 * (cap in ("publish", "plan"))
            revenue = price * demand * (1 + 0.5 * (cap == "publish"))
            payout = revenue * (1 - take)
            tR += revenue
            tC += payout
        cycles.append({"c": c, "rev": round(tR, 2), "payout": round(tC, 2)})
        rev += tR
        cost += tC
    p = f"{B}/mk_seg_{s}.json"
    open(p, "w").write(json.dumps({"ts": U(), "cycles": cycles}, separators=(",", ":")))
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    cap = {
        "cid": f"MKT-SEG{s}-{uuid.uuid4().hex[:6]}",
        "sha": sha,
        "prev": "genesis",
        "ts": U(),
        "payload": os.path.basename(p),
    }
    return {
        "seg": s,
        "rev": round(rev, 2),
        "cost": round(cost, 2),
        "gm": round(rev - cost, 2),
    }, cap


res = []
caps_out = []
prev = "genesis"
last = "genesis"
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for m, cap in ex.map(run_seg, range(1, SEG + 1)):
        cap["prev"] = prev
        prev = cap["sha"]
        last = hashlib.sha256((last + ":" + cap["sha"]).encode()).hexdigest()
        io.open(LED, "a", encoding="utf-8").write(
            json.dumps(
                {
                    "ts": U(),
                    "event": "market",
                    "cid": cap["cid"],
                    "sha": cap["sha"],
                    "prev": cap["prev"],
                },
                separators=(",", ":"),
            )
            + "\n"
        )
        open(f"{B}/{cap['cid']}.json", "w").write(
            json.dumps(cap, separators=(",", ":"))
        )
        res.append(m)
        caps_out.append(cap)
summary = {
    "ts": U(),
    "segments": SEG,
    "rev_total": round(sum(x["rev"] for x in res), 2),
    "payout_total": round(sum(x["cost"] for x in res), 2),
    "gross_margin": round(sum(x["gm"] for x in res), 2),
    "chain_last": last,
}
open(f"{B}/market_summary.json", "w").write(json.dumps(summary, separators=(",", ":")))
print(json.dumps(summary, separators=(",", ":")))
