#!/usr/bin/env python3
import json
import datetime as dt
import random

REGISTRY = "ledger/drip_registry.json"
LEDGER = "ledger/alpha_genesis_ledger.jsonl"
GLYPH_LOG = "ledger/roi_glyphs.jsonl"
FLASH_SALE_LOG = "ledger/flash_sale_log.jsonl"

# Load agent registry
def load_agents():
    with open(REGISTRY) as f:
        data = json.load(f)
    return data["agents"]

def mint_flash_sale(agent):
    entry = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_id": agent["agent_id"],
        "event": "flash_sale",
        "meshcredit": round(agent["rel"] * 2000, 2),
        "note": "2x meshcredit for flash sale"
    }
    with open(FLASH_SALE_LOG, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return entry

def get_top_roi_agents():
    agents = load_agents()
    # Simulate ROI as rel * lat for ranking
    ranked = sorted(agents, key=lambda a: a["rel"] * a["lat"], reverse=True)
    return ranked[:3]

def award_glyph(agent):
    glyph = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_id": agent["agent_id"],
        "glyph": f"ROI-Glyph-{random.randint(1000,9999)}",
        "reason": "Top 3 ROI agent in flash sale"
    }
    with open(GLYPH_LOG, "a") as f:
        f.write(json.dumps(glyph, separators=(",", ":")) + "\n")
    return glyph

def run_flash_sync_sale():
    agents = load_agents()
    for agent in agents:
        mint_flash_sale(agent)
    top_agents = get_top_roi_agents()
    for agent in top_agents:
        award_glyph(agent)
    print(f"Flash sale: 2x meshcredit for all agents. Top 3 ROI agents awarded glyphs.")

if __name__ == "__main__":
    run_flash_sync_sale()
