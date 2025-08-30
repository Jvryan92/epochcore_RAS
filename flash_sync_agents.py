#!/usr/bin/env python3
"""
Flash Sync Agents - Rapidly synchronizes agent state across the mesh network
"""

import base64
import datetime as dt
import glob
import hashlib
import hmac
import json
import os
import random
import statistics
import sys
import uuid


# Utility functions
def timestamp_utc():
    """Generate ISO-8601 UTC timestamp"""
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_short():
    """Generate short timestamp for filenames"""
    return dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def hash_bytes(b):
    """SHA-256 hash of bytes"""
    return hashlib.sha256(b).hexdigest()


def hash_string(s):
    """SHA-256 hash of string"""
    return hash_bytes(s.encode())


# Configuration
LEDGER_DIR = "./ledger"
SYNC_DIR = "./sync"
os.makedirs(LEDGER_DIR, exist_ok=True)
os.makedirs(SYNC_DIR, exist_ok=True)

# Environment and settings
SEED = os.getenv("SEED", "TrueNorth")
MESH_SECRET = os.getenv("MESH_SECRET", "mesh-demo-secret").encode()
FLASH_THRESHOLD = int(os.getenv("FLASH_THRESHOLD", "5"))
CONSENSUS_LEVEL = os.getenv("CONSENSUS_LEVEL", "pbft")  # Options: pbft, raft, paxos

# Signature generation


def sign_data(data):
    """Create HMAC signature for data"""
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(MESH_SECRET, serialized, hashlib.sha256).hexdigest()


# DID generation


def generate_did():
    """Generate a unique DID for mesh"""
    return "did:mesh:" + str(uuid.uuid4()).lower()


# JWK generation for agent


def generate_jwk(agent_id):
    """Generate JSON Web Key for agent authentication"""
    key_material = hash_string(agent_id + SEED).encode()
    return {
        "kty": "oct",
        "alg": "HS256",
        "kid": hash_string(agent_id)[:12],
        "k": base64.urlsafe_b64encode(key_material)[:32].decode(),
    }


# Agent definitions (could be loaded from registry)
AGENTS = [
    {
        "id": "agent://alpha",
        "did": generate_did(),
        "skills": [
            "scrape.web",
            "vector.store",
            "atomize.payload",
            "cohere.frames",
            "sandbox.dryrun",
        ],
        "rel": 0.94,
        "lat": 210,
        "status": "active",
    },
    {
        "id": "agent://bravo",
        "did": generate_did(),
        "skills": [
            "plan.compose",
            "review.policies",
            "diffuse.channels",
            "schedule.drip",
            "rollback.diff",
        ],
        "rel": 0.92,
        "lat": 250,
        "status": "active",
    },
    {
        "id": "agent://gamma",
        "did": generate_did(),
        "skills": [
            "echo.measure",
            "blackboard.merge",
            "snapshot.world",
            "sign.proof",
            "attest.supply",
        ],
        "rel": 0.90,
        "lat": 300,
        "status": "active",
    },
    {
        "id": "agent://delta",
        "did": generate_did(),
        "skills": ["stitch.docs", "index.graph", "publish.codex"],
        "rel": 0.91,
        "lat": 230,
        "status": "active",
    },
    {
        "id": "agent://epsilon",
        "did": generate_did(),
        "skills": ["sweep.sensors", "consensus.vote", "rollback.diff", "attest.supply"],
        "rel": 0.89,
        "lat": 275,
        "status": "active",
    },
]

# Flash sync operation


def flash_sync_agents():
    """Perform flash sync of all agents"""
    print(f"⚡ Starting flash sync of {len(AGENTS)} agents...")

    # 1. Generate sync manifest
    sync_id = f"sync-{timestamp_short()}"
    sync_manifest = {
        "id": sync_id,
        "ts": timestamp_utc(),
        "agents": [a["id"] for a in AGENTS],
        "consensus": CONSENSUS_LEVEL,
        "seed_fingerprint": hash_string(SEED)[:8],
    }

    # 2. Prepare agent state snapshots
    snapshots = []
    for agent in AGENTS:
        # Generate synthetic state data
        latency = agent["lat"] + random.randint(-20, 30)
        state_hash = hash_string(f"{agent['id']}:{timestamp_utc()}:{random.random()}")

        snapshot = {
            "agent_id": agent["id"],
            "ts": timestamp_utc(),
            "state_hash": state_hash,
            "latency_ms": latency,
            "reliability": round(agent["rel"] * (0.95 + random.random() * 0.1), 3),
            "skills_active": random.sample(
                agent["skills"], k=max(1, len(agent["skills"]) - 1)
            ),
            "memory_usage_mb": random.randint(120, 350),
        }
        snapshots.append(snapshot)

    # 3. Calculate mesh integrity metrics
    latencies = [s["latency_ms"] for s in snapshots]
    mean_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0

    reliability_scores = [s["reliability"] for s in snapshots]
    mean_reliability = sum(reliability_scores) / len(reliability_scores)

    # 4. Generate merkle tree of snapshots
    snapshot_hashes = [hash_string(json.dumps(s, sort_keys=True)) for s in snapshots]

    def build_merkle_tree(hashes):
        if not hashes:
            return ""
        if len(hashes) == 1:
            return hashes[0]

        next_level = []
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else hashes[i]
            combined = hash_string(left + right)
            next_level.append(combined)

        return build_merkle_tree(next_level)

    merkle_root = build_merkle_tree(snapshot_hashes)

    # 5. Create sync receipt
    sync_receipt = {
        "sync_id": sync_id,
        "ts": timestamp_utc(),
        "agent_count": len(AGENTS),
        "merkle_root": merkle_root,
        "stats": {
            "mean_latency_ms": round(mean_latency, 1),
            "p95_latency_ms": p95_latency,
            "mean_reliability": round(mean_reliability, 3),
        },
        "consensus_achieved": True,
        "anomalies": [],
    }

    # 6. Check for anomalies
    if latencies:
        stdev = statistics.pstdev(latencies) or 1.0
        for i, snapshot in enumerate(snapshots):
            z_score = (snapshot["latency_ms"] - mean_latency) / stdev
            if abs(z_score) > 1.5:
                anomaly = {
                    "agent_id": snapshot["agent_id"],
                    "metric": "latency",
                    "value": snapshot["latency_ms"],
                    "z_score": round(z_score, 2),
                    "action": "monitor" if abs(z_score) < 2.5 else "investigate",
                }
                sync_receipt["anomalies"].append(anomaly)
                sync_receipt["consensus_achieved"] = sync_receipt[
                    "consensus_achieved"
                ] and (abs(z_score) < FLASH_THRESHOLD)

    # 7. Generate signed consensus
    consensus_doc = {
        "sync_id": sync_id,
        "merkle_root": merkle_root,
        "ts": timestamp_utc(),
        "achieved": sync_receipt["consensus_achieved"],
    }

    signatures = []
    for agent in AGENTS:
        # Simulate PBFT consensus with agent signatures
        signatures.append(
            {
                "agent_id": agent["id"],
                "signature": sign_data({**consensus_doc, "signer": agent["id"]}),
                "ts": timestamp_utc(),
            }
        )

    consensus_doc["signatures"] = signatures

    # 8. Write outputs
    with open(f"{SYNC_DIR}/{sync_id}_manifest.json", "w") as f:
        json.dump(sync_manifest, f, separators=(",", ":"))

    with open(f"{SYNC_DIR}/{sync_id}_snapshots.json", "w") as f:
        json.dump(snapshots, f, separators=(",", ":"))

    with open(f"{SYNC_DIR}/{sync_id}_receipt.json", "w") as f:
        json.dump(sync_receipt, f, separators=(",", ":"))

    with open(f"{SYNC_DIR}/{sync_id}_consensus.json", "w") as f:
        json.dump(consensus_doc, f, separators=(",", ":"))

    # 9. Update ledger
    ledger_entry = {
        "ts": timestamp_utc(),
        "event": "flash_sync",
        "sync_id": sync_id,
        "merkle_root": merkle_root,
        "consensus": sync_receipt["consensus_achieved"],
        "anomaly_count": len(sync_receipt["anomalies"]),
        "signature": sign_data(
            {"sync_id": sync_id, "merkle_root": merkle_root, "ts": timestamp_utc()}
        ),
    }

    # Append to ledger
    ledger_file = f"{LEDGER_DIR}/sync_ledger.jsonl"
    with open(ledger_file, "a") as f:
        f.write(json.dumps(ledger_entry, separators=(",", ":")) + "\n")

    # 10. Update registry with latest state
    registry = {
        "version": "1.5",
        "ts": timestamp_utc(),
        "last_sync": sync_id,
        "agents": [
            {
                "agent_id": agent["id"],
                "did": agent["did"],
                "skills": agent["skills"],
                "status": "active",
                "reliability": next(
                    (
                        s["reliability"]
                        for s in snapshots
                        if s["agent_id"] == agent["id"]
                    ),
                    agent["rel"],
                ),
                "latency_ms": next(
                    (
                        s["latency_ms"]
                        for s in snapshots
                        if s["agent_id"] == agent["id"]
                    ),
                    agent["lat"],
                ),
                "last_seen": timestamp_utc(),
            }
            for agent in AGENTS
        ],
    }

    registry["signature"] = sign_data(registry)

    with open(f"{LEDGER_DIR}/mesh_registry_latest.json", "w") as f:
        json.dump(registry, f, separators=(",", ":"))

    # Return summary
    return {
        "sync_id": sync_id,
        "ts": timestamp_utc(),
        "agents_synced": len(AGENTS),
        "consensus_achieved": sync_receipt["consensus_achieved"],
        "anomalies": len(sync_receipt["anomalies"]),
        "artifacts": [
            f"{SYNC_DIR}/{sync_id}_manifest.json",
            f"{SYNC_DIR}/{sync_id}_snapshots.json",
            f"{SYNC_DIR}/{sync_id}_receipt.json",
            f"{SYNC_DIR}/{sync_id}_consensus.json",
            f"{LEDGER_DIR}/mesh_registry_latest.json",
        ],
        "ledger": ledger_file,
    }


if __name__ == "__main__":
    result = flash_sync_agents()
    print(json.dumps(result, indent=2))
    print(
        f"\n✅ Flash sync completed! Consensus {'achieved' if result['consensus_achieved'] else 'FAILED'}"
    )
    if result["anomalies"] > 0:
        print(
            f"⚠️  {result['anomalies']} anomalies detected - check receipt for details"
        )
    sys.exit(0 if result["consensus_achieved"] else 1)
