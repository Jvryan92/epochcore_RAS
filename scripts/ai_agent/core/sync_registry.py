"""
Enhanced Agent Registry with synchronization support for the epochcore RAS system.
Provides agent discovery, health monitoring, and sync coordination.
"""

import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum


class AgentStatus(Enum):
    """Agent status states"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SYNCING = "syncing"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    role: str
    status: AgentStatus
    last_seen: datetime
    last_action: str
    sync_capabilities: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['last_seen'] = self.last_seen.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Create from dictionary (JSON deserialization)"""
        data = data.copy()
        data['status'] = AgentStatus(data['status'])
        data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        return cls(**data)


class SynchronizedAgentRegistry:
    """Enhanced agent registry with synchronization support"""
    
    def __init__(self, registry_path: str = "./archive/EPOCH5/agents/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("strategy_ai_agent.registry")
        self._lock = asyncio.Lock()
        
    async def load_registry(self) -> Dict[str, AgentInfo]:
        """Load agent registry from file (async safe)"""
        async with self._lock:
            if not self.registry_path.exists():
                return {}
                
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    
                # Convert to AgentInfo objects
                registry = {}
                for agent_id, agent_data in data.get('agents', {}).items():
                    try:
                        registry[agent_id] = AgentInfo.from_dict(agent_data)
                    except Exception as e:
                        self.logger.warning(f"Failed to load agent {agent_id}: {e}")
                
                return registry
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}")
                return {}
    
    async def save_registry(self, registry: Dict[str, AgentInfo]):
        """Save agent registry to file (async safe)"""
        async with self._lock:
            try:
                # Convert to serializable format
                data = {
                    "agents": {agent_id: info.to_dict() for agent_id, info in registry.items()},
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_agents": len(registry)
                }
                
                # Atomic write
                temp_path = self.registry_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                temp_path.replace(self.registry_path)
                self.logger.debug(f"Registry saved with {len(registry)} agents")
                
            except Exception as e:
                self.logger.error(f"Failed to save registry: {e}")
                raise
    
    async def register_agent(
        self, 
        agent_id: str,
        role: str = "unknown",
        status: AgentStatus = AgentStatus.ACTIVE,
        sync_capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Register an agent in the registry"""
        try:
            registry = await self.load_registry()
            
            agent_info = AgentInfo(
                agent_id=agent_id,
                role=role,
                status=status,
                last_seen=datetime.now(timezone.utc),
                last_action="registered",
                sync_capabilities=sync_capabilities or [],
                metadata=metadata or {}
            )
            
            registry[agent_id] = agent_info
            await self.save_registry(registry)
            
            self.logger.info(f"Registered agent: {agent_id} with role: {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    async def update_agent_status(
        self,
        agent_id: str, 
        status: AgentStatus,
        action: str = "status_update"
    ) -> bool:
        """Update agent status and last seen time"""
        try:
            registry = await self.load_registry()
            
            if agent_id not in registry:
                self.logger.warning(f"Cannot update unknown agent: {agent_id}")
                return False
            
            agent_info = registry[agent_id]
            agent_info.status = status
            agent_info.last_seen = datetime.now(timezone.utc)
            agent_info.last_action = action
            
            await self.save_registry(registry)
            self.logger.debug(f"Updated agent {agent_id} status to {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update agent {agent_id}: {e}")
            return False
    
    async def get_active_agents(self) -> List[str]:
        """Get list of currently active agent IDs"""
        try:
            registry = await self.load_registry()
            return [
                agent_id for agent_id, info in registry.items() 
                if info.status == AgentStatus.ACTIVE
            ]
        except Exception as e:
            self.logger.error(f"Failed to get active agents: {e}")
            return []
    
    async def get_agents_with_sync_capability(self, capability: str) -> List[str]:
        """Get agents that support a specific sync capability"""
        try:
            registry = await self.load_registry()
            return [
                agent_id for agent_id, info in registry.items()
                if capability in info.sync_capabilities and info.status == AgentStatus.ACTIVE
            ]
        except Exception as e:
            self.logger.error(f"Failed to get agents with capability {capability}: {e}")
            return []
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat (last seen time)"""
        return await self.update_agent_status(agent_id, AgentStatus.ACTIVE, "heartbeat")
    
    async def cleanup_stale_agents(self, max_age_hours: int = 24) -> int:
        """Remove agents that haven't been seen for a long time"""
        try:
            registry = await self.load_registry()
            cutoff_time = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
            
            stale_agents = []
            for agent_id, info in registry.items():
                if info.last_seen.timestamp() < cutoff_time:
                    stale_agents.append(agent_id)
            
            for agent_id in stale_agents:
                del registry[agent_id]
                self.logger.info(f"Removed stale agent: {agent_id}")
            
            if stale_agents:
                await self.save_registry(registry)
            
            return len(stale_agents)
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup stale agents: {e}")
            return 0
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            registry = await self.load_registry()
            
            status_counts = {}
            for status in AgentStatus:
                status_counts[status.value] = sum(
                    1 for info in registry.values() if info.status == status
                )
            
            return {
                "total_agents": len(registry),
                "status_breakdown": status_counts,
                "sync_capabilities": self._count_capabilities(registry),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get registry stats: {e}")
            return {"error": str(e)}
    
    def _count_capabilities(self, registry: Dict[str, AgentInfo]) -> Dict[str, int]:
        """Count sync capabilities across all agents"""
        capabilities = {}
        for info in registry.values():
            for cap in info.sync_capabilities:
                capabilities[cap] = capabilities.get(cap, 0) + 1
        return capabilities