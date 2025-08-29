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
