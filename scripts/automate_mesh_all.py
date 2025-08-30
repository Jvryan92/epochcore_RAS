#!/usr/bin/env python3
import json
import datetime as dt

REGISTRY = "ledger/drip_registry.json"
SPAWN_LOG = "ledger/agent_spawn_log.jsonl"
LEDGER = "ledger/alpha_genesis_ledger.jsonl"
ALERTS = "ledger/mesh_alerts.log"

# Load agent registry
def load_agents():
    with open(REGISTRY) as f:
        data = json.load(f)
    return data["agents"]

def log_spawn(agent):
    entry = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_id": agent["agent_id"],
        "skills": agent["skills"],
        "rel": agent["rel"],
        "lat": agent["lat"]
    }
    with open(SPAWN_LOG, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return entry

def log_event(agent_id, event, value):
    capsule = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": agent_id,
        "event": event,
        "value": value,
        "capsule_id": f"{agent_id.split('//')[1]}-{event}-{value}-{dt.datetime.utcnow().strftime('%H%M%S')}"
    }
    with open(LEDGER, "a") as f:
        f.write(json.dumps(capsule, separators=(",", ":")) + "\n")
    return capsule

def alert(msg):
    with open(ALERTS, "a") as f:
        f.write(f"[{dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}\n")
    print(f"ALERT: {msg}")

def automate_all():
    agents = load_agents()
    for agent in agents:
        log_spawn(agent)
        # Mint onboarding, meshcredit, and sales capsules
        log_event(agent["agent_id"], "onboard", "init")
        log_event(agent["agent_id"], "meshcredit", round(agent["rel"] * 1000, 2))
        log_event(agent["agent_id"], "sale", round(agent["lat"] * 10, 2))
    # Weekly snapshot
    log_event("agent://loop", "snapshot", "weekly_performance")
    alert(f"Automated onboarding, meshcredit, sales, and spawn tracking for {len(agents)} agents.")

if __name__ == "__main__":
    automate_all()
