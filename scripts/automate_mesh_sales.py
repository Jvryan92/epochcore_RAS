#!/usr/bin/env python3
import os
import json
import datetime as dt
import random

REGISTRY = "ledger/drip_registry.json"
LEDGER = "ledger/alpha_genesis_ledger.jsonl"
AGENTS = [
    "agent://top.seller",
    "agent://upsell",
    "agent://provider",
    "agent://roi",
    "agent://loop",
    "agent://theta",
    "agent://zeta"
]
EVENTS = ["sale", "upsell", "onboard", "roi", "meshcredit"]

# Load agent registry
def load_agents():
    with open(REGISTRY) as f:
        data = json.load(f)
    return [a["agent_id"] for a in data["agents"]]

def mint_capsule(agent, event, value):
    capsule = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": agent,
        "event": event,
        "value": value,
        "capsule_id": f"{agent.split('//')[1]}-{event}-{random.randint(10000,99999)}"
    }
    with open(LEDGER, "a") as f:
        f.write(json.dumps(capsule, separators=(",", ":")) + "\n")
    return capsule

def automate_sales_loop():
    agents = load_agents()
    for agent in AGENTS:
        if agent in agents:
            # Simulate sales, upsell, onboarding, ROI, meshcredit
            for event in EVENTS:
                value = round(random.uniform(100, 5000), 2)
                mint_capsule(agent, event, value)
    # Weekly snapshot
    mint_capsule("agent://loop", "snapshot", "weekly_performance")
    print("Automated mesh sales, upsell, onboarding, ROI, and meshcredit events minted.")

if __name__ == "__main__":
    automate_sales_loop()
