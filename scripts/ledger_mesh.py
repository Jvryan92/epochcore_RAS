#!/usr/bin/env python3
"""
Ledger Mesh Network Simulation
This script simulates a network of interconnected agent meshes with cryptographic verification,
monetization models, and ledger-based tracking.
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
import secrets

# --- tiny utils ---------------------------------------------------------------
U = lambda: dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
H = lambda b: hashlib.sha256(b).hexdigest()
HS = lambda s: H(s.encode())
g = os.getenv
B = g('OUTDIR', './ledger')
os.makedirs(B, exist_ok=True)
SEG = max(1, min(100, int(g('SEG', '20'))))
CPS = max(1, min(100, int(g('CPS', '12'))))
SLO = int(g('SLO', '300'))
BUD = float(g('BUD', '5000'))
POW = max(1, int(g('POW', '12')))
SEED = g('SEED', 'TrueNorth')
SECSTR = g('MESH_SECRET', '')
ROOT = (bytes.fromhex(SECSTR) if SECSTR and all(c in '0123456789abcdefABCDEF' for c in SECSTR) and len(SECSTR) % 2 == 0 
        else (SECSTR.encode() if SECSTR else os.urandom(64)))
LED = f'{B}/alpha_genesis_ledger.jsonl'
CAS = f'{B}/cas'
LOG = f'{B}/alpha_genesis_log.jsonl'
os.makedirs(CAS, exist_ok=True)
io.open(LED, 'a').close()
L = lambda ev, **k: io.open(LOG, 'a', encoding='utf-8').write(json.dumps({'ts': U(), 'ev': ev, **k}, separators=(',', ':')) + '\n')
hkdf_ex = lambda salt, ikm: hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_okm(prk, info, L=32):
    T = b''
    okm = b''
    i = 1
    while len(okm) < L:
        T = hmac.new(prk, T + info + bytes([i]), hashlib.sha256).digest()
        okm += T
        i += 1
    return okm[:L]

def kdf(label):
    return hkdf_okm(hkdf_ex(HS('salt:' + label).encode(), ROOT), b'ALPHA:' + label.encode(), 32)

K_ORG = kdf('ORG')
put = lambda p: (lambda d: (lambda h: (open(f'{CAS}/{h}.bin', 'wb').write(d) if not os.path.exists(f'{CAS}/{h}.bin') else 0) or h)(H(d)))(open(p, 'rb').read())

def merkle(hs):
    ns = [bytes.fromhex(x) for x in hs] or [b'']
    while len(ns) > 1:
        ns = [hashlib.sha256(ns[i] + (ns[i+1] if i+1 < len(ns) else ns[i])).digest() for i in range(0, len(ns), 2)]
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

# --- agents & meshes ----------------------------------------------------------
AG = [
    {'id': 'agent://alpha', 'skills': ['scrape.web', 'vector.store', 'atomize.payload', 'cohere.frames', 'sandbox.dryrun'], 'rel': 0.94, 'lat': 210},
    {'id': 'agent://bravo', 'skills': ['plan.compose', 'review.policies', 'diffuse.channels', 'schedule.drip', 'rollback.diff', 'risk.scan'], 'rel': 0.92, 'lat': 250},
    {'id': 'agent://gamma', 'skills': ['echo.measure', 'blackboard.merge', 'snapshot.world', 'sign.proof', 'attest.supply'], 'rel': 0.90, 'lat': 300},
    {'id': 'agent://delta', 'skills': ['stitch.docs', 'index.graph', 'publish.codex'], 'rel': 0.91, 'lat': 230},
    {'id': 'agent://epsilon', 'skills': ['sweep.sensors', 'consensus.vote', 'rollback.diff', 'attest.supply'], 'rel': 0.89, 'lat': 275}
]

MESHES = {
    'drip': {
        'verb': 'drip.signal',
        'edges': {
            'drip.signal': ['atomize.payload', 'diffuse.channels', 'echo.measure', 'sign.proof'],
            'atomize.payload': ['hydrate.buffer'],
            'diffuse.channels': ['blackboard.merge', 'schedule.drip'],
            'echo.measure': ['replenish.cache'],
            'sign.proof': [],
            'hydrate.buffer': [],
            'blackboard.merge': [],
            'schedule.drip': [],
            'replenish.cache': []
        }
    },
    'pulse': {
        'verb': 'pulse.sync',
        'edges': {
            'pulse.sync': ['sweep.sensors', 'cohere.frames', 'echo.health', 'sign.proof'],
            'sweep.sensors': ['hydrate.buffer'],
            'cohere.frames': ['vector.store'],
            'echo.health': ['blackboard.merge'],
            'sign.proof': [],
            'hydrate.buffer': [],
            'vector.store': [],
            'blackboard.merge': []
        }
    },
    'weave': {
        'verb': 'weave.bind',
        'edges': {
            'weave.bind': ['stitch.docs', 'index.graph', 'publish.codex', 'sign.proof'],
            'stitch.docs': ['vector.store'],
            'index.graph': ['attest.supply'],
            'publish.codex': ['blackboard.merge'],
            'sign.proof': [],
            'vector.store': [],
            'attest.supply': [],
            'blackboard.merge': []
        }
    }
}

# monetization primitives
CH = [('Website', 0.00, 0.00), ('Ads', 1.2, 0.00), ('Newsletter', 0.2, 0.00), ('Partners', 0.0, 0.12), ('Marketplace', 0.0, 0.08)]
PL = [('Free', 0.0), ('Starter', 19.0), ('Pro', 79.0), ('Enterprise', 399.0)]
bandit = {c: {p: 0 for _, p in PL} for c, _, _ in CH}
wins = {c: {p: 1 for _, p in PL} for c, _, _ in CH}

def price_pick(ch):
    return (random.choice(PL)[1] if random.random() < 0.12 else max(PL, key=lambda x: wins[ch][x[1]] / (bandit[ch][x[1]] + 1))[1])

def conv_rate(ch, price):
    base = {'Website': 0.06, 'Ads': 0.03, 'Newsletter': 0.08, 'Partners': 0.05, 'Marketplace': 0.04}[ch]
    mult = 1.18 if price in (19.0, 79.0) else (0.72 if price >= 399.0 else 1.0)
    return max(0.002, min(0.22, base * mult + random.uniform(-0.01, 0.01)))

caps_pulse = ['discover', 'plan', 'execute', 'review', 'publish']
PLANS = [('U1', 10000, 0.002), ('U2', 100000, 0.0014), ('U3', 1000000, 0.0009)]

# --- run meshes ---------------------------------------------------------------
meta = []
super_roots = []
last_ring = {}
TOTAL = {'rev': 0.0, 'cost': 0.0, 'gm': 0.0}

for name, conf in MESHES.items():
    pre = name
    verb = conf['verb']
    edges = conf['edges']
    ORG = HS('genesis:' + pre + ':' + SEED)
    
    # headers
    open(f'{B}/{pre}_ontology.json', 'w').write(json.dumps({'ts': U(), 'graph': edges}, separators=(',', ':')))
    open(f'{B}/{pre}_registry.json', 'w').write(json.dumps({'ts': U(), 'agents': [{'agent_id': a['id'], 'skills': a['skills'], 'rel': a['rel'], 'lat': a['lat']} for a in AG]}, separators=(',', ':')))
    
    GR = {
        'version': '1.0',
        'allow': {
            'agent://alpha': ['vector.store', 'atomize.payload', 'cohere.frames', 'sandbox.dryrun'],
            'agent://bravo': ['diffuse.channels', 'review.policies', 'schedule.drip', 'rollback.diff', 'risk.scan'],
            'agent://gamma': ['echo.measure', 'blackboard.merge', 'sign.proof', 'snapshot.world', 'attest.supply'],
            'agent://delta': ['stitch.docs', 'index.graph', 'publish.codex'],
            'agent://epsilon': ['sweep.sensors', 'consensus.vote', 'rollback.diff', 'attest.supply']
        },
        'multisig': {'>=50USD': ['agent://bravo', 'agent://gamma']}
    }
    open(f'{B}/{pre}_grants.json', 'w').write(json.dumps(GR, separators=(',', ':')))
    
    POL = {
        'rules': [
            {'if': f'cap==\"{verb}\"', 'require': ['quorum==2', 'evidence']},
            {'if': 'usd>=50', 'require': ['quorum==2']},
            {'if': 'risk.radius!=\"low\"', 'require': ['backup', 'shadow_or_dryrun']}
        ]
    }
    open(f'{B}/{pre}_policies.json', 'w').write(json.dumps(POL, separators=(',', ':')))
    
    # dag+state
    CHAIN = dfs_chain(edges, verb)
    open(f'{B}/{pre}_dag_base.json', 'w').write(json.dumps({'ts': U(), 'chain': CHAIN}, separators=(',', ':')))
    STATE = {'ts': U(), 'root': ORG, 'last': 'genesis', 'segments': []}
    open(f'{B}/{pre}_chain_state.json', 'w').write(json.dumps(STATE, separators=(',', ':')))
    
    # metrics
    mesh_rev = mesh_cost = mesh_gm = 0.0
    seg_caps = []
    links = []
    
    # segments
    for s in range(1, SEG + 1):
        PRK = hkdf_ex(HS(f'{pre.upper()}:{s}:{SEED}').encode(), ROOT)
        K_SEG = hkdf_okm(PRK, b'SEG', 32)
        K_LED = hkdf_okm(PRK, b'LED', 32)
        cycles = []
        pb = hashlib.sha256()
        segR = segC = 0.0
        p95s = []
        
        # ---- cycles
        for c in range(1, CPS + 1):
            lat = []
            okc = True
            usd_c = 0.0
            mon = {}
            
            # base chain walk
            for j, cap in enumerate(CHAIN):
                cost = round(0.03 + 0.02 * j, 2)
                usd = round(cost * 100, 2)
                risk_low = (random.random() < 0.74)
                lat.append(random.randint(160, 340))
                okc = okc and risk_low and (usd < 420) and (segR <= BUD)
                usd_c += usd
                pb.update(f'{pre}:{s}:{c}:{cap}:pp'.encode())
                pb.update(f'{pre}:{s}:{c}:{cap}:pr'.encode())
                pb.update(f'{pre}:{s}:{c}:{cap}:cm'.encode())
            
            # monetization by mesh
            if pre == 'drip':
                ch, cpc, take = random.choice(CH)
                price = price_pick(ch)
                traffic = random.randint(900, 3500)
                clicks = int(traffic * (0.05 if cpc > 0 else 0.02) + random.randint(0, 45))
                signups = int(clicks * conv_rate(ch, price))
                arpu = (price * 0.9 if price > 0 else 0.0)
                churn = max(0.02, 0.16 - 0.05 * (price > 0) - 0.03 * (ch in ('Newsletter', 'Website'))) + random.uniform(-0.01, 0.01)
                ltv = arpu / max(0.02, min(0.3, churn))
                rev = signups * price + signups * ltv * 0.20
                cost = clicks * cpc + rev * take
                segR += rev
                segC += cost
                bandit[ch][price] += 1
                wins[ch][price] += max(0, signups)
                mon = {'engine': 'bandit', 'ch': ch, 'price': price, 'signups': signups, 'rev': round(rev, 2), 'cost': round(cost, 2)}
            elif pre == 'pulse':
                tR = tC = 0.0
                for i, cap in enumerate(caps_pulse):
                    base = 0.02 + 0.03 * i
                    bids = [
                        ('alpha', round(base * (1.2 - random.random() * 0.4) / 0.94, 4)),
                        ('bravo', round(base * (1.2 - random.random() * 0.4) / 0.92, 4)),
                        ('gamma', round(base * (1.2 - random.random() * 0.4) / 0.90, 4))
                    ]
                    aid, price = min(bids, key=lambda x: x[1])
                    demand = random.randint(5, 32)
                    take = 0.12 + 0.03 * (cap in ('publish', 'plan'))
                    revenue = price * demand * (1 + 0.5 * (cap == 'publish'))
                    payout = revenue * (1 - take)
                    tR += revenue
                    tC += payout
                segR += tR
                segC += tC
                mon = {'engine': 'auction', 'rev': round(tR, 2), 'payout': round(tC, 2)}
            else:  # weave -> SaaS usage
                plan, quota, ppc = random.choice(PLANS)
                use = random.randint(int(0.35 * quota), quota)
                over = max(0, use - quota)
                rev = quota * ppc + over * ppc * 1.6
                cost = use * ppc * 0.38 + 0.03 * use
                segR += rev
                segC += cost
                mon = {'engine': 'saas', 'plan': plan, 'use': use, 'rev': round(rev, 2), 'cost': round(cost, 2)}
            
            idx = max(0, int(0.95 * (len(lat) - 1)))
            p95 = sorted(lat)[idx]
            p95s.append(p95)
            cycles.append({'c': c, 'ok': okc, 'p95': p95, 'usd': round(usd_c / 100.0, 2), 'mon': mon})
        
        # ---- exec & SLA
        EXF = f'{B}/{pre}_seg_{s}_exec.json'
        open(EXF, 'w').write(json.dumps({'ts': U(), 'cycles': cycles, 'pbft_hash': pb.hexdigest()}, separators=(',', ':')))
        SLAF = f'{B}/{pre}_seg_{s}_sla.json'
        seg_p95 = (sorted(p95s)[max(0, int(0.95 * (len(p95s) - 1)))] if p95s else 0)
        open(SLAF, 'w').write(json.dumps({'ts': U(), 'p95_ms': seg_p95, 'ok': seg_p95 <= SLO, 'seg_rev': round(segR, 2), 'seg_cost': round(segC, 2), 'seg_gm': round(segR - segC, 2)}, separators=(',', ':')))
        hs = [put(EXF), put(SLAF)]
        ROOTM = merkle(hs)
        open(f'{B}/{pre}_seg_{s}_merkle.json', 'w').write(json.dumps({'ts': U(), 'files': hs, 'root': ROOTM}, separators=(',', ':')))
        
        # ---- capsule
        prev_sha = STATE['segments'][-1]['sha'] if STATE['segments'] else 'genesis'
        cid = f'ALPHA-{pre.upper()}-SEG{s}-{uuid.uuid4().hex[:8]}'
        cap = {
            'capsule_id': cid,
            'ts': U(),
            'provenance': {'prev_sha256': prev_sha, 'chain_prev': STATE['last'], 'merkle_root': ROOTM},
            'payload': {'exec': os.path.basename(EXF), 'sla': os.path.basename(SLAF), 'merkle': f'{pre}_seg_{s}_merkle.json'}
        }
        raw = json.dumps(cap, separators=(',', ':'), ensure_ascii=False).encode()
        sha = H(raw)
        open(f'{B}/{cid}.json', 'wb').write(raw)
        io.open(f'{B}/{cid}.sig.json', 'w').write(json.dumps({'ts': U(), 'sha256': sha, 'hmac': [hmac.new(K_SEG, raw, hashlib.sha256).hexdigest(), hmac.new(K_ORG, raw, hashlib.sha256).hexdigest()], 'hint': [H(K_SEG)[:12], H(K_ORG)[:12]]}, separators=(',', ':')))
        STATE['last'] = HS(STATE['last'] + ':' + sha)
        STATE['segments'].append({'seg': s, 'cid': cid, 'sha': sha, 'chain': STATE['last']})
        links.append({'seg': s, 'prev': prev_sha, 'curr': sha, 'chain': STATE['last']})
        seg_caps.append(cid)
        
        # ledger
        prev = 'genesis'
        if os.path.exists(LED):
            ln = [x for x in open(LED).read().splitlines() if x and x[0] == '{']
            if ln:
                j = json.loads(ln[-1])
                prev = (j.get('sha256') or j.get('provenance', {}).get('sha256', 'genesis'))
        line = {'ts': U(), 'mesh': pre, 'event': 'segment', 'capsule_id': cid, 'sha256': sha, 'prev': prev, 'p95': seg_p95, 'rev': round(segR, 2), 'cost': round(segC, 2), 'gm': round(segR - segC, 2), 'line_sha': None}
        base = json.dumps({k: v for k, v in line.items() if k != 'line_sha'}, separators=(',', ':'), ensure_ascii=False)
        line['line_sha'] = HS(base)
        io.open(LED, 'a', encoding='utf-8').write(json.dumps(line, separators=(',', ':'), ensure_ascii=False) + '\n')
        
        # bundle (zip)
        zipfile.ZipFile(f'{B}/{cid}.zip', 'w', zipfile.ZIP_DEFLATED).write(f'{B}/{cid}.json', arcname=f'{cid}.json')
        mesh_rev += segR
        mesh_cost += segC
        mesh_gm += max(0.0, segR - segC)
    
    # persist state + links
    open(f'{B}/{pre}_chain_state.json', 'w').write(json.dumps(STATE, separators=(',', ':')))
    open(f'{B}/{pre}_links_segments.json', 'w').write(json.dumps({'ts': U(), 'links': links}, separators=(',', ':')))
    
    # super meta
    arts = sorted([p for p in glob.glob(f'{B}/{pre}_seg_*_merkle.json')]) + [f'{B}/{c}.json' for c in seg_caps]
    mhs = [put(p) for p in arts]
    ns = [bytes.fromhex(x) for x in mhs] or [b'']
    while len(ns) > 1:
        ns = [hashlib.sha256(ns[i] + (ns[i+1] if i+1 < len(ns) else ns[i])).digest() for i in range(0, len(ns), 2)]
    sroot = ns[0].hex()
    meta_id = f'ALPHA-{pre.upper()}-SUPER-{uuid.uuid4().hex[:8]}'
    M = {
        'capsule_id': meta_id,
        'ts': U(),
        'provenance': {'super_merkle': sroot, 'chain_root': STATE['last']},
        'payload': {'segments': seg_caps, 'count': len(seg_caps), 'rev_total': round(mesh_rev, 2), 'cost_total': round(mesh_cost, 2), 'gm_total': round(mesh_gm, 2)}
    }
    mraw = json.dumps(M, separators=(',', ':'), ensure_ascii=False).encode()
    msha = H(mraw)
    open(f'{B}/{meta_id}.json', 'wb').write(mraw)
    io.open(f'{B}/{meta_id}.sig.json', 'w').write(json.dumps({'ts': U(), 'sha256': msha, 'hmac': [hmac.new(kdf(pre + "-META"), mraw, hashlib.sha256).hexdigest(), hmac.new(K_ORG, mraw, hashlib.sha256).hexdigest()], 'hint': [H(kdf(pre + "-META"))[:12], H(K_ORG)[:12]]}, separators=(',', ':')))
    prev = 'genesis'
    if os.path.exists(LED):
        ln = [x for x in open(LED).read().splitlines() if x and x[0] == '{']
        if ln:
            j = json.loads(ln[-1])
            prev = (j.get('sha256') or j.get('provenance', {}).get('sha256', 'genesis'))
    pline = {'ts': U(), 'mesh': pre, 'event': 'super', 'capsule_id': meta_id, 'sha256': msha, 'prev': prev, 'line_sha': None}
    base = json.dumps({k: v for k, v in pline.items() if k != 'line_sha'}, separators=(',', ':'), ensure_ascii=False)
    pline['line_sha'] = HS(base)
    io.open(LED, 'a', encoding='utf-8').write(json.dumps(pline, separators=(',', ':'), ensure_ascii=False) + '\n')
    zipfile.ZipFile(f'{B}/{meta_id}.zip', 'w', zipfile.ZIP_DEFLATED).write(f'{B}/{meta_id}.json', arcname=f'{meta_id}.json')
    
    # graph
    lnks = json.loads(open(f'{B}/{pre}_links_segments.json').read())['links'] if os.path.exists(f'{B}/{pre}_links_segments.json') else []
    dot = [f'digraph {pre} {{ rankdir=LR; node [shape=box,fontsize=10];']
    for lk in lnks:
        dot.append(f'  \"{lk.get("prev", "genesis")[:8]}\" -> \"{lk.get("curr", "")[:8]}\";')
    dot.append('}')
    open(f'{B}/{pre}_links.dot', 'w').write('\n'.join(dot))
    
    # meta rollup
    meta.append({'mesh': pre, 'super_root': sroot, 'last_chain': STATE['last'], 'segments': len(seg_caps), 'rev_total': round(mesh_rev, 2), 'cost_total': round(mesh_cost, 2), 'gm_total': round(mesh_gm, 2)})
    super_roots.append(sroot)
    last_ring[pre] = STATE['last']
    TOTAL['rev'] += mesh_rev
    TOTAL['cost'] += mesh_cost
    TOTAL['gm'] += mesh_gm

# --- hyper-meta over meshes ---------------------------------------------------
hs = [bytes.fromhex(H(x.encode())) for x in super_roots] or [b'']
while len(hs) > 1:
    hs = [hashlib.sha256(hs[i] + (hs[i+1] if i+1 < len(hs) else hs[i])).digest() for i in range(0, len(hs), 2)]
hyper_root = hs[0].hex()
hyper = f'ALPHA-HYPERMETA-{uuid.uuid4().hex[:8]}'
HYP = {
    'capsule_id': hyper,
    'ts': U(),
    'provenance': {'hyper_merkle': hyper_root, 'rings': [m['last_chain'] for m in meta]},
    'payload': {
        'meshes': meta,
        'count': len(meta),
        'rev_total': round(TOTAL['rev'], 2),
        'cost_total': round(TOTAL['cost'], 2),
        'gm_total': round(TOTAL['gm'], 2),
        'roi': round((TOTAL['rev'] - TOTAL['cost']) / max(1.0, TOTAL['cost']), 4)
    }
}
hraw = json.dumps(HYP, separators=(',', ':'), ensure_ascii=False).encode()
hsha = H(hraw)
open(f'{B}/{hyper}.json', 'wb').write(hraw)
io.open(f'{B}/{hyper}.sig.json', 'w').write(json.dumps({'ts': U(), 'sha256': hsha, 'hmac': [hmac.new(kdf("HYPER"), hraw, hashlib.sha256).hexdigest(), hmac.new(K_ORG, hraw, hashlib.sha256).hexdigest()], 'hint': [H(kdf("HYPER"))[:12], H(K_ORG)[:12]]}, separators=(',', ':')))
prev = 'genesis'
if os.path.exists(LED):
    ln = [x for x in open(LED).read().splitlines() if x and x[0] == '{']
    if ln:
        j = json.loads(ln[-1])
        prev = (j.get('sha256') or j.get('provenance', {}).get('sha256', 'genesis'))
hline = {'ts': U(), 'mesh': 'intermesh', 'event': 'hyper', 'capsule_id': hyper, 'sha256': hsha, 'prev': prev, 'line_sha': None}
base = json.dumps({k: v for k, v in hline.items() if k != 'line_sha'}, separators=(',', ':'), ensure_ascii=False)
hline['line_sha'] = HS(base)
io.open(LED, 'a', encoding='utf-8').write(json.dumps(hline, separators=(',', ':'), ensure_ascii=False) + '\n')
zipfile.ZipFile(f'{B}/{hyper}.zip', 'w', zipfile.ZIP_DEFLATED).write(f'{B}/{hyper}.json', arcname=f'{hyper}.json')
order = ['drip', 'pulse', 'weave']
ring = ['digraph intermesh { rankdir=LR; node [shape=ellipse,fontsize=11,style=filled];']
for i in range(len(order)):
    a = order[i]
    b = order[(i+1) % len(order)]
    ring.append(f'  \"{a}:{last_ring.get(a, "genesis")[:8]}\" -> \"{b}:{last_ring.get(b, "genesis")[:8]}\";')
ring.append('}')
open(f'{B}/intermesh.dot', 'w').write('\n'.join(ring))

# print final rollup
print(json.dumps({
    'ok': True,
    'hyper_root': hyper_root,
    'ledger': LED,
    'graphs': {'drip': 'drip_links.dot', 'pulse': 'pulse_links.dot', 'weave': 'weave_links.dot', 'intermesh': 'intermesh.dot'},
    'totals': {
        'rev': round(TOTAL['rev'], 2),
        'cost': round(TOTAL['cost'], 2),
        'gm': round(TOTAL['gm'], 2),
        'roi': round((TOTAL['rev'] - TOTAL['cost']) / max(1.0, TOTAL['cost']), 4)
    }
}, separators=(',', ':')))
