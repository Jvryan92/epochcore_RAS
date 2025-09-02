"""
EpochCore RAS - Recursive Autonomy Innovations
Package containing all recursive autonomy innovation implementations
"""

from .recursive_agent_networks import create_recursive_agent_network, RecursiveAgentNetwork

__all__ = [
    'create_recursive_agent_network',
    'RecursiveAgentNetwork'
]