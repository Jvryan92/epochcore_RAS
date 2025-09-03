#!/usr/bin/env python3
"""
Agent Register Sync - EpochCore RAS
Synchronizes agent registries across the system and ensures continuity
"""

import os
import json
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Any
import psutil
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRegisterSync:
    """Agent Registry Synchronization System"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "agent_registry_config.yaml"
        self.registry_path = "agent_registry.json"
        self.backup_path = "agent_registry_backup"
        self.sync_log_path = "logs/agent_sync.log"
        
        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        self.registry = self._load_registry()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load agent registry configuration."""
        default_config = {
            "sync_interval": 300,  # 5 minutes
            "max_backups": 10,
            "agent_types": ["autonomous", "recursive", "mvp", "workflow"],
            "required_fields": ["agent_id", "type", "status", "kpis", "created_at"],
            "sync_targets": ["local", "remote"],
            "health_check_interval": 60,
            "auto_recovery": True
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                
        return default_config
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load current agent registry."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading registry: {e}")
                
        return {
            "agents": {},
            "last_sync": None,
            "version": "1.0",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_agents": 0,
                "active_agents": 0
            }
        }
    
    def sync_agent_registry(self) -> Dict[str, Any]:
        """Main agent registry synchronization."""
        logger.info("Starting agent registry synchronization...")
        
        try:
            # Backup current registry
            self._backup_registry()
            
            # Discover active agents
            active_agents = self._discover_agents()
            
            # Update registry
            sync_result = self._update_registry(active_agents)
            
            # Validate registry integrity
            validation_result = self._validate_registry()
            
            # Save updated registry
            self._save_registry()
            
            # Log sync event
            self._log_sync_event(sync_result)
            
            logger.info("Agent registry synchronization completed successfully")
            
            return {
                "status": "success",
                "agents_synced": len(active_agents),
                "total_agents": len(self.registry["agents"]),
                "validation_passed": validation_result["passed"],
                "sync_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent registry sync failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sync_timestamp": datetime.now().isoformat()
            }
    
    def _discover_agents(self) -> List[Dict[str, Any]]:
        """Discover active agents in the system."""
        active_agents = []
        
        # Check recursive improvement engines
        try:
            from recursive_improvement.orchestrator import RecursiveOrchestrator
            # This would interface with the actual orchestrator
            engines = [
                "feedback_loop_engine", "experimentation_tree_engine", 
                "self_cloning_mvp_agent", "asset_library_engine",
                "weekly_auto_debrief_bot", "kpi_mutation_engine",
                "autonomous_escalation_logic", "recursive_workflow_automation",
                "content_stack_tree", "self_improving_playbook_generator",
                "ai_code_review_bot", "auto_refactor", "dependency_health",
                "workflow_auditor", "doc_updater"
            ]
            
            for engine_id in engines:
                agent_data = {
                    "agent_id": engine_id,
                    "type": "recursive_engine",
                    "status": "active",
                    "kpis": self._get_agent_kpis(engine_id),
                    "created_at": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "capabilities": self._get_agent_capabilities(engine_id),
                    "health_score": 1.0
                }
                active_agents.append(agent_data)
                
        except ImportError:
            logger.warning("Recursive improvement system not available for agent discovery")
        
        # Check system processes for additional agents
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if any(keyword in ' '.join(proc.info['cmdline'] or []) 
                      for keyword in ['agent', 'bot', 'engine', 'daemon']):
                    
                    agent_id = f"process_agent_{proc.info['pid']}"
                    agent_data = {
                        "agent_id": agent_id,
                        "type": "process_agent",
                        "status": "active",
                        "kpis": {"uptime": proc.create_time()},
                        "created_at": datetime.fromtimestamp(proc.create_time()).isoformat(),
                        "last_seen": datetime.now().isoformat(),
                        "process_info": {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": proc.info['cmdline']
                        }
                    }
                    active_agents.append(agent_data)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return active_agents
    
    def _get_agent_kpis(self, agent_id: str) -> Dict[str, Any]:
        """Get KPI data for an agent."""
        return {
            "tasks_completed": 0,
            "success_rate": 1.0,
            "efficiency_score": 0.8,
            "last_activity": datetime.now().isoformat(),
            "improvement_count": 0
        }
    
    def _get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities for an agent."""
        capability_map = {
            "feedback_loop_engine": ["analysis", "mutation", "feedback"],
            "experimentation_tree_engine": ["experimentation", "branch_management", "optimization"],
            "self_cloning_mvp_agent": ["cloning", "kpi_monitoring", "scaling"],
            "ai_code_review_bot": ["code_review", "pattern_learning", "security_analysis"],
            "auto_refactor": ["code_refactoring", "smell_detection", "improvement"],
            "dependency_health": ["security_scanning", "update_management", "health_monitoring"],
            "workflow_auditor": ["workflow_analysis", "optimization", "security_auditing"],
            "doc_updater": ["documentation", "synchronization", "drift_detection"]
        }
        return capability_map.get(agent_id, ["general_processing"])
    
    def _update_registry(self, active_agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update registry with discovered agents."""
        updated_count = 0
        new_count = 0
        
        for agent_data in active_agents:
            agent_id = agent_data["agent_id"]
            
            if agent_id in self.registry["agents"]:
                # Update existing agent
                existing_agent = self.registry["agents"][agent_id]
                existing_agent.update({
                    "status": agent_data["status"],
                    "last_seen": agent_data["last_seen"],
                    "kpis": agent_data["kpis"]
                })
                updated_count += 1
            else:
                # Add new agent
                self.registry["agents"][agent_id] = agent_data
                new_count += 1
        
        # Update metadata
        self.registry["metadata"].update({
            "total_agents": len(self.registry["agents"]),
            "active_agents": len([a for a in self.registry["agents"].values() 
                                if a["status"] == "active"]),
            "last_sync": datetime.now().isoformat()
        })
        
        return {
            "updated": updated_count,
            "new": new_count,
            "total": len(active_agents)
        }
    
    def _validate_registry(self) -> Dict[str, Any]:
        """Validate registry integrity."""
        errors = []
        warnings = []
        
        for agent_id, agent_data in self.registry["agents"].items():
            # Check required fields
            for field in self.config["required_fields"]:
                if field not in agent_data:
                    errors.append(f"Agent {agent_id} missing required field: {field}")
            
            # Check agent type
            if agent_data.get("type") not in self.config["agent_types"]:
                warnings.append(f"Agent {agent_id} has unknown type: {agent_data.get('type')}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_agents": len(self.registry["agents"])
        }
    
    def _backup_registry(self):
        """Create backup of current registry."""
        if os.path.exists(self.registry_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_path}/agent_registry_{timestamp}.json"
            
            try:
                with open(self.registry_path, 'r') as src:
                    with open(backup_file, 'w') as dst:
                        dst.write(src.read())
                logger.info(f"Registry backed up to: {backup_file}")
            except Exception as e:
                logger.error(f"Backup failed: {e}")
        
        # Clean old backups
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self):
        """Remove old backup files."""
        try:
            backup_files = sorted([f for f in os.listdir(self.backup_path) 
                                 if f.startswith("agent_registry_")])
            
            while len(backup_files) > self.config["max_backups"]:
                old_backup = backup_files.pop(0)
                os.remove(os.path.join(self.backup_path, old_backup))
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def _save_registry(self):
        """Save updated registry to file."""
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2, default=str)
            logger.info("Registry saved successfully")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _log_sync_event(self, sync_result: Dict[str, Any]):
        """Log synchronization event."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "agent_registry_sync",
                "result": sync_result,
                "registry_stats": self.registry["metadata"]
            }
            
            with open(self.sync_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log sync event: {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get current registry status."""
        return {
            "total_agents": len(self.registry["agents"]),
            "active_agents": len([a for a in self.registry["agents"].values() 
                                if a["status"] == "active"]),
            "last_sync": self.registry.get("last_sync"),
            "registry_version": self.registry.get("version", "1.0"),
            "health_status": "healthy" if self._validate_registry()["passed"] else "degraded"
        }
    
    def force_agent_registration(self, agent_data: Dict[str, Any]) -> bool:
        """Force register an agent."""
        try:
            # Validate required fields
            for field in self.config["required_fields"]:
                if field not in agent_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            agent_id = agent_data["agent_id"]
            self.registry["agents"][agent_id] = agent_data
            self._save_registry()
            
            logger.info(f"Force registered agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Force registration failed: {e}")
            return False

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Registry Synchronization")
    parser.add_argument("--sync", action="store_true", help="Run synchronization")
    parser.add_argument("--status", action="store_true", help="Show registry status")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    sync_system = AgentRegisterSync(args.config)
    
    if args.sync:
        result = sync_system.sync_agent_registry()
        print(json.dumps(result, indent=2))
    elif args.status:
        status = sync_system.get_registry_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --sync to synchronize or --status to check registry status")

if __name__ == "__main__":
    main()