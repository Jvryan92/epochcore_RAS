"""
Recursive Improvement Engines - Complete collection of autonomous improvement algorithms
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

# Recursive Autonomy Modules
from .ai_code_review_bot import AICodeReviewBotEngine
from .auto_refactor import AutoRefactorEngine
from .dependency_health import DependencyHealthEngine
from .workflow_auditor import WorkflowAuditorEngine
from .doc_updater import DocUpdaterEngine

# Complex Autonomy Innovation Engines - Advanced notification resolution
from .notification_intelligence_engine import NotificationIntelligenceEngine
from .autonomous_notification_resolver import AutonomousNotificationResolver
from .resolution_validator import ResolutionValidator
from .predictive_improvement_engine import PredictiveImprovementEngine

__all__ = [
    # Core 10 Recursive Engines
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
    
    # Recursive Autonomy Modules (5 additional)
    'AICodeReviewBotEngine',
    'AutoRefactorEngine',
    'DependencyHealthEngine',
    'WorkflowAuditorEngine',
    'DocUpdaterEngine',
    
    # Complex Autonomy Innovation Engines (4 additional)
    'NotificationIntelligenceEngine',
    'AutonomousNotificationResolver',
    'ResolutionValidator',
    'PredictiveImprovementEngine'
]