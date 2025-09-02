"""
All recursive improvement engines
"""

# Existing engines
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

# New autonomous engines (16 total as specified in requirements)
from .autonomous_issue_analyzer_engine import AutonomousIssueAnalyzerEngine
from .self_generating_test_suite_engine import SelfGeneratingTestSuiteEngine
from .recursive_dependency_graph_updater import RecursiveDependencyGraphUpdater
from .autonomous_documentation_enhancer_engine import AutonomousDocumentationEnhancer
from .self_tuning_prioritization_engine import SelfTuningPrioritizationEngine
from .automated_reference_implementation_engine import AutomatedReferenceImplementationEngine
from .continuous_engine_health_monitor import ContinuousEngineHealthMonitor
from .cross_engine_trigger_system import CrossEngineTriggerSystem
from .compounding_meta_issue_tracker import CompoundingMetaIssueTracker
from .compounding_root_cause_extractor import CompoundingRootCauseExtractor
from .recursive_impact_propagation_engine import RecursiveImpactPropagationEngine
from .self_evolving_test_matrix_engine import SelfEvolvingTestMatrixEngine
from .autonomous_knowledge_base_builder import AutonomousKnowledgeBaseBuilder
from .recursive_self_documenting_engine import RecursiveSelfDocumentingEngine

# Map to the required 16 engines from the problem statement
# Note: Some existing engines are renamed to match requirements
AutonomousPlaybookGeneratorEngine = SelfImprovingPlaybookGeneratorEngine  # Alias for compatibility

__all__ = [
    # Original 10 engines
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
    
    # The 16 specified engines from the problem statement
    'AutonomousIssueAnalyzerEngine',
    'SelfGeneratingTestSuiteEngine',
    'RecursiveDependencyGraphUpdater',
    'AutonomousDocumentationEnhancer',
    'SelfTuningPrioritizationEngine',
    'AutomatedReferenceImplementationEngine',
    'AutonomousPlaybookGeneratorEngine',  # Alias
    'ContinuousEngineHealthMonitor',
    'CrossEngineTriggerSystem',
    'CompoundingMetaIssueTracker',
    'CompoundingRootCauseExtractor',
    'RecursiveImpactPropagationEngine',
    'SelfEvolvingTestMatrixEngine',
    'AutonomousKnowledgeBaseBuilder',
    'RecursiveSelfDocumentingEngine'
]