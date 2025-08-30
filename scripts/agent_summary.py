#!/usr/bin/env python3
import json
from pathlib import Path

REGISTRY = "ledger/drip_registry.json"
AGENT_LOG = "ledger/agent_activity_log.jsonl"

# Load agent registry
def load_agents():
    if not Path(REGISTRY).exists():
        return []
    with open(REGISTRY) as f:
        data = json.load(f)
    return data.get("agents", [])

def summarize_agents():
    agents = load_agents()
    print("--- Agent Summary ---")
    print(f"Total agents: {len(agents)}")

    # Define ceiling work agent criteria (high reliability, critical skills, or backbone role)
    ceiling_agents = []
    for agent in agents:
        # Example criteria: reliability >= 0.95 or backbone skills
        backbone_skills = {
            "monitor.24x7",
            "self.heal",
            "meshcredit.grant",
            "attest.supply",
            "sign.proof",
            "resource.allocate"
        }
        if agent["rel"] >= 0.95 or backbone_skills.intersection(set(agent["skills"])):
            ceiling_agents.append(agent)

    print(f"Ceiling Work Agents: {len(ceiling_agents)}")
    for agent in ceiling_agents:
        print(f"[CEILING] ID: {agent['agent_id']}")
        print(f"  Skills: {', '.join(agent['skills'])}")
        print(f"  Reliability: {agent['rel']}")
        print(f"  Latency: {agent['lat']}")

    # Track activity and quota from agent_spawn_log.jsonl
    spawn_log_path = Path("ledger/agent_spawn_log.jsonl")
    activity = {agent["agent_id"]: 0 for agent in ceiling_agents}
    if spawn_log_path.exists():
        with open(spawn_log_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    aid = entry.get("agent_id")
                    if aid in activity:
                        activity[aid] += 1
                except Exception:
                    continue
    print("\nCeiling Agent Activity & Quota:")
    market_skills = {
        "market.scan", "lead.gen", "demo.run", "close.deal",
        "roi.track", "profit.analyze", "margin.boost", "cost.optimize",
        "deal.close", "quota.hit", "pipeline.max", "repeat.buy"
    }
    ready_for_market = []
    for agent in ceiling_agents:
        aid = agent["agent_id"]
        print(
            f"ID: {aid} | Activity Count: {activity[aid]} | "
            f"Reliability: {agent['rel']} | Latency: {agent['lat']}"
        )
        # Example quota check: flag if activity < 2 (can adjust threshold)
        if activity[aid] < 2:
            print(f"  [ALERT] {aid} below activity quota!")
        # Flag for market transition if agent has market skills and meets activity quota
        if market_skills.intersection(set(agent["skills"])) and activity[aid] >= 2:
            ready_for_market.append(agent)
    print("\nAgents Ready for Market Transition:")
    for agent in ready_for_market:
        print(
            f"[MARKET READY] ID: {agent['agent_id']} | Skills: {', '.join(agent['skills'])}"
        )
        print(
            f"  Activity: {activity[agent['agent_id']]} | Reliability: {agent['rel']}"
        )
    # Automate conversion: flag as market agent (simulate registry update)
    print("\nAutomated Conversion:")
    for agent in ready_for_market:
        print(f"Converted {agent['agent_id']} to MARKET AGENT.")
    print("--- End Summary ---")

  
if __name__ == "__main__":
    summarize_agents()
