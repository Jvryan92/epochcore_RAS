"""Base agent class for the StrategyDECK AI agent system with enhanced capabilities."""

import logging
import time
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Set
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


class BaseAgent(ABC):
    """Abstract base class for all AI agents in the system with advanced features."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base agent with enhanced monitoring and inter-agent communication.

        Args:
            name: Agent name
            config: Optional configuration dictionary with agent settings
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"strategy_ai_agent.{name}")
        self._is_running = False
        self._start_time = None
        self._last_run_duration = None
        self._error_count = 0
        self._success_count = 0
        self._performance_metrics: List[Dict[str, Any]] = []

        # Inter-agent communication
        self._message_queue: Dict[str, List[Dict[str, Any]]] = {}
        self._subscribed_topics: Set[str] = set()
        self._connected_agents: Dict[str, "BaseAgent"] = {}
        self._agent_interactions: List[Dict[str, Any]] = []
        self._last_error: Optional[Tuple[str, str]] = (
            None  # (error_type, error_message)
        )

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Execute the agent's main functionality.

        Returns:
            Dictionary containing execution results and status
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the agent's configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def setup(self):
        """Setup before agent execution. Can be overridden by subclasses."""
        pass

    def cleanup(self):
        """Cleanup after agent execution. Can be overridden by subclasses."""
        # Clear any pending messages
        self._message_queue.clear()
        self._agent_interactions.clear()

    def connect_to_agent(self, agent: "BaseAgent") -> None:
        """Establish a direct connection to another agent.

        Args:
            agent: The agent to connect with
        """
        self._connected_agents[agent.name] = agent
        self.logger.info(f"Connected to agent: {agent.name}")

    def disconnect_from_agent(self, agent_name: str) -> None:
        """Remove connection to an agent.

        Args:
            agent_name: Name of agent to disconnect from
        """
        if agent_name in self._connected_agents:
            del self._connected_agents[agent_name]
            self.logger.info(f"Disconnected from agent: {agent_name}")

    def subscribe_to_topic(self, topic: str) -> None:
        """Subscribe to a message topic.

        Args:
            topic: Topic to subscribe to
        """
        self._subscribed_topics.add(topic)
        self.logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe_from_topic(self, topic: str) -> None:
        """Unsubscribe from a message topic.

        Args:
            topic: Topic to unsubscribe from
        """
        if topic in self._subscribed_topics:
            self._subscribed_topics.remove(topic)
            self.logger.info(f"Unsubscribed from topic: {topic}")

    def send_message(
        self,
        recipient: Optional[str],
        topic: str,
        data: Dict[str, Any],
        priority: str = "normal",
    ) -> None:
        """Send a message to another agent or broadcast to a topic.

        Args:
            recipient: Target agent name, or None for broadcast
            topic: Message topic
            data: Message data
            priority: Message priority ('high', 'normal', 'low')
        """
        message = {
            "sender": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "data": data,
            "priority": priority,
        }

        # Record interaction
        self._agent_interactions.append(
            {
                "type": "send",
                "timestamp": message["timestamp"],
                "recipient": recipient or "broadcast",
                "topic": topic,
                "priority": priority,
            }
        )

        if recipient:
            if recipient in self._connected_agents:
                self._connected_agents[recipient]._receive_message(message)
                self.logger.debug(f"Sent message to {recipient} on topic {topic}")
            else:
                self.logger.warning(f"Agent {recipient} not connected")
        else:
            # Broadcast to all connected agents
            for agent in self._connected_agents.values():
                if topic in agent._subscribed_topics:
                    agent._receive_message(message)
            self.logger.debug(f"Broadcast message on topic {topic}")

    def _receive_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming message from another agent.

        Args:
            message: The received message
        """
        topic = message["topic"]
        if topic not in self._message_queue:
            self._message_queue[topic] = []

        self._message_queue[topic].append(message)

        # Record interaction
        self._agent_interactions.append(
            {
                "type": "receive",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sender": message["sender"],
                "topic": topic,
                "priority": message["priority"],
            }
        )

        self.logger.debug(f"Received message from {message['sender']} on topic {topic}")

        # Process high priority messages immediately
        if message["priority"] == "high":
            self._process_message(message)

    def get_messages(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get received messages, optionally filtered by topic.

        Args:
            topic: Optional topic filter

        Returns:
            List of messages
        """
        if topic:
            messages = self._message_queue.get(topic, [])
            self._message_queue[topic] = []  # Clear after reading
            return messages

        # Get all messages
        all_messages = []
        for topic_messages in self._message_queue.values():
            all_messages.extend(topic_messages)
        self._message_queue.clear()
        return all_messages

    def get_interaction_history(self) -> List[Dict[str, Any]]:
        """Get history of agent interactions.

        Returns:
            List of interaction records
        """
        return self._agent_interactions.copy()

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a received message. Override in subclasses.

        Args:
            message: Message to process
        """
        pass

    def start(self) -> Dict[str, Any]:
        """Start agent execution with enhanced monitoring and error handling.

        Returns:
            Dictionary containing execution results and detailed metrics
        """
        if self._is_running:
            return {"status": "error", "error": "Agent already running"}

        try:
            self._is_running = True
            self._start_time = time.time()
            self.logger.info(f"Starting agent: {self.name}")

            # Pre-execution validation
            if not self.validate_config():
                raise ValueError("Invalid configuration")

            # Setup phase
            self.setup()

            # Main execution
            result = self.run()

            # Record metrics
            duration = time.time() - self._start_time
            self._last_run_duration = duration
            self._success_count += 1

            # Add performance metrics
            self._performance_metrics.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "duration": duration,
                    "success": True,
                    "memory_usage": self._get_memory_usage(),
                }
            )

            # Cleanup phase
            self.cleanup()

            # Enhance result with metrics
            result.update(
                {
                    "status": "success",
                    "agent": self.name,
                    "execution_time": duration,
                    "success_rate": self._calculate_success_rate(),
                    "performance_metrics": self._get_latest_metrics(),
                }
            )

            return result

        except Exception as e:
            self._error_count += 1
            self._last_error = (type(e).__name__, str(e))
            self.logger.error(f"Error in agent {self.name}: {str(e)}")
            self.logger.debug(traceback.format_exc())

            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }

        finally:
            self._is_running = False
            self._start_time = None

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics.

        Returns:
            Dictionary with memory usage metrics
        """
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # RSS in MB
            "vms": memory_info.vms / 1024 / 1024,  # VMS in MB
        }

    def _calculate_success_rate(self) -> float:
        """Calculate the agent's success rate.

        Returns:
            Success rate as a percentage
        """
        total_runs = self._success_count + self._error_count
        return (self._success_count / total_runs * 100) if total_runs > 0 else 0.0

    def _get_latest_metrics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent performance metrics.

        Args:
            limit: Number of metrics to return

        Returns:
            List of recent performance metrics
        """
        return self._performance_metrics[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics.

        Returns:
            Dictionary containing agent status and performance metrics
        """
        return {
            "name": self.name,
            "running": self._is_running,
            "last_run_duration": self._last_run_duration,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "success_rate": self._calculate_success_rate(),
            "last_error": self._last_error,
            "recent_performance": self._get_latest_metrics(),
        }
        """Start the agent with error handling and logging.

        Returns:
            Dictionary containing execution results and status
        """
        # Validate configuration first
        if not self.validate_config():
            self.logger.error(f"Invalid configuration for agent {self.name}")
            return {
                "status": "error",
                "agent": self.name,
                "error": "Invalid configuration",
            }

        if self._is_running:
            self.logger.error(f"Agent {self.name} is already running")
            return {
                "status": "error",
                "agent": self.name,
                "error": "Agent is already running",
            }

        try:
            self.logger.info(f"Starting agent: {self.name}")
            self._is_running = True

            # Run setup
            self.setup()

            # Execute main logic
            result = self.run()

            self.logger.info(f"Agent {self.name} completed successfully")
            return {"status": "success", "agent": self.name, "result": result}

        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            return {"status": "error", "agent": self.name, "error": str(e)}
        finally:
            # Always run cleanup
            self.cleanup()
            self._is_running = False

    def is_running(self) -> bool:
        """Check if the agent is currently running.

        Returns:
            True if agent is running, False otherwise
        """
        return self._is_running

    def get_project_root(self) -> Path:
        """Get the project root directory.

        Returns:
            Path to project root
        """
        return Path(__file__).resolve().parent.parent.parent.parent
