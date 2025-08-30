import os
import json
import uuid
import hashlib
from datetime import datetime

ULTRA_TRIGGERS = [
    "TREASURYFLOW💵",
    "MARKETCAP📈",
    "PRICINGFORGE💳",
    "BONUSDROP🎁",
    "GOVCOUNCIL⚖️",
    "PULLREQUESTVOTE🔀",
    "ROLLBACKSEAL⏪",
    "MESHSPAWN🌱",
    "CIVILIZATIONBLOCK🌍",
    "EPOCHGENESIS🔗🪾",
    "SAASFLEET🔥📦",
    "RASRECURSE♾️🌌",
    "TRUE NORTH LOCK⚓",
    "LEDGERHEAL💊",
    "MESHSPAWN🌱",
    "MARKETDROP💸🎭",
    "QUORUMCALL🗳️",
    "AUTOCOMPOUND⏩",
    "PRIMALGLYPH🐉",
    "WORLDRAID⚔️",
    "METAFORGE⚙️",
    "CAPSULEFUSION💥",
    "CROWNSEAL👑",
    "INFINITELOOP♻️",
    "DISTRIBUTIONBLAST📡",
    "MYTHICRELIC🕎",
    "AUTONOMYBOOST🚀",
    "AUDITGRADE🔍",
    "LEGENDSEAL✨",
    "FOUNDERSEAL👑",
    "TREASURYDROP💰",
    "DAILYQUEST🎯",
    "SEASONFORGE🍂",
    "FLEETBUNDLE📦",
    "MARKETBLAST📡",
    "CIVILIZATION🌍",
    "PRIMALROOT🌳",
    "ECHOGLYPH🔊"
]

AGENT_TYPES = {
    "TREASURYFLOW💵": "Treasury_Agent",
    "MARKETCAP📈": "Market_Agent",
    "PRICINGFORGE💳": "Pricing_Agent",
    "BONUSDROP🎁": "Bonus_Agent",
    "GOVCOUNCIL⚖️": "Governance_Agent",
    "PULLREQUESTVOTE🔀": "Governance_Agent",
    "ROLLBACKSEAL⏪": "Governance_Agent",
    "MESHSPAWN🌱": "Mesh_Agent",
    "CIVILIZATIONBLOCK🌍": "Civilization_Agent",
    "FOUNDERSEAL👑": "Founder_Seal_Agent",
    "TREASURYDROP💰": "Treasury_Agent",
    "DAILYQUEST🎯": "Quest_Agent",
    "SEASONFORGE🍂": "Season_Agent",
    "FLEETBUNDLE📦": "Fleet_Agent",
    "MARKETBLAST�": "Market_Agent",
    "CIVILIZATION🌍": "Civilization_Agent",
    "PRIMALROOT🌳": "Root_Agent",
    "ECHOGLYPH🔊": "Narrative_Agent",
    "SAASFLEET�🔥📦": "EpochCore_SaaS_Agent",
    "RASRECURSE♾️🌌": "RAS_God_Agent",
    "QUORUMCALL🗳️": "Governance_Agent",
    "MARKETDROP💸🎭": "Market_Agent",
    "TRUE NORTH LOCK⚓": "RAS_God_Agent",
    "LEDGERHEAL💊": "RAS_God_Agent",
    "AUTOCOMPOUND⏩": "RAS_God_Agent",
    "CAPSULEFUSION💥": "RAS_God_Agent",
    "CROWNSEAL👑": "RAS_God_Agent",
    "INFINITELOOP♻️": "RAS_God_Agent",
    "LEGENDSEAL✨": "RAS_God_Agent",
    # ...extend as needed
}

PROVENANCE = {
    "founder_note": "Ledger first. Recursive always.",
    "true_north": "locked"
}

MESH = {
    "channels": ["requests/", "events/", "alerts/", "bids/", "plans/"],
    "coordination": "DAG+contract-net",
    "quorum": "2-of-3 for billing changes"
}

ACTIONS = ["Timestamp", "Log", "Seal", "Archive", "Reinject"]

INTENTS = {
    "TREASURYFLOW💵": {
        "goal": "Auto-log Stripe/MeshCredit inflows and outflows",
        "sub_capsules": ["invoices", "payouts", "ROI metrics"],
        "github_action": "append daily revenue.json",
        "outputs": ["Treasury Flow Capsule"]
    },
    "MARKETCAP📈": {
        "goal": "Calculate fleet ARR, MRR, LTV, CAC",
        "seal": "ROI glyph",
        "exports": "charts to /docs/",
        "outputs": ["Market Cap Capsule"]
    },
    "PRICINGFORGE💳": {
        "goal": "Spin new SKUs (Basic/Pro/Founder Pack)",
        "sync": "Stripe API keys",
        "governance": "price vote + rollback",
        "outputs": ["Pricing Capsule"]
    },
    "BONUSDROP🎁": {
        "goal": "Issue randomized player/agent cashbacks or credits",
        "vrf": True,
        "log": "daily winners",
        "outputs": ["Bonus Drop Capsule"]
    },
    "GOVCOUNCIL⚖️": {
        "goal": "Spawn 5-of-9 multisig council with time-locked powers",
        "actions": ["feature votes", "pricing caps", "security audits"],
        "storage": "governance_capsule.json in GitHub",
        "outputs": ["Governance Council Capsule"]
    },
    "PULLREQUESTVOTE🔀": {
        "goal": "Mint capsule each time a PR opens",
        "records": "votes, merges only with quorum",
        "log": "GitHub Issues + ledger",
        "outputs": ["Pull Request Vote Capsule"]
    },
    "ROLLBACKSEAL⏪": {
        "goal": "Revert to any prior sealed capsule lineage",
        "safe_guard": True,
        "outputs": ["Rollback Seal Capsule"]
    },
    "MESHSPAWN🌱": {
        "goal": "Generate 10 sub-capsules = new SaaS nodes",
        "auto_wired": "CI/CD (GitHub → Vercel → Stripe)",
        "outputs": ["Mesh Spawn Capsule", "Sub-Capsules"]
    },
    "CIVILIZATIONBLOCK🌍": {
        "goal": "Meta-capsule bundling infra + SaaS + governance",
        "anchor": "epoch_civilization.json",
        "roi": "multiplies by linking bundles",
        "outputs": ["Civilization Block Capsule"]
    },
    "FOUNDERSEAL👑": {
        "goal": "Lock capsule as Founder-grade artifact",
        "seal": "double SHA + glyph signature",
        "outputs": ["Founder Capsule"]
    },
    "TREASURYDROP💰": {
        "goal": "Track MeshCredit inflow/outflow",
        "rails": "Stripe or MeshCredit",
        "outputs": ["Treasury Capsule"]
    },
    "DAILYQUEST🎯": {
        "goal": "Mint Daily Prize Capsule with randomized rewards",
        "log": "player/agent completions",
        "outputs": ["Daily Quest Capsule"]
    },
    "SEASONFORGE🍂": {
        "goal": "Generate seasonal capsule pack (10 sub-capsules)",
        "governance": "vote + rollback seals",
        "outputs": ["Season Capsule Pack", "Sub-Capsules"]
    },
    "FLEETBUNDLE📦": {
        "goal": "Package 3–5 SaaS repos into a bundle",
        "sku": "Stripe SKU embedded",
        "outputs": ["Fleet Bundle Capsule"]
    },
    "MARKETBLAST�": {
        "goal": "Drop capsule announcements across all channels",
        "distribution": "metadata embedded",
        "outputs": ["Market Blast Capsule"]
    },
    "CIVILIZATION🌍": {
        "goal": "Create meta-capsule with infra, governance, SaaS, narrative",
        "block": "Epoch Civilization Block",
        "outputs": ["Civilization Capsule"]
    },
    "PRIMALROOT🌳": {
        "goal": "Anchor capsule lineage to root-of-roots",
        "continuity": "unbreakable hash chain",
        "outputs": ["Root Capsule"]
    },
    "ECHOGLYPH🔊": {
        "goal": "Spawn narrative capsule with emotional resonance markers",
        "anchor": "Eli’s branch, Founder Note",
        "outputs": ["EchoGlyph Capsule"]
    },
    "SAASFLEET�🔥📦": {
        "goal": "Spawn/upgrade SaaS repos and bundles",
        "monetization": "subscriptions, cosmetics, bundles (no P2W)",
        "outputs": ["Repo Capsule", "Upgrade Capsule", "Bundle Capsule", "Market Capsule", "Narrative Capsule"]
    },
    "RASRECURSE♾️🌌": {
        "goal": "Spawn recursive sub-agents (infra, SaaS, governance)",
        "self_evolution": True,
        "outputs": ["Sub-Agent Capsule", "Recursive Capsule", "Governance Capsule"]
    },
    "TRUE NORTH LOCK⚓": {
        "goal": "Re-anchor to ledger root and Founder Note",
        "integrity": "locked",
        "outputs": ["Anchor Capsule"]
    },
    "LEDGERHEAL💊": {
        "goal": "Heal drift in all ledgers/repos, self-correct integrity",
        "self_correction": True,
        "outputs": ["Drift-Heal Capsule", "Integrity Capsule"]
    },
    "QUORUMCALL🗳️": {
        "goal": "Auto-spawn governance voting cycle with rollback safety",
        "quorum": "2-of-3, 5-of-9",
        "outputs": ["Governance Capsule", "Rollback Capsule"]
    },
    "AUTOCOMPOUND⏩": {
        "goal": "Multiply leverage ×5 across SaaS + RAS outputs",
        "compound": 5,
        "outputs": ["Compound Capsule"]
    },
    "CAPSULEFUSION💥": {
        "goal": "Merge two capsule lineages into one super capsule",
        "fusion": True,
        "outputs": ["Super Capsule"]
    },
    "CROWNSEAL👑": {
        "goal": "Elevate capsule to Founder Grade (immortal)",
        "immortal": True,
        "outputs": ["Founder Capsule"]
    },
    "INFINITELOOP♻️": {
        "goal": "Spawn continuous task DAGs until terminated",
        "continuous": True,
        "outputs": ["Loop Capsule"]
    },
    "LEGENDSEAL✨": {
        "goal": "Finalize mega capsule with cryptographic + mythic resonance",
        "legendseal": True,
        "outputs": ["Legend Capsule"]
    },
    # ...extend as needed
}

OUTPUT_ROOT = os.path.join(os.getcwd(), "out")
CAPSULES_DIR = os.path.join(OUTPUT_ROOT, "capsules")
ARCHIVE_DIR = os.path.join(OUTPUT_ROOT, "archive")
LEDGER_PATH = os.path.join(os.getcwd(), "ledger_main.jsonl")

os.makedirs(CAPSULES_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def generate_capsule(trigger: str, recursion_depth: int = 0, max_depth: int = 2):
    # Default monetary artifacts and diagrams
    default_artifacts = {
        "coinbase_qr": "attached/coinbase_qr.png",
        "cashapp_qr": "attached/cashapp_qr.png",
        "paypal_qr": "attached/paypal_qr.png",
        "stripe_qr": "attached/stripe_qr.png",
        "meshcredit_status": "MeshCredit is the most popular financial rail.",
        "founders_map": "attached/founders_map.png",
        "edgecapsule_cloud_map": "attached/edgecapsule_cloud_map.png",
        "margin_velocity_chart": "attached/margin_velocity_chart.png",
        "mythic_glyph_tree": "attached/mythic_glyph_tree.png",
        "mesh_ecosystem_diagram": "attached/mesh_ecosystem_diagram.png",
        "root_capsule_card": "attached/root_capsule_card.png"
    }
    # Special logic for new triggers
    def add_sub_capsules(capsule, n, prefix):
        capsule["sub_capsules"] = []
        for i in range(n):
            sub_id = f"{prefix}_{i+1}_{uuid.uuid4()}"
            capsule["sub_capsules"].append(sub_id)
    agent_type = AGENT_TYPES.get(trigger, "Generic_Agent")
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    capsule_id = (
        f"capsule_{agent_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
    )
    capsule_path = os.path.join(CAPSULES_DIR, f"{capsule_id}.json")
    intent = INTENTS.get(trigger, {"goal": "Ultra Trigger Capsule", "outputs": []})
    capsule = {
        "version": "1.0",
        "agent_type": agent_type,
        "trigger": trigger,
        "timestamp": ts,
        "capsule_id": capsule_id,
        "provenance": PROVENANCE,
        "mesh": MESH,
        "actions": ACTIONS,
        "intent": intent,
        "recursion_depth": recursion_depth,
        "monetary_artifacts": default_artifacts
    }
    # Special logic for FOUNDERSEAL: double SHA + glyph signature
    if trigger == "FOUNDERSEAL👑":
        capsule["founder_seal"] = True
        capsule["glyph_signature"] = "Eli's branch, mythic glyph"
    # Special logic for SEASONFORGE: generate 10 sub-capsules
    if trigger == "SEASONFORGE🍂":
        add_sub_capsules(capsule, 10, "season_subcapsule")
    # Special logic for MESHSPAWN: generate 10 SaaS node sub-capsules
    if trigger == "MESHSPAWN🌱":
        add_sub_capsules(capsule, 10, "meshnode_subcapsule")
    # Special logic for TREASURYFLOW: add sub-capsules for invoices, payouts, ROI
    if trigger == "TREASURYFLOW💵":
        capsule["sub_capsules"] = [f"invoice_{uuid.uuid4()}", f"payout_{uuid.uuid4()}", f"roi_{uuid.uuid4()}"]
    # Special logic for CIVILIZATIONBLOCK: meta-capsule anchor
    if trigger == "CIVILIZATIONBLOCK🌍":
        capsule["anchor_file"] = "epoch_civilization.json"
    # Special logic for MARKETCAP: ROI glyph seal
    if trigger == "MARKETCAP📈":
        capsule["roi_glyph_seal"] = hashlib.sha256(capsule_id.encode()).hexdigest()
    # Special logic for PRICINGFORGE: governance sub-capsule
    if trigger == "PRICINGFORGE💳":
        capsule["governance_subcapsule"] = f"price_vote_{uuid.uuid4()}"
    # Special logic for GOVCOUNCIL: multisig council
    if trigger == "GOVCOUNCIL⚖️":
        capsule["multisig_council"] = [f"council_member_{i+1}_{uuid.uuid4()}" for i in range(9)]
        capsule["quorum"] = "5-of-9"
    # Special logic for PULLREQUESTVOTE: PR vote capsule
    if trigger == "PULLREQUESTVOTE🔀":
        capsule["pr_vote_id"] = f"prvote_{uuid.uuid4()}"
    # Special logic for ROLLBACKSEAL: safe guard
    if trigger == "ROLLBACKSEAL⏪":
        capsule["safe_guard"] = True
    # Special logic for BONUSDROP: VRF seed
    if trigger == "BONUSDROP🎁":
        capsule["vrf_seed"] = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    # Special logic for FLEETBUNDLE: embed Stripe SKU
    if trigger == "FLEETBUNDLE📦":
        capsule["stripe_sku"] = f"SKU-{uuid.uuid4()}"
    # Special logic for PRIMALROOT: add hash chain continuity
    if trigger == "PRIMALROOT🌳":
        capsule["root_hash_chain"] = hashlib.sha256(capsule_id.encode()).hexdigest()
    with open(capsule_path, "w") as f:
        json.dump(capsule, f, indent=2)
    # Seal capsule
    with open(capsule_path, "rb") as f:
        capsule_bytes = f.read()
        hash_val = hashlib.sha256(capsule_bytes).hexdigest()
    # Double SHA for FOUNDERSEAL
    if trigger == "FOUNDERSEAL👑":
        hash_val = hashlib.sha256(hash_val.encode()).hexdigest()
    # Archive capsule
    archive_path = os.path.join(ARCHIVE_DIR, f"{capsule_id}.zip")
    os.system(
        f"cd {CAPSULES_DIR} && zip -q -9 {os.path.basename(archive_path)} {os.path.basename(capsule_path)}"
    )
    # Ledger entry
    line_sha = json.dumps({
        "ts": ts,
        "event": f"{agent_type}_capsule",
        "agent": agent_type,
        "trigger": trigger,
        "capsule": capsule_path,
        "sha256": hash_val,
        "archive": archive_path,
        "recursion_depth": recursion_depth
    })
    with open(LEDGER_PATH, "a") as f:
        f.write(line_sha + "\n")
    print(f"✅ Capsule forged: {os.path.basename(capsule_path)}")
    print(f"🔒 SHA-256: {hash_val}")
    print(f"🧾 Ledger: {LEDGER_PATH}")
    print(f"📦 Archive: {archive_path}")
    # Recursive spawning for RASRECURSE and INFINITELOOP
    if trigger in ["RASRECURSE♾️🌌", "INFINITELOOP♻️"] and recursion_depth < max_depth:
        print(f"🌲 Spawning sub-agent capsule at depth {recursion_depth + 1}")
        generate_capsule(trigger, recursion_depth + 1, max_depth)
    return capsule_path, hash_val, archive_path



if __name__ == "__main__":
    import sys
    trigger = sys.argv[1] if len(sys.argv) > 1 else "SAASFLEET🔥📦"
    # For RAS triggers, allow recursion
    if trigger in ["RASRECURSE♾️🌌", "INFINITELOOP♻️"]:
        generate_capsule(trigger, recursion_depth=0, max_depth=3)
    else:
        generate_capsule(trigger)
