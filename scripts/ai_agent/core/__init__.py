"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Core AI agent framework components."""

from .agent_manager import AgentManager
from .base_agent import BaseAgent
from .logger import setup_logging

__all__ = ["AgentManager", "BaseAgent", "setup_logging"]
