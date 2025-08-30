#!/usr/bin/env python3
import os
import json
from pathlib import Path

# Inventory audit script for mesh ecosystem
ASSET_DIRS = [
    "assets/icons",
    "assets/masters",
    "out/capsules",
    "founder_pack",
    "ledger"
]
CAPSULE_EXTS = [".json", ".jsonl"]

def list_assets():
    inventory = {}
    for d in ASSET_DIRS:
        dir_path = Path(d)
        if dir_path.exists():
            files = [str(f) for f in dir_path.rglob("*") if f.is_file()]
            inventory[d] = files
        else:
            inventory[d] = []
    return inventory

def list_capsules():
    capsules = []
    for d in ASSET_DIRS:
        dir_path = Path(d)
        if dir_path.exists():
            for ext in CAPSULE_EXTS:
                capsules += [str(f) for f in dir_path.rglob(f"*{ext}")]
    return capsules

def meshcredit_pools():
    pools = {}
    ledger_path = Path("ledger/meshcredit_ledger.jsonl")
    if ledger_path.exists():
        supply = 0
        with open(ledger_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("event") == "mint":
                        supply += entry.get("amount", 0)
                    elif entry.get("event") == "burn":
                        supply -= entry.get("amount", 0)
                except Exception:
                    continue
        pools["meshcredit_supply"] = supply
    else:
        pools["meshcredit_supply"] = 0
    return pools

def main():
    print("--- Mesh Inventory Audit ---")
    assets = list_assets()
    print("Assets:")
    for k, v in assets.items():
        print(f"{k}: {len(v)} files")
    capsules = list_capsules()
    print(f"Total Capsules: {len(capsules)}")
    pools = meshcredit_pools()
    print(f"MeshCredit Supply: {pools['meshcredit_supply']}")
    print("--- End Audit ---")

if __name__ == "__main__":
    main()
