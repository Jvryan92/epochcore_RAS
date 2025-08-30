#!/usr/bin/env python3
"""
Tests for the Integrated Agent System

This file contains tests for the integrated agent system that connects
the Kids Friendly AI Guide, Epoch Audit, and Mesh Trigger components
with the existing EpochCore RAS agent architecture.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the system to test
from integrated_agent_system import (
    EpochAuditAdapter,
    IntegratedAgentSystem,
    KidsFriendlyAgentAdapter,
    MeshTriggerAdapter,
)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestKidsFriendlyAgentAdapter:
    """Tests for the Kids Friendly AI Guide Adapter."""

    @pytest.fixture
    def mock_agent_manager(self):
        """Mock agent manager."""
        with patch("integrated_agent_system.AgentManager") as mock:
            mock_instance = mock.return_value
            mock_instance.create_agent.return_value = {"did": "test_did"}
            yield mock_instance

    @pytest.fixture
    def mock_synchronizer(self):
        """Mock agent synchronizer."""
        with patch("integrated_agent_system.get_synchronizer") as mock:
            mock_instance = mock.return_value
            yield mock_instance

    @pytest.fixture
    def mock_guide(self):
        """Mock AI Friendly Guide."""
        with patch("integrated_agent_system.AIFriendlyGuide") as mock:
            mock_instance = mock.return_value
            mock_instance.get_ai_helper_explanation.return_value = "AI is your friend"
            mock_instance.get_age_appropriate_content.return_value = {
                "metaphor": "AI is like a helpful library",
                "stories": ["Once upon a time..."],
                "activities": ["Draw your AI friend"]
            }
            mock_instance.get_interactive_dialogue.return_value = [
                {"speaker": "Child", "text": "What is AI?"},
                {"speaker": "AI", "text": "I'm a helper!"}
            ]
            yield mock_instance

    def test_initialization(self, mock_agent_manager, mock_synchronizer, mock_guide):
        """Test adapter initialization."""
        adapter = KidsFriendlyAgentAdapter(agent_id="test_agent")

        assert adapter.agent_id == "test_agent"
        assert adapter.agent_did == "test_did"
        assert mock_agent_manager.create_agent.called
        assert mock_agent_manager.register_agent.called
        assert mock_synchronizer.register_agent.called

    def test_get_age_appropriate_explanation(self, mock_agent_manager, mock_synchronizer, mock_guide):
        """Test getting age-appropriate explanations."""
        adapter = KidsFriendlyAgentAdapter(agent_id="test_agent")

        result = adapter.get_age_appropriate_explanation(7)

        assert result == "AI is your friend"
        assert mock_guide.get_ai_helper_explanation.called
        assert mock_guide.get_ai_helper_explanation.call_args[0][0] == 7
        assert mock_agent_manager.log_heartbeat.called
        assert mock_agent_manager.update_agent_stats.called

    def test_get_content_for_child(self, mock_agent_manager, mock_synchronizer, mock_guide):
        """Test getting content for a child."""
        adapter = KidsFriendlyAgentAdapter(agent_id="test_agent")

        result = adapter.get_content_for_child(9)

        assert "metaphor" in result
        assert "stories" in result
        assert "activities" in result
        assert mock_guide.get_age_appropriate_content.called
        assert mock_guide.get_age_appropriate_content.call_args[0][0] == 9
        assert mock_agent_manager.log_heartbeat.called

    @pytest.mark.asyncio
    async def test_broadcast_activity(self, mock_agent_manager, mock_synchronizer, mock_guide):
        """Test broadcasting activities."""
        mock_async_sync = MagicMock()
        mock_async_sync.broadcast_message.return_value = True

        with patch("integrated_agent_system.get_async_synchronizer", return_value=mock_async_sync):
            adapter = KidsFriendlyAgentAdapter(agent_id="test_agent")

            result = await adapter.broadcast_activity([6, 8], "story")

            assert result is True
            assert mock_async_sync.broadcast_message.called
            call_args = mock_async_sync.broadcast_message.call_args[1]
            assert call_args["sender_id"] == "test_agent"
            assert call_args["message_type"] == "kids_friendly_activity"
            assert "age_range" in call_args["content"]
            assert call_args["content"]["age_range"] == [6, 8]


class TestEpochAuditAdapter:
    """Tests for the Epoch Audit Adapter."""

    @pytest.fixture
    def mock_agent_manager(self):
        """Mock agent manager."""
        with patch("integrated_agent_system.AgentManager") as mock:
            mock_instance = mock.return_value
            mock_instance.create_agent.return_value = {"did": "test_did"}
            yield mock_instance

    @pytest.fixture
    def mock_synchronizer(self):
        """Mock agent synchronizer."""
        with patch("integrated_agent_system.get_synchronizer") as mock:
            mock_instance = mock.return_value
            yield mock_instance

    @pytest.fixture
    def mock_audit(self):
        """Mock Epoch Audit."""
        with patch("integrated_agent_system.EpochAudit") as mock:
            mock_instance = mock.return_value
            mock_instance.log_event.return_value = {
                "event": "test_event",
                "timestamp": "2023-01-01T00:00:00Z",
                "agent_id": "test_agent"
            }
            mock_instance.enforce_alpha_ceiling.return_value = 100
            mock_instance.create_seal.return_value = {
                "file": "/tmp/test_seal.json",
                "hash": "abc123"
            }
            mock_instance.verify_seal.return_value = True
            mock_instance.phone_audit_scroll.return_value = {
                "file": "/tmp/audit_scroll.json",
                "entries": 10
            }
            mock_instance._get_timestamp.return_value = "2023-01-01T00:00:00Z"
            yield mock_instance

    def test_initialization(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test adapter initialization."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        assert adapter.agent_id == "test_agent"
        assert adapter.agent_did == "test_did"
        assert mock_agent_manager.create_agent.called
        assert mock_agent_manager.register_agent.called
        assert mock_synchronizer.register_agent.called
        assert mock_audit.schedule_audit.called

    def test_log_agent_event(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test logging agent events."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        result = adapter.log_agent_event(
            agent_id="some_agent",
            event="test_event",
            note="Test note",
            extra_field="extra_value"
        )

        assert result["event"] == "test_event"
        assert mock_audit.log_event.called
        call_args = mock_audit.log_event.call_args[1]
        assert call_args["event"] == "test_event"
        assert call_args["note"] == "Test note"
        assert call_args["agent_id"] == "some_agent"
        assert call_args["extra_field"] == "extra_value"
        assert mock_agent_manager.log_heartbeat.called

    def test_enforce_resource_limit(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test enforcing resource limits."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        # Test with no ceiling enforcement
        mock_audit.enforce_alpha_ceiling.return_value = 50
        result = adapter.enforce_resource_limit(50, "memory")
        assert result == 50

        # Test with ceiling enforcement
        mock_audit.enforce_alpha_ceiling.return_value = 100
        result = adapter.enforce_resource_limit(150, "memory", ceiling=100)
        assert result == 100
        assert mock_audit.enforce_alpha_ceiling.called

    def test_create_agent_seal(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test creating agent seals."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        result = adapter.create_agent_seal("some_agent", "test data")

        assert result["file"] == "/tmp/test_seal.json"
        assert mock_audit.create_seal.called

    def test_verify_agent_seal(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test verifying agent seals."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        result = adapter.verify_agent_seal(Path("/tmp/test_seal.json"), "test data")

        assert result is True
        assert mock_audit.verify_seal.called

    def test_create_phone_audit_scroll(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test creating phone audit scrolls."""
        adapter = EpochAuditAdapter(agent_id="test_agent", ledger_root=temp_data_dir)

        result = adapter.create_phone_audit_scroll()

        assert result["file"] == "/tmp/audit_scroll.json"
        assert mock_audit.phone_audit_scroll.called
        assert mock_agent_manager.log_heartbeat.called

    @pytest.mark.asyncio
    async def test_broadcast_audit_alert(self, mock_agent_manager, mock_synchronizer, mock_audit, temp_data_dir):
        """Test broadcasting audit alerts."""
        mock_async_sync = MagicMock()
        mock_async_sync.broadcast_message.return_value = True

        with patch("integrated_agent_system.get_async_synchronizer", return_value=mock_async_sync):
            adapter = EpochAuditAdapter(
                agent_id="test_agent", ledger_root=temp_data_dir)

            result = await adapter.broadcast_audit_alert(
                alert_type="test_alert",
                details={"level": "warning"}
            )

            assert result is True
            assert mock_async_sync.broadcast_message.called
            call_args = mock_async_sync.broadcast_message.call_args[1]
            assert call_args["sender_id"] == "test_agent"
            assert call_args["message_type"] == "audit_alert"
            assert call_args["content"]["alert_type"] == "test_alert"
            assert call_args["content"]["details"]["level"] == "warning"


class TestMeshTriggerAdapter:
    """Tests for the Mesh Trigger Adapter."""

    @pytest.fixture
    def mock_agent_manager(self):
        """Mock agent manager."""
        with patch("integrated_agent_system.AgentManager") as mock:
            mock_instance = mock.return_value
            mock_instance.create_agent.return_value = {"did": "test_did"}
            yield mock_instance

    @pytest.fixture
    def mock_synchronizer(self):
        """Mock agent synchronizer."""
        with patch("integrated_agent_system.get_synchronizer") as mock:
            mock_instance = mock.return_value
            yield mock_instance

    @pytest.fixture
    def mock_trigger(self):
        """Mock Mesh Trigger Core."""
        with patch("integrated_agent_system.MeshTriggerCore") as mock:
            mock_instance = mock.return_value
            mock_instance.register_trigger.return_value = {
                "id": "test_trigger",
                "description": "Test trigger",
                "resource_requirement": 50
            }
            mock_instance.register_handler.return_value = True
            mock_instance.create_trigger_seal.return_value = {
                "trigger_id": "test_trigger",
                "hash": "abc123",
                "timestamp": "2023-01-01T00:00:00Z"
            }
            mock_instance.verify_trigger_seal.return_value = True
            mock_instance.activate_trigger.return_value = {
                "status": "completed",
                "trigger_id": "test_trigger",
                "timestamp": "2023-01-01T00:00:00Z"
            }
            mock_instance.list_triggers.return_value = ["trigger1", "trigger2"]
            yield mock_instance

    def test_initialization(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test adapter initialization."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        assert adapter.agent_id == "test_agent"
        assert adapter.agent_did == "test_did"
        assert mock_agent_manager.create_agent.called
        assert mock_agent_manager.register_agent.called
        assert mock_synchronizer.register_agent.called
        # Check core triggers were registered
        assert mock_trigger.register_trigger.call_count >= 4

    def test_register_agent_trigger(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test registering agent triggers."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        result = adapter.register_agent_trigger(
            trigger_id="custom_trigger",
            description="Custom test trigger",
            resource_requirement=50,
            trigger_type="standard"
        )

        assert result["id"] == "test_trigger"
        assert mock_trigger.register_trigger.called
        call_args = mock_trigger.register_trigger.call_args[0]
        assert call_args[0] == "custom_trigger"
        assert call_args[1] == "Custom test trigger"
        assert call_args[2] == 50
        assert call_args[3] == "standard"
        assert mock_agent_manager.log_heartbeat.called

    def test_register_handler(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test registering handlers."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        def test_handler(context):
            return {"status": "ok"}

        result = adapter.register_handler("test_trigger", test_handler)

        assert result is True
        assert mock_trigger.register_handler.called
        call_args = mock_trigger.register_handler.call_args[0]
        assert call_args[0] == "test_trigger"
        assert callable(call_args[1])

    def test_create_trigger_seal(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test creating trigger seals."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        result = adapter.create_trigger_seal("test_trigger", {"test": True})

        assert result["trigger_id"] == "test_trigger"
        assert mock_trigger.create_trigger_seal.called
        call_args = mock_trigger.create_trigger_seal.call_args[0]
        assert call_args[0] == "test_trigger"
        assert call_args[1] == {"test": True}

    def test_verify_trigger_seal(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test verifying trigger seals."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        seal_data = {"trigger_id": "test_trigger", "hash": "abc123"}
        result = adapter.verify_trigger_seal(seal_data)

        assert result is True
        assert mock_trigger.verify_trigger_seal.called
        assert mock_trigger.verify_trigger_seal.call_args[0][0] == seal_data

    def test_activate_trigger(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test activating triggers."""
        adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

        result = adapter.activate_trigger(
            trigger_id="test_trigger",
            context={"test": True},
            verify_count=2
        )

        assert result["status"] == "completed"
        assert result["trigger_id"] == "test_trigger"
        assert mock_trigger.activate_trigger.called
        call_args = mock_trigger.activate_trigger.call_args[0]
        assert call_args[0] == "test_trigger"
        assert call_args[1] == {"test": True}
        assert call_args[2] == 2
        assert mock_agent_manager.log_heartbeat.called

    @pytest.mark.asyncio
    async def test_broadcast_trigger_activation(self, mock_agent_manager, mock_synchronizer, mock_trigger, temp_data_dir):
        """Test broadcasting trigger activations."""
        mock_async_sync = MagicMock()
        mock_async_sync.broadcast_message.return_value = True

        with patch("integrated_agent_system.get_async_synchronizer", return_value=mock_async_sync):
            adapter = MeshTriggerAdapter(agent_id="test_agent", base_dir=temp_data_dir)

            result = await adapter.broadcast_trigger_activation(
                trigger_id="test_trigger",
                context={"source": "test"}
            )

            assert result is True
            assert mock_async_sync.broadcast_message.called
            call_args = mock_async_sync.broadcast_message.call_args[1]
            assert call_args["sender_id"] == "test_agent"
            assert call_args["message_type"] == "trigger_activation"
            assert call_args["content"]["trigger_id"] == "test_trigger"
            assert call_args["content"]["context"]["source"] == "test"


class TestIntegratedAgentSystem:
    """Tests for the Integrated Agent System."""

    @pytest.fixture
    def mock_synchronizer(self):
        """Mock agent synchronizer."""
        with patch("integrated_agent_system.get_synchronizer") as mock:
            mock_instance = mock.return_value
            mock_instance.create_sync_point.return_value = "sync_123"
            yield mock_instance

    @pytest.fixture
    def mock_strategy_agent(self):
        """Mock StrategyDeck agent."""
        with patch("integrated_agent_system.StrategyDeckAgent") as mock:
            mock_instance = mock.return_value
            yield mock_instance

    @pytest.fixture
    def mock_kids_adapter(self):
        """Mock Kids Friendly adapter."""
        with patch("integrated_agent_system.KidsFriendlyAgentAdapter") as mock:
            mock_instance = mock.return_value
            mock_instance.agent_id = "kids_agent"
            mock_instance.get_age_appropriate_explanation.return_value = "AI is your friend"
            yield mock_instance

    @pytest.fixture
    def mock_audit_adapter(self):
        """Mock Epoch Audit adapter."""
        with patch("integrated_agent_system.EpochAuditAdapter") as mock:
            mock_instance = mock.return_value
            mock_instance.agent_id = "audit_agent"
            mock_instance.enforce_resource_limit.return_value = 10
            mock_instance.log_agent_event.return_value = {
                "event": "test_event",
                "timestamp": "2023-01-01T00:00:00Z"
            }
            mock_instance.create_phone_audit_scroll.return_value = {
                "file": "/tmp/audit_scroll.json",
                "entries": 10
            }
            yield mock_instance

    @pytest.fixture
    def mock_trigger_adapter(self):
        """Mock Mesh Trigger adapter."""
        with patch("integrated_agent_system.MeshTriggerAdapter") as mock:
            mock_instance = mock.return_value
            mock_instance.agent_id = "trigger_agent"
            mock_instance.create_trigger_seal.return_value = {
                "trigger_id": "test_trigger",
                "hash": "abc123"
            }
            mock_instance.verify_trigger_seal.return_value = True
            mock_instance.activate_trigger.return_value = {
                "status": "completed",
                "trigger_id": "test_trigger"
            }
            mock_instance.trigger_core.list_triggers.return_value = [
                "trigger1", "trigger2"]
            yield mock_instance

    def test_initialization(
        self,
        mock_synchronizer,
        mock_strategy_agent,
        mock_kids_adapter,
        mock_audit_adapter,
        mock_trigger_adapter,
        temp_data_dir
    ):
        """Test system initialization."""
        system = IntegratedAgentSystem(
            name="TestSystem",
            data_dir=temp_data_dir
        )

        assert system.name == "TestSystem"
        assert system.data_dir == Path(temp_data_dir)
        assert mock_synchronizer.register_message_handler.call_count >= 3
        assert mock_synchronizer.create_sync_point.called

    @pytest.mark.asyncio
    async def test_get_child_friendly_explanation(
        self,
        mock_synchronizer,
        mock_strategy_agent,
        mock_kids_adapter,
        mock_audit_adapter,
        mock_trigger_adapter,
        temp_data_dir
    ):
        """Test getting child-friendly explanations."""
        # Replace the constructor to avoid creating real objects
        with patch("integrated_agent_system.KidsFriendlyAgentAdapter", return_value=mock_kids_adapter):
            with patch("integrated_agent_system.EpochAuditAdapter", return_value=mock_audit_adapter):
                system = IntegratedAgentSystem(
                    name="TestSystem",
                    data_dir=temp_data_dir
                )

                result = await system.get_child_friendly_explanation(12)

                assert result == "AI is your friend"
                assert mock_audit_adapter.enforce_resource_limit.called
                assert mock_kids_adapter.get_age_appropriate_explanation.called
                assert mock_audit_adapter.log_agent_event.called

    @pytest.mark.asyncio
    async def test_activate_system_trigger(
        self,
        mock_synchronizer,
        mock_strategy_agent,
        mock_kids_adapter,
        mock_audit_adapter,
        mock_trigger_adapter,
        temp_data_dir
    ):
        """Test activating system triggers."""
        # Replace the constructor to avoid creating real objects
        with patch("integrated_agent_system.MeshTriggerAdapter", return_value=mock_trigger_adapter):
            with patch("integrated_agent_system.EpochAuditAdapter", return_value=mock_audit_adapter):
                system = IntegratedAgentSystem(
                    name="TestSystem",
                    data_dir=temp_data_dir
                )

                result = await system.activate_system_trigger(
                    "test_trigger",
                    {"test": True},
                    is_critical=True
                )

                assert result["status"] == "completed"
                assert mock_trigger_adapter.create_trigger_seal.called
                assert mock_trigger_adapter.verify_trigger_seal.called
                assert mock_trigger_adapter.activate_trigger.called
                assert mock_audit_adapter.log_agent_event.called

                # Test with invalid seal
                mock_trigger_adapter.verify_trigger_seal.return_value = False

                with pytest.raises(ValueError):
                    await system.activate_system_trigger(
                        "test_trigger",
                        {"test": True}
                    )

    def test_create_system_audit(
        self,
        mock_synchronizer,
        mock_strategy_agent,
        mock_kids_adapter,
        mock_audit_adapter,
        mock_trigger_adapter,
        temp_data_dir
    ):
        """Test creating system audits."""
        # Replace the constructor to avoid creating real objects
        with patch("integrated_agent_system.EpochAuditAdapter", return_value=mock_audit_adapter):
            with patch("integrated_agent_system.MeshTriggerAdapter", return_value=mock_trigger_adapter):
                system = IntegratedAgentSystem(
                    name="TestSystem",
                    data_dir=temp_data_dir
                )

                result = system.create_system_audit()

                assert "timestamp" in result
                assert "audit_scroll" in result
                assert result["audit_scroll"]["file"] == "/tmp/audit_scroll.json"
                assert mock_audit_adapter.create_phone_audit_scroll.called
                assert mock_audit_adapter.log_agent_event.called

                # Test with audit disabled
                with patch("integrated_agent_system.EpochAuditAdapter", return_value=None):
                    system = IntegratedAgentSystem(
                        name="TestSystem",
                        enable_epoch_audit=False,
                        data_dir=temp_data_dir
                    )

                    with pytest.raises(ValueError):
                        system.create_system_audit()

    @pytest.mark.asyncio
    async def test_optimize_system(
        self,
        mock_synchronizer,
        mock_strategy_agent,
        mock_kids_adapter,
        mock_audit_adapter,
        mock_trigger_adapter,
        temp_data_dir
    ):
        """Test system optimization."""
        # Set up mock for optimize_mesh_async
        mock_metrics = MagicMock()
        mock_metrics.success_rate = 0.95
        mock_metrics.resource_utilization = 0.85
        mock_metrics.mesh_stability = 0.90
        mock_metrics.ethical_alignment = 0.98
        mock_metrics.cognitive_coherence = 0.92

        mock_strategy_agent.optimize_mesh_async = MagicMock()
        mock_strategy_agent.optimize_mesh_async.return_value = mock_metrics

        # Replace the constructor to avoid creating real objects
        with patch("integrated_agent_system.MeshTriggerAdapter", return_value=mock_trigger_adapter):
            with patch("integrated_agent_system.EpochAuditAdapter", return_value=mock_audit_adapter):
                system = IntegratedAgentSystem(
                    name="TestSystem",
                    data_dir=temp_data_dir
                )

                result = await system.optimize_system()

                assert result["success"] is True
                assert "mesh_metrics" in result
                assert result["mesh_metrics"]["success_rate"] == 0.95
                assert mock_trigger_adapter.activate_trigger.called
                assert mock_strategy_agent.optimize_mesh_async.called

                # Test without optimize_mesh_async
                mock_strategy_agent.optimize_mesh_async = None

                result = await system.optimize_system()

                assert result["success"] is False
                assert "error" in result


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
