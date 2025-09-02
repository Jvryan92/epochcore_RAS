"""
All recursive improvement engines
"""

from .feedback_loop_engine import RecursiveFeedbackLoopEngine
from .experimentation_tree_engine import AutonomousExperimentationTreeEngine
from .cloning_agent_engine import SelfCloningMVPAgentEngine
from .asset_library_engine import AssetLibraryEngine
from .debrief_bot_engine import WeeklyAutoDebriefBotEngine
from .kpi_mutation_engine import KPIMutationEngine
from .escalation_logic_engine import AutonomousEscalationLogicEngine
from .workflow_automation_engine import RecursiveWorkflowAutomationEngine
from .content_stack_engine import ContentStackTreeEngine
from .playbook_generator_engine import SelfImprovingPlaybookGeneratorEngine

# New autonomous engines
from .issue_analyzer_engine import AutonomousIssueAnalyzerEngine
from .test_suite_engine import SelfGeneratingTestSuiteEngine
from .dependency_graph_engine import RecursiveDependencyGraphUpdater
from .documentation_enhancer_engine import AutonomousDocumentationEnhancer
from .health_monitor_engine import ContinuousEngineHealthMonitor
from .additional_engines import (
    CrossEngineTriggerSystem,
    CompoundingMetaIssueTracker,
    RecursiveImpactPropagationEngine,
    AutonomousKnowledgeBaseBuilder
)

__all__ = [
    # Existing engines
    'RecursiveFeedbackLoopEngine',
    'AutonomousExperimentationTreeEngine',
    'SelfCloningMVPAgentEngine',
    'AssetLibraryEngine',
    'WeeklyAutoDebriefBotEngine',
    'KPIMutationEngine',
    'AutonomousEscalationLogicEngine',
    'RecursiveWorkflowAutomationEngine',
    'ContentStackTreeEngine',
    'SelfImprovingPlaybookGeneratorEngine',
    # New autonomous engines
    'AutonomousIssueAnalyzerEngine',
    'SelfGeneratingTestSuiteEngine',
    'RecursiveDependencyGraphUpdater',
    'AutonomousDocumentationEnhancer',
    'ContinuousEngineHealthMonitor',
    'CrossEngineTriggerSystem',
    'CompoundingMetaIssueTracker',
    'RecursiveImpactPropagationEngine',
    'AutonomousKnowledgeBaseBuilder'
]