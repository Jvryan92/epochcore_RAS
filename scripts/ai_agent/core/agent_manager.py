import datetime as dt
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from .base_agent import BaseAgent
from .logger import setup_logging


class AgentManager:
    """Manager class for coordinating multiple AI agents with compounding features."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.config = self._load_config_internal(config_path)
        self.compound_decisions: Dict[str, List[Dict[str, Any]]] = {}
        self.agent_dependencies: Dict[str, Set[str]] = {}

        # Setup logging
        log_file = None
        if self.config.get("logging", {}).get("file"):
            log_file = Path(self.config["logging"]["file"])

        self.logger = setup_logging(
            log_level=self.config.get("logging", {}).get("level", "INFO"),
            log_file=log_file,
            console_output=self.config.get("logging", {}).get("console", True),
        )

    def load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file and configure all agents.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        # Accept str or Path
        if isinstance(config_path, str):
            config_path = Path(config_path)
        self.config = self._load_config_internal(config_path)
        # Configure agents based on loaded config
        for agent_name, agent_config in self.config.get("agents", {}).items():
            if agent_name in self.agents:
                self.agents[agent_name].config.update(agent_config)
        # Also update config for agents registered after config load
        for agent in self.agents.values():
            if (
                self.config
                and "agents" in self.config
                and agent.name in self.config["agents"]
            ):
                agent.config.update(self.config["agents"][agent.name])
        return self.config

    def get_agent(self, agent_name: str):
        """Return the agent instance by name."""
        return self.agents.get(agent_name)

    def stop_agent(self, agent_name: str):
        """Stop the agent if it has a cleanup method."""
        agent = self.agents.get(agent_name)
        if agent and hasattr(agent, "cleanup"):
            agent.cleanup()
            return {"status": "success"}
        return {"status": "error", "message": "Agent not found or cannot be stopped."}

    def stop_all_agents(self) -> Dict[str, Any]:
        """Stop all registered agents and return their results as a dict."""
        results = {}
        for agent_name, agent in self.agents.items():
            if hasattr(agent, "cleanup"):
                agent.cleanup()
                results[agent_name] = {"status": "success"}
            else:
                results[agent_name] = {
                    "status": "error",
                    "message": "No cleanup method.",
                }
        return results

        return self.config

    def _load_config_internal(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if config_path and config_path.exists():
            import json

            with open(config_path, "r") as f:
                return json.load(f)

        # Default configuration
        return {
            "logging": {"level": "INFO", "console": True, "file": None},
            "agents": {},
        }

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the manager.

        Args:
            agent: Agent instance to register
        """
        if agent.name in self.agents:
            raise ValueError(f"Agent '{agent.name}' is already registered.")
        self.agents[agent.name] = agent
        # Update agent config if present in manager config
        if (
            self.config
            and "agents" in self.config
            and agent.name in self.config["agents"]
        ):
            self.agents[agent.name].config.update(self.config["agents"][agent.name])
        self.logger.info(f"Registered agent: {agent.name}")

    def start_all_agents(self) -> Dict[str, Any]:
        """Start all registered agents and return their results as a dict."""
        results = {}
        for agent_name in self.agents:
            results[agent_name] = self.start_agent(agent_name)
        return results

    def start_agent(self, agent_name: str) -> Dict[str, Any]:
        """Start a specific agent by name.

        Args:
            agent_name: Name of the agent to run

        Returns:
            Dictionary containing execution results
        """
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found"
            self.logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        self.logger.info(f"Starting agent: {agent_name}")
        return self.agents[agent_name].start()

    def run_agent(self, agent_name: str) -> Dict[str, Any]:
        """Run a specific agent by name (alias for start_agent).

        Args:
            agent_name: Name of the agent to run

        Returns:
            Dictionary containing execution results
        """
        return self.start_agent(agent_name)

    def run_all_agents(self) -> List[Dict[str, Any]]:
        """Run all registered agents.

        Returns:
            List of execution results for all agents
        """
        results = []
        self.logger.info("Running all agents")

        for agent_name in self.agents:
            result = self.run_agent(agent_name)
            results.append(result)

        return results

    def list_agents(self) -> List[str]:
        """Get list of registered agent names.

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def get_agent_status(self) -> Dict[str, bool]:
        """Get running status of all agents.

        Returns:
            Dictionary mapping agent names to their running status
        """
        return {name: agent.is_running() for name, agent in self.agents.items()}

    def deregister_agent(self, agent_name: str) -> None:
        """Remove an agent from the manager."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info(f"Deregistered agent: {agent_name}")
        else:
            raise ValueError(f"Agent '{agent_name}' not found.")

    def get_all_agents(self) -> List[BaseAgent]:
        """Return a list of all agent instances."""
        return list(self.agents.values())

    def register_compound_feature(
        self, feature_id: str, dependent_agents: List[str]
    ) -> None:
        """Register a compound feature that requires multiple agents to make decisions.

        Args:
            feature_id: Unique identifier for the compound feature
            dependent_agents: List of agent names that need to contribute to decisions
        """
        for agent_name in dependent_agents:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not registered")

        self.compound_decisions[feature_id] = []
        for agent_name in dependent_agents:
            self.agent_dependencies.setdefault(agent_name, set()).add(feature_id)

    def contribute_decision(
        self, agent_name: str, feature_id: str, decision: Dict[str, Any]
    ) -> None:
        """Contribute an agent's decision to a compound feature.

        Args:
            agent_name: Name of the agent making the decision
            feature_id: ID of the compound feature
            decision: The agent's decision data
        """
        if feature_id not in self.compound_decisions:
            raise ValueError(f"Compound feature '{feature_id}' not registered")

        if feature_id not in self.agent_dependencies.get(agent_name, set()):
            raise ValueError(
                f"Agent '{agent_name}' not registered for feature '{feature_id}'"
            )

        self.compound_decisions[feature_id].append(
            {
                "agent": agent_name,
                "decision": decision,
                "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            }
        )

    def get_compound_decision(self, feature_id: str) -> Dict[str, Any]:
        """Get the final compound decision by combining all agent contributions.

        Args:
            feature_id: ID of the compound feature

        Returns:
            Combined decision data from all contributing agents
        """
        if feature_id not in self.compound_decisions:
            raise ValueError(f"Compound feature '{feature_id}' not registered")

        decisions = self.compound_decisions[feature_id]
        if not decisions:
            return {"status": "pending", "message": "No decisions contributed yet"}

        # Combine decisions (can be customized based on feature needs)
        combined = {
            "status": "complete",
            "decisions": decisions,
            "summary": self._summarize_decisions(decisions),
        }

        return combined

    def _summarize_decisions(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize multiple agent decisions into a final recommendation.

        Args:
            decisions: List of individual agent decisions

        Returns:
            Summary of combined decisions
        """
        # This is a simple example - customize based on your needs
        summary = {
            "agents_involved": len(decisions),
            "agreement_level": 0.0,
            "recommendations": [],
            "metrics": {},
        }

        # Collect all metrics and recommendations
        metrics_count = defaultdict(int)
        metrics_sum = defaultdict(float)
        all_recommendations = []

        for decision in decisions:
            if "metrics" in decision["decision"]:
                for k, v in decision["decision"]["metrics"].items():
                    metrics_count[k] += 1
                    metrics_sum[k] += float(v)

            if "recommendations" in decision["decision"]:
                all_recommendations.extend(decision["decision"]["recommendations"])

        # Average metrics
        for metric, count in metrics_count.items():
            if count > 0:
                summary["metrics"][metric] = metrics_sum[metric] / count

        # Include most common recommendations
        from collections import Counter

        if all_recommendations:
            recommendation_counts = Counter(all_recommendations)
            total_recs = len(decisions)
            summary["recommendations"] = [
                rec
                for rec, count in recommendation_counts.most_common()
                if count >= total_recs * 0.5  # At least 50% agreement
            ]

            # Calculate agreement level
            summary["agreement_level"] = len(summary["recommendations"]) / len(
                all_recommendations
            )

        return summary
