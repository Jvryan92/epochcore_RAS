import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from security_manager import SecurityManager
from agent_management import AgentManager, AgentManagementError
from enhanced_logging import EnhancedLogger


@pytest.fixture
def security_manager():
    return SecurityManager("test_secret_key")


@pytest.fixture
def agent_manager(tmp_path):
    return AgentManager(str(tmp_path))


@pytest.fixture
def enhanced_logger(tmp_path):
    return EnhancedLogger("test_logger", tmp_path)


class TestSecurityIntegration:
    def test_secure_agent_session(self, security_manager, agent_manager):
        # Create an agent
        agent = agent_manager.create_agent(["test_skill"], "test_agent")
        assert agent["did"], "Agent should have a DID"

        # Generate session
        session = security_manager.generate_session_token(agent["did"])
        assert session["token"], "Should generate session token"

        # Validate session
        assert security_manager.validate_session(
            agent["did"], session["token"]
        ), "Session should be valid"


class TestLoggingIntegration:
    def test_log_agent_events(self, enhanced_logger, agent_manager):
        # Create an agent
        agent = agent_manager.create_agent(["test_skill"], "test_agent")

        # Log event
        enhanced_logger.log_event(
            "agent_created", {"did": agent["did"], "skills": agent["skills"]}
        )

        # Verify log file exists
        log_file = Path(enhanced_logger.logger.handlers[0].baseFilename)
        assert log_file.exists(), "Log file should be created"
        assert log_file.stat().st_size > 0, "Log file should contain data"
