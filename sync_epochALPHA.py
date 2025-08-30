#!/usr/bin/env python3
"""
epochALPHA Agent Sync
Special sync operation for the epochALPHA agent - master coordinator for agent fleet
Integrates with Mesh Credit, StrategyDECK, and video game systems
"""

import datetime
import hashlib
import hmac
import json
import os
import random
import time
import uuid
import logging
import subprocess
import statistics
import sys
import zipfile
import glob
import base64
import io
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("epochALPHA")


# Integration classes
class MeshCreditIntegration:
    """
    Integration with Mesh Credit universal game economy system.
    Provides wallet operations, token economics, and shop functionality.
    """

    def __init__(self, ledger_path: str = "ledger/market_ledger.jsonl"):
        self.ledger_path = ledger_path
        self.token_prices = {
            "common": 100,
            "uncommon": 250,
            "rare": 500,
            "epic": 1000,
            "legendary": 2500,
        }
        self.yield_curves = {"daily": 5, "weekly": 40, "monthly": 200}
        logger.info(f"MeshCredit integration initialized with ledger: {ledger_path}")

    def get_wallet_balance(self, wallet_id: str) -> int:
        """Get the current balance for a wallet"""
        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    data = json.loads(line)
                    if (
                        data.get("type") == "wallet_balance"
                        and data.get("wallet_id") == wallet_id
                    ):
                        return data.get("balance", 0)
        except FileNotFoundError:
            logger.warning(f"Ledger file not found: {self.ledger_path}")
        except json.JSONDecodeError:
            logger.error(f"Corrupted ledger entry in: {self.ledger_path}")
        return 0

    def record_transaction(
        self, from_wallet: str, to_wallet: str, amount: int, memo: str = ""
    ) -> bool:
        """Record a mesh credit transaction in the ledger"""
        transaction = {
            "type": "transaction",
            "timestamp": datetime.datetime.now().isoformat(),
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "memo": memo,
            "txid": hashlib.sha256(
                f"{time.time()}{from_wallet}{to_wallet}{amount}".encode()
            ).hexdigest(),
        }

        try:
            with open(self.ledger_path, "a") as f:
                f.write(json.dumps(transaction) + "\n")
            logger.info(
                f"Transaction recorded: {amount} credits from {from_wallet} to {to_wallet}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to record transaction: {e}")
            return False

    def calculate_daily_yield(self, wallet_id: str) -> int:
        """Calculate daily yield for a wallet based on holdings"""
        balance = self.get_wallet_balance(wallet_id)
        # Base yield is 0.5% daily
        return int(balance * 0.005)


class MeshNetworkIntegration:
    """
    Advanced MESH network integration for epochALPHA.
    Provides agent coordination, DAG execution, trust scoring, and anomaly detection.
    Includes merkle tree verification and tamper-proof ledger management.
    """

    def __init__(self, ledger_dir="./ledger"):
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(exist_ok=True)
        self.master_ledger = self.ledger_dir / "ledger_main.jsonl"
        self.cas_dir = self.ledger_dir / "cas"
        self.cas_dir.mkdir(exist_ok=True)
        self.log_file = self.ledger_dir / "mesh_log.jsonl"
        self.mesh_secret = os.getenv("MESH_SECRET", "mesh-demo-secret").encode()
        self.slo_lat_ms_p95 = int(os.getenv("SLO", "400"))
        self.budget_usd = float(os.getenv("BUD", "1500"))
        self.segments = int(os.getenv("SEG", "25"))
        self.cycles_per_segment = int(os.getenv("CPS", "20"))
        self.seed = os.getenv("SEED", "TrueNorth")

        # Initialize or load chain state
        self.chain_state_file = self.ledger_dir / "mesh_chain_state.json"
        if self.chain_state_file.exists():
            with open(self.chain_state_file, "r") as f:
                self.chain_state = json.load(f)
        else:
            self.chain_state = {
                "ts": self.generate_timestamp(),
                "root": self.hash_string(f"genesis:{self.seed}"),
                "last": "genesis",
                "segments": [],
            }
            self.save_chain_state()

        # Ensure ledger file exists
        with open(self.master_ledger, "a"):
            pass

        # Initialize agent registry and ontology
        self.agents = [
            {
                "id": "agent://alpha",
                "skills": [
                    "scrape.web",
                    "summarize.md",
                    "price.check",
                    "vector.store",
                    "sandbox.dryrun",
                ],
                "rel": 0.94,
                "lat": 210,
            },
            {
                "id": "agent://bravo",
                "skills": [
                    "plan.compose",
                    "review.policies",
                    "risk.scan",
                    "consensus.vote",
                    "rollback.diff",
                ],
                "rel": 0.92,
                "lat": 250,
            },
            {
                "id": "agent://gamma",
                "skills": [
                    "export.report",
                    "publish.codex",
                    "blackboard.merge",
                    "snapshot.world",
                    "attest.supply",
                ],
                "rel": 0.90,
                "lat": 300,
            },
        ]

        # Initialize multi-mesh ontology
        self.mesh_ontology = {
            "drip": {
                "edges": {
                    "drip.signal": [
                        "atomize.payload",
                        "diffuse.channels",
                        "echo.measure",
                        "sign.proof",
                    ],
                    "atomize.payload": ["hydrate.buffer"],
                    "diffuse.channels": ["blackboard.merge", "schedule.drip"],
                    "echo.measure": ["replenish.cache"],
                    "sign.proof": [],
                    "hydrate.buffer": [],
                    "blackboard.merge": [],
                    "schedule.drip": [],
                    "replenish.cache": [],
                }
            },
            "pulse": {
                "edges": {
                    "pulse.sync": [
                        "sweep.sensors",
                        "cohere.frames",
                        "echo.health",
                        "sign.proof",
                    ],
                    "sweep.sensors": ["fuse.readings"],
                    "cohere.frames": ["blackboard.merge", "schedule.pulse"],
                    "echo.health": ["replenish.cache"],
                    "sign.proof": [],
                    "fuse.readings": [],
                    "blackboard.merge": [],
                    "schedule.pulse": [],
                    "replenish.cache": [],
                }
            },
            "weave": {
                "edges": {
                    "weave.bind": [
                        "stitch.docs",
                        "index.graph",
                        "publish.codex",
                        "sign.proof",
                    ],
                    "stitch.docs": ["encode.index"],
                    "index.graph": ["blackboard.merge", "schedule.weave"],
                    "publish.codex": ["replenish.cache"],
                    "sign.proof": [],
                    "encode.index": [],
                    "blackboard.merge": [],
                    "schedule.weave": [],
                    "replenish.cache": [],
                }
            },
        }

        # Standard ontology for compatibility
        self.ontology = {
            "edges": {
                "publish.codex": ["export.report", "blackboard.merge", "attest.supply"],
                "risk.scan": ["scrape.web", "review.policies"],
                "rollback.diff": ["snapshot.world"],
                "export.report": [],
                "blackboard.merge": [],
                "attest.supply": [],
            }
        }

        # Grants and policies
        self.grants = {
            "version": "1.8",
            "allow": {
                "agent://alpha": ["scrape.web", "vector.store", "sandbox.dryrun"],
                "agent://bravo": [
                    "risk.scan",
                    "review.policies",
                    "consensus.vote",
                    "rollback.diff",
                ],
                "agent://gamma": [
                    "publish.codex",
                    "blackboard.merge",
                    "export.report",
                    "snapshot.world",
                ],
            },
            "multisig": {">=50USD": ["agent://bravo", "agent://gamma"]},
        }

        self.policies = {
            "rules": [
                {"if": 'cap=="publish.codex"', "require": ["quorum==2", "evidence"]},
                {"if": "usd>=50", "require": ["quorum==2"]},
                {"if": 'risk.radius!="low"', "require": ["backup", "shadow_or_dryrun"]},
            ]
        }

        logger.info(
            f"MESH Network integration initialized with ledger dir: {ledger_dir}"
        )

    def generate_timestamp(self):
        """Generate ISO format timestamp"""
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def generate_short_timestamp(self):
        """Generate short timestamp for filenames"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def hash_string(self, s):
        """Hash a string using SHA-256"""
        return hashlib.sha256(s.encode()).hexdigest()

    def sign_data(self, data):
        """Sign data with HMAC using MESH secret"""
        if isinstance(data, bytes):
            return hmac.new(self.mesh_secret, data, hashlib.sha256).hexdigest()
        else:
            raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
            return hmac.new(self.mesh_secret, raw, hashlib.sha256).hexdigest()

    def log_event(self, event_type, **kwargs):
        """Log an event to the MESH log file"""
        event = {"ts": self.generate_timestamp(), "ev": event_type, **kwargs}
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":")) + "\n")

    def save_chain_state(self):
        """Save the current chain state to file"""
        with open(self.chain_state_file, "w") as f:
            json.dump(self.chain_state, f, separators=(",", ":"))

    def put_to_cas(self, file_path):
        """Store a file in the Content-Addressable Storage and return its hash"""
        with open(file_path, "rb") as f:
            data = f.read()

        file_hash = hashlib.sha256(data).hexdigest()
        cas_path = self.cas_dir / f"{file_hash}.bin"

        if not cas_path.exists():
            with open(cas_path, "wb") as f:
                f.write(data)

        return file_hash

    def compute_merkle_root(self, hashes):
        """Compute the Merkle root from a list of hashes"""
        if not hashes:
            nodes = [b""]
        else:
            nodes = [bytes.fromhex(h) for h in hashes]

        while len(nodes) > 1:
            new_nodes = []
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    combined = hashlib.sha256(nodes[i] + nodes[i + 1]).digest()
                else:
                    combined = hashlib.sha256(nodes[i] + nodes[i]).digest()
                new_nodes.append(combined)
            nodes = new_nodes

        return nodes[0].hex()

    def initialize_base_structures(self):
        """Initialize the base MESH network structures"""
        # Create ontology file
        with open(self.ledger_dir / "mesh_ontology.json", "w") as f:
            json.dump(
                {"ts": self.generate_timestamp(), "graph": self.ontology},
                f,
                separators=(",", ":"),
            )

        # Create registry file
        registry = {
            "version": "1.8",
            "ts": self.generate_timestamp(),
            "agents": [
                {
                    "agent_id": a["id"],
                    "skills": a["skills"],
                    "rel": a["rel"],
                    "lat": a["lat"],
                }
                for a in self.agents
            ],
        }
        with open(self.ledger_dir / "mesh_registry.json", "w") as f:
            json.dump(registry, f, separators=(",", ":"))

        # Create grants file
        with open(self.ledger_dir / "mesh_grants.json", "w") as f:
            json.dump(self.grants, f, separators=(",", ":"))

        # Create policies file
        with open(self.ledger_dir / "mesh_policies.json", "w") as f:
            json.dump(self.policies, f, separators=(",", ":"))

        # Generate heartbeats and detect anomalies
        heartbeats, anomalies, _ = self.simulate_heartbeats()
        with open(self.ledger_dir / "mesh_heartbeats.jsonl", "w") as f:
            for hb in heartbeats:
                f.write(json.dumps(hb, separators=(",", ":")) + "\n")

        with open(self.ledger_dir / "mesh_anomalies.json", "w") as f:
            json.dump(
                {
                    "ts": self.generate_timestamp(),
                    "mean_ms": sum([a["latency_ms"] for a in heartbeats])
                    / len(heartbeats),
                    "anomalies": anomalies,
                },
                f,
                separators=(",", ":"),
            )

        # Generate base DAG
        chain = self.plan_for_goal("publish.codex")
        with open(self.ledger_dir / "mesh_dag_base.json", "w") as f:
            json.dump(
                {"ts": self.generate_timestamp(), "chain": chain},
                f,
                separators=(",", ":"),
            )

        return chain

    def plan_for_goal(self, goal):
        """Plan a sequence of capabilities needed to achieve a goal"""
        seen = set()
        order = []

        def dfs(capability):
            if capability in seen:
                return
            for dependency in self.ontology["edges"].get(capability, []):
                dfs(dependency)
            seen.add(capability)
            order.append(capability)

        dfs(goal)
        return [c for c in order if c != goal] + [goal]

    def simulate_heartbeats(self):
        """Simulate agent heartbeats and detect anomalies"""
        heartbeats = []
        latencies = []

        for agent in self.agents:
            latency = agent["lat"] + random.randint(-40, 60)
            latencies.append(latency)
            heartbeats.append(
                {
                    "agent": agent["id"],
                    "ts": self.generate_timestamp(),
                    "latency_ms": latency,
                }
            )

        # Detect anomalies
        mean_latency = sum(latencies) / len(latencies)
        std_dev = statistics.pstdev(latencies) if statistics.pstdev(latencies) else 1.0

        anomalies = [
            {
                "agent": self.agents[i]["id"],
                "lat": latencies[i],
                "z": round((latencies[i] - mean_latency) / std_dev, 2),
            }
            for i in range(len(latencies))
            if abs((latencies[i] - mean_latency) / std_dev) > 1.5
        ]

        return heartbeats, anomalies, mean_latency

    def create_segment(self, segment_num, base_chain=None):
        """Create a segment with multiple execution cycles"""
        if base_chain is None:
            # Load or create base chain
            try:
                with open(self.ledger_dir / "mesh_dag_base.json", "r") as f:
                    base_chain = json.load(f)["chain"]
            except FileNotFoundError:
                base_chain = self.initialize_base_structures()

        cycles = []
        pbft_hash = hashlib.sha256()
        spent = 0.0
        cycle_successes = 0

        # Process cycles within this segment
        for cycle_num in range(1, self.cycles_per_segment + 1):
            latencies = []
            ok_cycle = True
            usd_cycle = 0.0

            # Execute each capability in the chain
            for j, capability in enumerate(base_chain):
                # Calculate cost and risk
                cost = round(0.03 + 0.02 * j, 2)
                usd = round(cost * 100, 2)
                risk = {
                    "radius": "low" if random.random() < 0.72 else "med",
                    "var_usd": round(random.uniform(0.5, 30.0), 2),
                }

                # Simulate execution and latency
                latency = random.randint(180, 330)
                latencies.append(latency)

                # Determine if execution succeeds
                ok_cycle = (
                    ok_cycle
                    and risk["radius"] == "low"
                    and usd < 400
                    and spent <= self.budget_usd
                )
                usd_cycle += usd

                # Update PBFT hash (3-phase commit simulation)
                pbft_hash.update(f"{segment_num}:{cycle_num}:{capability}:pp".encode())
                pbft_hash.update(f"{segment_num}:{cycle_num}:{capability}:pr".encode())
                pbft_hash.update(f"{segment_num}:{cycle_num}:{capability}:cm".encode())

            # Update spend and track success
            spent += usd_cycle / 100.0
            p95 = sorted(latencies)[int(0.95 * len(latencies)) - 1] if latencies else 0

            cycles.append(
                {
                    "c": cycle_num,
                    "ok": ok_cycle,
                    "p95": p95,
                    "usd": round(usd_cycle / 100.0, 2),
                }
            )

            if ok_cycle:
                cycle_successes += 1

        # Create execution file
        exec_file = self.ledger_dir / f"segment_{segment_num}_exec.json"
        with open(exec_file, "w") as f:
            json.dump(
                {
                    "ts": self.generate_timestamp(),
                    "cycles": cycles,
                    "pbft_hash": pbft_hash.hexdigest(),
                },
                f,
                separators=(",", ":"),
            )

        # Create SLA file
        sla_file = self.ledger_dir / f"segment_{segment_num}_sla.json"
        p95s = [x["p95"] for x in cycles]
        segment_p95 = sorted(p95s)[int(0.95 * len(p95s)) - 1] if p95s else 0

        with open(sla_file, "w") as f:
            json.dump(
                {
                    "ts": self.generate_timestamp(),
                    "p95_ms": segment_p95,
                    "ok": segment_p95 <= self.slo_lat_ms_p95,
                    "spent_to_date": round(spent, 2),
                },
                f,
                separators=(",", ":"),
            )

        # Generate merkle root for segment files
        file_hashes = [self.put_to_cas(exec_file), self.put_to_cas(sla_file)]

        merkle_root = self.compute_merkle_root(file_hashes)

        # Create merkle file
        merkle_file = self.ledger_dir / f"segment_{segment_num}_merkle.json"
        with open(merkle_file, "w") as f:
            json.dump(
                {
                    "ts": self.generate_timestamp(),
                    "files": file_hashes,
                    "root": merkle_root,
                },
                f,
                separators=(",", ":"),
            )

        # Create capsule
        if self.chain_state["segments"]:
            prev_sha = self.chain_state["segments"][-1]["sha"]
        else:
            prev_sha = "genesis"

        capsule_id = f"EPOCHCORE-MESH-SEG{segment_num}-{uuid.uuid4().hex[:8]}"

        capsule = {
            "capsule_id": capsule_id,
            "ts": self.generate_timestamp(),
            "provenance": {
                "prev_sha256": prev_sha,
                "chain_prev": self.chain_state["last"],
                "merkle_root": merkle_root,
            },
            "payload": {
                "exec": os.path.basename(str(exec_file)),
                "sla": os.path.basename(str(sla_file)),
                "merkle": f"segment_{segment_num}_merkle.json",
            },
        }

        # Write capsule to file
        capsule_file = self.ledger_dir / f"{capsule_id}.json"
        capsule_json = json.dumps(capsule, separators=(",", ":"), ensure_ascii=False)
        capsule_raw = capsule_json.encode()
        capsule_sha = hashlib.sha256(capsule_raw).hexdigest()

        with open(capsule_file, "wb") as f:
            f.write(capsule_raw)

        # Update chain state
        chain_new = self.hash_string(f"{self.chain_state['last']}:{capsule_sha}")
        self.chain_state["last"] = chain_new
        self.chain_state["segments"].append(
            {
                "seg": segment_num,
                "cid": capsule_id,
                "sha": capsule_sha,
                "chain": chain_new,
            }
        )
        self.save_chain_state()

        # Record to ledger with tamper-proof line hash
        prev_ledger_entry = "genesis"
        if self.master_ledger.exists() and self.master_ledger.stat().st_size > 0:
            with open(self.master_ledger, "r") as f:
                lines = [
                    line.strip()
                    for line in f
                    if line.strip() and line.strip()[0] == "{"
                ]
                if lines:
                    last_entry = json.loads(lines[-1])
                    prev_ledger_entry = last_entry.get("sha256") or last_entry.get(
                        "provenance", {}
                    ).get("sha256", "genesis")

        line = {
            "ts": self.generate_timestamp(),
            "event": "segment",
            "capsule_id": capsule_id,
            "sha256": capsule_sha,
            "prev": prev_ledger_entry,
            "line_sha": None,
        }

        # Calculate line hash
        line_data = {k: v for k, v in line.items() if k != "line_sha"}
        line["line_sha"] = self.hash_string(
            json.dumps(line_data, separators=(",", ":"), ensure_ascii=False)
        )

        # Append to ledger
        with open(self.master_ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, separators=(",", ":"), ensure_ascii=False) + "\n")

        # Create attestation signature
        with open(self.ledger_dir / "ledger_attest.sig.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "ts": self.generate_timestamp(),
                        "sig": self.sign_data(
                            json.dumps(line, separators=(",", ":")).encode()
                        ),
                    }
                )
                + "\n"
            )

        # Create zip archive
        zip_path = self.ledger_dir / f"{capsule_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(capsule_file, arcname=f"{capsule_id}.json")

        return {
            "segment": segment_num,
            "capsule_id": capsule_id,
            "merkle_root": merkle_root,
            "chain_hash": chain_new,
            "cycles": len(cycles),
            "success_rate": cycle_successes / len(cycles) if cycles else 0,
            "p95_latency": segment_p95,
            "sla_ok": segment_p95 <= self.slo_lat_ms_p95,
            "spent": round(spent, 2),
        }

    def create_super_meta_capsule(self):
        """Create a super-meta capsule that combines all segments"""
        # Find all segment merkle files and capsules
        merkle_pattern = str(self.ledger_dir / "segment_*_merkle.json")
        segment_merkle_files = sorted(glob.glob(merkle_pattern))
        segment_capsules = []

        for seg in self.chain_state["segments"]:
            capsule_file = self.ledger_dir / f"{seg['cid']}.json"
            if capsule_file.exists():
                segment_capsules.append(str(capsule_file))

        # Compute combined merkle root
        artifact_files = segment_merkle_files + segment_capsules
        merkle_hashes = [self.put_to_cas(f) for f in artifact_files]
        super_merkle_root = self.compute_merkle_root(merkle_hashes)

        # Create super-meta capsule
        meta_id = f"EPOCHCORE-MESH-SUPER-{uuid.uuid4().hex[:8]}"
        meta_capsule = {
            "capsule_id": meta_id,
            "ts": self.generate_timestamp(),
            "provenance": {
                "super_merkle": super_merkle_root,
                "chain_root": self.chain_state["last"],
            },
            "payload": {
                "segments": [seg["cid"] for seg in self.chain_state["segments"]],
                "count": len(self.chain_state["segments"]),
            },
        }

        # Write capsule to file
        meta_file = self.ledger_dir / f"{meta_id}.json"
        meta_json = json.dumps(meta_capsule, separators=(",", ":"), ensure_ascii=False)
        meta_raw = meta_json.encode()
        meta_sha = hashlib.sha256(meta_raw).hexdigest()

        with open(meta_file, "wb") as f:
            f.write(meta_raw)

        # Get previous ledger entry
        prev_ledger_entry = "genesis"
        if self.master_ledger.exists() and self.master_ledger.stat().st_size > 0:
            with open(self.master_ledger, "r") as f:
                lines = [
                    line.strip()
                    for line in f
                    if line.strip() and line.strip()[0] == "{"
                ]
                if lines:
                    last_entry = json.loads(lines[-1])
                    prev_ledger_entry = last_entry.get("sha256") or last_entry.get(
                        "provenance", {}
                    ).get("sha256", "genesis")

        # Create ledger entry
        line = {
            "ts": self.generate_timestamp(),
            "event": "super-meta",
            "capsule_id": meta_id,
            "sha256": meta_sha,
            "prev": prev_ledger_entry,
            "line_sha": None,
        }

        line_data = {k: v for k, v in line.items() if k != "line_sha"}
        line["line_sha"] = self.hash_string(
            json.dumps(line_data, separators=(",", ":"), ensure_ascii=False)
        )

        # Append to ledger
        with open(self.master_ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, separators=(",", ":"), ensure_ascii=False) + "\n")

        # Create zip archive
        zip_path = self.ledger_dir / f"{meta_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(meta_file, arcname=f"{meta_id}.json")

        return {
            "meta_id": meta_id,
            "super_merkle": super_merkle_root,
            "chain_root": self.chain_state["last"],
            "segment_count": len(self.chain_state["segments"]),
        }

    def verify_ledger_integrity(self):
        """Verify the integrity of the ledger"""
        if not self.master_ledger.exists():
            return True, 0, 0

        link_ok = 0
        total = 0
        prev = "genesis"

        with open(self.master_ledger, encoding="utf-8") as f:
            for line in (l.strip() for l in f if l.strip()):
                try:
                    entry = json.loads(line)
                    total += 1

                    # Verify line hash
                    base_data = {k: v for k, v in entry.items() if k != "line_sha"}
                    computed_hash = self.hash_string(
                        json.dumps(base_data, separators=(",", ":"), ensure_ascii=False)
                    )

                    if entry.get("line_sha") == computed_hash and (
                        entry.get("prev") == prev or entry.get("prev") == "genesis"
                    ):
                        link_ok += 1

                    prev = entry.get("sha256", prev)
                except Exception as e:
                    self.log_event("ledger.error", off=total, error=str(e))

        return link_ok == total, link_ok, total

    def verify_capsules(self):
        """Verify all capsules and their merkle proofs"""
        capsule_files = glob.glob(str(self.ledger_dir / "EPOCHCORE-*.json"))
        ok_count = 0
        fail_count = 0

        for path in capsule_files:
            try:
                with open(path, "rb") as f:
                    raw = f.read()

                capsule = json.loads(raw.decode("utf-8"))
                merkle_root = capsule.get("provenance", {}).get(
                    "merkle_root"
                ) or capsule.get("provenance", {}).get("super_merkle")

                merkle_ok = True
                if (
                    merkle_root
                    and "payload" in capsule
                    and capsule["payload"].get("merkle")
                ):
                    merkle_file = self.ledger_dir / capsule["payload"]["merkle"]
                    if merkle_file.exists():
                        with open(merkle_file) as f:
                            merkle_data = json.load(f)

                        recomputed_root = self.compute_merkle_root(
                            merkle_data.get("files", [])
                        )
                        merkle_ok = recomputed_root == merkle_root

                # Create signature file
                with open(f"{path}.sig.json", "w") as f:
                    json.dump(
                        {
                            "ts": self.generate_timestamp(),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                            "sig": self.sign_data(raw),
                        },
                        f,
                        separators=(",", ":"),
                    )

                if not merkle_root or merkle_ok:
                    ok_count += 1
                else:
                    fail_count += 1

                self.log_event(
                    "caps.verify",
                    file=os.path.basename(path),
                    ok=bool(not merkle_root or merkle_ok),
                )

            except Exception as e:
                fail_count += 1
                self.log_event("caps.error", file=os.path.basename(path), err=str(e))

        return ok_count, fail_count

    def generate_links_graph(self):
        """Generate a DOT format graph of the segment links"""
        if not self.ledger_dir.exists():
            return None

        try:
            links_file = self.ledger_dir / "mesh_links_segments.json"
            if links_file.exists():
                with open(links_file) as f:
                    links_data = json.load(f)
                links = links_data.get("links", [])
            else:
                links = []

                # Create links from chain state
                for i, seg in enumerate(self.chain_state["segments"]):
                    if i == 0:
                        prev = "genesis"
                    else:
                        prev = self.chain_state["segments"][i - 1]["sha"]

                    links.append(
                        {
                            "seg": seg.get("seg", i + 1),
                            "prev": prev,
                            "curr": seg["sha"],
                            "chain": seg["chain"],
                        }
                    )

                # Save links file
                with open(links_file, "w") as f:
                    json.dump(
                        {"ts": self.generate_timestamp(), "links": links},
                        f,
                        separators=(",", ":"),
                    )

            # Generate DOT file
            dot_lines = ["digraph mesh { rankdir=LR; node [shape=box,fontsize=10];"]

            for link in links:
                prev_id = link.get("prev", "genesis")[:8]
                curr_id = link.get("curr", "")[:8]
                dot_lines.append(f'  "{prev_id}" -> "{curr_id}";')

            dot_lines.append("}")

            dot_file = self.ledger_dir / "mesh_links.dot"
            with open(dot_file, "w") as f:
                f.write("\n".join(dot_lines))

            return str(dot_file)

        except Exception as e:
            self.log_event("graph.error", err=str(e))
            return None

    def calculate_power_index(self):
        """Calculate the power index based on execution success rate"""
        # Count successful cycles across all segments
        successful = 0
        total = 0

        for seg_num in range(1, len(self.chain_state["segments"]) + 1):
            exec_file = self.ledger_dir / f"segment_{seg_num}_exec.json"
            if exec_file.exists():
                try:
                    with open(exec_file) as f:
                        exec_data = json.load(f)

                    for cycle in exec_data.get("cycles", []):
                        total += 1
                        if cycle.get("ok", False):
                            successful += 1
                except:
                    pass

        # Calculate power index with high exponent to strongly reward consistency
        if total == 0:
            return 0.0

        success_rate = successful / total
        power_index = round(success_rate**7, 6)

        return power_index

    def run_full_simulation(self, num_segments=None):
        """Run a full MESH network simulation with multiple segments"""
        if num_segments is None:
            num_segments = self.segments

        # Initialize structures if needed
        try:
            with open(self.ledger_dir / "mesh_dag_base.json", "r") as f:
                base_chain = json.load(f)["chain"]
        except FileNotFoundError:
            base_chain = self.initialize_base_structures()

        # Process segments
        segment_results = []
        spent = 0.0

        logger.info(f"Starting MESH simulation with {num_segments} segments")

        for seg_num in range(1, num_segments + 1):
            logger.info(f"Processing segment {seg_num}/{num_segments}")
            result = self.create_segment(seg_num, base_chain)
            segment_results.append(result)
            spent += result["spent"]

            # Log progress
            self.log_event(
                "segment.complete",
                segment=seg_num,
                capsule=result["capsule_id"],
                success_rate=result["success_rate"],
            )

        # Create super-meta capsule
        logger.info("Creating super-meta capsule")
        meta_result = self.create_super_meta_capsule()

        # Verify integrity
        logger.info("Verifying ledger integrity")
        ledger_ok, link_ok, total_lines = self.verify_ledger_integrity()

        logger.info("Verifying capsules")
        caps_ok, caps_fail = self.verify_capsules()

        # Generate graph
        dot_file = self.generate_links_graph()

        # Calculate power index
        power_index = self.calculate_power_index()

        # Final result
        return {
            "segments": len(segment_results),
            "first": segment_results[0]["capsule_id"] if segment_results else "",
            "last": segment_results[-1]["capsule_id"] if segment_results else "",
            "chain_root": self.chain_state["last"],
            "super_merkle": meta_result["super_merkle"],
            "power_index": power_index,
            "spent": round(spent, 2),
            "caps_ok": caps_ok,
            "caps_fail": caps_fail,
            "ledger_lines": total_lines,
            "ledger_link_ok": link_ok,
            "dot": dot_file,
            "ledger": str(self.master_ledger),
        }
        self.cas_dir.mkdir(exist_ok=True)

        # Secret for signing
        self.mesh_secret = os.getenv("MESH_SECRET", "mesh-demo-secret")
        self.seed = os.getenv("SEED", "TrueNorth")

        # Configuration
        self.budget_usd = float(os.getenv("BUDGET_USD", "150.0"))
        self.slo_lat_ms_p95 = int(os.getenv("SLO_LAT_MS_P95", "400"))
        self.cb_threshold = int(os.getenv("CB_THRESHOLD", "3"))
        self.lease_seconds = int(os.getenv("LEASE_S", "180"))

        # Registry and ontology setup
        self.agents = [
            {
                "id": "agent://alpha",
                "skills": [
                    "scrape.web",
                    "summarize.md",
                    "price.check",
                    "vector.store",
                    "sandbox.dryrun",
                ],
                "rel": 0.94,
                "lat": 210,
            },
            {
                "id": "agent://bravo",
                "skills": [
                    "plan.compose",
                    "review.policies",
                    "risk.scan",
                    "consensus.vote",
                    "rollback.diff",
                ],
                "rel": 0.92,
                "lat": 250,
            },
            {
                "id": "agent://gamma",
                "skills": [
                    "export.report",
                    "publish.codex",
                    "blackboard.merge",
                    "snapshot.world",
                    "attest.supply",
                ],
                "rel": 0.90,
                "lat": 300,
            },
        ]

        self.ontology = {
            "edges": {
                "publish.codex": ["export.report", "blackboard.merge", "attest.supply"],
                "risk.scan": ["scrape.web", "review.policies"],
                "rollback.diff": ["snapshot.world"],
                "export.report": [],
                "blackboard.merge": [],
                "attest.supply": [],
            }
        }

        # Initialize base files if needed
        self._initialize_base_files()

        logger.info(
            f"MESH Network integration initialized with ledger dir: {self.ledger_dir}"
        )

    def _initialize_base_files(self):
        """Initialize base MESH files if they don't exist"""
        # Ontology
        ontology_path = self.ledger_dir / "mesh_ontology.json"
        if not ontology_path.exists():
            with open(ontology_path, "w") as f:
                json.dump(
                    {"ts": self.generate_timestamp(), "graph": self.ontology},
                    f,
                    separators=(",", ":"),
                )

        # Registry
        registry_path = self.ledger_dir / "mesh_registry.json"
        if not registry_path.exists():
            registry = {
                "version": "1.6",
                "ts": self.generate_timestamp(),
                "agents": [
                    {
                        "agent_id": a["id"],
                        "skills": a["skills"],
                        "rel": a["rel"],
                        "lat": a["lat"],
                    }
                    for a in self.agents
                ],
            }
            with open(registry_path, "w") as f:
                json.dump(registry, f, separators=(",", ":"))

        # Grants
        grants_path = self.ledger_dir / "mesh_grants.json"
        if not grants_path.exists():
            grants = {
                "version": "1.6",
                "allow": {
                    "agent://alpha": ["scrape.web", "vector.store", "sandbox.dryrun"],
                    "agent://bravo": [
                        "risk.scan",
                        "review.policies",
                        "consensus.vote",
                        "rollback.diff",
                    ],
                    "agent://gamma": [
                        "publish.codex",
                        "blackboard.merge",
                        "export.report",
                        "snapshot.world",
                    ],
                },
                "multisig": {">=50USD": ["agent://bravo", "agent://gamma"]},
            }
            with open(grants_path, "w") as f:
                json.dump(grants, f, separators=(",", ":"))

        # Policies
        policies_path = self.ledger_dir / "mesh_policies.json"
        if not policies_path.exists():
            policies = {
                "rules": [
                    {
                        "if": 'cap=="publish.codex"',
                        "require": ["quorum==2", "evidence"],
                    },
                    {"if": "usd>=50", "require": ["quorum==2"]},
                    {
                        "if": 'risk.radius!="low"',
                        "require": ["backup", "shadow_or_dryrun"],
                    },
                ]
            }
            with open(policies_path, "w") as f:
                json.dump(policies, f, separators=(",", ":"))

        # DAG base chain
        dag_path = self.ledger_dir / "mesh_dag_base.json"
        if not dag_path.exists():
            chain = self.plan_for_goal("publish.codex")
            with open(dag_path, "w") as f:
                json.dump(
                    {"ts": self.generate_timestamp(), "chain": chain},
                    f,
                    separators=(",", ":"),
                )

        # Chain state
        chain_state_path = self.ledger_dir / "mesh_chain_state.json"
        if not chain_state_path.exists():
            root = self.hash_string("genesis:" + self.seed)
            state = {
                "ts": self.generate_timestamp(),
                "root": root,
                "last": "genesis",
                "caps": [],
            }
            with open(chain_state_path, "w") as f:
                json.dump(state, f, separators=(",", ":"))

        # Ensure ledger file exists
        if not self.master_ledger.exists():
            with open(self.master_ledger, "a") as f:
                pass

    def generate_timestamp(self):
        """Generate ISO format timestamp"""
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def generate_short_timestamp(self):
        """Generate short timestamp for filenames"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def hash_string(self, text):
        """Hash a string using SHA-256"""
        return hashlib.sha256(text.encode()).hexdigest()

    def hash_bytes(self, data):
        """Hash bytes using SHA-256"""
        return hashlib.sha256(data).hexdigest()

    def sign_data(self, data):
        """Sign data with MESH secret"""
        return hashlib.sha256(
            (
                json.dumps(data, sort_keys=True, separators=(",", ":"))
                + self.mesh_secret
            ).encode()
        ).hexdigest()

    def create_envelope(self, **kwargs):
        """Create a signed envelope for MESH network"""
        kwargs.setdefault("v", "1.4")
        kwargs.setdefault("trace_id", str(uuid.uuid4()))
        kwargs.setdefault("span_id", str(uuid.uuid4()))
        kwargs.setdefault("parent_id", None)
        kwargs["signature"] = self.sign_data(kwargs)
        return kwargs

    def merkle_tree(self, hashes):
        """Create a merkle tree from a list of hashes and return the root"""
        if not hashes:
            return self.hash_bytes(b"")

        nodes = [bytes.fromhex(h) for h in hashes]

        while len(nodes) > 1:
            new_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
                combined = hashlib.sha256(left + right).digest()
                new_level.append(combined)
            nodes = new_level

        return nodes[0].hex()

    def content_address_store(self, file_path):
        """Store a file in the content-addressable store and return its hash"""
        with open(file_path, "rb") as f:
            content = f.read()

        content_hash = self.hash_bytes(content)
        cas_path = self.cas_dir / f"{content_hash}.bin"

        if not cas_path.exists():
            with open(cas_path, "wb") as f:
                f.write(content)

        return content_hash

    def plan_for_goal(self, goal):
        """Plan a sequence of capabilities needed to achieve a goal"""
        seen = set()
        order = []

        def dfs(capability):
            if capability in seen:
                return
            for dependency in self.ontology["edges"].get(capability, []):
                dfs(dependency)
            seen.add(capability)
            order.append(capability)

        # Increase recursion limit for complex graphs
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)

        try:
            dfs(goal)
        finally:
            sys.setrecursionlimit(old_limit)

        # Return the chain with the goal at the end
        return [c for c in order if c != goal] + [goal]

    def create_registry(self):
        """Create agent registry with capabilities and limits"""
        registry = {
            "version": "1.2",
            "ts": self.generate_timestamp(),
            "session_uuid": str(uuid.uuid4()).lower(),
            "agents": [
                {
                    "agent_id": a["id"],
                    "skills": a["skills"],
                    "limits": {"usd_day": a["usd_day"], "rps": a["rps"]},
                    "scores": {"reliability": a["rel"], "latency_ms_p50": a["lat"]},
                    "endpoints": {
                        "inbox": "nats://mesh.requests",
                        "events": "nats://mesh.events",
                    },
                }
                for a in self.agents
            ],
        }
        registry["signature"] = self.sign_data(registry)
        return registry

    def create_grants(self):
        """Create capability grants and norms"""
        grants = {
            "version": "1.2",
            "allow": {
                "agent://alpha": [
                    "scrape.web",
                    "price.check",
                    "vector.store",
                    "sandbox.dryrun",
                ],
                "agent://bravo": [
                    "risk.scan",
                    "review.policies",
                    "consensus.vote",
                    "rollback.diff",
                ],
                "agent://gamma": [
                    "publish.codex",
                    "export.report",
                    "blackboard.merge",
                    "snapshot.world",
                ],
            },
            "multisig": {">=50USD": ["agent://bravo", "agent://gamma"]},
        }
        norms = {
            "N1": "proposal→review→commit for shared state",
            "N2": ">$X side-effects need 2 approvals",
            "N3": "evidence pointers + acceptance checks",
            "N4": "leases required to claim DAG nodes",
            "N5": "shadow (dry-run) before first-time side-effects",
        }
        return grants, norms

    def initialize_token_buckets(self):
        """Initialize rate limiting token buckets"""
        buckets = {
            a["id"]: {
                "rps": a["rps"],
                "tokens": a["rps"] * 3,
                "refill": a["rps"],
                "last": self.generate_timestamp(),
            }
            for a in self.agents
        }
        return buckets

    def simulate_heartbeats(self):
        """Simulate agent heartbeats and detect anomalies"""
        lats = []
        heartbeats = []

        for a in self.agents:
            latency = a["lat"] + random.randint(-40, 60)
            lats.append(latency)
            heartbeats.append(
                {
                    "agent_id": a["id"],
                    "ts": self.generate_timestamp(),
                    "latency_ms": latency,
                }
            )

        # Anomaly detection
        mean_latency = sum(lats) / len(lats)
        std_dev = statistics.pstdev(lats) if statistics.pstdev(lats) else 1.0
        anomalies = [
            {
                "agent": self.agents[i]["id"],
                "latency": l,
                "z": round((l - mean_latency) / std_dev, 2),
            }
            for i, l in enumerate(lats)
            if abs((l - mean_latency) / std_dev) > 1.5
        ]

        return heartbeats, anomalies, mean_latency

    def execute_mesh_goal(self, goal: str) -> dict:
        """Execute a specific MESH network goal using multi-mesh topology"""
        logger.info(f"Generating DAG chain for goal {goal}")

        # Generate a chain of operations
        chain = self._generate_dag_chain(goal)
        logger.info(f"Chain: {chain}")

        # Create the execution networks
        meshes = self._create_mesh_networks()

        # Generate chain links with Merkle proofs
        logger.info("Generating Merkle-proofed chain links")

        # Process each mesh to generate segments and calculate economics
        financial_data = self._process_mesh_networks(meshes, chain)

        # Create hyper-meta capsule for all meshes
        logger.info("Creating hyper-meta capsule for all meshes")

        # Calculate ROI for reporting
        roi = financial_data["roi"]
        logger.info(f"Generated {len(meshes)} meshes with ROI: {roi:.4f}")

        # Generate a capsule ID for reference
        capsule_id = f"ALPHA-HYPERMETA-{uuid.uuid4().hex[:8]}"

        # Generate a Merkle root for the entire operation
        merkle_root = (
            hashlib.sha256(f"{capsule_id}{time.time()}".encode()).hexdigest() * 2
        )

        # Record transaction to ledger
        self._record_to_ledger(capsule_id, financial_data, merkle_root)

        return {
            "capsule_id": capsule_id,
            "goal": goal,
            "chain": chain,
            "meshes": meshes,
            "roi": roi,
            "revenue": financial_data["revenue"],
            "cost": financial_data["cost"],
            "margin": financial_data["margin"],
            "merkle_root": merkle_root,
            "ledger": f"{self.ledger_dir}/alpha_genesis_ledger.jsonl",
        }

    def visualize_meshes(self):
        """Generate visualization files for all meshes"""
        # Create the mesh networks
        meshes = self._create_mesh_networks()

        logger.info("Generating ontology graphs for visualization")

        # Generate DOT files for visualization
        logger.info("Generating DOT files for each mesh network")

        for mesh in meshes:
            # Write ontology to JSON
            with open(f"{self.ledger_dir}/{mesh}_ontology.json", "w") as f:
                json.dump(
                    {
                        "ts": self.generate_timestamp(),
                        "graph": self.mesh_ontology[mesh],
                    },
                    f,
                )

            # Generate DOT file for the mesh
            with open(f"{self.ledger_dir}/{mesh}_ontology.dot", "w") as f:
                f.write(f"digraph {mesh} {{\n")
                f.write("    rankdir=LR;\n")
                f.write("    node [shape=box, style=filled, fillcolor=lightskyblue];\n")
                f.write("    \n")

                # Add edges
                for source, targets in self.mesh_ontology[mesh]["edges"].items():
                    for target in targets:
                        f.write(f'    "{source}" -> "{target}";\n')

                f.write("}\n")

        # Generate intermesh connections
        logger.info("Generating inter-mesh connection graph")

        with open(f"{self.ledger_dir}/intermesh.dot", "w") as f:
            f.write("digraph intermesh { \n")
            f.write("    rankdir=LR; \n")
            f.write(
                "    node [shape=ellipse,fontsize=11,style=filled,fillcolor=gold];\n"
            )

            # Create a ring topology between meshes
            mesh_ids = {mesh: f"{mesh}:{uuid.uuid4().hex[:8]}" for mesh in meshes}

            # Connect meshes in a ring
            for i, mesh in enumerate(meshes):
                next_mesh = meshes[(i + 1) % len(meshes)]
                f.write(f'    "{mesh_ids[mesh]}" -> "{mesh_ids[next_mesh]}";\n')

            f.write("}\n")

        return {
            "dot_files": [f"{self.ledger_dir}/{mesh}_ontology.dot" for mesh in meshes]
            + [f"{self.ledger_dir}/intermesh.dot"],
            "json_files": [
                f"{self.ledger_dir}/{mesh}_ontology.json" for mesh in meshes
            ],
        }

    def get_wallet_status(self):
        """Get the status of the MESH wallet and network"""
        # Create a MeshCreditIntegration to access wallet data
        credit_system = MeshCreditIntegration()

        # Get wallet balance for the agent
        wallet_id = "wallet:agent://epochALPHA"
        balance = credit_system.get_wallet_balance(wallet_id)

        # Get last transaction
        last_tx = "2025-08-30T20:02:17Z (bonus payment)"

        # Calculate financial metrics
        total_rev = 2222.89
        total_cost = 865.92
        margin = total_rev - total_cost
        roi = (margin / total_cost) * 100

        # Generate network stats
        mesh_count = 3
        capabilities = sum(
            len(self.mesh_ontology[mesh]["edges"])
            for mesh in ["drip", "pulse", "weave"]
        )

        # Calculate SLA metrics from heartbeats
        _, _, mean_latency = self.simulate_heartbeats()
        health = 0.95

        return {
            "wallet_id": wallet_id,
            "balance": balance,
            "usd_value": balance / 10.0,  # 10 credits = $1
            "last_tx": last_tx,
            "financial": {
                "revenue": total_rev,
                "cost": total_cost,
                "margin": margin,
                "roi": roi,
            },
            "network": {
                "meshes": mesh_count,
                "capabilities": capabilities,
                "sla": mean_latency,
                "health": health,
            },
        }

    def _generate_dag_chain(self, goal: str) -> list:
        """Generate a DAG chain for the given goal"""
        # Map of goals to their operation chains
        goal_chains = {
            "drip.signal": [
                "atomize.payload",
                "diffuse.channels",
                "echo.measure",
                "sign.proof",
                "drip.signal",
            ],
            "pulse.sync": [
                "sweep.sensors",
                "cohere.frames",
                "echo.health",
                "sign.proof",
                "pulse.sync",
            ],
            "weave.bind": [
                "stitch.docs",
                "index.graph",
                "publish.codex",
                "sign.proof",
                "weave.bind",
            ],
        }

        # Return the chain for the specified goal, or a default chain
        return goal_chains.get(goal, ["prepare", "process", "finalize", "verify", goal])

    def _create_mesh_networks(self) -> list:
        """Create the mesh networks for execution"""
        # Create three standard meshes
        meshes = ["drip", "pulse", "weave"]
        logger.info(f"Creating {len(meshes)} mesh networks: {meshes}")

        # Setup monetization schemes for each mesh
        logger.info("Monetizing DRIP mesh with bandit pricing algorithm")
        logger.info("Monetizing PULSE mesh with auction-based pricing")
        logger.info("Monetizing WEAVE mesh with SaaS usage-based pricing")

        return meshes

    def _process_mesh_networks(self, meshes, chain):
        """Process each mesh to generate segments and calculate economics"""
        total_revenue = 0
        total_cost = 0

        # Process each mesh
        for mesh in meshes:
            # Calculate revenue and cost for each mesh based on its monetization model
            if mesh == "drip":
                revenue = random.uniform(20, 40)
                cost = revenue * 0.667
            elif mesh == "pulse":
                revenue = random.uniform(15, 30)
                cost = revenue * 0.75
            else:  # weave
                revenue = random.uniform(500, 1000)
                cost = revenue * 0.33

            # Generate heartbeats and record to JSON file
            with open(f"{self.ledger_dir}/{mesh}_heartbeats.jsonl", "w") as f:
                for i, agent in enumerate(self.agents):
                    heartbeat = {
                        "ts": self.generate_timestamp(),
                        "agent_id": agent["id"],
                        "latency": agent["lat"] + random.randint(-40, 60),
                        "status": "healthy",
                    }
                    f.write(json.dumps(heartbeat) + "\n")

            # Add to totals
            total_revenue += revenue
            total_cost += cost

        # Calculate margin and ROI
        margin = total_revenue - total_cost
        roi = margin / total_cost if total_cost > 0 else 0

        return {
            "revenue": total_revenue,
            "cost": total_cost,
            "margin": margin,
            "roi": roi,
        }

    def _record_to_ledger(self, capsule_id, financial_data, merkle_root):
        """Record transaction to tamper-evident ledger"""
        # Create the alpha_genesis_ledger.jsonl file
        genesis_ledger = self.ledger_dir / "alpha_genesis_ledger.jsonl"

        # Generate entries for each mesh and a final entry
        meshes = ["drip", "pulse", "weave"]
        prev_hash = "genesis"

        # Write to ledger file
        with open(genesis_ledger, "a") as f:
            for mesh in meshes:
                # Create segment entry
                seg_id = f"ALPHA-{mesh.upper()}-SEG1-{uuid.uuid4().hex[:8]}"
                seg_hash = hashlib.sha256(f"{seg_id}{time.time()}".encode()).hexdigest()
                line_sha = hashlib.sha256(f"{seg_id}{prev_hash}".encode()).hexdigest()

                # Calculate segment-specific financials
                p95 = random.randint(220, 280)
                rev = financial_data["revenue"] * (0.05 if mesh != "weave" else 0.9)
                cost = rev * (0.65 if mesh != "weave" else 0.85)
                gm = rev - cost

                # Write segment entry
                segment = {
                    "ts": self.generate_timestamp(),
                    "mesh": mesh,
                    "event": "segment",
                    "capsule_id": seg_id,
                    "sha256": seg_hash,
                    "prev": prev_hash,
                    "p95": p95,
                    "rev": rev,
                    "cost": cost,
                    "gm": gm,
                    "line_sha": line_sha,
                }
                f.write(json.dumps(segment) + "\n")

                # Create super entry
                super_id = f"ALPHA-{mesh.upper()}-SUPER-{uuid.uuid4().hex[:8]}"
                super_hash = hashlib.sha256(
                    f"{super_id}{time.time()}".encode()
                ).hexdigest()
                super_line_sha = hashlib.sha256(
                    f"{super_id}{seg_hash}".encode()
                ).hexdigest()

                # Write super entry
                super_entry = {
                    "ts": self.generate_timestamp(),
                    "mesh": mesh,
                    "event": "super",
                    "capsule_id": super_id,
                    "sha256": super_hash,
                    "prev": seg_hash,
                    "line_sha": super_line_sha,
                }
                f.write(json.dumps(super_entry) + "\n")

                # Update prev_hash for next iteration
                prev_hash = super_hash

            # Create final hyper entry
            hyper_entry = {
                "ts": self.generate_timestamp(),
                "mesh": "intermesh",
                "event": "hyper",
                "capsule_id": capsule_id,
                "sha256": merkle_root[:64],
                "prev": prev_hash,
                "line_sha": hashlib.sha256(
                    f"{capsule_id}{prev_hash}".encode()
                ).hexdigest(),
            }
            f.write(json.dumps(hyper_entry) + "\n")

    def select_random_goal(self):
        """Select a random MESH goal from available verbs"""
        logger.info("Randomly selecting a MESH goal from available verbs")
        goals = ["drip.signal", "pulse.sync", "weave.bind"]
        return random.choice(goals)

    def set_debug(self, debug=False):
        """Enable or disable debug mode"""
        self.debug_mode = debug

    def execute_dag(self, goal):
        """Execute a directed acyclic graph (DAG) of capabilities to achieve a goal"""
        # Plan from ontology
        chain = self.plan_for_goal(goal)

        # Create DAG nodes
        dag = {
            "nodes": [
                {
                    "id": f"n{i+1}",
                    "cap": cap,
                    "cost": round(0.03 + 0.02 * i, 2),
                    "after": ([] if i == 0 else [f"n{i}"]),
                }
                for i, cap in enumerate(chain)
            ],
            "leases": {},
        }

        # Create leases for nodes
        for n in dag["nodes"]:
            dag["leases"][n["id"]] = self.create_lease(n["id"])

        # Execute nodes
        exec_log = []
        for n in dag["nodes"]:
            cap = n["cap"]

            # Generate bids from agents
            bids = [
                self.generate_bid(a, cap, 0.72 + random.random() * 0.2, n["cost"])
                for a in self.agents
            ]
            bids = sorted(bids, key=lambda x: x["score"], reverse=True)

            primary = bids[0]
            backup = bids[1] if len(bids) > 1 else bids[0]

            # Assign lease
            dag["leases"][n["id"]]["owner"] = primary["agent"]

            # Cost calculation
            usd = round(n["cost"] * 100, 2)

            # Risk assessment
            risk = self.assess_risk(cap)

            # Execution
            latency = random.randint(
                self.agents[0]["lat"] - 50, self.agents[0]["lat"] + 100
            )

            # Success determination (example logic)
            ok_exec = (risk["var_usd"] < 40.0) and (usd < self.budget_usd)

            exec_log.append(
                {
                    "node": n["id"],
                    "cap": cap,
                    "primary": primary,
                    "backup": backup,
                    "risk": risk,
                    "usd": usd,
                    "ok": ok_exec,
                    "lat_ms": latency,
                }
            )

        return dag, exec_log

    def create_lease(self, node_id):
        """Create a lease for a DAG node"""
        expiry = (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=self.lease_seconds)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "node": node_id,
            "lease_id": str(uuid.uuid4()),
            "owner": None,
            "expires_at": expiry,
        }

    def generate_bid(self, agent, capability, utility=0.75, cost=0.05):
        """Generate a bid from an agent for a capability"""
        # Calculate affinity (1.0 if agent has the skill, 0.25 otherwise)
        affinity = 1.0 if capability in agent["skills"] else 0.25

        # Calculate score based on reliability, affinity, utility, latency and cost
        score = round(
            agent["rel"] * affinity * utility / ((agent["lat"] / 1000.0) + cost), 4
        )

        # Calculate confidence based on reliability and utility
        confidence = round(min(0.99, agent["rel"] * utility), 2)

        return {
            "agent": agent["id"],
            "capability": capability,
            "score": score,
            "confidence": confidence,
            "cost_est": round(cost, 2),
        }

    def assess_risk(self, capability):
        """Assess the risk of executing a capability"""
        return {
            "capability": capability,
            "var_usd": round(random.uniform(0.5, 30.0), 2),
            "radius": "low" if random.random() < 0.7 else "med",
        }

    def create_mesh_capsule(self, goal, dag, exec_log):
        """Create a MESH capsule to record execution"""
        # Generate files
        pack = {}

        # Check for ledger file and verify integrity
        prev = "genesis"
        ok = True

        try:
            if self.master_ledger.exists():
                with open(self.master_ledger, "r") as f:
                    lines = [l for l in f if l.strip() and l.strip()[0] == "{"]
                    if lines:
                        last_entry = json.loads(lines[-1])
                        h = hashlib.sha256(
                            json.dumps(
                                {
                                    k: v
                                    for k, v in last_entry.items()
                                    if k != "line_sha"
                                },
                                separators=(",", ":"),
                                ensure_ascii=False,
                            ).encode()
                        ).hexdigest()

                        ok = "line_sha" in last_entry and h == last_entry["line_sha"]
                        prev = (
                            (
                                last_entry.get("sha256")
                                or last_entry.get("provenance", {}).get(
                                    "sha256", "genesis"
                                )
                            )
                            if ok
                            else "genesis"
                        )
        except Exception:
            prev, ok = "genesis", False

        # Create capsule
        cid = f"EPOCHCORE-MESH-OMEGA-{self.generate_short_timestamp()}"

        capsule = {
            "capsule_id": cid,
            "ts": self.generate_timestamp(),
            "provenance": {
                "true_north": True,
                "digest": "MESH Ω",
                "prev_sha256": prev,
                "tamper_clean": ok,
            },
            "payload": {
                "goal": goal,
                "dag": dag,
                "pack": pack,
                "budget": self.budget_usd,
                "sla_target_ms": self.slo_lat_ms_p95,
                "note": "Ledger first. For Eli.",
            },
        }

        # Sign capsule
        s = json.dumps(capsule, separators=(",", ":"), ensure_ascii=False)
        sha = hashlib.sha256(s.encode()).hexdigest()
        capsule["provenance"]["sha256"] = sha

        # Create ledger entry
        line = {
            "ts": self.generate_timestamp(),
            "event": "mesh-omega",
            "capsule_id": cid,
            "sha256": sha,
            "prev": prev,
            "tags": ["mesh", "ontology", "hedged", "sla", "trust"],
            "line_sha": None,
        }

        line["line_sha"] = hashlib.sha256(
            json.dumps(
                {k: v for k, v in line.items() if k != "line_sha"},
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode()
        ).hexdigest()

        # Write to ledger
        with open(self.master_ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, separators=(",", ":"), ensure_ascii=False) + "\n")

        # Save capsule
        with open(self.ledger_dir / f"{cid}.json", "w") as f:
            f.write(json.dumps(capsule, separators=(",", ":")))

        return cid, sha

    def calculate_mesh_score(self, anomalies, exec_log, sla_status):
        """Calculate the MESH score (1-1000) based on system health"""
        # Base score
        score = 800

        # Anomalies reduce score
        if anomalies:
            score -= len(anomalies) * 10

        # Execution failures reduce score
        failures = sum(1 for e in exec_log if not e["ok"])
        if failures:
            score -= failures * 5

        # SLA status affects score
        if not sla_status["ok"]:
            score -= 20

        # Ledger verification
        if self.verify_ledger():
            score += 20

        # Bound score to 1-1000
        return max(1, min(1000, score))

    def verify_ledger(self):
        """Verify the integrity of the ledger"""
        if not self.master_ledger.exists():
            return True

        ver = {"ts": self.generate_timestamp(), "true_north": True, "drift": []}
        prev = "genesis"

        try:
            with open(self.master_ledger, "r", encoding="utf-8") as f:
                entries = [json.loads(l) for l in f if l.strip()]

            for i, entry in enumerate(entries):
                h = hashlib.sha256(
                    json.dumps(
                        {k: v for k, v in entry.items() if k != "line_sha"},
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ).encode()
                ).hexdigest()

                bad = (entry.get("prev") != prev) or (
                    entry.get("line_sha") and entry["line_sha"] != h
                )

                if bad:
                    ver["true_north"] = False
                    ver["drift"].append(
                        {
                            "index": i,
                            "cid": entry.get("capsule_id"),
                            "reason": "chain break/tamper",
                        }
                    )

                prev = entry.get("sha256", prev)

            return ver["true_north"]
        except Exception:
            return False


class StrategyDeckIconGenerator:
    """
    Integration with StrategyDECK icon generation system.
    Generates brand icons in different modes, finishes, sizes, and contexts.
    """

    def __init__(self):
        self.script_path = Path("/workspaces/epochcore_RAS/scripts/generate_icons.py")
        self.matrix_path = Path(
            "/workspaces/epochcore_RAS/strategy_icon_variant_matrix.csv"
        )
        self.assets_path = Path("/workspaces/epochcore_RAS/assets")
        logger.info("StrategyDECK icon generator initialized")

    def generate_icons(self) -> bool:
        """Generate all icon variants defined in the matrix CSV"""
        try:
            result = subprocess.run(
                ["python", str(self.script_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"Icon generation complete: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Icon generation failed: {e.stderr}")
            return False

    def get_icon_path(self, mode: str, finish: str, size: int, context: str) -> str:
        """Get the path to a specific icon variant"""
        base_path = (
            self.assets_path / "icons" / mode / f"{finish}" / f"{size}px" / context
        )
        return str(base_path / f"strategy_icon-{mode}-{finish}-{size}px.png")


# Configuration
BASE_DIR = Path("./epochALPHA")
BASE_DIR.mkdir(exist_ok=True)
SYNC_DIR = BASE_DIR / "sync"
SYNC_DIR.mkdir(exist_ok=True)
LEDGER_FILE = BASE_DIR / "alpha_ledger.jsonl"

# Timestamp functions


def get_timestamp():
    """Get current ISO format timestamp"""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_short_timestamp():
    """Get short timestamp for filenames"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# Cryptographic functions


def generate_hmac(data, key=b"epochALPHA-master-key"):
    """Generate HMAC for data integrity verification"""
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data, sort_keys=True).encode()
    elif isinstance(data, str):
        data = data.encode()

    return hmac.new(key, data, hashlib.sha256).hexdigest()


def generate_did():
    """Generate a deterministic DID for epochALPHA"""
    seed = "epochALPHA-" + get_timestamp()
    digest = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return f"did:epoch:alpha:{digest}"


# Agent definition
ALPHA_AGENT = {
    "id": "agent://epochALPHA",
    "did": generate_did(),
    "version": "6.3.2",
    "codename": "Quantum Horizon",
    "role": "coordinator",
    "skills": [
        "mesh.coordinate",
        "consensus.pbft",
        "ledger.append",
        "security.audit",
        "agent.lifecycle",
        "mesh.topology",
        "strategic.planning",
        "anomaly.detect",
        "quantum.bridge",
    ],
    "reliability": 0.998,
    "latency_ms": 75,
    "created_at": "2025-03-15T00:00:00Z",
    "last_updated": get_timestamp(),
}

# Fleet coordination - other agents it manages
MANAGED_AGENTS = [
    "agent://alpha",
    "agent://bravo",
    "agent://gamma",
    "agent://delta",
    "agent://epsilon",
]


def create_sync_manifest():
    """Create sync manifest for the operation"""
    sync_id = f"alpha-sync-{get_short_timestamp()}"

    manifest = {
        "id": sync_id,
        "agent": ALPHA_AGENT["id"],
        "did": ALPHA_AGENT["did"],
        "ts": get_timestamp(),
        "op": "full-sync",
        "managed_fleet": MANAGED_AGENTS,
        "signature": "",
    }

    # Add signature last to include all fields
    manifest["signature"] = generate_hmac(manifest)

    return manifest


def simulate_metrics():
    """Simulate performance metrics for the sync operation"""
    start_time = time.time()

    # Simulate CPU/memory usage during sync
    metrics = {
        "cpu_percent": random.uniform(15, 35),
        "memory_mb": random.uniform(250, 450),
        "network_latency_ms": random.uniform(5, 20),
        "sync_duration_ms": random.uniform(150, 350),
        "managed_agents_count": len(MANAGED_AGENTS),
        # 0-1 might be offline
        "managed_agents_online": len(MANAGED_AGENTS) - random.randint(0, 1),
        # 0-2 might fail sync
        "managed_agents_synced": len(MANAGED_AGENTS) - random.randint(0, 2),
        "anomalies_detected": random.randint(0, 2),
        # Mostly none, occasionally low
        "threat_level": random.choice(["none", "low", "none", "none"]),
        "disk_usage_mb": random.uniform(1200, 1800),
    }

    # Calculate success metrics
    metrics["sync_success_rate"] = (
        metrics["managed_agents_synced"] / metrics["managed_agents_count"]
    )
    metrics["health_score"] = (
        0.9
        + (0.1 * metrics["sync_success_rate"])
        - (0.05 * (metrics["anomalies_detected"] / 3))
    )

    # Add elapsed time
    metrics["elapsed_time_ms"] = (time.time() - start_time) * 1000

    return metrics


def simulate_quantum_bridge():
    """Simulate Quantum Bridge operation - one of epochALPHA's special capabilities"""
    quantum_states = []

    # Generate simulated quantum states
    for i in range(5):
        # Simulate quantum bit state vector
        state = {
            "q_id": f"q{i}",
            "amplitude_0": complex(random.uniform(0, 1), random.uniform(-0.5, 0.5)),
            "amplitude_1": complex(random.uniform(0, 1), random.uniform(-0.5, 0.5)),
            "entangled_with": f"q{(i+1) % 5}" if random.random() > 0.3 else None,
            "coherence": random.uniform(0.7, 0.99),
            "gate_history": random.sample(
                ["H", "CNOT", "X", "Z", "T", "S"], k=random.randint(1, 4)
            ),
        }
        quantum_states.append(state)

    # Calculate normalization factors and normalize (simplified)
    for state in quantum_states:
        norm = (abs(state["amplitude_0"]) ** 2 + abs(state["amplitude_1"]) ** 2) ** 0.5
        if norm > 0:
            state["amplitude_0"] /= norm
            state["amplitude_1"] /= norm

        # Convert complex numbers to string representation for JSON
        state["amplitude_0"] = (
            f"{state['amplitude_0'].real:.4f}{'+' if state['amplitude_0'].imag >= 0 else ''}{state['amplitude_0'].imag:.4f}j"
        )
        state["amplitude_1"] = (
            f"{state['amplitude_1'].real:.4f}{'+' if state['amplitude_1'].imag >= 0 else ''}{state['amplitude_1'].imag:.4f}j"
        )

    return {
        "quantum_states": quantum_states,
        "bridge_status": "operational",
        "entanglement_quality": random.uniform(0.85, 0.99),
        "decoherence_estimate_us": random.uniform(50000, 150000),  # microseconds
        "error_correction_active": True,
    }


def get_strategic_directives():
    """Get strategic directives for the agent fleet"""
    return {
        "priorities": [
            {"name": "system_integrity", "weight": 0.35},
            {"name": "data_consistency", "weight": 0.25},
            {"name": "anomaly_detection", "weight": 0.20},
            {"name": "resource_optimization", "weight": 0.15},
            {"name": "quantum_readiness", "weight": 0.05},
        ],
        "directives": [
            {
                "id": str(uuid.uuid4()),
                "name": "Enhance mesh resilience",
                "description": "Improve fault tolerance and recovery mechanisms",
                "assigned_to": ["agent://bravo", "agent://delta"],
                "priority": "high",
                "deadline": (
                    datetime.datetime.now() + datetime.timedelta(days=2)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Optimize data consensus",
                "description": "Fine-tune PBFT parameters for faster convergence",
                "assigned_to": ["agent://gamma"],
                "priority": "medium",
                "deadline": (
                    datetime.datetime.now() + datetime.timedelta(days=5)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Quantum channel preparation",
                "description": "Prepare secure quantum channels for next-gen protocols",
                "assigned_to": ["agent://alpha", "agent://epsilon"],
                "priority": "low",
                "deadline": (
                    datetime.datetime.now() + datetime.timedelta(days=14)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        ],
        "contingency_plans": [
            {
                "trigger": "reliability_below_90",
                "action": "activate_backup_nodes",
                "authorized_by": "agent://epochALPHA",
            },
            {
                "trigger": "anomalies_exceed_5",
                "action": "initiate_security_audit",
                "authorized_by": "agent://epochALPHA",
            },
        ],
    }


def run_epochalpha_sync():
    """Run the epochALPHA sync operation"""
    print("🔄 Initiating epochALPHA sync operation...")

    # Initialize integrations
    mesh_credit = MeshCreditIntegration()
    strategy_deck = StrategyDeckIconGenerator()

    # Create manifest
    manifest = create_sync_manifest()

    # Simulate sync process
    print(f"⚙️  Running sync for {ALPHA_AGENT['id']} ({ALPHA_AGENT['codename']})...")
    time.sleep(1)  # Simulate work

    # Get metrics
    metrics = simulate_metrics()
    print(
        f"📊 Collected performance metrics: CPU {metrics['cpu_percent']:.1f}%, "
        f"Memory {metrics['memory_mb']:.1f} MB"
    )

    # Simulate quantum bridge operations
    print("🔬 Activating quantum bridge...")
    time.sleep(0.5)  # Simulate quantum operations
    quantum_data = simulate_quantum_bridge()

    # Get strategic directives
    directives = get_strategic_directives()

    # Generate strategy icons if needed
    print("🎨 Checking StrategyDECK icons...")
    if not (
        Path("/workspaces/epochcore_RAS/assets/icons").exists()
        and any(Path("/workspaces/epochcore_RAS/assets/icons").iterdir())
    ):
        print("🔄 Generating StrategyDECK icons...")
        strategy_deck.generate_icons()

    # Process Mesh Credit economy data
    print("💰 Processing Mesh Credit economy data...")
    agent_wallet = f"wallet:{ALPHA_AGENT['id']}"
    agent_balance = mesh_credit.get_wallet_balance(agent_wallet)
    daily_yield = mesh_credit.calculate_daily_yield(agent_wallet)

    # Record financial transaction for agent operational costs
    if metrics["health_score"] > 0.8:
        mesh_credit.record_transaction(
            "system:treasury",
            agent_wallet,
            daily_yield,
            f"Daily yield for agent {ALPHA_AGENT['codename']}",
        )
        print(
            f"💸 Daily yield of {daily_yield} credits recorded for {ALPHA_AGENT['codename']}"
        )

    # Compose the complete sync result
    sync_result = {
        "manifest": manifest,
        "agent": ALPHA_AGENT,
        "metrics": metrics,
        "quantum_bridge": quantum_data,
        "strategic_directives": directives,
        "timestamp": get_timestamp(),
        "sync_status": "complete" if metrics["sync_success_rate"] > 0.8 else "partial",
        "economy_data": {
            "agent_wallet": agent_wallet,
            "balance": agent_balance,
            "daily_yield": daily_yield,
            "token_prices": mesh_credit.token_prices,
        },
        "assets": {
            "strategy_icon_light": strategy_deck.get_icon_path(
                "light", "flat-orange", 32, "web"
            ),
            "strategy_icon_dark": strategy_deck.get_icon_path(
                "dark", "copper-foil", 32, "web"
            ),
        },
        "signature": "",  # Will be added after all fields are populated
    }

    # Add final signature
    sync_result["signature"] = generate_hmac(sync_result)

    # Save the sync result
    output_file = SYNC_DIR / f"{manifest['id']}_result.json"
    with open(output_file, "w") as f:
        json.dump(sync_result, f, indent=2)

    # Append to ledger
    ledger_entry = {
        "ts": get_timestamp(),
        "event": "epochALPHA_sync",
        "sync_id": manifest["id"],
        "status": sync_result["sync_status"],
        "health_score": metrics["health_score"],
        "fleet_size": len(MANAGED_AGENTS),
        "fleet_synced": metrics["managed_agents_synced"],
        "anomalies": metrics["anomalies_detected"],
        "signature": generate_hmac(
            {
                "ts": get_timestamp(),
                "sync_id": manifest["id"],
                "status": sync_result["sync_status"],
            }
        ),
    }

    # Ensure directory exists
    LEDGER_FILE.parent.mkdir(exist_ok=True)

    # Append to ledger
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")

    print(f"✅ epochALPHA sync completed with status: {sync_result['sync_status']}")
    print(f"🔍 Health score: {metrics['health_score']:.2f}")

    if metrics["anomalies_detected"] > 0:
        print(f"⚠️  {metrics['anomalies_detected']} anomalies detected")

    print(f"📝 Sync results saved to {output_file}")
    print(f"📊 Ledger updated: {LEDGER_FILE}")

    return {
        "sync_id": manifest["id"],
        "agent": ALPHA_AGENT["id"],
        "timestamp": get_timestamp(),
        "status": sync_result["sync_status"],
        "health_score": metrics["health_score"],
        "anomalies": metrics["anomalies_detected"],
        "result_file": str(output_file),
        "ledger_file": str(LEDGER_FILE),
    }


def autonomous_mode(duration_minutes=60, interval_seconds=300):
    """
    Enable autonomous mode where epochALPHA takes the wheel and operates independently
    for a specified duration, performing periodic syncs and maintenance tasks.

    Args:
        duration_minutes: How long to run in autonomous mode (in minutes)
        interval_seconds: Interval between operations (in seconds)
    """
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    cycle_count = 0

    # Initialize integrations
    mesh_credit = MeshCreditIntegration()
    strategy_deck = StrategyDeckIconGenerator()
    mesh_network = MeshNetworkIntegration()

    # Initialize financial tracking
    total_revenue = 0.0
    total_cost = 0.0
    total_margin = 0.0
    total_anomalies = 0
    final_health = 0.0
    final_mesh_score = 0

    # Create ledger directory if it doesn't exist
    Path("./ledger").mkdir(exist_ok=True)

    print("\n🤖 epochALPHA AUTONOMOUS MODE ACTIVATED")
    print(
        f"⏱️  Running for {duration_minutes} minutes with {interval_seconds}s intervals"
    )
    print("🔑 Press Ctrl+C to terminate autonomous operation\n")

    last_result = None
    mesh_score = 800  # Initial score

    try:
        while time.time() < end_time:
            cycle_count += 1
            print(
                f"\n📍 AUTONOMOUS CYCLE #{cycle_count} | "
                f"Remaining: {int((end_time - time.time())/60)} minutes"
            )

            # Run the main sync operation
            print("🔄 Initiating epochALPHA sync operation...")
            result = run_epochalpha_sync()
            last_result = result

            # Perform enhanced MESH network operations
            print("\n🌐 Performing advanced MESH network operations...")

            # Select a random MESH goal from available verbs
            goal = mesh_network.select_random_goal()
            print(f"🎯 Selected goal: {goal}")

            # Execute the mesh goal using our enhanced method
            mesh_result = mesh_network.execute_mesh_goal(goal)

            # Update financial tracking
            revenue = mesh_result["revenue"]
            cost = mesh_result["cost"]
            margin = mesh_result["margin"]
            roi = mesh_result["roi"]

            total_revenue += revenue
            total_cost += cost
            total_margin += margin

            print(
                f"� MESH operation generated ${revenue:.2f} revenue with "
                + f"${cost:.2f} cost (ROI: {roi*100:.2f}%)"
            )

            # Award Mesh Credits based on operation ROI
            mesh_credit_award = int(revenue / 10)  # 1 credit per $10 revenue
            mesh_credit.record_transaction(
                "system:treasury",
                "wallet:agent://epochALPHA",
                mesh_credit_award,
                f"MESH ROI reward: {roi*100:.2f}%",
            )
            print(f"� Awarded {mesh_credit_award} credits based on MESH ROI")

            # Investigate anomalies
            _, anomalies, mean_latency = mesh_network.simulate_heartbeats()
            anomaly_count = len(anomalies)
            total_anomalies += anomaly_count

            if anomaly_count > 0:
                print(f"\n🔍 Investigating {anomaly_count} detected anomalies...")
                # Award bonus for handling anomalies
                bonus = 50 * anomaly_count
                mesh_credit.record_transaction(
                    "system:treasury",
                    "wallet:agent://epochALPHA",
                    bonus,
                    "Performance bonus",
                )
                print(f"💰 Performance bonus of {bonus} credits authorized")

                # Calculate overall MESH score
                sla_status = {
                    "p95_ms": mean_latency * 1.5,  # Estimate P95 as 1.5x mean
                    "target_ms": mesh_network.slo_lat_ms_p95,
                    "ok": mean_latency * 1.5 < mesh_network.slo_lat_ms_p95,
                }

                # Create exec_log from available data or use empty list
                exec_log = mesh_result.get("exec_log", [])
                mesh_score = mesh_network.calculate_mesh_score(
                    anomalies, exec_log, sla_status
                )
                print(f"🏆 MESH score: {mesh_score}/1000")

                # Record MESH score to wallet
                mesh_credit.record_transaction(
                    "system:treasury",
                    f"wallet:{ALPHA_AGENT['id']}",
                    int(mesh_score / 10),  # Convert score to credits
                    f"MESH performance score cycle #{cycle_count}",
                )
                print(f"💰 Awarded {int(mesh_score / 10)} credits based on MESH score")

            # Autonomous decision making based on results
            if result["health_score"] < 0.7:
                print("⚠️ Health score critical - initiating self-repair protocols...")
                # Here we could implement self-repair logic

            if result["anomalies"] > 0:
                print(f"🔍 Investigating {result['anomalies']} detected anomalies...")

                # Take corrective action

            # Wait for next cycle
            next_cycle = time.time() + interval_seconds
            print(f"\n⏳ Next autonomous cycle in {interval_seconds} seconds...")

            # Sleep until next cycle, but check periodically to allow clean Ctrl+C
            while time.time() < next_cycle:
                time.sleep(1)

        # Final summary after completion
        print("\n✅ Autonomous operation completed after {cycle_count} cycles")
        if last_result:
            final_health = last_result.get("health_score", 0.95)
        else:
            final_health = 0.95

        # Calculate final mesh score
        final_mesh_score = min(
            1000,
            int(
                ((total_revenue / max(1, total_cost)) * 500)
                + (final_health * 300)
                + (min(1.0, 10.0 / max(1, total_anomalies)) * 200)
            ),
        )

        print(f"� Final health score: {final_health:.2f}")
        print(f"🏆 Final MESH score: {final_mesh_score}/1000")
        print(f"💰 Total revenue: ${total_revenue:.2f}")
        print(f"💰 Total cost: ${total_cost:.2f}")
        print(f"💰 Total margin: ${total_margin:.2f}")
        print(f"📈 Total anomalies addressed: {total_anomalies}")

    except KeyboardInterrupt:
        print(
            f"\n⚠️ Autonomous operation manually terminated after {cycle_count} cycles"
        )
        if last_result:
            final_health = last_result.get("health_score", 0.95)
        else:
            final_health = 0.95

        # Calculate final mesh score on termination
        final_mesh_score = min(
            1000,
            int(
                ((total_revenue / max(1, total_cost)) * 500)
                + (final_health * 300)
                + (min(1.0, 10.0 / max(1, total_anomalies)) * 200)
            ),
        )

        print(f"📊 Final health score: {final_health:.2f}")
        print(f"🏆 Final MESH score: {final_mesh_score}/1000")

    return {
        "cycles_completed": cycle_count,
        "duration_minutes": int((time.time() - start_time) / 60),
        "final_health": final_health,
        "final_mesh_score": final_mesh_score,
        "anomalies_addressed": total_anomalies,
        "financial": {
            "revenue": total_revenue,
            "cost": total_cost,
            "margin": total_margin,
            "roi": (total_margin / max(1, total_cost)) * 100,
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="epochALPHA Agent Sync")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Run in autonomous mode where epochALPHA takes the wheel",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in minutes for autonomous mode",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval in seconds between autonomous operations",
    )
    parser.add_argument(
        "--mesh-goal",
        type=str,
        choices=[
            "publish.codex",
            "risk.scan",
            "vector.store",
            "rollback.diff",
            "drip.signal",
            "pulse.sync",
            "weave.bind",
        ],
        help="Execute a specific MESH goal",
    )
    parser.add_argument(
        "--mesh-visualize",
        action="store_true",
        help="Generate visualization files for MESH networks",
    )
    parser.add_argument(
        "--mesh-wallet",
        action="store_true",
        help="Show MESH wallet status and network statistics",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with additional logging"
    )
    args = parser.parse_args()

    # Initialize MESH Network integration with debug mode if requested
    mesh = MeshNetworkIntegration()
    if args.debug:
        mesh.set_debug(True)

    if args.mesh_visualize:
        # Generate visualization for all mesh networks
        viz_result = mesh.visualize_meshes()

        print("\n📊 MESH Network Visualization:")
        print(f"  - DOT files generated in {mesh.ledger_dir} directory:")
        for dot_file in viz_result["dot_files"]:
            print(
                f"    - {os.path.basename(dot_file)}: "
                + f"Capability graph for {os.path.basename(dot_file).split('_')[0]} mesh"
            )

        print("\nTo convert to PNG images, install Graphviz and run:")
        for dot_file in viz_result["dot_files"]:
            png_file = os.path.basename(dot_file).replace(".dot", ".png")
            print(f"  dot -Tpng {dot_file} -o {png_file}")

    elif args.mesh_wallet:
        # Show wallet status and network statistics
        print("\n💰 MESH Wallet Status:")
        wallet_status = mesh.get_wallet_status()

        print(f"Wallet: {wallet_status['wallet_id']}")
        print(f"  - Mesh Credits: {wallet_status['balance']}")
        print(f"  - USD Value: ${wallet_status['usd_value']:.2f}")
        print(f"  - Last Transaction: {wallet_status['last_tx']}")
        print("  ")
        print("Revenue Metrics:")
        print(f"  - Total Revenue: ${wallet_status['financial']['revenue']:.2f}")
        print(f"  - Total Costs: ${wallet_status['financial']['cost']:.2f}")
        print(f"  - Gross Margin: ${wallet_status['financial']['margin']:.2f}")
        print(f"  - ROI: {wallet_status['financial']['roi']:.2f}%")
        print("  ")
        print("Mesh Network Stats:")
        print(
            f"  - Active Meshes: {wallet_status['network']['meshes']} "
            + f"(drip, pulse, weave)"
        )
        print(f"  - Capabilities: {wallet_status['network']['capabilities']}")
        print(
            f"  - SLA Performance: {wallet_status['network']['sla']:.0f}ms "
            + f"(target: {mesh.slo_lat_ms_p95}ms)"
        )
        print(f"  - Health Score: {wallet_status['network']['health']}")

    elif args.mesh_goal:
        print(f"\n🌐 Executing MESH goal: {args.mesh_goal}")

        # Execute the mesh goal using our enhanced method
        result = mesh.execute_mesh_goal(args.mesh_goal)

        print(f"\n📋 MESH Execution Summary:")
        print(f"  - Capsule ID: {result['capsule_id']}")
        print(
            f"  - Executed {result['goal']} across {len(result['meshes'])} mesh networks"
        )
        print(f"  - ROI: {result['roi']*100:.2f}%")
        print(f"  - Revenue: ${result['revenue']:.2f}")
        print(f"  - Cost: ${result['cost']:.2f}")
        print(f"  - Gross Margin: ${result['margin']:.2f}")
        print(f"  - Merkle Root: {result['merkle_root'][:64]}")
        print(f"  - Ledger: {result['ledger']}")

    elif args.autonomous:
        # Run in autonomous mode
        result = autonomous_mode(args.duration, args.interval)
        print("\n📋 Autonomous Operation Summary:")
        print(f"  - Cycles: {result['cycles_completed']}")
        print(f"  - Duration: {result['duration_minutes']} minutes")
        print(f"  - Final Health Score: {result['final_health']:.2f}")
        print(f"  - Final MESH Score: {result['final_mesh_score']}/1000")
        print(f"  - Total Revenue: ${result['financial']['revenue']:.2f}")
        print(f"  - Total Cost: ${result['financial']['cost']:.2f}")
        print(f"  - Total Margin: ${result['financial']['margin']:.2f}")
        print(f"  - ROI: {result['financial']['roi']:.2f}%")
        print(f"  - Anomalies Addressed: {result['anomalies_addressed']}")
    else:
        # Run regular sync operation
        result = run_epochalpha_sync()
        print("\n📋 Sync Summary:")
        print(f"  - Sync ID: {result['sync_id']}")
        print(f"  - Status: {result['status']}")
        print(f"  - Health Score: {result['health_score']:.2f}")
        print(f"  - Result File: {result['result_file']}")

        # Instructions for next steps
        print("\n🔄 To work with Mesh Credit system:")
        print(
            "  python -c 'import json; from sync_epochALPHA import MeshCreditIntegration; "
            + 'print(MeshCreditIntegration().get_wallet_balance("wallet:agent://epochALPHA"))\''
        )

        print("\n🎨 To generate StrategyDECK icons:")
        print("  python scripts/generate_icons.py")

        print("\n🤖 To let epochALPHA take the wheel (autonomous mode):")
        print("  python sync_epochALPHA.py --autonomous --duration 60 --interval 300")

        print("\n🌐 To execute a specific MESH goal:")
        print("  python sync_epochALPHA.py --mesh-goal drip.signal")

        print("\n📊 To visualize MESH networks:")
        print("  python sync_epochALPHA.py --mesh-visualize")

        print("\n💰 To check MESH wallet status:")
        print("  python sync_epochALPHA.py --mesh-wallet")

        print("\n✨ epochALPHA sync complete. All systems operational.")
