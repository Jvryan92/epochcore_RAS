#!/usr/bin/env python3
"""
Policy and Grant System - Security enforcement through policies, rules, and grants
Integrates with EPOCH5 logging and agent management for secure operations
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class PolicyType(Enum):
    QUORUM = "quorum"
    MULTI_SIG = "multi_sig"
    RATE_LIMIT = "rate_limit"
    SKILL_REQUIRED = "skill_required"
    TRUST_THRESHOLD = "trust_threshold"


class PolicyManager:
    def __init__(self, base_dir: str = "./archive/EPOCH5"):
        self.base_dir = Path(base_dir)
        self.policy_dir = self.base_dir / "policies"
        self.policy_dir.mkdir(parents=True, exist_ok=True)
        self.policies_file = self.policy_dir / "policies.json"
        self.grants_file = self.policy_dir / "grants.json"
        self.violations_file = self.policy_dir / "violations.log"

    def timestamp(self) -> str:
        """Generate ISO timestamp consistent with EPOCH5"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash consistent with EPOCH5"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def create_policy(
        self,
        policy_id: str,
        policy_type: PolicyType,
        parameters: Dict[str, Any],
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new security policy"""
        policy = {
            "policy_id": policy_id,
            "type": policy_type.value,
            "parameters": parameters,
            "description": description,
            "created_at": self.timestamp(),
            "active": True,
            "enforced_count": 0,
            "violation_count": 0,
            "hash": self.sha256(
                f"{policy_id}|{policy_type.value}|{json.dumps(parameters, sort_keys=True)}"
            ),
        }
        return policy

    def save_policies(self, policies: Dict[str, Any]):
        """Save policies to file"""
        policies["last_updated"] = self.timestamp()
        with open(self.policies_file, "w") as f:
            json.dump(policies, f, indent=2)

    def load_policies(self) -> Dict[str, Any]:
        """Load policies from file"""
        if self.policies_file.exists():
            with open(self.policies_file, "r") as f:
                return json.load(f)
        return {"policies": {}, "last_updated": self.timestamp()}

    def add_policy(self, policy: Dict[str, Any]) -> bool:
        """Add policy to the system"""
        policies = self.load_policies()
        policies["policies"][policy["policy_id"]] = policy
        self.save_policies(policies)
        return True

    def create_grant(
        self,
        grant_id: str,
        grantee_did: str,
        resource: str,
        actions: List[str],
        conditions: Dict[str, Any] = None,
        expires_at: str = None,
    ) -> Dict[str, Any]:
        """Create a new grant for resource access"""
        if expires_at is None:
            # Default 24 hour expiration
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        grant = {
            "grant_id": grant_id,
            "grantee_did": grantee_did,
            "resource": resource,
            "actions": actions,
            "conditions": conditions or {},
            "created_at": self.timestamp(),
            "expires_at": expires_at,
            "used_count": 0,
            "active": True,
            "hash": self.sha256(
                f"{grant_id}|{grantee_did}|{resource}|{','.join(actions)}"
            ),
        }
        return grant

    def save_grants(self, grants: Dict[str, Any]):
        """Save grants to file"""
        grants["last_updated"] = self.timestamp()
        with open(self.grants_file, "w") as f:
            json.dump(grants, f, indent=2)

    def load_grants(self) -> Dict[str, Any]:
        """Load grants from file"""
        if self.grants_file.exists():
            with open(self.grants_file, "r") as f:
                return json.load(f)
        return {"grants": {}, "last_updated": self.timestamp()}

    def add_grant(self, grant: Dict[str, Any]) -> bool:
        """Add grant to the system"""
        grants = self.load_grants()
        grants["grants"][grant["grant_id"]] = grant
        self.save_grants(grants)
        return True

    def check_quorum_policy(self, policy: Dict[str, Any], approvers: List[str]) -> bool:
        """Check if quorum requirement is met"""
        required_count = policy["parameters"]["required_count"]
        return len(set(approvers)) >= required_count

    def check_multi_sig_policy(
        self, policy: Dict[str, Any], signatures: List[str]
    ) -> bool:
        """Check if multi-signature requirement is met"""
        required_sigs = policy["parameters"]["required_signatures"]
        authorized_signers = set(policy["parameters"]["authorized_signers"])
        valid_sigs = [sig for sig in signatures if sig in authorized_signers]
        return len(set(valid_sigs)) >= required_sigs

    def check_rate_limit_policy(
        self, policy: Dict[str, Any], did: str, current_requests: int
    ) -> bool:
        """Check if rate limit policy is satisfied"""
        max_requests = policy["parameters"]["max_requests_per_hour"]
        return current_requests <= max_requests

    def check_skill_required_policy(
        self, policy: Dict[str, Any], agent_skills: List[str]
    ) -> bool:
        """Check if required skills policy is satisfied"""
        required_skills = set(policy["parameters"]["required_skills"])
        agent_skill_set = set(agent_skills)
        return required_skills.issubset(agent_skill_set)

    def check_trust_threshold_policy(
        self, policy: Dict[str, Any], agent_reliability: float
    ) -> bool:
        """Check if trust threshold policy is satisfied"""
        min_reliability = policy["parameters"]["min_reliability"]
        return agent_reliability >= min_reliability

    def evaluate_policy(self, policy_id: str, context: Dict[str, Any]) -> bool:
        """Evaluate a specific policy against provided context"""
        policies = self.load_policies()
        if policy_id not in policies["policies"]:
            return False

        policy = policies["policies"][policy_id]
        if not policy["active"]:
            return False

        policy_type = PolicyType(policy["type"])

        try:
            if policy_type == PolicyType.QUORUM:
                result = self.check_quorum_policy(policy, context.get("approvers", []))
            elif policy_type == PolicyType.MULTI_SIG:
                result = self.check_multi_sig_policy(
                    policy, context.get("signatures", [])
                )
            elif policy_type == PolicyType.RATE_LIMIT:
                result = self.check_rate_limit_policy(
                    policy, context.get("did", ""), context.get("current_requests", 0)
                )
            elif policy_type == PolicyType.SKILL_REQUIRED:
                result = self.check_skill_required_policy(
                    policy, context.get("agent_skills", [])
                )
            elif policy_type == PolicyType.TRUST_THRESHOLD:
                result = self.check_trust_threshold_policy(
                    policy, context.get("agent_reliability", 0.0)
                )
            else:
                result = False

            # Update policy statistics
            if result:
                policy["enforced_count"] += 1
            else:
                policy["violation_count"] += 1
                self.log_violation(policy_id, context)

            policies["policies"][policy_id] = policy
            self.save_policies(policies)

            return result

        except Exception as e:
            self.log_violation(policy_id, {"error": str(e), "context": context})
            return False

    def check_grant(
        self, grant_id: str, requester_did: str, resource: str, action: str
    ) -> bool:
        """Check if a grant allows the requested action"""
        grants = self.load_grants()
        if grant_id not in grants["grants"]:
            return False

        grant = grants["grants"][grant_id]

        # Check if grant is active
        if not grant["active"]:
            return False

        # Check if grant has expired
        if datetime.now(timezone.utc) > datetime.fromisoformat(
            grant["expires_at"].replace("Z", "+00:00")
        ):
            grant["active"] = False
            self.save_grants(grants)
            return False

        # Check if requester matches grantee
        if grant["grantee_did"] != requester_did:
            return False

        # Check if resource matches
        if grant["resource"] != resource:
            return False

        # Check if action is allowed
        if action not in grant["actions"]:
            return False

        # Update usage count
        grant["used_count"] += 1
        grants["grants"][grant_id] = grant
        self.save_grants(grants)

        return True

    def log_violation(self, policy_id: str, context: Dict[str, Any]):
        """Log policy violation"""
        violation = {
            "timestamp": self.timestamp(),
            "policy_id": policy_id,
            "context": context,
            "hash": self.sha256(
                f"{self.timestamp()}|{policy_id}|{json.dumps(context, sort_keys=True)}"
            ),
        }

        with open(self.violations_file, "a") as f:
            f.write(f"{json.dumps(violation)}\n")

    def get_active_policies(self) -> List[Dict[str, Any]]:
        """Get all active policies"""
        policies = self.load_policies()
        return [p for p in policies["policies"].values() if p["active"]]

    def get_valid_grants(self, did: str) -> List[Dict[str, Any]]:
        """Get all valid grants for a specific DID"""
        grants = self.load_grants()
        now = datetime.now(timezone.utc)

        valid_grants = []
        for grant in grants["grants"].values():
            if (
                grant["active"]
                and grant["grantee_did"] == did
                and now
                <= datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
            ):
                valid_grants.append(grant)

        return valid_grants


# CLI interface for policy management
def main():
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 Policy and Grant System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Policy creation
    policy_parser = subparsers.add_parser("create-policy", help="Create a new policy")
    policy_parser.add_argument("policy_id", help="Policy identifier")
    policy_parser.add_argument(
        "policy_type",
        choices=[
            "quorum",
            "multi_sig",
            "rate_limit",
            "skill_required",
            "trust_threshold",
        ],
    )
    policy_parser.add_argument("parameters", help="JSON parameters for policy")

    # Grant creation
    grant_parser = subparsers.add_parser("create-grant", help="Create a new grant")
    grant_parser.add_argument("grant_id", help="Grant identifier")
    grant_parser.add_argument("grantee_did", help="Grantee DID")
    grant_parser.add_argument("resource", help="Resource name")
    grant_parser.add_argument("actions", nargs="+", help="Allowed actions")

    # Policy evaluation
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a policy")
    eval_parser.add_argument("policy_id", help="Policy to evaluate")
    eval_parser.add_argument("context", help="JSON context for evaluation")

    # List commands
    subparsers.add_parser("list-policies", help="List all policies")
    subparsers.add_parser("list-grants", help="List all grants")

    args = parser.parse_args()
    manager = PolicyManager()

    if args.command == "create-policy":
        parameters = json.loads(args.parameters)
        policy = manager.create_policy(
            args.policy_id, PolicyType(args.policy_type), parameters
        )
        manager.add_policy(policy)
        print(f"Created policy: {policy['policy_id']} ({policy['hash']})")

    elif args.command == "create-grant":
        grant = manager.create_grant(
            args.grant_id, args.grantee_did, args.resource, args.actions
        )
        manager.add_grant(grant)
        print(f"Created grant: {grant['grant_id']} ({grant['hash']})")

    elif args.command == "evaluate":
        context = json.loads(args.context)
        result = manager.evaluate_policy(args.policy_id, context)
        print(f"Policy {args.policy_id} evaluation: {'PASS' if result else 'FAIL'}")

    elif args.command == "list-policies":
        policies = manager.get_active_policies()
        print(f"Active Policies ({len(policies)}):")
        for policy in policies:
            print(
                f"  {policy['policy_id']}: {policy['type']} (enforced: {policy['enforced_count']}, violations: {policy['violation_count']})"
            )

    elif args.command == "list-grants":
        grants = manager.load_grants()
        print(f"All Grants ({len(grants['grants'])}):")
        for grant in grants["grants"].values():
            status = "ACTIVE" if grant["active"] else "INACTIVE"
            print(
                f"  {grant['grant_id']}: {grant['grantee_did']} -> {grant['resource']} [{status}]"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
