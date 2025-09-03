#!/usr/bin/env python3
"""
Agent Registry Synchronization System
EpochCore RAS Repository Automation

Automated discovery, registration, and health monitoring of all 15 recursive improvement engines
plus system processes with backup & recovery capabilities.
"""

import json
import os
import time
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from recursive_improvement import RecursiveOrchestrator
from recursive_improvement.engines import *


class AgentRegistrySync:
    """Manages agent registry synchronization and health monitoring."""
    
    def __init__(self, config_path: str = "config/agent_registry.yaml"):
        self.config_path = config_path
        self.registry_path = "data/agent_registry.json"
        self.backup_dir = "backups/agent_registry"
        self.health_log_path = "logs/agent_health.json"
        
        # Ensure directories exist
        for path in [self.backup_dir, "data", "logs", "config"]:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize orchestrator
        self.orchestrator = None
        
        # Registry data
        self.registry = {
            "agents": {},
            "metadata": {
                "last_sync": None,
                "total_agents": 0,
                "active_agents": 0,
                "health_status": "unknown",
                "backup_count": 0
            }
        }
        
        # Load existing registry if present
        self.load_registry()
    
    def initialize_orchestrator(self) -> bool:
        """Initialize the recursive orchestrator if not already done."""
        if self.orchestrator is not None:
            return True
        
        try:
            from integration import initialize_recursive_improvement_system
            self.orchestrator = initialize_recursive_improvement_system()
            return self.orchestrator is not None
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            return False
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """Discover all available agents in the system."""
        agents = []
        
        # Initialize orchestrator first
        if not self.initialize_orchestrator():
            self.logger.error("Cannot discover agents without orchestrator")
            return agents
        
        # Get all registered engines from orchestrator
        if hasattr(self.orchestrator, 'engines'):
            for engine_name, engine in self.orchestrator.engines.items():
                agent_info = {
                    "id": engine_name,
                    "name": engine_name,
                    "type": "recursive_engine",
                    "class_name": engine.__class__.__name__,
                    "status": "active" if hasattr(engine, 'running') and engine.running else "inactive",
                    "discovered_at": datetime.now().isoformat(),
                    "capabilities": self.get_engine_capabilities(engine),
                    "health_score": self.calculate_health_score(engine),
                    "kpi_metrics": self.get_kpi_metrics(engine)
                }
                agents.append(agent_info)
        
        # Add system process agents
        system_agents = self.discover_system_processes()
        agents.extend(system_agents)
        
        self.logger.info(f"Discovered {len(agents)} agents")
        return agents
    
    def get_engine_capabilities(self, engine) -> List[str]:
        """Extract capabilities from an engine."""
        capabilities = []
        
        # Check for standard methods
        if hasattr(engine, 'execute_main_action'):
            capabilities.append('main_execution')
        if hasattr(engine, 'execute_pre_action'):
            capabilities.append('pre_action')
        if hasattr(engine, 'execute_with_compounding'):
            capabilities.append('compounding')
        if hasattr(engine, 'get_status'):
            capabilities.append('status_reporting')
        
        # Check engine-specific capabilities
        engine_name = engine.__class__.__name__.lower()
        if 'feedback' in engine_name:
            capabilities.extend(['feedback_analysis', 'system_auditing'])
        elif 'experimentation' in engine_name:
            capabilities.extend(['branch_management', 'experiment_pruning'])
        elif 'cloning' in engine_name:
            capabilities.extend(['agent_cloning', 'kpi_monitoring'])
        elif 'review' in engine_name:
            capabilities.extend(['code_analysis', 'pattern_learning'])
        elif 'refactor' in engine_name:
            capabilities.extend(['code_optimization', 'refactoring'])
        elif 'dependency' in engine_name:
            capabilities.extend(['security_scanning', 'update_management'])
        elif 'workflow' in engine_name:
            capabilities.extend(['workflow_analysis', 'optimization'])
        elif 'doc' in engine_name:
            capabilities.extend(['documentation_sync', 'content_management'])
        
        return capabilities
    
    def calculate_health_score(self, engine) -> float:
        """Calculate health score for an engine (0.0 to 1.0)."""
        try:
            base_score = 0.5
            
            # Check if running
            if hasattr(engine, 'running') and engine.running:
                base_score += 0.3
            
            # Check if it has status method and works
            if hasattr(engine, 'get_status'):
                try:
                    status = engine.get_status()
                    if isinstance(status, dict):
                        base_score += 0.1
                        if status.get('total_executions', 0) > 0:
                            base_score += 0.1
                except:
                    pass
            
            return min(1.0, base_score)
        except:
            return 0.0
    
    def get_kpi_metrics(self, engine) -> Dict[str, Any]:
        """Get KPI metrics for an engine."""
        try:
            if hasattr(engine, 'get_status'):
                status = engine.get_status()
                return {
                    "total_executions": status.get('total_executions', 0),
                    "last_execution": status.get('last_execution'),
                    "running": status.get('running', False),
                    "uptime": status.get('uptime', 0)
                }
        except:
            pass
        
        return {
            "total_executions": 0,
            "last_execution": None,
            "running": False,
            "uptime": 0
        }
    
    def discover_system_processes(self) -> List[Dict[str, Any]]:
        """Discover relevant system processes."""
        system_agents = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    
                    # Check for relevant processes
                    if any(keyword in cmdline.lower() for keyword in ['integration.py', 'dashboard.py', 'recursive']):
                        agent_info = {
                            "id": f"process_{proc_info['pid']}",
                            "name": proc_info['name'],
                            "type": "system_process",
                            "class_name": "SystemProcess",
                            "status": "active",
                            "discovered_at": datetime.now().isoformat(),
                            "capabilities": ["system_process"],
                            "health_score": 1.0,
                            "kpi_metrics": {
                                "pid": proc_info['pid'],
                                "cmdline": cmdline
                            }
                        }
                        system_agents.append(agent_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            self.logger.warning(f"Error discovering system processes: {e}")
        
        return system_agents
    
    def register_agents(self, agents: List[Dict[str, Any]]) -> int:
        """Register discovered agents in the registry."""
        registered_count = 0
        
        for agent in agents:
            agent_id = agent['id']
            self.registry['agents'][agent_id] = agent
            registered_count += 1
            self.logger.info(f"Registered agent: {agent_id}")
        
        # Update metadata
        self.registry['metadata'].update({
            'last_sync': datetime.now().isoformat(),
            'total_agents': len(self.registry['agents']),
            'active_agents': len([a for a in self.registry['agents'].values() if a['status'] == 'active']),
            'health_status': self.calculate_overall_health()
        })
        
        return registered_count
    
    def calculate_overall_health(self) -> str:
        """Calculate overall health status of the registry."""
        if not self.registry['agents']:
            return 'unknown'
        
        health_scores = [agent['health_score'] for agent in self.registry['agents'].values()]
        avg_health = sum(health_scores) / len(health_scores)
        
        if avg_health >= 0.8:
            return 'healthy'
        elif avg_health >= 0.5:
            return 'warning'
        else:
            return 'critical'
    
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor health of all registered agents."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "summary": {
                "total": 0,
                "healthy": 0,
                "warning": 0,
                "critical": 0
            }
        }
        
        # Re-check health of all agents
        if self.initialize_orchestrator():
            for agent_id, agent in self.registry['agents'].items():
                if agent['type'] == 'recursive_engine' and agent_id in self.orchestrator.engines:
                    engine = self.orchestrator.engines[agent_id]
                    health_score = self.calculate_health_score(engine)
                    kpi_metrics = self.get_kpi_metrics(engine)
                    
                    # Update agent data
                    self.registry['agents'][agent_id]['health_score'] = health_score
                    self.registry['agents'][agent_id]['kpi_metrics'] = kpi_metrics
                    
                    health_report['agents'][agent_id] = {
                        "health_score": health_score,
                        "status": agent['status'],
                        "kpi_metrics": kpi_metrics
                    }
                    
                    # Update summary
                    health_report['summary']['total'] += 1
                    if health_score >= 0.8:
                        health_report['summary']['healthy'] += 1
                    elif health_score >= 0.5:
                        health_report['summary']['warning'] += 1
                    else:
                        health_report['summary']['critical'] += 1
        
        # Save health report
        with open(self.health_log_path, 'w') as f:
            json.dump(health_report, f, indent=2)
        
        return health_report
    
    def create_backup(self) -> str:
        """Create a backup of the current registry."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"registry_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            with open(backup_path, 'w') as f:
                json.dump(self.registry, f, indent=2)
            
            self.registry['metadata']['backup_count'] = self.registry['metadata'].get('backup_count', 0) + 1
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return ""
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Cleanup old backup files."""
        if not os.path.exists(self.backup_dir):
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cleaned_count = 0
        
        try:
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        cleaned_count += 1
                        self.logger.info(f"Cleaned up old backup: {filename}")
        except Exception as e:
            self.logger.error(f"Error during backup cleanup: {e}")
        
        return cleaned_count
    
    def validate_registry(self) -> Dict[str, Any]:
        """Validate registry integrity."""
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {
                "total_agents": len(self.registry['agents']),
                "active_agents": 0,
                "engine_agents": 0,
                "system_agents": 0
            }
        }
        
        try:
            # Check required fields
            required_agent_fields = ['id', 'name', 'type', 'status', 'health_score']
            for agent_id, agent in self.registry['agents'].items():
                for field in required_agent_fields:
                    if field not in agent:
                        validation_report['errors'].append(f"Agent {agent_id} missing required field: {field}")
                        validation_report['is_valid'] = False
                
                # Update statistics
                if agent['status'] == 'active':
                    validation_report['statistics']['active_agents'] += 1
                
                if agent['type'] == 'recursive_engine':
                    validation_report['statistics']['engine_agents'] += 1
                elif agent['type'] == 'system_process':
                    validation_report['statistics']['system_agents'] += 1
            
            # Check if we have expected number of engines
            expected_engines = 15
            actual_engines = validation_report['statistics']['engine_agents']
            if actual_engines < expected_engines:
                validation_report['warnings'].append(f"Expected {expected_engines} engines, found {actual_engines}")
        
        except Exception as e:
            validation_report['errors'].append(f"Validation error: {str(e)}")
            validation_report['is_valid'] = False
        
        return validation_report
    
    def load_registry(self) -> bool:
        """Load existing registry from file."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    self.registry = json.load(f)
                self.logger.info("Loaded existing registry")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}")
        
        return False
    
    def save_registry(self) -> bool:
        """Save current registry to file."""
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2)
            self.logger.info("Saved registry to file")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")
            return False
    
    def full_sync(self) -> Dict[str, Any]:
        """Perform a complete synchronization cycle."""
        sync_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": "starting",
            "success": False,
            "agents_discovered": 0,
            "agents_registered": 0,
            "health_status": "unknown",
            "backup_created": False,
            "validation_passed": False
        }
        
        try:
            # Phase 1: Create backup
            sync_report['phase'] = 'backup'
            backup_path = self.create_backup()
            sync_report['backup_created'] = bool(backup_path)
            
            # Phase 2: Discover agents
            sync_report['phase'] = 'discovery'
            agents = self.discover_agents()
            sync_report['agents_discovered'] = len(agents)
            
            # Phase 3: Register agents
            sync_report['phase'] = 'registration'
            registered_count = self.register_agents(agents)
            sync_report['agents_registered'] = registered_count
            
            # Phase 4: Health monitoring
            sync_report['phase'] = 'health_monitoring'
            health_report = self.monitor_health()
            sync_report['health_status'] = self.registry['metadata']['health_status']
            
            # Phase 5: Validation
            sync_report['phase'] = 'validation'
            validation = self.validate_registry()
            sync_report['validation_passed'] = validation['is_valid']
            
            # Phase 6: Save registry
            sync_report['phase'] = 'saving'
            save_success = self.save_registry()
            
            # Phase 7: Cleanup
            sync_report['phase'] = 'cleanup'
            cleaned_backups = self.cleanup_old_backups()
            
            sync_report['phase'] = 'complete'
            sync_report['success'] = save_success and validation['is_valid']
            
        except Exception as e:
            sync_report['error'] = str(e)
            self.logger.error(f"Full sync failed: {e}")
        
        return sync_report
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the registry."""
        return {
            "registry_metadata": self.registry['metadata'],
            "agent_count": len(self.registry['agents']),
            "registry_file_exists": os.path.exists(self.registry_path),
            "backup_count": len(os.listdir(self.backup_dir)) if os.path.exists(self.backup_dir) else 0,
            "orchestrator_initialized": self.orchestrator is not None
        }


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Registry Synchronization")
    parser.add_argument('--sync', action='store_true', help='Perform full synchronization')
    parser.add_argument('--status', action='store_true', help='Get registry status')
    parser.add_argument('--validate', action='store_true', help='Validate registry integrity')
    parser.add_argument('--monitor', action='store_true', help='Monitor agent health')
    
    args = parser.parse_args()
    
    registry = AgentRegistrySync()
    
    if args.sync:
        result = registry.full_sync()
        print(json.dumps(result, indent=2))
    elif args.status:
        status = registry.get_status()
        print(json.dumps(status, indent=2))
    elif args.validate:
        validation = registry.validate_registry()
        print(json.dumps(validation, indent=2))
    elif args.monitor:
        health = registry.monitor_health()
        print(json.dumps(health, indent=2))
    else:
        print("Use --sync, --status, --validate, or --monitor")


if __name__ == "__main__":
    main()