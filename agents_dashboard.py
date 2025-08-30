#!/usr/bin/env python3
"""
Agents Dashboard - A Streamlit dashboard for the EpochCore Ultra Trigger Pack
"""

import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

# Try to import streamlit - install it if not available
try:
    import streamlit as st
except ImportError:
    print("Streamlit not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

# Configuration
ROOT = Path(os.getcwd())
LEDGER_PATH = ROOT / "ledger_main.jsonl"
CAPSULES_DIR = ROOT / "out" / "capsules"
ARCHIVES_DIR = ROOT / "out" / "archive"

# Mathematical model parameters from our analysis
LEVERAGE_FACTOR = 10.0
VELOCITY_FACTOR = 5.0
BASE_COMPOUND_RATE = 0.010072
TRIGGER_MULTIPLIERS = {
    "TREASURYFLOW💵": 1.0,      # base impact
    "MARKETCAP📈": 1.5,         # stronger impact
    "PRICINGFORGE💳": 1.2,      # moderate impact
    "BONUSDROP🎁": 1.8,         # high variability
    "GOVCOUNCIL⚖️": 1.0,        # stability-focused
    "PULLREQUESTVOTE🔀": 1.0,   # stability-focused
    "ROLLBACKSEAL⏪": 0.8,       # safety, slightly reduces growth
    "MESHSPAWN🌱": 2.0,         # strong network effect
    "CIVILIZATIONBLOCK🌍": 2.5,  # strongest compound effect
    "AUTOCOMPOUND⏩": 10.0       # direct 10X multiplier
}

BATCH_CONFIGS = {
    "roi-burst": ["TREASURYFLOW💵", "MARKETCAP📈", "PRICINGFORGE💳", "BONUSDROP🎁", "AUTOCOMPOUND⏩"],
    "gov-harden": ["GOVCOUNCIL⚖️", "PULLREQUESTVOTE🔀", "ROLLBACKSEAL⏪", "AUTOCOMPOUND⏩"],
    "mesh-expand": ["MESHSPAWN🌱", "CIVILIZATIONBLOCK🌍", "AUTOCOMPOUND⏩"],
    "full-send": list(TRIGGER_MULTIPLIERS.keys())
}


def load_ledger():
    """Load the ledger file and return a list of entries"""
    entries = []
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    pass
    return entries


def load_capsule(path):
    """Load a capsule file and return its contents"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def calculate_growth(triggers, initial_value=7.0, activations=100):
    """Calculate the growth based on the triggers used"""
    # Stage 1: Leverage (if AUTOCOMPOUND is present)
    leverage_value = initial_value * \
        LEVERAGE_FACTOR if "AUTOCOMPOUND⏩" in triggers else initial_value

    # Stage 2: Velocity
    velocity_value = leverage_value * VELOCITY_FACTOR

    # Stage 3: Escalation (compound growth)
    effective_rate = sum(BASE_COMPOUND_RATE * TRIGGER_MULTIPLIERS[t]
                         for t in triggers if t != "AUTOCOMPOUND⏩")

    # Apply compound growth
    final_value = velocity_value * math.pow(1 + effective_rate, activations)

    return {
        "initial": initial_value,
        "leverage": leverage_value,
        "velocity": velocity_value,
        "final": final_value,
        "effective_rate": effective_rate,
        "growth_factor": final_value / initial_value,
        "doubling_time": 72 / (effective_rate * 100) if effective_rate > 0 else float('inf')
    }


def main():
    st.set_page_config(
        page_title="EpochCore Ultra Trigger Pack Dashboard",
        page_icon="🚀",
        layout="wide"
    )

    st.title("🚀 EpochCore Ultra Trigger Pack Dashboard")
    st.write("A mathematical analysis of trigger system performance")

    # Sidebar controls
    st.sidebar.header("Controls")
    initial_value = st.sidebar.number_input("Initial Value", value=7.0, min_value=0.1)
    activations = st.sidebar.slider(
        "Activations", min_value=1, max_value=200, value=100)

    # Load data
    ledger_entries = load_ledger()

    # Show overall stats
    st.header("System Status")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Capsules Forged", len(ledger_entries))

    with col2:
        trigger_counts = {}
        for entry in ledger_entries:
            trigger = entry.get("trigger", "unknown")
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        st.metric("Unique Triggers", len(trigger_counts))

    with col3:
        latest_time = max([datetime.fromisoformat(entry.get("ts", "2000-01-01T00:00:00Z").replace("Z", "+00:00"))
                           for entry in ledger_entries]) if ledger_entries else None
        st.metric("Last Activity", latest_time.strftime(
            "%Y-%m-%d %H:%M:%S") if latest_time else "Never")

    # Growth Analysis Tab
    st.header("Growth Analysis")

    # Calculate growth for each batch
    growth_results = {}
    for batch_name, triggers in BATCH_CONFIGS.items():
        growth_results[batch_name] = calculate_growth(
            triggers, initial_value, activations)

    # Display growth table
    st.subheader("Growth Comparison by Batch Configuration")
    growth_df = {
        "Batch": [],
        "Initial Value": [],
        "Final Value": [],
        "Growth Factor": [],
        "Effective Rate": [],
        "Doubling Time": []
    }

    for batch_name, result in growth_results.items():
        growth_df["Batch"].append(batch_name)
        growth_df["Initial Value"].append(f"{result['initial']:.2f}")
        growth_df["Final Value"].append(f"{result['final']:.2f}")
        growth_df["Growth Factor"].append(f"{result['growth_factor']:.2f}x")
        growth_df["Effective Rate"].append(f"{result['effective_rate']*100:.4f}%")
        growth_df["Doubling Time"].append(f"{result['doubling_time']:.1f} triggers")

    st.table(growth_df)

    # Show three-stage breakdown for the selected batch
    selected_batch = st.selectbox(
        "Select Batch for Detailed Analysis", list(BATCH_CONFIGS.keys()))

    st.subheader(f"Three-Stage Growth Breakdown: {selected_batch}")
    result = growth_results[selected_batch]

    st.write(
        f"**Stage 1 - Leverage:** {result['initial']:.2f} → {result['leverage']:.2f} (×{LEVERAGE_FACTOR:.1f})")
    st.write(
        f"**Stage 2 - Velocity:** {result['leverage']:.2f} → {result['velocity']:.2f} (×{VELOCITY_FACTOR:.1f})")
    leverage_velocity_factor = result['velocity'] / result['initial']
    st.write(f"**Combined L×V factor:** {leverage_velocity_factor:.2f}x")

    escalation_factor = result['final'] / result['velocity']
    st.write(
        f"**Stage 3 - Escalation:** {result['velocity']:.2f} → {result['final']:.2f} (×{escalation_factor:.2f})")
    st.write(f"**Effective compound rate:** {result['effective_rate']*100:.4f}%")
    st.write(f"**Total growth factor:** {result['growth_factor']:.2f}x")

    # Mathematical formula
    st.subheader("Mathematical Formula")
    st.latex(
        r"Final = Initial \times Leverage \times Velocity \times (1 + EffectiveRate)^{Activations}")

    # Example for selected batch
    st.write(f"**Example ({selected_batch} batch):**")
    st.latex(
        f"Final = {result['initial']} \\times {LEVERAGE_FACTOR} \\times {VELOCITY_FACTOR} \\times (1 + {result['effective_rate']:.6f})^{{{activations}}}")
    st.latex(
        f"Final = {result['initial']} \\times {LEVERAGE_FACTOR * VELOCITY_FACTOR} \\times {math.pow(1 + result['effective_rate'], activations):.6f}")
    st.latex(f"Final = {result['final']:.2f}")

    # Recent Activity
    st.header("Recent Activity")
    if ledger_entries:
        # Sort by timestamp, newest first
        sorted_entries = sorted(
            ledger_entries, key=lambda x: x.get("ts", ""), reverse=True)

        for i, entry in enumerate(sorted_entries[:5]):  # Show last 5 entries
            with st.expander(f"Capsule: {Path(entry.get('capsule', '')).name}", expanded=(i == 0)):
                st.write(f"**Trigger:** {entry.get('trigger', 'Unknown')}")
                st.write(f"**Timestamp:** {entry.get('ts', 'Unknown')}")
                st.write(f"**SHA-256:** {entry.get('sha256', 'Unknown')}")

                # Try to load and display the capsule
                capsule_path = Path(entry.get('capsule', ''))
                if capsule_path.exists():
                    capsule = load_capsule(capsule_path)
                    if capsule:
                        st.json(capsule)
    else:
        st.write("No capsules have been forged yet.")

    # Footer
    st.markdown("---")
    st.markdown("*EpochCore Ultra Trigger Pack v10.0 — Batch Forge Dashboard*")
    st.markdown(
        "*Mathematical analysis based on the three-stage growth model: Leverage → Velocity → Escalation*")


if __name__ == "__main__":
    main()
