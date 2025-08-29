"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, TypedDict

class AgentConfig(TypedDict):
    did: str
    skills: List[str]
    status: str

class PolicyConfig(TypedDict):
    policy_id: str
    quorum: int
    rules: List[str]

class CeilingConfig(TypedDict):
    config_id: str
    service_tier: str
    performance_score: float

class TaskAssignment(TypedDict):
    task_id: str
    agent_did: str
    estimated_cost: float

class WorkflowResult(TypedDict):
    started_at: str
    steps: Dict[str, Any]
    errors: List[str]
    success: bool
