"""
EpochCore RAS - Recursive Autonomy Innovations
Package containing all recursive autonomy innovation implementations
"""

from .recursive_agent_networks import create_recursive_agent_network, RecursiveAgentNetwork
from .meta_recursive_auditing import create_meta_recursive_auditor, MetaRecursiveAuditor
from .recursive_data_pipeline_optimization import create_recursive_data_pipeline_optimizer, RecursiveDataPipelineOptimizer
from .hierarchical_recursive_governance import create_hierarchical_recursive_governance, HierarchicalRecursiveGovernance
from .recursive_knowledge_graph import create_recursive_knowledge_graph, RecursiveKnowledgeGraph

# Import stub innovations (will be created by setup script if not present)
try:
    from .autonomous_simulation_testing import create_autonomous_simulation_testing
    from .api_integration_discovery import create_api_integration_discovery
    from .autonomous_security_testing import create_autonomous_security_testing
    from .autonomous_ip_generation import create_autonomous_ip_generation
    from .talent_skill_network import create_talent_skill_network
    
    STUB_INNOVATIONS_AVAILABLE = True
except ImportError:
    STUB_INNOVATIONS_AVAILABLE = False

__all__ = [
    'create_recursive_agent_network',
    'RecursiveAgentNetwork',
    'create_meta_recursive_auditor',
    'MetaRecursiveAuditor',
    'create_recursive_data_pipeline_optimizer',
    'RecursiveDataPipelineOptimizer',
    'create_hierarchical_recursive_governance', 
    'HierarchicalRecursiveGovernance',
    'create_recursive_knowledge_graph',
    'RecursiveKnowledgeGraph'
]

if STUB_INNOVATIONS_AVAILABLE:
    __all__.extend([
        'create_autonomous_simulation_testing',
        'create_api_integration_discovery',
        'create_autonomous_security_testing',
        'create_autonomous_ip_generation',
        'create_talent_skill_network'
    ])


def get_all_innovations():
    """Get all available innovation creators"""
    innovations = {
        'recursive_agent_networks': create_recursive_agent_network,
        'meta_recursive_auditing': create_meta_recursive_auditor,
        'recursive_data_pipeline_optimization': create_recursive_data_pipeline_optimizer,
        'hierarchical_recursive_governance': create_hierarchical_recursive_governance,
        'recursive_knowledge_graph': create_recursive_knowledge_graph
    }
    
    if STUB_INNOVATIONS_AVAILABLE:
        innovations.update({
            'autonomous_simulation_testing': create_autonomous_simulation_testing,
            'api_integration_discovery': create_api_integration_discovery,
            'autonomous_security_testing': create_autonomous_security_testing,
            'autonomous_ip_generation': create_autonomous_ip_generation,
            'talent_skill_network': create_talent_skill_network
        })
    
    return innovations