#!/usr/bin/env python3
import os
import json
import datetime as dt

REGISTRY = "ledger/drip_registry.json"
SPAWN_LOG = "ledger/agent_spawn_log.jsonl"

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

def track_all_spawns():
    agents = load_agents()
    for agent in agents:
        log_spawn(agent)
    print(f"Logged {len(agents)} agent spawns to {SPAWN_LOG}.")

if __name__ == "__main__":
    track_all_spawns()
