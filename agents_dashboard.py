import json
import os
from glob import glob

import pandas as pd
import streamlit as st

st.set_page_config(page_title="EpochCore Agents Dashboard", layout="wide")
st.title("EpochCore Agents Dashboard")

capsule_dir = "out/capsules"
ledger_file = "ledger_main.jsonl"


def load_capsules():
    capsules = []
    for f in glob(os.path.join(capsule_dir, "*.json")):
        with open(f) as cf:
            try:
                capsules.append(json.load(cf))
            except Exception:
                continue
    return capsules


# Load ledger events


def load_ledger():
    events = []
    if os.path.exists(ledger_file):
        with open(ledger_file) as lf:
            for line in lf:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
    return events


capsules = load_capsules()
events = load_ledger()

st.sidebar.title("Agent & Capsule Filters")
search = st.sidebar.text_input("Search Capsule/Agent/Trigger")

if search:
    capsules = [c for c in capsules if search.lower() in str(c).lower()]
    events = [e for e in events if search.lower() in str(e).lower()]

st.subheader("Agent Capsule Metrics")
if capsules:
    df_caps = pd.DataFrame(capsules)
    st.dataframe(df_caps)
    st.bar_chart(df_caps["trigger"].value_counts())
    st.write(f"Total Capsules: {len(df_caps)}")
    st.write(f"Triggers: {df_caps['trigger'].unique().tolist()}")
    st.write(
        f"ROI Capsules: {df_caps[df_caps['trigger'].str.contains('ROI|TREASURYFLOW|MARKETCAP|PRICINGFORGE|BONUSDROP|AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )
else:
    st.write("No capsules found.")

st.subheader("Ledger Events & ROI Analytics")
if events:
    df_events = pd.DataFrame(events)
    st.dataframe(df_events)
    st.line_chart(df_events["ts"].value_counts().sort_index())
    st.bar_chart(df_events["event"].value_counts())
    st.write(f"Total Ledger Events: {len(df_events)}")
    st.write(
        f"ROI Events: {df_events[df_events['trigger'].str.contains('ROI|TREASURYFLOW|MARKETCAP|PRICINGFORGE|BONUSDROP|AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )
else:
    st.write("No ledger events found.")

st.subheader("Agent Performance & Governance")
if capsules:
    st.write(
        f"Governance Capsules: {df_caps[df_caps['trigger'].str.contains('GOVCOUNCIL|PULLREQUESTVOTE|ROLLBACKSEAL', case=False, na=False)].shape[0]}"
    )
    st.write(
        f"Mesh Expansion Capsules: {df_caps[df_caps['trigger'].str.contains('MESHSPAWN|CIVILIZATIONBLOCK', case=False, na=False)].shape[0]}"
    )
    st.write(
        f"Compound Capsules: {df_caps[df_caps['trigger'].str.contains('AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )

st.sidebar.markdown("---")
st.sidebar.write("Export capsules or ledger as JSON")
if st.sidebar.button("Export Capsules"):
    st.sidebar.download_button(
        "Download Capsules", json.dumps(capsules, indent=2), "capsules.json"
    )
if st.sidebar.button("Export Ledger"):
    st.sidebar.download_button(
        "Download Ledger", json.dumps(events, indent=2), "ledger.json"
    )
