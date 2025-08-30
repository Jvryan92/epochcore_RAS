import streamlit as st
import json
import pandas as pd
from glob import glob
import os
import subprocess

st.sidebar.markdown("---")
st.sidebar.title("Asset Glyphs by Rank")
st.sidebar.markdown(
    "**Dark Mode**\n- **burnt-orange (Premium)**: 48px/print\n    - strategy_icon-dark-burnt-orange-48px.png\n    - strategy_icon-dark-burnt-orange-48px.svg\n- **copper-foil (Elite)**: 32px/web\n    - strategy_icon-dark-copper-foil-32px.png\n    - strategy_icon-dark-copper-foil-32px.svg\n- **flat-orange (Standard)**: 16px/32px/48px/web\n    - strategy_icon-dark-flat-orange-16px.png\n    - strategy_icon-dark-flat-orange-16px.svg\n    - strategy_icon-dark-flat-orange-32px.png\n    - strategy_icon-dark-flat-orange-32px.svg\n    - strategy_icon-dark-flat-orange-48px.png\n    - strategy_icon-dark-flat-orange-48px.svg\n\n**Light Mode**\n- **flat-orange (Standard)**: 16px/32px/48px/web\n    - strategy_icon-light-flat-orange-16px.png\n    - strategy_icon-light-flat-orange-16px.svg\n    - strategy_icon-light-flat-orange-32px.png\n    - strategy_icon-light-flat-orange-32px.svg\n    - strategy_icon-light-flat-orange-48px.png\n    - strategy_icon-light-flat-orange-48px.svg\n- **matte-carbon (Executive)**: 16px/32px/print\n    - strategy_icon-light-matte-carbon-16px.png\n    - strategy_icon-light-matte-carbon-16px.svg\n    - strategy_icon-light-matte-carbon-32px.png\n    - strategy_icon-light-matte-carbon-32px.svg"
)

st.sidebar.markdown("---")
st.sidebar.title("Strike Actions")
st.sidebar.markdown(
    "1. **Strike 1:** Mint revenue/ROI capsule  \\`./ultra_trigger_pack_batch.sh --batch roi-burst\\`\n2. **Strike 2:** Mint mesh/network expansion capsule  \\`./ultra_trigger_pack_batch.sh --batch mesh-expand\\`\n3. **Strike 3:** Mint governance/security capsule  \\`./ultra_trigger_pack_batch.sh --batch gov-harden\\`\n4. **Strike 4:** Mint all types at once  \\`./ultra_trigger_pack_batch.sh --batch full-send\\`\n5. **Strike 5:** Custom selection (ask Copilot)  \\`./ultra_trigger_pack_batch.sh --pick '1 3 8 10'\\`"
)
st.sidebar.markdown("---")
st.sidebar.title("Plain English Actions")
st.sidebar.write("Choose a business action:")


def run_strike(strike_cmd):
    result = subprocess.run(strike_cmd, shell=True, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else result.stderr


st.sidebar.markdown("---")
st.sidebar.title("Plain English Actions")
st.sidebar.write("Choose a business action:")
if st.sidebar.button("Strike 1: Mint revenue/ROI capsule"):
    st.sidebar.write(run_strike("./ultra_trigger_pack_batch.sh --batch roi-burst"))
if st.sidebar.button("Strike 2: Mint mesh/network expansion capsule"):
    st.sidebar.write(run_strike("./ultra_trigger_pack_batch.sh --batch mesh-expand"))
if st.sidebar.button("Strike 3: Mint governance/security capsule"):
    st.sidebar.write(run_strike("./ultra_trigger_pack_batch.sh --batch gov-harden"))
if st.sidebar.button("Strike 4: Mint all types at once"):
    st.sidebar.write(run_strike("./ultra_trigger_pack_batch.sh --batch full-send"))
st.sidebar.markdown("---")
st.sidebar.title("Plain English Actions")
st.sidebar.write("Choose a business action:")
st.sidebar.write("- Strike 1: Mint revenue/ROI capsule")
st.sidebar.write("- Strike 2: Mint mesh/network expansion capsule")
st.sidebar.write("- Strike 3: Mint governance/security capsule")
st.sidebar.write("- Strike 4: Mint all types at once")
st.sidebar.write("- Strike 5: Custom selection (ask Copilot)")

st.sidebar.markdown("---")
st.sidebar.title("Quick Commands & Scripts")
st.sidebar.write("Copy and run these in your terminal:")
st.sidebar.code(
    "./ultra_trigger_pack_batch.sh --batch roi-burst  # Strike 1", language="bash"
)
st.sidebar.code(
    "./ultra_trigger_pack_batch.sh --batch mesh-expand  # Strike 2", language="bash"
)
st.sidebar.code(
    "./ultra_trigger_pack_batch.sh --batch gov-harden   # Strike 3", language="bash"
)
st.sidebar.code(
    "./ultra_trigger_pack_batch.sh --batch full-send    # Strike 4", language="bash"
)
st.sidebar.code(
    "./ultra_trigger_pack_batch.sh --pick '1 3 8 10'    # Strike 5", language="bash"
)
st.sidebar.code("streamlit run capsule_dashboard.py", language="bash")
st.sidebar.code("streamlit run agents_dashboard.py", language="bash")


st.set_page_config(page_title="MeshCredit & Capsule Dashboard", layout="wide")
st.title("MeshCredit & Capsule Dashboard")

capsule_dir = "out/capsules"
ledger_file = "ledger_main.jsonl"

# Load capsules


def load_capsules():
    capsules = []
    for f in glob(os.path.join(capsule_dir, "*.json")):
        try:
            with open(f) as cf:
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

# Payment status simulation (can be replaced with real API integration)


def get_payment_status(capsule):
    # Simulate paid/unpaid based on hash or random
    import hashlib

    h = hashlib.sha256(json.dumps(capsule).encode()).hexdigest()
    return "Paid" if int(h, 16) % 2 == 0 else "Unpaid"


st.subheader("Capsule Sales & Incentives")
for capsule in capsules:
    st.markdown(
        f"### {capsule.get('bundle_type', capsule.get('capsule_id', 'Capsule'))}"
    )
    st.write({k: v for k, v in capsule.items() if k not in ["payment_options"]})
    pay_opts = capsule.get("payment_options", {})
    cols = st.columns(len(pay_opts) + 1)
    with cols[0]:
        status = get_payment_status(capsule)
        st.markdown(
            f"**Payment Status:** {'🟢 Paid' if status == 'Paid' else '🔴 Unpaid'}"
        )
    for i, (label, img_path) in enumerate(pay_opts.items()):
        with cols[i + 1]:
            st.markdown(f"**{label.replace('_qr_image','').replace('_',' ').title()}**")
            if os.path.exists(img_path):
                st.image(img_path, width=150)
            else:
                st.write(img_path)

st.subheader("Ledger Events & Transactions")
if events:
    df = pd.DataFrame(events)
    st.dataframe(df)
    st.line_chart(df["ts"].value_counts().sort_index())
    st.bar_chart(df["event"].value_counts())
else:
    st.write("No ledger events found.")

st.subheader("Analytics & Summary")
st.write(f"Total Capsules: {len(capsules)}")
st.write(f"Total Ledger Events: {len(events)}")
paid = sum(get_payment_status(c) == "Paid" for c in capsules)
unpaid = len(capsules) - paid
st.write(f"Paid Capsules: {paid}")
st.write(f"Unpaid Capsules: {unpaid}")
st.progress(paid / max(1, len(capsules)))

st.sidebar.title("Search & Filter")
search = st.sidebar.text_input("Search Capsule ID or Type")
if search:
    filtered = [c for c in capsules if search.lower() in str(c).lower()]
    st.write(f"Filtered Capsules: {len(filtered)}")
    for capsule in filtered:
        st.write(capsule)

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

st.sidebar.markdown("---")
st.sidebar.title("Quick Commands & Scripts")
st.sidebar.write("Copy and run these in your terminal:")
st.sidebar.code("./ultra_trigger_pack_batch.sh --batch roi-burst", language="bash")
st.sidebar.code("./ultra_trigger_pack_batch.sh --batch mesh-expand", language="bash")
st.sidebar.code("./ultra_trigger_pack_batch.sh --batch full-send", language="bash")
st.sidebar.code("./ultra_trigger_pack_batch.sh --pick '1 3 8 10'", language="bash")
st.sidebar.code("streamlit run capsule_dashboard.py", language="bash")
st.sidebar.code("streamlit run agents_dashboard.py", language="bash")
