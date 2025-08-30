#!/usr/bin/env python3
import json
import datetime as dt
from pathlib import Path

MESH_LEDGER = "ledger/meshcredit_ledger.jsonl"
SUPPLY_CAP = 1000000  # Example supply cap
YIELD_CURVE = 0.03    # Example yield rate (3% per period)
BANKER_AGENT = "agent://banker"
ALERTS = "ledger/meshcredit_alerts.log"

# Utility functions
def log_event(event):
    with open(MESH_LEDGER, "a") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")

def alert(msg):
    with open(ALERTS, "a") as f:
        f.write(f"[{dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}\n")
    print(f"ALERT: {msg}")

def get_current_supply():
    if not Path(MESH_LEDGER).exists():
        return 0
    supply = 0
    with open(MESH_LEDGER) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("event") == "mint":
                    supply += entry.get("amount", 0)
                elif entry.get("event") == "burn":
                    supply -= entry.get("amount", 0)
            except Exception:
                continue
    return supply

def mint_meshcredit(amount, agent=BANKER_AGENT):
    supply = get_current_supply()
    if supply + amount > SUPPLY_CAP:
        alert(f"MeshCredit supply cap exceeded! Mint blocked. Current: {supply}, Attempted: {amount}")
        return False
    event = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": "mint",
        "agent": agent,
        "amount": amount,
        "supply_after": supply + amount
    }
    log_event(event)
    return True

def burn_meshcredit(amount, agent=BANKER_AGENT):
    supply = get_current_supply()
    if amount > supply:
        alert(f"MeshCredit burn exceeds supply! Burn blocked. Current: {supply}, Attempted: {amount}")
        return False
    event = {
        "ts": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": "burn",
        "agent": agent,
        "amount": amount,
        "supply_after": supply - amount
    }
    log_event(event)
    return True

def apply_yield():
    supply = get_current_supply()
    yield_amt = round(supply * YIELD_CURVE, 2)
    if yield_amt > 0 and supply + yield_amt <= SUPPLY_CAP:
        mint_meshcredit(yield_amt, agent=BANKER_AGENT)
        alert(f"Yield applied: {yield_amt} MeshCredit minted.")
    else:
        alert(f"Yield blocked: would exceed supply cap. Current: {supply}, Attempted: {yield_amt}")

def monitor_meshcredit():
    supply = get_current_supply()
    print(f"Current MeshCredit supply: {supply} / {SUPPLY_CAP}")
    if supply > SUPPLY_CAP * 0.95:
        alert(f"MeshCredit supply nearing cap! Current: {supply}")
    # Optionally apply yield
    apply_yield()

if __name__ == "__main__":
    monitor_meshcredit()
