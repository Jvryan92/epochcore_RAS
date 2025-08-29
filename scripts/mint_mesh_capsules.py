#!/usr/bin/env python3
"""
MeshCredit Capsule Minting Automation
Mints all capsule primitives across all domains into tamper-evident ledger and JSON files.
"""
import datetime as dt
import hashlib

# Imports
import json
import os
import random

# List of 40 advanced compounding strategies
COMPOUNDING_STRATEGIES = [
    "Recursive Yield Amplification",
    "Temporal Mesh Rebalancing",
    "Quantum Liquidity Loop",
    "Autonomous Capsule Fusion",
    "MeshCredit Cascade",
    "Ledger Provenance Chaining",
    "Adaptive Interest Compounding",
    "Multi-Domain Mesh Synthesis",
    "Capsule Swarm Optimization",
    "Self-Referential Growth",
    "Dynamic Capsule Forking",
    "Resilience Mesh Overlay",
    "StrategyDeck Interlink",
    "Ethical Reflection Loop",
    "Evolutionary Capsule Mutation",
    "Temporal Ledger Stacking",
    "Collaborative Mesh Expansion",
    "Intelligence Capsule Chaining",
    "Autonomous Strategy Rotation",
    "Capsule Provenance Recursion",
    "MeshCredit Recursive Mint",
    "Capsule Ledger Interlock",
    "Self-Improvement Cascade",
    "Quantum Mesh Fork",
    "Adaptive Mesh Reallocation",
    "StrategyDeck Provenance",
    "Temporal Compounding Chain",
    "Capsule Swarm Compounding",
    "Autonomous Mesh Rebalancer",
    "Recursive Ledger Growth",
    "Capsule Evolution Overlay",
    "Ethical Compounding Loop",
    "Collaborative Capsule Fusion",
    "Intelligence Mesh Cascade",
    "StrategyDeck Capsule Chain",
    "Self-Referential Ledger",
    "Quantum Capsule Amplification",
    "Adaptive Mesh Forking",
    "Temporal Mesh Overlay",
    "Capsule Provenance Amplifier",
    "Recursive Mesh Expansion",
]


def now():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


# Output directories


LEDGER = "ledger_main.jsonl"

OUTDIR = "out/genesis_capsules"
os.makedirs(OUTDIR, exist_ok=True)

# Capsule primitives by domain
CAPSULES = {
    "finance": [
        ("MeshCredit Yield Capsule", "ROI = staked capsule flow."),
        ("Liquidity Loop Capsule", "mesh auto-recycles liquidity daily."),
        ("Compounding Capsule Bond", "interest escalates per epoch."),
        ("Cross-Pool Capsule", "bridges pools into single capsule."),
        ("MeshCredit Yield ETF", "bundle of capsule yields."),
        ("Capsule Stable Yield", "locked stable ROI."),
        ("Capsule Yield Futures", "forward yield capsule contracts."),
        ("Capsule ROI Swap", "ROI tokenized as swap capsule."),
        ("Capsule Infinite Loop", "perpetual compounding mesh credit."),
        ("Capsule ROI Crown", "annual top yield capsule."),
    ],
    "trading": [
        ("Capsule DEX Share", "capsule = trading equity."),
        ("Capsule Fee Split", "earn % of DEX fees."),
        ("Capsule Spread Bonds", "ROI tied to spread capture."),
        ("Capsule Arbitrage", "sealed arb strategies as capsules."),
        ("Capsule Leverage", "capsule = leveraged mesh credit."),
        ("Capsule Short Capsule", "short other capsules."),
        ("Capsule Perp", "perpetual mesh credit derivative."),
        ("Capsule Market-Maker", "capsule = LP position."),
        ("Capsule Flash Credit", "flash loan capsules."),
        ("Capsule DEX Crown", "top trader annual capsule."),
    ],
    "lending": [
        ("Capsule Credit Line", "capsule grants revolving loan."),
        ("Capsule Mortgage", "SaaS asset tied to capsule loan."),
        ("Capsule Payday", "instant cash capsule."),
        ("Capsule Credit Score", "capsule reputation rating."),
        ("Capsule Risk Bond", "capsule insures borrower."),
        ("Capsule Margin", "credit-backed capsule leverage."),
        ("Capsule Collateral Vault", "capsule as locked collateral."),
        ("Capsule Loan Crowns", "lending guild award."),
        ("Capsule MicroLoan", "tiny capsule loans for mesh agents."),
        ("Capsule Lending Thrones", "elite lender governance."),
    ],
    "insurance": [
        ("Capsule Coverage", "insurance capsule."),
        ("Capsule Mesh Pool", "shared insurance pool."),
        ("Capsule Drift Insurance", "covers agent drift."),
        ("Capsule Market Crash Bond", "pays on market dips."),
        ("Capsule Weather Credit", "climate risk sealed in capsule."),
        ("Capsule Health Mesh", "health insurance capsules."),
        ("Capsule Safety Fund", "pooled risk capsule."),
        ("Capsule Fraud Vault", "detect/report fraud as capsule."),
        ("Capsule Black Swan", "payout for rare events."),
        ("Capsule Risk Thrones", "elite risk crowning."),
    ],
    "gaming": [
        ("Capsule Loot Bonds", "loot tied to MeshCredit."),
        ("Capsule PvP Stakes", "battle staked capsules."),
        ("Capsule Speedrun ROI", "WR = MeshCredit prize."),
        ("Capsule Clan Treasury", "guilds manage capsule credits."),
        ("Capsule eSports Mesh", "tournament prize capsule."),
        ("Capsule Seasonal Vaults", "prize vault capsules."),
        ("Capsule RNG Drop", "provable fair capsule."),
        ("Capsule Victory Crowns", "crown capsule for winner."),
        ("Capsule Quest Tokens", "quest payouts as capsules."),
        ("Capsule Game Thrones", "eSports ruler sealed yearly."),
    ],
    "saas": [
        ("Capsule Subscription ROI", "SaaS subs sealed."),
        ("Capsule Seat Credit", "capsule seat monetized."),
        ("Capsule Upgrade Bond", "SaaS upgrade rights."),
        ("Capsule Referral Credit", "growth referral capsule."),
        ("Capsule Usage Token", "SaaS usage metered as capsule."),
        ("Capsule Feature Rights", "feature toggle capsule."),
        ("Capsule App Loyalty", "loyalty capsule."),
        ("Capsule Churn Insurance", "protects revenue drop."),
        ("Capsule Upsell Vault", "upsell as capsule."),
        ("Capsule SaaS Thrones", "SaaS king crowned."),
    ],
    "iaas": [
        ("Capsule VM Credits", "compute credits minted."),
        ("Capsule Bandwidth Bonds", "bandwidth rights capsule."),
        ("Capsule Power Mesh", "power tied to capsule."),
        ("Capsule Edge Compute", "edge capsule ROI."),
        ("Capsule Quantum Lease", "quantum slot capsule."),
        ("Capsule SLA Bond", "ROI tied to uptime."),
        ("Capsule Disaster Pool", "disaster fund capsule."),
        ("Capsule Energy Crown", "energy ROI capsule."),
        ("Capsule Carbon Credits", "carbon offset capsules."),
        ("Capsule Infra Thrones", "infra kings crowned."),
    ],
    "paas": [
        ("Capsule API Keys", "API quota capsules."),
        ("Capsule Plugin Rights", "plugin slot as capsule."),
        ("Capsule Debug Vault", "debug as service capsule."),
        ("Capsule Dev Guild", "guild ROI capsules."),
        ("Capsule CI Badge Bonds", "test coverage capsule."),
        ("Capsule Hackathon Pool", "hackathon capsule fund."),
        ("Capsule Doc Proof", "sealed docs as capsule."),
        ("Capsule Builder Rewards", "builder credit capsule."),
        ("Capsule SDK Crown", "SDK king capsule."),
        ("Capsule Dev Thrones", "dev ruler crowned."),
    ],
    "ras": [
        ("Capsule Clone Credit", "clone agent ROI."),
        ("Capsule Mesh Link", "agent link credit."),
        ("Capsule Skill Bond", "skills monetized capsule."),
        ("Capsule Drift Pool", "insure drift ROI."),
        ("Capsule Jury Credits", "jury duty ROI capsule."),
        ("Capsule Memory Seals", "memory capsule monetized."),
        ("Capsule Swarm ROI", "swarm capsule ROI."),
        ("Capsule Evolution Pool", "recursive growth capsules."),
        ("Capsule Agent Thrones", "recursive ruler."),
        ("Capsule AI Crown", "AI leader capsule."),
    ],
    "governance": [
        ("Capsule Vote Bonds", "governance = ROI."),
        ("Capsule Quorum Credits", "quorum sealed ROI."),
        ("Capsule Veto Rights", "veto monetized."),
        ("Capsule Proposal Bonds", "proposal cost capsule."),
        ("Capsule Term Vaults", "term-limited capsule funds."),
        ("Capsule Treasury Mesh", "treasury capsule pool."),
        ("Capsule Audit Credit", "audit = credit capsule."),
        ("Capsule Council Crowns", "council sealed capsule."),
        ("Capsule Civic Credit", "citizen ROI."),
        ("Capsule Gov Thrones", "governance rulers."),
    ],
    "culture": [
        ("Capsule Music Royalties", "music capsule ROI."),
        ("Capsule Film Credits", "film capsule ROI."),
        ("Capsule Art Bonds", "art capsule royalties."),
        ("Capsule Festival Tokens", "cultural mesh credits."),
        ("Capsule Myth Rights", "myth minted as capsule."),
        ("Capsule Lore Chains", "lore capsule ROI."),
        ("Capsule Story Credit", "writer capsule ROI."),
        ("Capsule Legend Crowns", "legendary capsule."),
        ("Capsule Heritage Mesh", "heritage asset capsules."),
        ("Capsule Founder Thrones", "founder culture capsule."),
    ],
    "education": [
        ("Capsule Learning Credits", "capsule = class credit."),
        ("Capsule Puzzle Tokens", "puzzle rewards capsule."),
        ("Capsule School Vault", "school fund capsule."),
        ("Capsule Teacher Bonds", "teacher ROI capsules."),
        ("Capsule Kid Quests", "quest capsule for kids."),
        ("Capsule Knowledge Rights", "sealed knowledge capsule."),
        ("Capsule Study Mesh", "study session ROI."),
        ("Capsule Education Crowns", "annual capsule awards."),
        ("Capsule Kid Thrones", "children’s leader capsule."),
        ("Capsule Family Mesh", "family credit capsule."),
    ],
    "health": [
        ("Capsule Fitness Credits", "workout capsule ROI."),
        ("Capsule Diet Bonds", "nutrition capsule."),
        ("Capsule Sleep Tokens", "sleep mesh credits."),
        ("Capsule Health Pools", "group health capsule."),
        ("Capsule Therapy Rights", "therapy access capsule."),
        ("Capsule Wellness Crown", "wellness capsule."),
        ("Capsule Meditation Mesh", "meditation ROI."),
        ("Capsule Bio Data Rights", "capsule for data."),
        ("Capsule Health Thrones", "health ruler."),
        ("Capsule DNA Mesh", "capsule DNA health."),
    ],
    "ai": [
        ("Capsule Model Rights", "model ROI capsule."),
        ("Capsule Training Credits", "training time capsule."),
        ("Capsule Dataset Bonds", "data ROI capsules."),
        ("Capsule API Calls", "inference calls capsule."),
        ("Capsule Fine-Tune ROI", "fine-tuning capsule."),
        ("Capsule Model Crowns", "model capsule awards."),
        ("Capsule AI Futures", "model performance capsules."),
        ("Capsule Patent Capsules", "IP sealed as capsules."),
        ("Capsule AI Thrones", "AI capsule kings."),
        ("Capsule Research Mesh", "research capsule ROI."),
    ],
    "energy": [
        ("Capsule Solar Credits", "solar ROI capsule."),
        ("Capsule Wind Bonds", "wind capsule ROI."),
        ("Capsule Hydro Mesh", "hydro capsule ROI."),
        ("Capsule Nuclear Credits", "nuclear ROI."),
        ("Capsule Energy Pools", "energy capsule funds."),
        ("Capsule Grid Crowns", "grid leader capsules."),
        ("Capsule Carbon Mesh", "capsule carbon ROI."),
        ("Capsule Battery Bonds", "battery capsule ROI."),
        ("Capsule Green Thrones", "green ruler capsules."),
        ("Capsule Energy Royals", "energy crown capsule."),
    ],
    "global": [
        ("Capsule Border Rights", "border trade capsule."),
        ("Capsule Currency Mesh", "currency as capsule."),
        ("Capsule Trade Bonds", "capsule trade credits."),
        ("Capsule Tariff Proofs", "tariff ROI capsules."),
        ("Capsule Port Crowns", "port capsule ROI."),
        ("Capsule Global Thrones", "world ruler capsules."),
        ("Capsule Diplomacy Mesh", "diplomacy capsule ROI."),
        ("Capsule Peace Bonds", "capsule peace ROI."),
        ("Capsule War Insurance", "conflict ROI capsule."),
        ("Capsule World Crown", "global mesh ruler."),
    ],
}


def mint_capsules():
    prev = "genesis"
    count = 0
    for domain, items in CAPSULES.items():
        idx = 0
        for capsule in items:
            title, desc = capsule
            idx += 1
            count += 1
            cap_id = f"CAP-{domain.upper()}-{idx:03d}"
            ts = now()
            # Assign 2-4 random compounding strategies to each capsule
            k_strat = random.randint(2, 4)
            strategies = random.sample(COMPOUNDING_STRATEGIES, k=k_strat)
            body = {
                "capsule_id": cap_id,
                "domain": domain,
                "title": title,
                "description": desc,
                "timestamp": ts,
                "provenance": {
                    "prev_hash": prev,
                    "compounding_strategy": strategies,
                },
            }
            h = sha256(json.dumps(body, separators=(",", ":")))
            capsule_obj = dict(body)
            capsule_obj["self_sha256"] = h
            with open(f"{OUTDIR}/{cap_id}.json", "w") as f:
                json.dump(capsule_obj, f, separators=(",", ":"))
            entry = {
                "ts": ts,
                "capsule_id": cap_id,
                "entry_hash": h,
                "prev_hash": prev,
                "compounding_strategy": strategies,
            }
            with open(LEDGER, "a") as f:
                f.write(json.dumps(entry, separators=(",", ":")) + "\n")
            prev = h
            strat_str = ", ".join(strategies)
            print(f"✅ Minted {cap_id} — {title} [{strat_str}]")
    print(f"🔒 Forge complete. Ledger tip: {prev}. Total capsules: {count}")
