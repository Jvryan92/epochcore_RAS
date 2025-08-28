#!/usr/bin/env python3
"""
Agent Management System - Decentralized identifiers, registry, and monitoring
Integrates with EPOCH5 logging, hashing, and provenance tracking
"""

import json
import uuid
import time
import hashlib
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


class AgentManagementError(Exception):
    """Base exception for agent management errors"""
    pass

class AgentNotFoundError(AgentManagementError):
    """Raised when an agent cannot be found"""
    pass

class AgentValidationError(AgentManagementError):
    """Raised when agent validation fails"""
    pass

class AgentManager:
    def __init__(self, base_dir: str = "./archive/EPOCH5"):
        self.base_dir = Path(base_dir)
        self.agents_dir = self.base_dir / "agents"
        
        # Ensure directory structure exists
        try:
            self.agents_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise AgentManagementError(f"Failed to create agent directory: {e}")
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.agents_dir / "registry.json"
        self.anomalies_file = self.agents_dir / "anomalies.log"
        self.heartbeat_file = self.agents_dir / "agent_heartbeats.log"

    def timestamp(self) -> str:
        """Generate ISO timestamp consistent with EPOCH5"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash consistent with EPOCH5"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def generate_did(self, agent_type: str = "agent") -> str:
        """Generate decentralized identifier for agent"""
        unique_id = str(uuid.uuid4())
        timestamp = self.timestamp()
        did_data = f"{agent_type}|{unique_id}|{timestamp}"
        did_hash = self.sha256(did_data)[:16]
        return f"did:epoch5:{agent_type}:{did_hash}"

    def create_agent(
        self, skills: List[str], agent_type: str = "agent"
    ) -> Dict[str, Any]:
        """Create new agent with DID and initial properties"""
        did = self.generate_did(agent_type)
        agent = {
            "did": did,
            "type": agent_type,
            "created_at": self.timestamp(),
            "skills": skills,
            "reliability_score": 1.0,
            "average_latency": 0.0,
            "total_tasks": 0,
            "successful_tasks": 0,
            "last_heartbeat": self.timestamp(),
            "status": "active",
            "ethical_metrics": {
                "ethical_score": 1.0,
                "constraint_satisfaction_rate": 1.0,
                "reflection_confidence": 0.5,
                "total_ethical_assessments": 0,
                "successful_ethical_assessments": 0,
                "principle_performance": {},
                "stakeholder_impact": {},
                "last_reflection": None
            },
            "metadata": {
                "creation_hash": self.sha256(f"{did}|{skills}|{self.timestamp()}")
            },
        }

        self.log_heartbeat(did, "AGENT_CREATED")
        return agent

    def load_registry(self) -> Dict[str, Any]:
        """Load agent registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file, "r") as f:
                return json.load(f)
        return {"agents": {}, "last_updated": self.timestamp()}

    def save_registry(self, registry: Dict[str, Any]):
        """Save agent registry to file"""
        registry["last_updated"] = self.timestamp()
        with open(self.registry_file, "w") as f:
            json.dump(registry, f, indent=2)

    def register_agent(self, agent: Dict[str, Any]) -> bool:
        """Register agent in the registry"""
        registry = self.load_registry()
        registry["agents"][agent["did"]] = agent
        self.save_registry(registry)
        return True

    def get_agent(self, did: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent by DID"""
        registry = self.load_registry()
        return registry["agents"].get(did)

    def update_agent_stats(self, did: str, success: bool, latency: float, ethical_metrics: Optional[Dict[str, Any]] = None):
        """Update agent performance statistics including ethical metrics"""
        registry = self.load_registry()
        if did in registry["agents"]:
            agent = registry["agents"][did]
            agent["total_tasks"] += 1
            if success:
                agent["successful_tasks"] += 1

            # Update reliability score (weighted average)
            agent["reliability_score"] = (
                agent["successful_tasks"] / agent["total_tasks"]
            )

            # Update average latency (exponential moving average)
            alpha = 0.1
            agent["average_latency"] = (alpha * latency) + (
                (1 - alpha) * agent["average_latency"]
            )

            # Update ethical metrics if provided
            if ethical_metrics:
                self.update_ethical_metrics(did, ethical_metrics)

            self.save_registry(registry)
            return True
        return False

    def update_ethical_metrics(self, did: str, metrics: Dict[str, Any]):
        """Update agent's ethical metrics"""
        registry = self.load_registry()
        if did in registry["agents"]:
            agent = registry["agents"][did]
            ethical = agent["ethical_metrics"]
            
            # Update assessment counts
            ethical["total_ethical_assessments"] += 1
            if metrics.get("assessment_success", False):
                ethical["successful_ethical_assessments"] += 1

            # Update scores with exponential moving averages
            alpha = 0.1  # Learning rate
            ethical["ethical_score"] = (alpha * metrics.get("ethical_score", 1.0) + 
                                      (1 - alpha) * ethical["ethical_score"])
            ethical["constraint_satisfaction_rate"] = (alpha * metrics.get("constraint_satisfaction", 1.0) +
                                                     (1 - alpha) * ethical["constraint_satisfaction_rate"])
            ethical["reflection_confidence"] = (alpha * metrics.get("reflection_confidence", 0.5) +
                                             (1 - alpha) * ethical["reflection_confidence"])

            # Update principle performance
            for principle, score in metrics.get("principle_performance", {}).items():
                if principle not in ethical["principle_performance"]:
                    ethical["principle_performance"][principle] = score
                else:
                    ethical["principle_performance"][principle] = (
                        alpha * score +
                        (1 - alpha) * ethical["principle_performance"][principle]
                    )

            # Update stakeholder impact tracking
            for stakeholder, impact in metrics.get("stakeholder_impact", {}).items():
                if stakeholder not in ethical["stakeholder_impact"]:
                    ethical["stakeholder_impact"][stakeholder] = {
                        "total_impact": impact,
                        "impact_count": 1,
                        "average_impact": impact
                    }
                else:
                    stake_data = ethical["stakeholder_impact"][stakeholder]
                    stake_data["total_impact"] += impact
                    stake_data["impact_count"] += 1
                    stake_data["average_impact"] = (
                        stake_data["total_impact"] / stake_data["impact_count"]
                    )

            # Update reflection timestamp
            ethical["last_reflection"] = self.timestamp()

            self.save_registry(registry)
            return True
        return False

    def log_heartbeat(self, did: str, status: str = "HEARTBEAT"):
        """Log agent heartbeat with EPOCH5 compatible format"""
        timestamp = self.timestamp()
        with open(self.heartbeat_file, "a") as f:
            f.write(f"{timestamp} | DID={did} | {status}\n")

        # Update last heartbeat in registry
        registry = self.load_registry()
        if did in registry["agents"]:
            registry["agents"][did]["last_heartbeat"] = timestamp
            self.save_registry(registry)

    def detect_anomaly(self, did: str, anomaly_type: str, details: str):
        """Log agent anomaly for monitoring"""
        timestamp = self.timestamp()
        anomaly = {
            "timestamp": timestamp,
            "did": did,
            "type": anomaly_type,
            "details": details,
            "hash": self.sha256(f"{timestamp}|{did}|{anomaly_type}|{details}"),
        }

        with open(self.anomalies_file, "a") as f:
            f.write(f"{json.dumps(anomaly)}\n")

        return anomaly

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get list of active agents"""
        registry = self.load_registry()
        return [
            agent
            for agent in registry["agents"].values()
            if agent["status"] == "active"
        ]

    def get_agents_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Get agents that have a specific skill"""
        registry = self.load_registry()
        return [
            agent
            for agent in registry["agents"].values()
            if skill in agent["skills"] and agent["status"] == "active"
        ]


# CLI interface for agent management
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 Agent Management")
    parser.add_argument("--create", nargs="+", help="Create agent with skills")
    parser.add_argument("--list", action="store_true", help="List all agents")
    parser.add_argument("--heartbeat", help="Log heartbeat for DID")
    parser.add_argument(
        "--anomaly", nargs=3, metavar=("DID", "TYPE", "DETAILS"), help="Log anomaly"
    )

    args = parser.parse_args()
    manager = AgentManager()

    if args.create:
        agent = manager.create_agent(args.create)
        manager.register_agent(agent)
        print(f"Created agent: {agent['did']}")
        print(f"Skills: {', '.join(agent['skills'])}")

    elif args.list:
        registry = manager.load_registry()
        print(f"Agent Registry ({len(registry['agents'])} agents):")
        for did, agent in registry["agents"].items():
            print(
                f"  {did}: {agent['skills']} (reliability: {agent['reliability_score']:.2f})"
            )

    elif args.heartbeat:
        manager.log_heartbeat(args.heartbeat)
        print(f"Heartbeat logged for {args.heartbeat}")

    elif args.anomaly:
        did, anomaly_type, details = args.anomaly
        anomaly = manager.detect_anomaly(did, anomaly_type, details)
        print(f"Anomaly logged: {anomaly['hash']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
