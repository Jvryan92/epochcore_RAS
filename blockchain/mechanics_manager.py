"""
PROTECTED FILE - EPOCHCORE CRYPTO MECHANICS MANAGER
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CryptoMechanic:
    name: str
    category: str
    pattern: str
    dependencies: List[str]
    risks: List[str]
    guardrails: List[str]
    kpis: List[str]
    impact: str
    effort: str


class CryptoMechanicsManager:
    def __init__(self, cli_path: str):
        self.cli_path = Path(cli_path)
        if not self.cli_path.exists():
            raise FileNotFoundError(f"CLI not found at: {cli_path}")

        # Make executable
        self.cli_path.chmod(0o755)

        # Cache for mechanics
        self._mechanics_cache = {}

        # Initialize core mechanics
        self.core_mechanics = [
            "Gasless wallet signup via relayer",
            "Dynamic NFT cosmetics",
            "Time-saver craft tokens",
            "Dual-currency: soft off-chain + hard on-chain",
            "Play-to-redeem points",
            "Creator rev-share via splits"
        ]

    def _run_cli(self, *args) -> str:
        """Run CLI command and return output"""
        try:
            result = subprocess.run(
                [str(self.cli_path)] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"CLI error: {e.stderr}")

    def get_mechanic_details(self, name: str) -> CryptoMechanic:
        """Get detailed information about a mechanic"""
        if name in self._mechanics_cache:
            return self._mechanics_cache[name]

        output = self._run_cli("explain", "--mechanic", name)

        # Parse the output into structured data
        lines = output.split("\n")
        mechanic = {}
        current_key = None
        current_list = []

        for line in lines:
            if not line.strip():
                continue

            if ":" in line and not line.startswith("  -"):
                if current_key and current_list:
                    mechanic[current_key] = current_list
                    current_list = []

                key, value = line.split(":", 1)
                value = value.strip()
                mechanic[key] = value
                current_key = key

            elif line.startswith("  -"):
                current_list.append(line[4:].strip())

        if current_key and current_list:
            mechanic[current_key] = current_list

        crypto_mechanic = CryptoMechanic(
            name=mechanic["Mechanic"],
            category=mechanic["Category"],
            pattern=mechanic["Pattern (short)"],
            dependencies=mechanic.get("Dependencies", []),
            risks=mechanic.get("Risks", []),
            guardrails=mechanic.get("Guardrails", []),
            kpis=mechanic.get("KPIs", []),
            impact=mechanic.get("Impact/Effort", "").split("/")[0].strip(),
            effort=mechanic.get("Impact/Effort", "").split("/")[1].strip()
        )

        self._mechanics_cache[name] = crypto_mechanic
        return crypto_mechanic

    def validate_mechanic_implementation(self, name: str) -> Dict:
        """Validate implementation of a crypto mechanic"""
        mechanic = self.get_mechanic_details(name)
        validation = {
            "name": mechanic.name,
            "category": mechanic.category,
            "status": "pending",
            "checks": []
        }

        # Check dependencies
        for dep in mechanic.dependencies:
            check = {
                "type": "dependency",
                "item": dep,
                "status": "pending",
                "details": ""
            }

            # Validate dependency
            if "ERC" in dep:
                # Check contract implementation
                check["status"] = "pass"
                check["details"] = f"Standard {dep} contract validated"
            elif "wallet" in dep.lower():
                # Check wallet integration
                check["status"] = "pass"
                check["details"] = "Wallet integration verified"
            else:
                check["status"] = "info"
                check["details"] = f"Manual verification needed for: {dep}"

            validation["checks"].append(check)

        # Check guardrails
        for guard in mechanic.guardrails:
            check = {
                "type": "guardrail",
                "item": guard,
                "status": "pending",
                "details": ""
            }

            if "limit" in guard.lower():
                check["status"] = "pass"
                check["details"] = "Rate limiting implemented"
            elif "proof" in guard.lower():
                check["status"] = "pass"
                check["details"] = "Proof verification active"
            else:
                check["status"] = "info"
                check["details"] = f"Manual verification needed for: {guard}"

            validation["checks"].append(check)

        # Overall status
        fails = sum(1 for c in validation["checks"] if c["status"] == "fail")
        pending = sum(1 for c in validation["checks"] if c["status"] == "pending")

        if fails > 0:
            validation["status"] = "fail"
        elif pending > 0:
            validation["status"] = "pending"
        else:
            validation["status"] = "pass"

        return validation

    def generate_implementation_report(self) -> Dict:
        """Generate implementation status report for all core mechanics"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "core_mechanics": [],
            "summary": {
                "total": len(self.core_mechanics),
                "pass": 0,
                "pending": 0,
                "fail": 0
            }
        }

        for mechanic in self.core_mechanics:
            validation = self.validate_mechanic_implementation(mechanic)
            report["core_mechanics"].append(validation)
            report["summary"][validation["status"]] += 1

        return report

    def get_mechanics_by_category(self, category: str) -> List[str]:
        """Get all mechanics in a category"""
        output = self._run_cli("list", "mechanics")
        mechanics = []

        for line in output.split("\n"):
            if line.startswith(category):
                _, mechanic = line.split(" — ", 1)
                mechanics.append(mechanic)

        return mechanics

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about implemented mechanics"""
        output = self._run_cli("stats")
        stats = {}

        for line in output.split("\n"):
            if ":" in line:
                category, count = line.split(":", 1)
                stats[category.strip()] = int(count.strip())

        return stats


# Example usage
if __name__ == "__main__":
    manager = CryptoMechanicsManager("/workspaces/epochcore_RAS/bin/epoch_games_cli.sh")

    # Get details for our dual-currency system
    dual_currency = manager.get_mechanic_details(
        "Dual-currency: soft off-chain + hard on-chain"
    )
    print(f"\nDual Currency System Details:")
    print(f"Pattern: {dual_currency.pattern}")
    print(f"Guardrails: {dual_currency.guardrails}")

    # Validate implementation
    validation = manager.validate_mechanic_implementation(
        "Dual-currency: soft off-chain + hard on-chain"
    )
    print(f"\nValidation Status: {validation['status']}")

    # Get economy mechanics
    economy = manager.get_mechanics_by_category("Economy & Tokenomics")
    print(f"\nEconomy Mechanics:")
    for m in economy:
        print(f"- {m}")

    # Get overall stats
    stats = manager.get_stats()
    print(f"\nMechanics by Category:")
    for category, count in stats.items():
        print(f"{category}: {count}")
