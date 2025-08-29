#!/usr/bin/env python3
"""
Mesh/Capsule/Ledger Generator
Refactored from user-provided one-liner for maintainability and automation.
Usage:
  python scripts/generate_mesh_capsule_ledger.py
Environment variables:
  MESH_SECRET, SEG, CPS, POW, SLO, BUD, OUTDIR, SEED
"""
import os
import json
import hashlib
import uuid
import datetime as dt
import zipfile
import glob
import random
import statistics
import hmac
import io
import sys

# Utility functions


def U():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def H(b):
    return hashlib.sha256(b).hexdigest()


def HS(s):
    return H(s.encode())


g = os.getenv
B = g("OUTDIR", "./ledger")
os.makedirs(B, exist_ok=True)
SEG = max(1, min(100, int(g("SEG", "20"))))
CPS = max(1, min(100, int(g("CPS", "12"))))
SLO = int(g("SLO", "300"))
BUD = float(g("BUD", "5000"))
POW = max(1, int(g("POW", "12")))
SEED = g("SEED", "TrueNorth")
SECSTR = g("MESH_SECRET", "mesh-demo-secret")
LED = f"{B}/ledger_main.jsonl"
CAS = f"{B}/cas"
LOG = f"{B}/intermesh_log.jsonl"
os.makedirs(CAS, exist_ok=True)
io.open(LED, "a").close()


def log_event(ev, **k):
    entry = {"ts": U(), "ev": ev}
    entry.update(k)
    io.open(LOG, "a", encoding="utf-8").write(
        json.dumps(entry, separators=(",", ":")) + "\n"
    )


# --- hkdf

# --- hkdf


def parse_sec(s):
    t = s.strip()
    try:
        if all(c in "0123456789abcdefABCDEF" for c in t) and len(t) % 2 == 0:
            return bytes.fromhex(t)
        else:
            return t.encode()
    except Exception:
        return t.encode()


ROOT = parse_sec(SECSTR)


def hkdf_ex(salt, ikm):
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def hkdf_okm(prk, info, L=32):
    T = b""
    okm = b""
    i = 1
    while len(okm) < L:
        T = hmac.new(prk, T + info + bytes([i]), hashlib.sha256).digest()
    okm += T
    i += 1
    return okm[:L]


def kdf(label):
    return hkdf_okm(
        hkdf_ex(HS("salt:" + label).encode(), ROOT), b"IMESH:" + label.encode(), 32
    )


K_ORG = kdf("ORG")
# --- agents
AG = [
    {
        "id": "agent://alpha",
        "skills": [
            "scrape.web",
            "vector.store",
            "atomize.payload",
            "cohere.frames",
            "sandbox.dryrun",
        ],
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
        ],
        "rel": 0.90,
        "lat": 300,
    },
    {
        "id": "agent://delta",
        "skills": ["stitch.docs", "index.graph", "publish.codex", "risk.scan"],
        "rel": 0.91,
        "lat": 230,
    },
    {
        "id": "agent://epsilon",
        "skills": ["sweep.sensors", "consensus.vote", "rollback.diff", "attest.supply"],
        "rel": 0.89,
        "lat": 275,
    },
]
# --- meshes
MESHES = {
    "drip": {
        "verb": "drip.signal",
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
        },
    },
    "pulse": {
        "verb": "pulse.sync",
        "edges": {
            "pulse.sync": [
                "sweep.sensors",
                "cohere.frames",
                "echo.health",
                "sign.proof",
            ],
            "sweep.sensors": ["hydrate.buffer"],
            "cohere.frames": ["vector.store"],
            "echo.health": ["blackboard.merge"],
            "sign.proof": [],
            "hydrate.buffer": [],
            "vector.store": [],
            "blackboard.merge": [],
        },
    },
    "weave": {
        "verb": "weave.bind",
        "edges": {
            "weave.bind": ["stitch.docs", "index.graph", "publish.codex", "sign.proof"],
            "stitch.docs": ["vector.store"],
            "index.graph": ["attest.supply"],
            "publish.codex": ["blackboard.merge"],
            "sign.proof": [],
            "vector.store": [],
            "attest.supply": [],
            "blackboard.merge": [],
        },
    },
}


# --- helpers
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


def dfs_chain(edges, root):
    seen = set()
    out = []
    sys.setrecursionlimit(10000)

    def dfs(x):
        if x in seen:
            return
        for y in edges.get(x, []):
            dfs(y)
        seen.add(x)
        out.append(x)

    dfs(root)
    return [x for x in out if x != root] + [root]


# --- run each mesh
mesh_meta = []
super_roots = []
mesh_last = {}
for name, conf in MESHES.items():
    pre = name
    verb = conf["verb"]
    edges = conf["edges"]
    ORG = HS("genesis:" + pre + ":" + SEED)
    # files
    open(f"{B}/{pre}_ontology.json", "w").write(
        json.dumps({"ts": U(), "graph": edges}, separators=(",", ":"))
    )
    open(f"{B}/{pre}_registry.json", "w").write(
        json.dumps(
            {
                "ts": U(),
                "agents": [
                    {
                        "agent_id": a["id"],
                        "skills": a["skills"],
                        "rel": a["rel"],
                        "lat": a["lat"],
                    }
                    for a in AG
                ],
            },
            separators=(",", ":"),
        )
    )
    GR = {
        "version": "1.0",
        "allow": {
            "agent://alpha": [
                "vector.store",
                "atomize.payload",
                "cohere.frames",
                "sandbox.dryrun",
            ],
            "agent://bravo": [
                "diffuse.channels",
                "review.policies",
                "schedule.drip",
                "rollback.diff",
                "risk.scan",
            ],
            "agent://gamma": [
                "echo.measure",
                "blackboard.merge",
                "sign.proof",
                "snapshot.world",
                "attest.supply",
            ],
            "agent://delta": ["stitch.docs", "index.graph", "publish.codex"],
            "agent://epsilon": [
                "sweep.sensors",
                "consensus.vote",
                "rollback.diff",
                "attest.supply",
            ],
        },
        "multisig": {">=50USD": ["agent://bravo", "agent://gamma"]},
    }
    open(f"{B}/{pre}_grants.json", "w").write(json.dumps(GR, separators=(",", ":")))
    POL = {
        "rules": [
            {"if": f'cap=="{verb}"', "require": ["quorum==2", "evidence"]},
            {"if": "usd>=50", "require": ["quorum==2"]},
            {"if": 'risk.radius!="low"', "require": ["backup", "shadow_or_dryrun"]},
        ]
    }
    open(f"{B}/{pre}_policies.json", "w").write(json.dumps(POL, separators=(",", ":")))
    HB = [a["lat"] + random.randint(-40, 60) for a in AG]
    open(f"{B}/{pre}_heartbeats.jsonl", "w").write(
        "\n".join(
            json.dumps(
                {"agent": AG[i]["id"], "ts": U(), "latency_ms": HB[i]},
                separators=(",", ":"),
            )
            for i in range(len(AG))
        )
    )
    mu = sum(HB) / len(HB)
    sd = statistics.pstdev(HB) or 1.0
    AN = [
        {"agent": AG[i]["id"], "lat": HB[i], "z": round((HB[i] - mu) / sd, 2)}
        for i in range(len(AG))
        if abs((HB[i] - mu) / sd) > 1.5
    ]
    open(f"{B}/{pre}_anomalies.json", "w").write(
        json.dumps({"ts": U(), "mean_ms": mu, "anomalies": AN}, separators=(",", ":"))
    )
    CH = dfs_chain(edges, verb)
    open(f"{B}/{pre}_dag_base.json", "w").write(
        json.dumps({"ts": U(), "chain": CH}, separators=(",", ":"))
    )
    STATE = {"ts": U(), "root": ORG, "last": "genesis", "segments": []}
    open(f"{B}/{pre}_chain_state.json", "w").write(
        json.dumps(STATE, separators=(",", ":"))
    )
    # segments × cycles
    seg_caps = []
    links = []
    spent = 0.0
    oks = tot = 0
    for s in range(1, SEG + 1):
        PRK = hkdf_ex(HS(f"{pre.upper()}:{s}:{SEED}").encode(), ROOT)
        K_SEG = hkdf_okm(PRK, b"SEG", 32)
        K_LED = hkdf_okm(PRK, b"LED", 32)
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
                    "radius": ("low" if random.random() < 0.74 else "med"),
                    "var_usd": round(random.uniform(0.5, 28.0), 2),
                }
                lat.append(random.randint(160, 340))
                okc = (
                    okc and (risk["radius"] == "low") and (usd < 420) and (spent <= BUD)
                )
                usd_c += usd
                pb.update(f"{pre}:{s}:{c}:{cap}:pp".encode())
                pb.update(f"{pre}:{s}:{c}:{cap}:pr".encode())
                pb.update(f"{pre}:{s}:{c}:{cap}:cm".encode())
            spent += usd_c / 100.0
            p95 = sorted(lat)[int(0.95 * len(lat)) - 1]
            cycles.append(
                {"c": c, "ok": okc, "p95": p95, "usd": round(usd_c / 100.0, 2)}
            )
            oks += 1 if okc else 0
            tot += 1
        EXF = f"{B}/{pre}_seg_{s}_exec.json"
        open(EXF, "w").write(
            json.dumps(
                {"ts": U(), "cycles": cycles, "pbft_hash": pb.hexdigest()},
                separators=(",", ":"),
            )
        )
        SLAF = f"{B}/{pre}_seg_{s}_sla.json"
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
        open(f"{B}/{pre}_seg_{s}_merkle.json", "w").write(
            json.dumps({"ts": U(), "files": hs, "root": root}, separators=(",", ":"))
        )
        prev_sha = STATE["segments"][-1]["sha"] if STATE["segments"] else "genesis"
        cid = f"EPOCHCORE-{pre.upper()}-SEG{s}-{uuid.uuid4().hex[:8]}"
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
                "merkle": f"{pre}_seg_{s}_merkle.json",
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
        STATE["segments"].append(
            {"seg": s, "cid": cid, "sha": sha, "chain": STATE["last"]}
        )
        links.append({"seg": s, "prev": prev_sha, "curr": sha, "chain": STATE["last"]})
        seg_caps.append(cid)
        prev = "genesis"
        if os.path.exists(LED):
            ln = [x for x in open(LED).read().splitlines() if x and x[0] == "{"]
            if ln:
                j = json.loads(ln[-1])
                prev = j.get("sha256") or j.get("provenance", {}).get(
                    "sha256", "genesis"
                )
        line = {
            "ts": U(),
            "mesh": pre,
            "event": "segment",
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
        io.open(f"{B}/{pre}_ledger_attest.sig.jsonl", "a").write(
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
    # persist + links
    open(f"{B}/{pre}_chain_state.json", "w").write(
        json.dumps(STATE, separators=(",", ":"))
    )
    open(f"{B}/{pre}_links_segments.json", "w").write(
        json.dumps({"ts": U(), "links": links}, separators=(",", ":"))
    )
    # super
    arts = sorted([p for p in glob.glob(f"{B}/{pre}_seg_*_merkle.json")]) + [
        f"{B}/{c}.json" for c in seg_caps
    ]
    mhs = [put(p) for p in arts]
    ns = [bytes.fromhex(x) for x in mhs] or [b""]
    while len(ns) > 1:
        ns = [
            hashlib.sha256(ns[i] + (ns[i + 1] if i + 1 < len(ns) else ns[i])).digest()
            for i in range(0, len(ns), 2)
        ]
    sroot = ns[0].hex()
    meta = f"EPOCHCORE-{pre.upper()}-SUPER-{uuid.uuid4().hex[:8]}"
    M = {
        "capsule_id": meta,
        "ts": U(),
        "provenance": {"super_merkle": sroot, "chain_root": STATE["last"]},
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
                    hmac.new(kdf(pre + "-META"), mraw, hashlib.sha256).hexdigest(),
                    hmac.new(K_ORG, mraw, hashlib.sha256).hexdigest(),
                ],
                "hint": [H(kdf(pre + "-META"))[:12], H(K_ORG)[:12]],
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
        "mesh": pre,
        "event": "super",
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
    # mesh graph
    links = (
        json.loads(open(f"{B}/{pre}_links_segments.json").read())["links"]
        if os.path.exists(f"{B}/{pre}_links_segments.json")
        else []
    )
    dot = [f"digraph {pre} {{ rankdir=LR; node [shape=box,fontsize=10];"]
    for lk in links:
        dot.append(
            f'  "{lk.get("prev", "genesis")[:8]}" -> "{lk.get("curr", "")[:8]}";'
        )
    dot.append("}")
    open(f"{B}/{pre}_links.dot", "w").write("\n".join(dot))
    power = round(((sum(1 for p in seg_caps) / max(1, SEG * CPS)) ** POW), 6)
    mesh_meta.append(
        {
            "mesh": pre,
            "super_root": sroot,
            "last_chain": STATE["last"],
            "power": power,
            "segments": len(seg_caps),
        }
    )
    super_roots.append(sroot)
    mesh_last[pre] = STATE["last"]
# --- hyper-meta over all meshes
hs = [bytes.fromhex(H(x.encode())) for x in super_roots] or [b""]
while len(hs) > 1:
    hs = [
        hashlib.sha256(hs[i] + (hs[i + 1] if i + 1 < len(hs) else hs[i])).digest()
        for i in range(0, len(hs), 2)
    ]
hyper_root = hs[0].hex()
hyper = f"EPOCHCORE-HYPERMETA-{uuid.uuid4().hex[:8]}"
HYP = {
    "capsule_id": hyper,
    "ts": U(),
    "provenance": {
        "hyper_merkle": hyper_root,
        "rings": [m["last_chain"] for m in mesh_meta],
    },
    "payload": {"meshes": mesh_meta, "count": len(mesh_meta)},
}
hraw = json.dumps(HYP, separators=(",", ":"), ensure_ascii=False).encode()
hsha = H(hraw)
open(f"{B}/{hyper}.json", "wb").write(hraw)
io.open(f"{B}/{hyper}.sig.json", "w").write(
    json.dumps(
        {
            "ts": U(),
            "sha256": hsha,
            "hmac": [
                hmac.new(kdf("HYPER"), hraw, hashlib.sha256).hexdigest(),
                hmac.new(K_ORG, hraw, hashlib.sha256).hexdigest(),
            ],
            "hint": [H(kdf("HYPER"))[:12], H(K_ORG)[:12]],
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
hline = {
    "ts": U(),
    "mesh": "intermesh",
    "event": "hyper",
    "capsule_id": hyper,
    "sha256": hsha,
    "prev": prev,
    "line_sha": None,
}
base = json.dumps(
    {k: v for k, v in hline.items() if k != "line_sha"},
    separators=(",", ":"),
    ensure_ascii=False,
)
hline["line_sha"] = HS(base)
io.open(LED, "a", encoding="utf-8").write(
    json.dumps(hline, separators=(",", ":"), ensure_ascii=False) + "\n"
)
zipfile.ZipFile(f"{B}/{hyper}.zip", "w", zipfile.ZIP_DEFLATED).write(
    f"{B}/{hyper}.json", arcname=f"{hyper}.json"
)
# intermesh DOT ring (drip->pulse->weave->drip)
order = ["drip", "pulse", "weave"]
ring = [
    "digraph intermesh { rankdir=LR; node [shape=ellipse,fontsize=11,style=filled];"
]
for i, m in enumerate(order):
    a = order[i]
    b = order[(i + 1) % len(order)]
    ring.append(
        (
            f'  "{a}:{mesh_last.get(a, "genesis")[:8]}" -> '
            f'"{b}:{mesh_last.get(b, "genesis")[:8]}";'
        )
    )
ring.append("}")
open(f"{B}/intermesh.dot", "w").write("\n".join(ring))
print(
    json.dumps(
        {
            "ok": True,
            "meshes": [m["mesh"] for m in mesh_meta],
            "super_roots": [m["super_root"] for m in mesh_meta],
            "hyper_root": hyper_root,
            "ledger": LED,
            "graphs": {
                "drip": "drip_links.dot",
                "pulse": "pulse_links.dot",
                "weave": "weave_links.dot",
                "intermesh": "intermesh.dot",
            },
        },
        separators=(",", ":"),
    )
)
