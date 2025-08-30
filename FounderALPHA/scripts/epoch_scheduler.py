#!/usr/bin/env python3
"""
epoch_scheduler.py — Topological trigger runner with phased cycles

- Loads triggers from epoch_triggers.jsonl and edges from epoch_triggers_edges.csv
- Performs dependency-aware (topological) iteration
- Applies a repeating, safe 3-phase cycle:
    1) compress    — lightweight optimize/validate pass
    2) ultracomp   — deeper optimize/validate pass
    3) ignite      — "execute step" placeholder (safe no-op unless you add handlers)

Usage examples:
  python3 epoch_scheduler.py --dry-run --limit 50
  python3 epoch_scheduler.py --family ASTRA --phase-window 5 --intensity 1000
  python3 epoch_scheduler.py --start 100 --end 300 --json-log out.jsonl

This script does NOT execute arbitrary code. "ignite" is a placeholder that simply logs.
You can add your own safe handlers in `run_step()` to hook into your systems.
"""

import argparse, sys, json, csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, deque

PACKDIR = Path(__file__).resolve().parent
JSONL = PACKDIR / "epoch_triggers.jsonl"
EDGES = PACKDIR / "epoch_triggers_edges.csv"

def load_nodes(jsonl_path):
    nodes = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                nodes[int(r["id"])] = r
    return nodes

def load_edges(csv_path):
    edges = []
    if not csv_path.exists():
        return edges
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                edges.append((int(row["from"]), int(row["to"]))
            except Exception:
                continue
    return edges

def topo_order(nodes, edges, start=None, end=None):
    # Build graph
    N = set(nodes.keys())
    if start is not None or end is not None:
        N = {i for i in N if (start is None or i >= start) and (end is None or i <= end)}
    adj = defaultdict(list)
    indeg = {i: 0 for i in N}
    for u, v in edges:
        if u in N and v in N:
            adj[u].append(v)
            indeg[v] += 1
    q = deque([i for i in N if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    # If cycle exists, append remaining nodes in id order to avoid stalling
    if len(order) < len(N):
        remaining = [i for i in N if i not in set(order)]
        order.extend(sorted(remaining))
    return order

def policy_gate(record):
    """Minimal policy gate. Extend as needed."""
    blocked_terms = ["explosive", "weapon", "malware", "harm"]
    blob = " ".join([str(record.get(k, "")) for k in ("title","exec","comp","full")]).lower()
    for t in blocked_terms:
        if t in blob:
            return False, f"blocked_term:{t}"
    return True, "ok"

def run_step(record, phase, intensity, dry_run=True):
def run_step(record, phase, intensity, dry_run=True, handlers=None, mesh_integration=None, logger=None):
    """
    Advanced performer with handler registry, mesh agent integration, and logging.
    """
    rid = record["id"]
    key = record["key"]
    title = record["title"]
    action = {"compress": "compress", "ultracomp": "ultracomp", "ignite": "ignite"}.get(phase, phase)
    result = {
        "id": rid, "key": key, "title": title,
        "phase": phase, "action": action,
        "intensity": intensity,
        "status": "dry-run" if dry_run else "ok"
    }
    # Custom phase handler
    if handlers and phase in handlers:
        try:
            handler_result = handlers[phase](record, intensity, dry_run)
            result["handler_result"] = handler_result
        except Exception as e:
            result["handler_error"] = str(e)
    # Mesh agent integration (callable)
    if mesh_integration:
        try:
            mesh_result = mesh_integration(record, phase, intensity, dry_run)
            result["mesh_result"] = mesh_result
        except Exception as e:
            result["mesh_error"] = str(e)
    # External logger hook
    if logger:
        try:
            logger(result)
        except Exception:
            pass
    return result

def cycle_phase(index, phase_window):
    # Phases repeat: [compress x phase_window] -> [ultracomp x phase_window] -> [ignite x phase_window]
    block = (index // phase_window) % 3
    return ["compress", "ultracomp", "ignite"][block]

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--packdir", default=str(PACKDIR))
    ap.add_argument("--jsonl", default=str(JSONL))
    ap.add_argument("--edges", default=str(EDGES))
    ap.add_argument("--family", help="Only include triggers whose family matches (prefix of key)")
    ap.add_argument("--start", type=int, help="Min id")
    ap.add_argument("--end", type=int, help="Max id")
    ap.add_argument("--limit", type=int, help="Max number of steps to process")
    ap.add_argument("--phase-window", type=int, default=5, help="How many steps per phase before cycling")
    ap.add_argument("--intensity", type=int, default=1000, help="Tuning knob for compression depth")
    ap.add_argument("--dry-run", action="store_true", help="Log only, do not execute handlers")
    ap.add_argument("--json-log", help="Path to write JSONL run log")
    args = ap.parse_args(argv)

    jsonl = Path(args.jsonl)
    edgesp = Path(args.edges)

    nodes = load_nodes(jsonl)
    edges = load_edges(edgesp)

    # optional family filter (based on key prefix before '-')
    if args.family:
        fam = args.family.strip().upper()
        nodes = {i:r for i,r in nodes.items() if (r.get("family","").upper()==fam or r.get("key","").upper().startswith(fam+"-"))}

    order = topo_order(nodes, edges, start=args.start, end=args.end)
    ap = argparse.ArgumentParser()
    ap.add_argument("--packdir", default=str(PACKDIR))
    ap.add_argument("--jsonl", default=str(JSONL))
    ap.add_argument("--edges", default=str(EDGES))
    ap.add_argument("--family", help="Only include triggers whose family matches (prefix of key)")
    ap.add_argument("--start", type=int, help="Min id")
    ap.add_argument("--end", type=int, help="Max id")
    ap.add_argument("--limit", type=int, help="Max number of steps to process")
    ap.add_argument("--phase-window", type=int, default=5, help="How many steps per phase before cycling")
    ap.add_argument("--intensity", type=int, default=1000, help="Tuning knob for compression depth")
    ap.add_argument("--dry-run", action="store_true", help="Log only, do not execute handlers")
    ap.add_argument("--json-log", help="Path to write JSONL run log")
    ap.add_argument("--dashboard-log", action="store_true", help="Send logs to dashboard")
    ap.add_argument("--mesh-integration", action="store_true", help="Enable mesh agent integration")
    args = ap.parse_args(argv)
        else:
            phase = cycle_phase(idx, args.phase_window)
            result = run_step(rec, phase, args.intensity, dry_run=args.dry_run)
            entry = {"ts": ts, **result}
        line = json.dumps(entry, ensure_ascii=False)
        print(line)
        if outfh:
            outfh.write(line+"\n")
        processed += 1

    if outfh:
        outfh.close()

    print(f"# Summary: processed={processed}, phasesize={args.phase_window}, intensity={args.intensity}", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1:])
