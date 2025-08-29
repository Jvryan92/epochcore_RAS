"""Multi-agent coordination system for investment strategy."""

from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
import asyncio
import logging
from enum import Enum
from datetime import datetime

from .base_agent import BaseAgent


class AgentRole(Enum):
    """Defined roles for specialized agents."""

    ANALYST = "analyst"  # Market and data analysis
    STRATEGIST = "strategist"  # Strategy development
    RISK_MANAGER = "risk"  # Risk assessment and management
    TAX_ADVISOR = "tax"  # Tax optimization
    MONITOR = "monitor"  # Performance monitoring
    COORDINATOR = "coordinator"  # Inter-agent coordination


@dataclass
class AgentContext:
    """Shared context for agent collaboration."""

    timestamp: datetime
    market_data: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    strategy_state: Dict[str, Any]
    agent_messages: List[Dict[str, Any]]
    active_tasks: Dict[str, Any]


class AgentMessage:
    """Message structure for inter-agent communication."""

    def __init__(
        self,
        sender: AgentRole,
        receiver: AgentRole,
        message_type: str,
        content: Dict[str, Any],
        priority: int = 1,
    ):
        """Initialize agent message.

        Args:
            sender: Role of sending agent
            receiver: Role of receiving agent
            message_type: Type of message
            content: Message content
            priority: Message priority (1-5)
        """
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.priority = max(1, min(5, priority))
        self.timestamp = datetime.now()


class BaseStrategyAgent(BaseAgent):
    """Base class for strategy-focused agents."""

    def __init__(
        self, role: AgentRole, name: str, context: Optional[AgentContext] = None
    ):
        """Initialize strategy agent.

        Args:
            role: Agent's role in the system
            name: Agent's name
            context: Shared context instance
        """
        super().__init__(name)
        self.role = role
        self.context = context or AgentContext(
            timestamp=datetime.now(),
            market_data={},
            risk_metrics={},
            strategy_state={},
            agent_messages=[],
            active_tasks={},
        )
        self.message_queue = asyncio.Queue()
        self._running = False

    async def start(self):
        """Start agent's message processing loop."""
        self._running = True
        while self._running:
            try:
                message = await self.message_queue.get()
                await self.process_message(message)
                self.message_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    async def stop(self):
        """Stop agent's message processing."""
        self._running = False

    async def send_message(
        self,
        receiver: AgentRole,
        message_type: str,
        content: Dict[str, Any],
        priority: int = 1,
    ):
        """Send message to another agent.

        Args:
            receiver: Role of receiving agent
            message_type: Type of message
            content: Message content
            priority: Message priority
        """
        message = AgentMessage(
            sender=self.role,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority,
        )
        self.context.agent_messages.append(
            {
                "timestamp": message.timestamp,
                "sender": message.sender.value,
                "receiver": message.receiver.value,
                "type": message.message_type,
                "priority": message.priority,
            }
        )
        await self.message_queue.put(message)

    async def process_message(self, message: AgentMessage):
        """Process received message.

        Args:
            message: Received message
        """
        raise NotImplementedError("Subclasses must implement process_message()")

    def update_context(self, updates: Dict[str, Any]):
        """Update shared context.

        Args:
            updates: Context updates
        """
        for key, value in updates.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)

    async def request_analysis(
        self, analysis_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request analysis from analyst agent.

        Args:
            analysis_type: Type of analysis needed
            data: Data for analysis

        Returns:
            Analysis results
        """
        await self.send_message(
            receiver=AgentRole.ANALYST,
            message_type="analysis_request",
            content={"type": analysis_type, "data": data},
        )
        # In real implementation, would wait for response
        return {}

    async def request_risk_assessment(
        self, portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request risk assessment from risk manager.

        Args:
            portfolio: Portfolio data

        Returns:
            Risk assessment results
        """
        await self.send_message(
            receiver=AgentRole.RISK_MANAGER,
            message_type="risk_assessment",
            content={"portfolio": portfolio},
            priority=3,
        )
        # In real implementation, would wait for response
        return {}
