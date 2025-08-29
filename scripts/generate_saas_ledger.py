#!/usr/bin/env python3
"""
SaaS Ledger Generator
Refactored from user-provided one-liner for maintainability and automation.
Usage:
  python scripts/generate_saas_ledger.py
Environment variables:
  OUTDIR, SEG, CPS, SEED
"""
import datetime as dt
import hashlib
import io
import json
import os
import random
import secrets
import uuid
import zipfile


def U():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def H(s):
    return hashlib.sha256(s.encode()).hexdigest()


g = os.getenv
B = g("OUTDIR", "./ledger")
os.makedirs(B, exist_ok=True)
SEG = int(g("SEG", "18"))
CPS = int(g("CPS", "10"))
PL = [("U1", 10000, 0.002), ("U2", 100000, 0.0014), ("U3", 1000000, 0.0009)]
LED = f"{B}/saas_ledger.jsonl"
open(LED, "a").close()


def lic():
    return "-".join([secrets.token_hex(4) for _ in range(4)]).upper()


state = {"last": "genesis", "root": H("saas:" + g("SEED", "TrueNorth")), "segs": []}
R = C = 0.0
for s in range(1, SEG + 1):
    sku = f"SKU-{s:03d}-{uuid.uuid4().hex[:6]}"
    plan, quota, ppc = random.choice(PL)

    users = random.randint(40, 400)
    cycles = []
    segR = segC = 0.0

    L = []
    for c in range(1, CPS + 1):
        use = random.randint(int(0.3 * quota), quota)

        over = max(0, use - quota)
        rev = quota * ppc + over * ppc * 1.5
        cost = use * ppc * 0.35 + users * 0.05
        segR += rev

        segC += cost
    cycles.append(
        {"c": c, "usage": use, "rev": round(rev, 2), "cost": round(cost, 2)}
    )
    for _ in range(min(12, users)):
        L.append({"key": lic(), "sku": sku, "plan": plan, "ppc": ppc, "issued": U()})
    pack = f"{B}/{sku}.json"
    open(pack, "w").write(
        json.dumps(
            {
                "ts": U(),
                "sku": sku,
                "plan": plan,
                "ppc": ppc,
                "cycles": cycles,
                "licenses": L,
            },
            separators=(",", ":"),
        )
    )

    zipfile.ZipFile(f"{B}/{sku}.zip", "w", zipfile.ZIP_DEFLATED).write(
        pack, arcname=os.path.basename(pack)
    )
    sha = hashlib.sha256(open(pack, "rb").read()).hexdigest()
    cid = f"SAAS-SEG{s}-{uuid.uuid4().hex[:6]}"

    open(f"{B}/{cid}.json", "w").write(
        json.dumps(
            {
                "cid": cid,
                "ts": U(),
                "sha": sha,
                "prev": (state["segs"][-1]["sha"] if state["segs"] else "genesis"),
                "sku": sku,
            },
            separators=(",", ":"),
        )
    )
    state["last"] = hashlib.sha256((state["last"] + ":" + sha).encode()).hexdigest()
    state["segs"].append({"sha": sha, "cid": cid})

    io.open(LED, "a", encoding="utf-8").write(
        json.dumps(
            {
                "ts": U(),
                "event": "saas",
                "cid": cid,
                "sku": sku,
                "sha": sha,
                "rev": round(segR, 2),
                "cost": round(segC, 2),
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    R += segR
    C += segC
sumry = {
    "ts": U(),
    "segments": SEG,
    "rev_total": round(R, 2),
    "cost_total": round(C, 2),
    "gross_margin": round(R - C, 2),
    "chain_last": state["last"],
}
open(f"{B}/saas_summary.json", "w").write(json.dumps(sumry, separators=(",", ":")))
print(json.dumps(sumry, separators=(",", ":")))
