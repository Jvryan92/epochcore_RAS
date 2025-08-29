"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
import os
import json
import hashlib
import datetime as dt
import uuid
import hmac
import argparse
from typing import List, Dict, Tuple, Optional

# Core cryptographic primitives
def ts() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256(obj) -> str:
    s = json.dumps(obj, separators=(",",":"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def hmac_sign(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()

# Base trigger definitions
BASES = {
    "VELOCITY", "CONSTELLATION", "LEDGERLOCK",
    "AMPLIFY", "STARGATE", "MARGIN"
}

# Compound formation rules
PAIR_OVERRIDES = {
    ("LEDGERLOCK","MARGIN"): "MARGIN_LOCK",
    ("MARGIN","LEDGERLOCK"): "MARGIN_LOCK",
}

# Meta formation rules
TRIPLE_OVERRIDES = {
    ("VELOCITY_CONSTELLATION","LEDGERLOCK"): "FLOW_SEAL_SIGIL",
    ("MARGIN_LOCK","AMPLIFY"): "AMPLIFIED_PROOF", 
    ("AMPLIFY_STARGATE","CONSTELLATION"): "CONSTELLATION_GATE"
}

class TriggerMint:
    def __init__(self, cas_path: str, mesh_key: Optional[bytes] = None):
        """Initialize trigger minting with CAS storage and optional mesh key."""
        self.cas_path = cas_path
        self.mesh_key = mesh_key or os.urandom(32)
        os.makedirs(cas_path, exist_ok=True)

    def put_content(self, data: str) -> str:
        """Store content in CAS with deduplication."""
        h = sha256(data)
        path = os.path.join(self.cas_path, f"{h}.bin")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data.encode())
        return h

    def compound(self, a: str, b: str) -> str:
        """Form compound trigger from two bases."""
        return PAIR_OVERRIDES.get((a,b), f"{a}_{b}")

    def meta(self, comp: str, base: str) -> str:
        """Form meta trigger from compound and base."""
        return TRIPLE_OVERRIDES.get((comp,base), f"{comp}+{base}")

    def mint(self, triggers: List[str]) -> List[Dict]:
        """Mint compound and meta triggers from base triggers."""
        trig = [t.strip().upper() for t in triggers if t.strip()]
        bad = [t for t in trig if t not in BASES]
        if bad:
            allowed = ",".join(sorted(BASES))
            raise ValueError(f"Unknown BASE(s): {bad} | Allowed: {allowed}")

        out = []
        if len(trig) < 2:
            out.append({
                "level": "BASE",
                "name": trig[0] if trig else None,
                "note": "<2 triggers — nothing to mint>"
            })
            return out

        # Form compound
        comp = self.compound(trig[0], trig[1])
        out.append({
            "level": "COMPOUND",
            "name": comp,
            "from": [trig[0], trig[1]]
        })

        # Form metas from remaining triggers
        for b in trig[2:]:
            m = self.meta(comp, b)
            out.append({
                "level": "META",
                "name": m,
                "from": [comp, b]
            })
            comp = m

        return out

    def write_ledger(self, records: List[Dict], outdir: str = "ledger",
                    capsule_note: str = "auto-mint", dry_run: bool = False) -> None:
        """Write minted triggers to ledger with cryptographic proofs."""
        os.makedirs(outdir, exist_ok=True)
        run_id = f"MINT-{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}-{uuid.uuid4().hex[:8]}"
        path = os.path.join(outdir, "trigger_mints.jsonl")
        merkle_leaves = []

        for r in records:
            # Create core entry with cryptographic binding
            entry_core = {
                "schema": "epoch.trigger-mint.v1",
                "run_id": run_id,
                "timestamp": ts(),
                "level": r["level"],
                "name": r["name"],
                "from": r.get("from"),
                "capsule_note": capsule_note,
                "cas_root": self.cas_path
            }

            # Sign and hash entry
            entry_core["hash"] = sha256(entry_core)
            entry_core["hmac"] = hmac_sign(self.mesh_key, json.dumps(entry_core))
            merkle_leaves.append(entry_core["hash"])

            print(f"{entry_core['level']:8} {entry_core['name']}   ← {entry_core.get('from')}")

            if not dry_run:
                # Store entry in CAS
                entry_hash = self.put_content(json.dumps(entry_core))

                # Append to ledger
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry_core, ensure_ascii=False) + "\n")

        if not dry_run:
            print(f"\n🧾 ledger → {path}")
            # Store merkle root for batch verification
            merkle_root = self._calculate_merkle_root(merkle_leaves)
            with open(os.path.join(outdir, f"{run_id}_merkle.json"), "w") as f:
                json.dump({
                    "run_id": run_id,
                    "merkle_root": merkle_root,
                    "leaf_count": len(merkle_leaves)
                }, f, indent=2)
        else:
            print("\n(dry‑run) nothing written")

    def _calculate_merkle_root(self, leaves: List[str]) -> str:
        """Calculate merkle root from list of leaf hashes."""
        if not leaves:
            return sha256("")
        nodes = leaves
        while len(nodes) > 1:
            pairs = [(nodes[i], nodes[i+1] if i+1 < len(nodes) else nodes[i])
                    for i in range(0, len(nodes), 2)]
            nodes = [hashlib.sha256(
                bytes.fromhex(a) + bytes.fromhex(b)
            ).hexdigest() for a, b in pairs]
        return nodes[0]

def main():
    ap = argparse.ArgumentParser(
        description="Mint COMPOUND/META glyphs from BASE triggers with cryptographic proofs."
    )
    ap.add_argument("triggers", nargs="*", help="e.g. VELOCITY CONSTELLATION LEDGERLOCK")
    ap.add_argument("--note", "-n",
                   default="capsule contains ≥2 triggers → auto‑mint",
                   help="capsule note")
    ap.add_argument("--outdir", "-o", default="ledger",
                   help="ledger output directory")
    ap.add_argument("--cas", "-c", default="cas",
                   help="content-addressable storage directory")
    ap.add_argument("--dry-run", "-d", action="store_true",
                   help="print only; do not write")
    args = ap.parse_args()

    if not args.triggers:
        ap.print_usage()
        print("\nExample: trigger_mint.py VELOCITY CONSTELLATION LEDGERLOCK")
        return 1

    minter = TriggerMint(args.cas)
    try:
        records = minter.mint(args.triggers)
        minter.write_ledger(records,
                          outdir=args.outdir,
                          capsule_note=args.note,
                          dry_run=args.dry_run)
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
