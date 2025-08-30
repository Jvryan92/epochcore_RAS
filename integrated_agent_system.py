#!/usr/bin/env python3
"""
EpochCore RAS Integration Module

This module connects the Kids Friendly AI Guide, Epoch Audit System,
and Mesh Trigger Core with the existing EpochCore RAS agent architecture.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Import core EpochCore RAS components
from agent_management import AgentManager
from agent_synchronization import SyncMessage, get_async_synchronizer, get_synchronizer
from mock_strategydeck_agent import StrategyDeckAgent
from scripts.epoch_audit import EpochAudit

# Import the new components
from scripts.kids_friendly_ai_guide import AIFriendlyGuide, KidsFriendlyMetaphor
from scripts.mesh.trigger_core import MeshTriggerCore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("RASIntegration")


class KidsFriendlyAgentAdapter:
    """
    Adapter that integrates Kids Friendly AI Guide with the agent system.

    This adapter enables agents to provide child-friendly explanations and 
    educational content about AI, ensuring a positive framing that emphasizes
    AI as a helper, not something to fear.
    """

    def __init__(self, agent_id: str = "kids_friendly_agent"):
        """
        Initialize the Kids Friendly AI Guide adapter.

        Args:
            agent_id: Identifier for the agent in the EpochCore RAS system
        """
        self.agent_id = agent_id
        self.guide = AIFriendlyGuide()
        self.agent_manager = AgentManager()
        self.synchronizer = get_synchronizer()

        # Register with agent manager
        self._register_agent()

        logger.info(
            f"Kids Friendly AI Guide adapter initialized with agent ID: {agent_id}")

    def _register_agent(self) -> None:
        """Register the Kids Friendly AI Guide as an agent in the system."""
        skills = [
            "ai_explanation",
            "age_appropriate_content",
            "educational_storytelling",
            "interactive_activities",
            "child_friendly_metaphors"
        ]

        # Create and register agent
        agent = self.agent_manager.create_agent(skills, "education")
        self.agent_manager.register_agent(agent)
        self.agent_did = agent["did"]

        # Register with synchronizer
        self.synchronizer.register_agent(
            self.agent_id,
            capabilities=skills
        )

        logger.info(
            f"Kids Friendly AI Guide registered as agent with DID: {self.agent_did}")

    def get_age_appropriate_explanation(self, age: int, context: Dict[str, Any] = None) -> str:
        """
        Get an age-appropriate explanation of AI as a helper.

        Args:
            age: Age of the child
            context: Additional context for the explanation

        Returns:
            Age-appropriate explanation
        """
        explanation = self.guide.get_ai_helper_explanation(age)

        # Log the interaction
        self.agent_manager.log_heartbeat(self.agent_did, "EXPLANATION_PROVIDED")

        # Update agent stats
        self.agent_manager.update_agent_stats(
            self.agent_did,
            success=True,
            latency=0.1,
            ethical_metrics={
                "ethical_score": 1.0,
                "assessment_success": True,
                "constraint_satisfaction": 1.0,
                "reflection_confidence": 0.9,
                "principle_performance": {
                    "age_appropriate": 1.0,
                    "educational_value": 0.9,
                    "positive_framing": 1.0
                },
                "stakeholder_impact": {
                    "child": 0.9,
                    "parents": 0.8,
                    "educators": 0.9
                }
            }
        )

        return explanation

    def get_content_for_child(self, age: int) -> Dict[str, Any]:
        """
        Get complete age-appropriate content package for a child.

        Args:
            age: Age of the child

        Returns:
            Dictionary with metaphors, stories, and activities
        """
        content = self.guide.get_age_appropriate_content(age)

        # Log the interaction
        self.agent_manager.log_heartbeat(self.agent_did, "CONTENT_PROVIDED")

        return content

    def get_dialog_for_child(self, age: int) -> List[Dict[str, str]]:
        """
        Get an interactive dialog explaining AI concepts for a child.

        Args:
            age: Age of the child

        Returns:
            List of dialog exchanges (speaker, text)
        """
        return self.guide.get_interactive_dialogue(age)

    async def broadcast_activity(self, age_range: List[int], activity_type: str) -> bool:
        """
        Broadcast an activity suggestion to other agents.

        Args:
            age_range: Range of ages the activity is appropriate for
            activity_type: Type of activity (story, game, etc.)

        Returns:
            True if successfully broadcast
        """
        # Find appropriate content
        min_age, max_age = min(age_range), max(age_range)
        mid_age = (min_age + max_age) // 2
        content = self.guide.get_age_appropriate_content(mid_age)

        # Select content based on type
        if activity_type == "story" and content["stories"]:
            activity_content = content["stories"][0]
        elif activity_type == "activity" and content["activities"]:
            activity_content = content["activities"][0]
        else:
            activity_content = content["metaphor"]

        # Broadcast to other agents
        async_sync = get_async_synchronizer()
        success = await async_sync.broadcast_message(
            sender_id=self.agent_id,
            message_type="kids_friendly_activity",
            content={
                "age_range": age_range,
                "activity_type": activity_type,
                "content": activity_content
            }
        )

        return success


class EpochAuditAdapter:
    """
    Adapter that integrates the Epoch Audit System with the agent architecture.

    This adapter provides secure audit logging, verification, integrity checks,
    and Alpha Ceiling enforcement for the agent system.
    """

    def __init__(self, agent_id: str = "epoch_audit_agent", ledger_root: str = "./ledger"):
        """
        Initialize the Epoch Audit adapter.

        Args:
            agent_id: Identifier for the agent in the EpochCore RAS system
            ledger_root: Root directory for audit ledger data
        """
        self.agent_id = agent_id
        self.audit = EpochAudit(ledger_root=ledger_root)
        self.agent_manager = AgentManager()
        self.synchronizer = get_synchronizer()

        # Register with agent manager
        self._register_agent()

        # Schedule periodic audits
        self._schedule_audits()

        logger.info(f"Epoch Audit adapter initialized with agent ID: {agent_id}")

    def _register_agent(self) -> None:
        """Register the Epoch Audit as an agent in the system."""
        skills = [
            "audit_logging",
            "cryptographic_sealing",
            "integrity_verification",
            "alpha_ceiling_enforcement",
            "gbt_epoch_timestamping",
            "phone_audit_scroll"
        ]

        # Create and register agent
        agent = self.agent_manager.create_agent(skills, "security")
        self.agent_manager.register_agent(agent)
        self.agent_did = agent["did"]

        # Register with synchronizer
        self.synchronizer.register_agent(
            self.agent_id,
            capabilities=skills
        )

        logger.info(f"Epoch Audit registered as agent with DID: {self.agent_did}")

    def _schedule_audits(self) -> None:
        """Schedule periodic audits."""
        # Schedule hourly audits
        self.audit.schedule_audit(3600)  # 1 hour

        logger.info("Scheduled periodic audits")

    def log_agent_event(self, agent_id: str, event: str, note: str, **kwargs) -> Dict[str, Any]:
        """
        Log an agent event to the audit system.

        Args:
            agent_id: ID of the agent
            event: Event type identifier
            note: Description of the event
            **kwargs: Additional fields to include in the log entry

        Returns:
            The complete log entry
        """
        entry = self.audit.log_event(
            event=event,
            note=note,
            agent_id=agent_id,
            **kwargs
        )

        # Log the audit action
        self.agent_manager.log_heartbeat(self.agent_did, "AUDIT_LOG_CREATED")

        return entry

    def enforce_resource_limit(self, resource_value: int, resource_type: str, ceiling: Optional[int] = None) -> int:
        """
        Enforce Alpha Ceiling on a resource value.

        Args:
            resource_value: The value to check
            resource_type: Type of resource (compute, memory, etc.)
            ceiling: Optional override for the default alpha ceiling

        Returns:
            The value, capped at the ceiling if necessary
        """
        capped_value = self.audit.enforce_alpha_ceiling(resource_value, ceiling)

        # Log if ceiling was enforced
        if capped_value != resource_value:
            self.log_agent_event(
                agent_id=self.agent_id,
                event="alpha_ceiling_enforced",
                note=f"Resource limit enforced on {resource_type}",
                original_value=resource_value,
                capped_value=capped_value,
                resource_type=resource_type
            )

        return capped_value

    def create_agent_seal(self, agent_id: str, data: str) -> Dict[str, Any]:
        """
        Create a cryptographic seal for agent data.

        Args:
            agent_id: ID of the agent
            data: The data to seal

        Returns:
            Seal information
        """
        seal_name = f"agent_{agent_id}_{int(time.time())}"
        return self.audit.create_seal(seal_name, data)

    def verify_agent_seal(self, seal_file: Path, data: str) -> bool:
        """
        Verify that agent data matches a previously created seal.

        Args:
            seal_file: Path to the seal file
            data: The data to verify

        Returns:
            True if the seal verifies, False otherwise
        """
        return self.audit.verify_seal(seal_file, data)

    def create_phone_audit_scroll(self) -> Dict[str, Any]:
        """
        Create a Phone Audit Scroll for the agent system.

        Returns:
            Audit information
        """
        audit_info = self.audit.phone_audit_scroll()

        # Log the audit action
        self.agent_manager.log_heartbeat(self.agent_did, "PHONE_AUDIT_CREATED")

        return audit_info

    async def broadcast_audit_alert(self, alert_type: str, details: Dict[str, Any]) -> bool:
        """
        Broadcast an audit alert to all agents.

        Args:
            alert_type: Type of alert (ceiling_breach, integrity_error, etc.)
            details: Details about the alert

        Returns:
            True if successfully broadcast
        """
        async_sync = get_async_synchronizer()
        success = await async_sync.broadcast_message(
            sender_id=self.agent_id,
            message_type="audit_alert",
            content={
                "alert_type": alert_type,
                "timestamp": self.audit._get_timestamp(),
                "details": details
            }
        )

        # Log the alert
        self.log_agent_event(
            agent_id=self.agent_id,
            event="audit_alert_broadcast",
            note=f"Broadcast audit alert: {alert_type}",
            alert_details=details
        )

        return success


class MeshTriggerAdapter:
    """
    Adapter that integrates the Mesh Trigger Core with the agent architecture.

    This adapter provides secure trigger management, activation, and verification
    for the agent mesh network.
    """

    def __init__(self, agent_id: str = "mesh_trigger_agent", base_dir: str = "./ledger"):
        """
        Initialize the Mesh Trigger adapter.

        Args:
            agent_id: Identifier for the agent in the EpochCore RAS system
            base_dir: Base directory for trigger data
        """
        self.agent_id = agent_id
        self.trigger_core = MeshTriggerCore(base_dir=base_dir)
        self.agent_manager = AgentManager()
        self.synchronizer = get_synchronizer()

        # Register with agent manager
        self._register_agent()

        # Register core system triggers
        self._register_core_triggers()

        logger.info(f"Mesh Trigger adapter initialized with agent ID: {agent_id}")

    def _register_agent(self) -> None:
        """Register the Mesh Trigger as an agent in the system."""
        skills = [
            "trigger_management",
            "trigger_activation",
            "seal_verification",
            "mesh_coordination",
            "alpha_ceiling_enforcement",
            "critical_trigger_verification"
        ]

        # Create and register agent
        agent = self.agent_manager.create_agent(skills, "mesh")
        self.agent_manager.register_agent(agent)
        self.agent_did = agent["did"]

        # Register with synchronizer
        self.synchronizer.register_agent(
            self.agent_id,
            capabilities=skills
        )

        logger.info(f"Mesh Trigger registered as agent with DID: {self.agent_did}")

    def _register_core_triggers(self) -> None:
        """Register core system triggers."""
        # Register standard triggers
        self.trigger_core.register_trigger(
            "system_heartbeat",
            "Regular system heartbeat to verify component health",
            resource_requirement=10,
            trigger_type="standard"
        )

        self.trigger_core.register_trigger(
            "mesh_optimize",
            "Optimize mesh configuration and performance",
            resource_requirement=50,
            trigger_type="standard"
        )

        # Register critical triggers
        self.trigger_core.register_trigger(
            "system_restart",
            "Restart system components after critical failure",
            resource_requirement=80,
            trigger_type="critical"
        )

        self.trigger_core.register_trigger(
            "security_alert",
            "Handle security breach or anomaly",
            resource_requirement=90,
            trigger_type="critical"
        )

        logger.info("Core system triggers registered")

    def register_agent_trigger(
        self,
        trigger_id: str,
        description: str,
        resource_requirement: int,
        trigger_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Register a new trigger for an agent.

        Args:
            trigger_id: Unique identifier for trigger
            description: Human-readable description
            resource_requirement: Resource cost (subject to Alpha Ceiling)
            trigger_type: Type of trigger (standard, critical, etc.)

        Returns:
            Trigger information
        """
        trigger_info = self.trigger_core.register_trigger(
            trigger_id,
            description,
            resource_requirement,
            trigger_type
        )

        # Log the registration
        self.agent_manager.log_heartbeat(
            self.agent_did, f"TRIGGER_REGISTERED:{trigger_id}")

        return trigger_info

    def register_handler(self, trigger_id: str, handler: Callable) -> bool:
        """
        Register a handler function for a trigger.

        Args:
            trigger_id: Trigger to handle
            handler: Function to call when trigger activates

        Returns:
            True if registered successfully, False otherwise
        """
        return self.trigger_core.register_handler(trigger_id, handler)

    def create_trigger_seal(self, trigger_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a cryptographic seal for a trigger.

        Args:
            trigger_id: Trigger to seal
            context: Additional context for the seal

        Returns:
            Seal information
        """
        return self.trigger_core.create_trigger_seal(trigger_id, context)

    def verify_trigger_seal(self, seal_data: Dict[str, Any]) -> bool:
        """
        Verify a trigger seal's integrity.

        Args:
            seal_data: The seal data to verify

        Returns:
            True if seal is valid, False otherwise
        """
        return self.trigger_core.verify_trigger_seal(seal_data)

    def activate_trigger(
        self,
        trigger_id: str,
        context: Dict[str, Any] = None,
        verify_count: int = 1
    ) -> Dict[str, Any]:
        """
        Activate a trigger and execute its handlers.

        Args:
            trigger_id: Trigger to activate
            context: Activation context
            verify_count: Number of verifications required (for critical triggers)

        Returns:
            Activation information
        """
        activation = self.trigger_core.activate_trigger(
            trigger_id,
            context or {},
            verify_count
        )

        # Log the activation
        if activation.get("status") == "completed":
            self.agent_manager.log_heartbeat(
                self.agent_did,
                f"TRIGGER_ACTIVATED:{trigger_id}"
            )
        else:
            self.agent_manager.detect_anomaly(
                self.agent_did,
                "TRIGGER_ACTIVATION_FAILED",
                f"Failed to activate trigger {trigger_id}: {activation.get('error', 'Unknown error')}"
            )

        return activation

    async def broadcast_trigger_activation(
        self,
        trigger_id: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Broadcast a trigger activation to all agents.

        Args:
            trigger_id: Trigger to activate
            context: Activation context

        Returns:
            True if successfully broadcast
        """
        async_sync = get_async_synchronizer()
        success = await async_sync.broadcast_message(
            sender_id=self.agent_id,
            message_type="trigger_activation",
            content={
                "trigger_id": trigger_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context or {}
            }
        )

        return success


class IntegratedAgentSystem:
    """
    Integrated system that combines all components into a cohesive whole.

    This class ties together the existing StrategyDeck agent with the
    new Kids Friendly AI Guide, Epoch Audit, and Mesh Trigger components.
    """

    def __init__(
        self,
        name: str = "IntegratedAgentSystem",
        enable_kids_friendly: bool = True,
        enable_epoch_audit: bool = True,
        enable_mesh_trigger: bool = True,
        data_dir: str = "./data"
    ):
        """
        Initialize the integrated agent system.

        Args:
            name: System name
            enable_kids_friendly: Whether to enable the Kids Friendly AI Guide
            enable_epoch_audit: Whether to enable the Epoch Audit System
            enable_mesh_trigger: Whether to enable the Mesh Trigger Core
            data_dir: Directory for system data
        """
        self.name = name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agent synchronizer
        self.synchronizer = get_synchronizer()

        # Initialize base StrategyDeck agent
        self.strategy_agent = StrategyDeckAgent(name=f"{name}_strategy")

        # Initialize the components
        if enable_kids_friendly:
            self.kids_friendly = KidsFriendlyAgentAdapter(f"{name}_kids_friendly")
        else:
            self.kids_friendly = None

        if enable_epoch_audit:
            self.epoch_audit = EpochAuditAdapter(
                f"{name}_epoch_audit",
                ledger_root=str(self.data_dir / "ledger")
            )
        else:
            self.epoch_audit = None

        if enable_mesh_trigger:
            self.mesh_trigger = MeshTriggerAdapter(
                f"{name}_mesh_trigger",
                base_dir=str(self.data_dir / "triggers")
            )
        else:
            self.mesh_trigger = None

        # Register message handlers
        self._register_message_handlers()

        # Create sync point for initialization
        self._create_init_sync_point()

        logger.info(f"Integrated Agent System initialized: {name}")

    def _register_message_handlers(self) -> None:
        """Register handlers for system messages."""
        # Register handler for kids friendly activities
        self.synchronizer.register_message_handler(
            "kids_friendly_activity",
            self._handle_kids_friendly_activity
        )

        # Register handler for audit alerts
        self.synchronizer.register_message_handler(
            "audit_alert",
            self._handle_audit_alert
        )

        # Register handler for trigger activations
        self.synchronizer.register_message_handler(
            "trigger_activation",
            self._handle_trigger_activation
        )

        logger.info("Message handlers registered")

    def _handle_kids_friendly_activity(self, message: SyncMessage) -> None:
        """Handle kids friendly activity messages."""
        logger.info(
            f"Received kids friendly activity: {message.content.get('activity_type')}")

        # Log activity reception
        if self.epoch_audit:
            self.epoch_audit.log_agent_event(
                agent_id=message.receiver_id,
                event="kids_activity_received",
                note=f"Received kids friendly {message.content.get('activity_type')}",
                activity=message.content
            )

    def _handle_audit_alert(self, message: SyncMessage) -> None:
        """Handle audit alert messages."""
        alert_type = message.content.get("alert_type")
        logger.warning(f"Received audit alert: {alert_type}")

        # Take action based on alert type
        if alert_type == "ceiling_breach" and self.mesh_trigger:
            # Activate security alert trigger
            self.mesh_trigger.activate_trigger(
                "security_alert",
                context=message.content.get("details", {})
            )

    def _handle_trigger_activation(self, message: SyncMessage) -> None:
        """Handle trigger activation messages."""
        trigger_id = message.content.get("trigger_id")
        logger.info(f"Received trigger activation: {trigger_id}")

        # Log trigger activation
        if self.epoch_audit:
            self.epoch_audit.log_agent_event(
                agent_id=message.receiver_id,
                event="trigger_received",
                note=f"Received trigger activation: {trigger_id}",
                trigger_context=message.content.get("context", {})
            )

        # Handle specific triggers
        if trigger_id == "mesh_optimize" and hasattr(self.strategy_agent, "optimize_mesh_async"):
            asyncio.create_task(self.strategy_agent.optimize_mesh_async())

    def _create_init_sync_point(self) -> None:
        """Create a synchronization point for initialization."""
        # Get all agent IDs
        agent_ids = []
        if self.kids_friendly:
            agent_ids.append(self.kids_friendly.agent_id)
        if self.epoch_audit:
            agent_ids.append(self.epoch_audit.agent_id)
        if self.mesh_trigger:
            agent_ids.append(self.mesh_trigger.agent_id)

        # Create sync point
        sync_id = self.synchronizer.create_sync_point(
            "system_initialization",
            agent_ids
        )

        if sync_id:
            # Mark agents as ready
            for agent_id in agent_ids:
                self.synchronizer.agent_ready_for_sync(sync_id, agent_id)

            # Wait for synchronization
            self.synchronizer.wait_for_sync(sync_id)
            logger.info("System initialization synchronized")

    async def get_child_friendly_explanation(self, age: int, context: Dict[str, Any] = None) -> str:
        """
        Get a child-friendly explanation of AI with audit logging.

        Args:
            age: Age of the child
            context: Additional context

        Returns:
            Age-appropriate explanation
        """
        if not self.kids_friendly:
            raise ValueError("Kids Friendly AI Guide is not enabled")

        # Enforce age range limits
        if self.epoch_audit:
            age = self.epoch_audit.enforce_resource_limit(age, "age", ceiling=14)

        # Get explanation
        explanation = self.kids_friendly.get_age_appropriate_explanation(age, context)

        # Log the event
        if self.epoch_audit:
            self.epoch_audit.log_agent_event(
                agent_id=self.kids_friendly.agent_id,
                event="child_explanation",
                note=f"Provided AI explanation for age {age}",
                age=age,
                context_type=type(context).__name__ if context else None
            )

        return explanation

    async def activate_system_trigger(
        self,
        trigger_id: str,
        context: Dict[str, Any] = None,
        is_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Activate a system trigger with proper verification and audit.

        Args:
            trigger_id: Trigger to activate
            context: Activation context
            is_critical: Whether this is a critical trigger

        Returns:
            Activation information
        """
        if not self.mesh_trigger:
            raise ValueError("Mesh Trigger Core is not enabled")

        # Create a trigger seal
        seal = self.mesh_trigger.create_trigger_seal(trigger_id, context or {})

        # Verify the seal
        is_valid = self.mesh_trigger.verify_trigger_seal(seal)
        if not is_valid:
            if self.epoch_audit:
                self.epoch_audit.log_agent_event(
                    agent_id=self.mesh_trigger.agent_id,
                    event="seal_verification_failed",
                    note=f"Failed to verify seal for trigger {trigger_id}",
                    trigger_id=trigger_id
                )
            raise ValueError(f"Invalid trigger seal for {trigger_id}")

        # Determine verification count
        verify_count = 3 if is_critical else 1

        # Activate the trigger
        activation = self.mesh_trigger.activate_trigger(
            trigger_id,
            context or {},
            verify_count
        )

        # Log the activation
        if self.epoch_audit:
            self.epoch_audit.log_agent_event(
                agent_id=self.mesh_trigger.agent_id,
                event="trigger_activated" if activation.get(
                    "status") == "completed" else "trigger_failed",
                note=f"Activated trigger {trigger_id}",
                trigger_id=trigger_id,
                activation_status=activation.get("status"),
                error=activation.get("error")
            )

        # Broadcast if successful
        if activation.get("status") == "completed":
            await self.mesh_trigger.broadcast_trigger_activation(trigger_id, context)

        return activation

    async def optimize_system(self) -> Dict[str, Any]:
        """
        Optimize the entire integrated system.

        Returns:
            Optimization results
        """
        # Activate mesh optimization trigger
        if self.mesh_trigger:
            self.mesh_trigger.activate_trigger(
                "mesh_optimize",
                {"source": self.name, "timestamp": datetime.now(
                    timezone.utc).isoformat()}
            )

        # Optimize StrategyDeck agent mesh
        if hasattr(self.strategy_agent, "optimize_mesh_async"):
            metrics = await self.strategy_agent.optimize_mesh_async()

            # Log optimization results
            if self.epoch_audit:
                self.epoch_audit.log_agent_event(
                    agent_id=self.name,
                    event="system_optimization",
                    note="System-wide optimization performed",
                    mesh_metrics={
                        "success_rate": metrics.success_rate,
                        "resource_utilization": metrics.resource_utilization,
                        "mesh_stability": metrics.mesh_stability,
                        "ethical_alignment": metrics.ethical_alignment,
                        "cognitive_coherence": metrics.cognitive_coherence
                    }
                )

            return {
                "success": True,
                "mesh_metrics": {
                    "success_rate": metrics.success_rate,
                    "resource_utilization": metrics.resource_utilization,
                    "mesh_stability": metrics.mesh_stability,
                    "ethical_alignment": metrics.ethical_alignment,
                    "cognitive_coherence": metrics.cognitive_coherence
                }
            }

        return {"success": False, "error": "Mesh optimization not available"}

    def create_system_audit(self) -> Dict[str, Any]:
        """
        Create a comprehensive system audit.

        Returns:
            Audit information
        """
        if not self.epoch_audit:
            raise ValueError("Epoch Audit System is not enabled")

        # Create a Phone Audit Scroll
        audit_info = self.epoch_audit.create_phone_audit_scroll()

        # Get agent performance metrics
        agent_metrics = {}
        if hasattr(self.strategy_agent, "get_performance_metrics"):
            agent_metrics["strategy_agent"] = self.strategy_agent.get_performance_metrics()

        # Combine audit information
        combined_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "audit_scroll": audit_info,
            "agent_metrics": agent_metrics,
            "trigger_stats": {
                "total_triggers": len(self.mesh_trigger.trigger_core.list_triggers())
                if self.mesh_trigger else 0
            }
        }

        # Log the audit
        self.epoch_audit.log_agent_event(
            agent_id=self.name,
            event="system_audit",
            note="System-wide audit performed",
            audit_summary={
                "timestamp": combined_info["timestamp"],
                "total_agents": len(agent_metrics),
                "total_triggers": combined_info["trigger_stats"]["total_triggers"]
            }
        )

        return combined_info

    def shutdown(self) -> None:
        """Shutdown the integrated system."""
        logger.info(f"Shutting down Integrated Agent System: {self.name}")

        # Create final audit
        if self.epoch_audit:
            try:
                self.create_system_audit()
            except Exception as e:
                logger.error(f"Error creating final audit: {e}")

        # Shutdown synchronizer
        try:
            self.synchronizer.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down synchronizer: {e}")

        logger.info("System shutdown complete")


# CLI interface for integrated system
def main():
    """Command line interface for the integrated system."""
    import argparse

    parser = argparse.ArgumentParser(description="EpochCore RAS Integrated System")
    parser.add_argument("--child-explanation", type=int,
                        help="Get explanation for child of specified age")
    parser.add_argument("--activate-trigger", help="Activate a system trigger")
    parser.add_argument("--audit", action="store_true", help="Create system audit")
    parser.add_argument("--optimize", action="store_true", help="Optimize system")

    args = parser.parse_args()

    # Create integrated system
    system = IntegratedAgentSystem()

    if args.child_explanation:
        explanation = asyncio.run(
            system.get_child_friendly_explanation(args.child_explanation))
        print(f"\n=== AI Explanation for {args.child_explanation}-year-old ===")
        print(explanation)

    elif args.activate_trigger:
        activation = asyncio.run(system.activate_system_trigger(args.activate_trigger))
        print(f"\n=== Trigger Activation: {args.activate_trigger} ===")
        print(f"Status: {activation.get('status')}")
        if activation.get("error"):
            print(f"Error: {activation.get('error')}")

    elif args.audit:
        audit_info = system.create_system_audit()
        print("\n=== System Audit ===")
        print(f"Timestamp: {audit_info.get('timestamp')}")
        print(f"Audit Scroll: {audit_info.get('audit_scroll', {}).get('file')}")
        print(
            f"Total Triggers: {audit_info.get('trigger_stats', {}).get('total_triggers')}")

    elif args.optimize:
        results = asyncio.run(system.optimize_system())
        print("\n=== System Optimization ===")
        print(f"Success: {results.get('success')}")
        if "mesh_metrics" in results:
            metrics = results["mesh_metrics"]
            print(f"Success Rate: {metrics.get('success_rate', 0):.2%}")
            print(f"Resource Utilization: {metrics.get('resource_utilization', 0):.2%}")
            print(f"Mesh Stability: {metrics.get('mesh_stability', 0):.2%}")
            print(f"Ethical Alignment: {metrics.get('ethical_alignment', 0):.2%}")
            print(f"Cognitive Coherence: {metrics.get('cognitive_coherence', 0):.2%}")

    else:
        parser.print_help()

    # Clean shutdown
    system.shutdown()


if __name__ == "__main__":
    main()
