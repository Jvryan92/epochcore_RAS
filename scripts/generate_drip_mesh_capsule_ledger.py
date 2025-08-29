#!/usr/bin/env python3
"""
DRIP Mesh/Capsule/Ledger Generator
Refactored from user-provided one-liner for maintainability and automation.
Usage:
  python scripts/generate_drip_mesh_capsule_ledger.py
Environment variables:
  MESH_SECRET, SEG, CPS, POW, SLO, BUD, OUTDIR, SEED
"""
import datetime as dt
import glob
import hashlib
import hmac
import io
import json
import os
import random
import statistics
import sys
import uuid
import zipfile


def U():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def H(b):
    return hashlib.sha256(b).hexdigest()


def HS(s):
    return H(s.encode())


g = os.getenv
B = g("OUTDIR", "./ledger")
os.makedirs(B, exist_ok=True)
SEG = max(1, min(100, int(g("SEG", "100"))))
CPS = max(1, min(100, int(g("CPS", "100"))))
SLO = int(g("SLO", "300"))
BUD = float(g("BUD", "5000"))
POW = max(1, int(g("POW", "16")))
SEED = g("SEED", "TrueNorth")
SECSTR = g("MESH_SECRET", "mesh-demo-secret")


def parse_sec(s):
    try:
        t = s.strip()
        if all(c in "0123456789abcdefABCDEF" for c in t) and len(t) % 2 == 0:
            return bytes.fromhex(t)
    except Exception:
        pass
    return s.encode()


ROOT = parse_sec(SECSTR)


def hkdf_ex(salt, ikm):
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def hkdf_exp(prk, info, L=32):
    T = b""
    okm = b""
    i = 1
    while len(okm) < L:
        T = hmac.new(prk, T + info + bytes([i]), hashlib.sha256).digest()
        okm += T
        i += 1
    return okm[:L]


def kdf(label):
    return hkdf_exp(
        hkdf_ex(HS("salt:" + label).encode(), ROOT), b"DRIP:" + label.encode(), 32
    )


K_ORG = kdf("ORG")
LED = f"{B}/ledger_main.jsonl"
CAS = f"{B}/cas"
LOG = f"{B}/drip_log.jsonl"
os.makedirs(CAS, exist_ok=True)
io.open(LED, "a").close()


def log_event(ev, **k):
    entry = {"ts": U(), "ev": ev}
    entry.update(k)
    io.open(LOG, "a", encoding="utf-8").write(
        json.dumps(entry, separators=(",", ":")) + "\n"
    )


# --- seed (DRIP verb): agents / ontology / registry / grants / policies
# --- heartbeats / DAG
A = [
    {
        "id": "agent://alpha",
        "skills": ["scrape.web", "vector.store", "atomize.payload", "sandbox.dryrun"],
        "rel": 0.94,
        "lat": 210,
    },
    {
        "id": "agent://bravo",
        "skills": [
            "plan.compose",
            "review.policies",
            "diffuse.channels",
            "schedule.drip",
            "rollback.diff",
        ],
        "rel": 0.92,
        "lat": 250,
    },
    {
        "id": "agent://gamma",
        "skills": [
            "echo.measure",
            "blackboard.merge",
            "snapshot.world",
            "sign.proof",
            "attest.supply",
            "drip.signal",
        ],
        "rel": 0.90,
        "lat": 300,
    },
]
ontology_graph = {
    "edges": {
        "drip.signal": [
            "atomize.payload",
            "diffuse.channels",
            "echo.measure",
            "sign.proof",
        ],
        "atomize.payload": ["hydrate.buffer"],
        "diffuse.channels": ["blackboard.merge", "schedule.drip"],
        "echo.measure": ["replenish.cache"],
        "sign.proof": [],
        "hydrate.buffer": [],
        "blackboard.merge": [],
        "schedule.drip": [],
        "replenish.cache": [],
    }
}
open(f"{B}/drip_ontology.json", "w").write(
    json.dumps({"ts": U(), "graph": ontology_graph}, separators=(",", ":"))
)
R = {
    "version": "D2",
    "ts": U(),
    "agents": [
        {"agent_id": a["id"], "skills": a["skills"], "rel": a["rel"], "lat": a["lat"]}
        for a in A
    ],
}
open(f"{B}/drip_registry.json", "w").write(json.dumps(R, separators=(",", ":")))
G = {
    "version": "D2",
    "allow": {
        "agent://alpha": ["atomize.payload", "vector.store", "sandbox.dryrun"],
        "agent://bravo": [
            "diffuse.channels",
            "review.policies",
            "schedule.drip",
            "rollback.diff",
        ],
        "agent://gamma": [
            "drip.signal",
            "echo.measure",
            "blackboard.merge",
            "sign.proof",
            "snapshot.world",
        ],
    },
    "multisig": {">=50USD": ["agent://bravo", "agent://gamma"]},
}
open(f"{B}/drip_grants.json", "w").write(json.dumps(G, separators=(",", ":")))
P = {
    "rules": [
        {"if": 'cap=="drip.signal"', "require": ["quorum==2", "evidence"]},
        {"if": "usd>=50", "require": ["quorum==2"]},
        {"if": 'risk.radius!="low"', "require": ["backup", "shadow_or_dryrun"]},
    ]
}
open(f"{B}/drip_policies.json", "w").write(json.dumps(P, separators=(",", ":")))
HB = [a["lat"] + random.randint(-40, 60) for a in A]
open(f"{B}/drip_heartbeats.jsonl", "w").write(
    "\n".join(
        json.dumps(
            {"agent": A[i]["id"], "ts": U(), "latency_ms": HB[i]}, separators=(",", ":")
        )
        for i in range(len(A))
    )
)
mu = sum(HB) / len(HB)
sd = statistics.pstdev(HB) or 1.0
AN = [
    {"agent": A[i]["id"], "lat": HB[i], "z": round((HB[i] - mu) / sd, 2)}
    for i in range(len(A))
    if abs((HB[i] - mu) / sd) > 1.5
]
open(f"{B}/drip_anomalies.json", "w").write(
    json.dumps({"ts": U(), "mean_ms": mu, "anomalies": AN}, separators=(",", ":"))
)
seen = set()
setord = []
sys.setrecursionlimit(10000)


def dfs(x):
    if x in seen:
        return
    for y in ontology_graph["edges"].get(x, []):
        dfs(y)
    seen.add(x)
    setord.append(x)


dfs("drip.signal")
CH = [x for x in setord if x != "drip.signal"] + ["drip.signal"]
open(f"{B}/drip_dag_base.json", "w").write(
    json.dumps({"ts": U(), "chain": CH}, separators=(",", ":"))
)
STATE = {
    "ts": U(),
    "root": HS("genesis:drip:" + SEED),
    "last": "genesis",
    "segments": [],
}
open(f"{B}/drip_chain_state.json", "w").write(json.dumps(STATE, separators=(",", ":")))


def put(p):
    d = open(p, "rb").read()
    h = H(d)
    out_path = f"{CAS}/{h}.bin"
    if not os.path.exists(out_path):
        open(out_path, "wb").write(d)
    return h


def merkle(hs):
    ns = [bytes.fromhex(x) for x in hs] or [b""]
    while len(ns) > 1:
        ns = [
            hashlib.sha256(ns[i] + (ns[i + 1] if i + 1 < len(ns) else ns[i])).digest()
            for i in range(0, len(ns), 2)
        ]
    return ns[0].hex()


seg_caps = []
links = []
spent = 0.0
oks = tot = 0
for s in range(1, SEG + 1):
    PRK = hkdf_ex(HS(f"SEG:{s}:{SEED}").encode(), ROOT)
    K_SEG = hkdf_exp(PRK, b"DRIP-SEG", 32)
    K_LED = hkdf_exp(PRK, b"LEDGER", 32)
    cycles = []
    pb = hashlib.sha256()
    for c in range(1, CPS + 1):
        lat = []
        okc = True
        usd_c = 0.0
        for j, cap in enumerate(CH):
            cost = round(0.03 + 0.02 * j, 2)
            usd = round(cost * 100, 2)
            risk = {
                "radius": ("low" if random.random() < 0.72 else "med"),
                "var_usd": round(random.uniform(0.5, 30.0), 2),
            }
            lat.append(random.randint(180, 330))
            okc = okc and (risk["radius"] == "low") and (usd < 400) and (spent <= BUD)
            usd_c += usd
            pb.update(f"{s}:{c}:{cap}:pp".encode())
            pb.update(f"{s}:{c}:{cap}:pr".encode())
            pb.update(f"{s}:{c}:{cap}:cm".encode())
        spent += usd_c / 100.0
        p95 = sorted(lat)[int(0.95 * len(lat)) - 1]
        cycles.append({"c": c, "ok": okc, "p95": p95, "usd": round(usd_c / 100.0, 2)})
        oks += 1 if okc else 0
        tot += 1
    EXF = f"{B}/drip_seg_{s}_exec.json"
    open(EXF, "w").write(
        json.dumps(
            {"ts": U(), "cycles": cycles, "pbft_hash": pb.hexdigest()},
            separators=(",", ":"),
        )
    )
    SLAF = f"{B}/drip_seg_{s}_sla.json"
    P95s = [x["p95"] for x in cycles]
    seg_p95 = sorted(P95s)[int(0.95 * len(P95s)) - 1] if P95s else 0
    open(SLAF, "w").write(
        json.dumps(
            {
                "ts": U(),
                "p95_ms": seg_p95,
                "ok": seg_p95 <= SLO,
                "spent_to_date": round(spent, 2),
            },
            separators=(",", ":"),
        )
    )
    hs = [put(EXF), put(SLAF)]
    root = merkle(hs)
    open(f"{B}/drip_seg_{s}_merkle.json", "w").write(
        json.dumps({"ts": U(), "files": hs, "root": root}, separators=(",", ":"))
    )
    prev_sha = STATE["segments"][-1]["sha"] if STATE["segments"] else "genesis"
    cid = f"EPOCHCORE-DRIP-SEG{s}-{uuid.uuid4().hex[:8]}"
    cap = {
        "capsule_id": cid,
        "ts": U(),
        "provenance": {
            "prev_sha256": prev_sha,
            "chain_prev": STATE["last"],
            "merkle_root": root,
        },
        "payload": {
            "exec": os.path.basename(EXF),
            "sla": os.path.basename(SLAF),
            "merkle": f"drip_seg_{s}_merkle.json",
        },
    }
    raw = json.dumps(cap, separators=(",", ":"), ensure_ascii=False).encode()
    sha = H(raw)
    open(f"{B}/{cid}.json", "wb").write(raw)
    io.open(f"{B}/{cid}.sig.json", "w").write(
        json.dumps(
            {
                "ts": U(),
                "sha256": sha,
                "hmac": [
                    hmac.new(K_SEG, raw, hashlib.sha256).hexdigest(),
                    hmac.new(K_ORG, raw, hashlib.sha256).hexdigest(),
                ],
                "hint": [H(K_SEG)[:12], H(K_ORG)[:12]],
            },
            separators=(",", ":"),
        )
    )
    STATE["last"] = HS(STATE["last"] + ":" + sha)
    STATE["segments"].append({"seg": s, "cid": cid, "sha": sha, "chain": STATE["last"]})
    links.append({"seg": s, "prev": prev_sha, "curr": sha, "chain": STATE["last"]})
    seg_caps.append(cid)
    prev = "genesis"
    if os.path.exists(LED):
        ln = [x for x in open(LED).read().splitlines() if x and x[0] == "{"]
        if ln:
            j = json.loads(ln[-1])
            prev = j.get("sha256") or j.get("provenance", {}).get("sha256", "genesis")
    line = {
        "ts": U(),
        "event": "drip-seg",
        "capsule_id": cid,
        "sha256": sha,
        "prev": prev,
        "line_sha": None,
    }
    base = json.dumps(
        {k: v for k, v in line.items() if k != "line_sha"},
        separators=(",", ":"),
        ensure_ascii=False,
    )
    line["line_sha"] = HS(base)
    io.open(LED, "a", encoding="utf-8").write(
        json.dumps(line, separators=(",", ":"), ensure_ascii=False) + "\n"
    )
    io.open(f"{B}/ledger_attest.sig.jsonl", "a").write(
        json.dumps(
            {
                "ts": U(),
                "hmac": [
                    hmac.new(K_LED, base.encode(), hashlib.sha256).hexdigest(),
                    hmac.new(K_ORG, base.encode(), hashlib.sha256).hexdigest(),
                ],
                "hint": [H(K_LED)[:12], H(K_ORG)[:12]],
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    zipfile.ZipFile(f"{B}/{cid}.zip", "w", zipfile.ZIP_DEFLATED).write(
        f"{B}/{cid}.json", arcname=f"{cid}.json"
    )
open(f"{B}/drip_chain_state.json", "w").write(json.dumps(STATE, separators=(",", ":")))
open(f"{B}/drip_links_segments.json", "w").write(
    json.dumps({"ts": U(), "links": links}, separators=(",", ":"))
)
# SUPER-META
arts = sorted([p for p in glob.glob(f"{B}/drip_seg_*_merkle.json")]) + [
    f"{B}/{c}.json" for c in seg_caps
]
mhs = [put(p) for p in arts]
ns = [bytes.fromhex(x) for x in mhs] or [b""]
while len(ns) > 1:
    ns = [
        hashlib.sha256(ns[i] + (ns[i + 1] if i + 1 < len(ns) else ns[i])).digest()
        for i in range(0, len(ns), 2)
    ]
super_root = ns[0].hex()
meta = f"EPOCHCORE-DRIP-SUPER-{uuid.uuid4().hex[:8]}"
M = {
    "capsule_id": meta,
    "ts": U(),
    "provenance": {"super_merkle": super_root, "chain_root": STATE["last"]},
    "payload": {"segments": seg_caps, "count": len(seg_caps)},
}
mraw = json.dumps(M, separators=(",", ":"), ensure_ascii=False).encode()
msha = H(mraw)
open(f"{B}/{meta}.json", "wb").write(mraw)
io.open(f"{B}/{meta}.sig.json", "w").write(
    json.dumps(
        {
            "ts": U(),
            "sha256": msha,
            "hmac": [
                hmac.new(kdf("META"), mraw, hashlib.sha256).hexdigest(),
                hmac.new(K_ORG, mraw, hashlib.sha256).hexdigest(),
            ],
            "hint": [H(kdf("META"))[:12], H(K_ORG)[:12]],
        },
        separators=(",", ":"),
    )
)
prev = "genesis"
if os.path.exists(LED):
    ln = [x for x in open(LED).read().splitlines() if x and x[0] == "{"]
    if ln:
        j = json.loads(ln[-1])
        prev = j.get("sha256") or j.get("provenance", {}).get("sha256", "genesis")
pline = {
    "ts": U(),
    "event": "drip-super",
    "capsule_id": meta,
    "sha256": msha,
    "prev": prev,
    "line_sha": None,
}
base = json.dumps(
    {k: v for k, v in pline.items() if k != "line_sha"},
    separators=(",", ":"),
    ensure_ascii=False,
)
pline["line_sha"] = HS(base)
io.open(LED, "a", encoding="utf-8").write(
    json.dumps(pline, separators=(",", ":"), ensure_ascii=False) + "\n"
)
zipfile.ZipFile(f"{B}/{meta}.zip", "w", zipfile.ZIP_DEFLATED).write(
    f"{B}/{meta}.json", arcname=f"{meta}.json"
)


# verify + DOT
def m_ok(j):
    r = j.get("provenance", {}).get("merkle_root") or j.get("provenance", {}).get(
        "super_merkle"
    )
    mf = j.get("payload", {}).get("merkle")
    if r and mf and os.path.exists(f"{B}/" + mf):
        mj = json.loads(open(f"{B}/" + mf).read())
        ns = [bytes.fromhex(x) for x in mj.get("files", [])] or [b""]
        while len(ns) > 1:
            ns = [
                hashlib.sha256(
                    ns[i] + (ns[i + 1] if i + 1 < len(ns) else ns[i])
                ).digest()
                for i in range(0, len(ns), 2)
            ]
        return ns[0].hex() == r
    return True


caps = sorted([p for p in glob.glob(f"{B}/EPOCHCORE-DRIP-*.json") if os.path.isfile(p)])
okc = 0
failc = 0
for path in caps:
    try:
        raw = open(path, "rb").read()
        okm = m_ok(json.loads(raw))
        okc += 1 if okm else 0
        failc += 0 if okm else 1
        log_event("drip.caps.verify", file=os.path.basename(path), ok=okm)
    except Exception as e:
        failc += 1
        log_event("drip.caps.error", file=os.path.basename(path), err=str(e))
prev = "genesis"
link_ok = 0
total = 0
for line in (line.strip() for line in open(LED, encoding="utf-8") if line.strip()):
    try:
        j = json.loads(line)
        base = json.dumps(
            {k: v for k, v in j.items() if k != "line_sha"},
            separators=(",", ":"),
            ensure_ascii=False,
        )
        lh = HS(base)
        total += 1
        link_ok += (
            1
            if (
                j.get("line_sha") == lh
                and (j.get("prev") == prev or j.get("prev") == "genesis")
            )
            else 0
        )
        prev = j.get("sha256", prev)
    except Exception:
        log_event("drip.ledger.error", off=total)
links = (
    json.loads(open(f"{B}/drip_links_segments.json").read())["links"]
    if os.path.exists(f"{B}/drip_links_segments.json")
    else []
)
dot = ["digraph drip { rankdir=LR; node [shape=box,fontsize=10];"]
for lk in links:
    dot.append(f'  "{lk.get("prev", "genesis")[:8]}" -> "{lk.get("curr", "")[:8]}";')
dot.append("}")
open(f"{B}/drip_links.dot", "w").write("\n".join(dot))
power = round((oks / max(1, tot)) ** POW, 6)
print(
    json.dumps(
        {
            "segments": len(seg_caps),
            "first": seg_caps[0] if seg_caps else "",
            "last": seg_caps[-1] if seg_caps else "",
            "chain_root": STATE["last"],
            "super_merkle": super_root,
            "power_index": power,
            "spent": round(spent, 2),
            "caps_ok": okc,
            "caps_fail": failc,
            "ledger_lines": total,
            "ledger_link_ok": link_ok,
            "dot": "drip_links.dot",
            "ledger": LED,
            "org_hint": H(K_ORG)[:12],
        },
        separators=(",", ":"),
    )
)
