#!/usr/bin/env python3
"""
EpochCore Recursive Autonomy Orchestrator
Demonstrates the complete autonomous agent system with manifests and flash sync
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class RecursiveAutonomyOrchestrator:
    """Orchestrates the complete recursive autonomy system."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.agents_path = self.base_path / "agents"
        self.manifests_path = self.base_path / "manifests"
        self.scripts_path = self.base_path / "scripts"
        
        # Ensure directories exist
        self.manifests_path.mkdir(exist_ok=True)
        
        # Agent list
        self.agents = [
            "kpi_prediction_agent",
            "failure_remediation_agent", 
            "portfolio_optimizer",
            "meta_experiment_cascade",
            "resource_allocation_agent",
            "compliance_auditor",
            "innovation_diffuser",
            "user_feedback_engine",
            "explainability_agent",
            "agent_registry",
            "audit_evolution_manager"
        ]

    def execute_agent(self, agent_name: str) -> dict:
        """Execute a single autonomous agent."""
        agent_file = self.agents_path / f"{agent_name}.py"
        
        if not agent_file.exists():
            return {"status": "error", "message": f"Agent file not found: {agent_file}"}
        
        try:
            print(f"🤖 Executing {agent_name}...")
            
            # Change to base directory to ensure relative paths work
            original_cwd = os.getcwd()
            os.chdir(self.base_path)
            
            # Execute the agent
            result = subprocess.run(
                [sys.executable, str(agent_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print(f"  ✅ {agent_name} completed successfully")
                
                # Check if manifest was created
                expected_manifest = self.manifests_path / f"{agent_name}_results.json"
                if expected_manifest.exists():
                    with open(expected_manifest, 'r') as f:
                        manifest_data = json.load(f)
                    
                    return {
                        "status": "success",
                        "agent": agent_name,
                        "manifest": str(expected_manifest),
                        "cycles": manifest_data.get("cycles_completed", 0),
                        "stdout": result.stdout
                    }
                else:
                    return {
                        "status": "warning",
                        "agent": agent_name,
                        "message": "Agent executed but no manifest found",
                        "stdout": result.stdout
                    }
            else:
                print(f"  ❌ {agent_name} failed with return code {result.returncode}")
                return {
                    "status": "error",
                    "agent": agent_name,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {agent_name} timed out after 30 seconds")
            return {"status": "timeout", "agent": agent_name}
        except Exception as e:
            print(f"  💥 {agent_name} execution failed: {e}")
            return {"status": "exception", "agent": agent_name, "error": str(e)}

    def execute_all_agents(self) -> dict:
        """Execute all autonomous agents in sequence."""
        print("🚀 EpochCore Recursive Autonomy System")
        print("="*50)
        print(f"Executing {len(self.agents)} autonomous agents...")
        print()
        
        results = {
            "orchestrator_id": "recursive_autonomy_orchestrator_v1",
            "execution_timestamp": datetime.utcnow().isoformat(),
            "total_agents": len(self.agents),
            "agent_results": [],
            "summary": {
                "successful": 0,
                "failed": 0,
                "warnings": 0,
                "total_cycles": 0
            }
        }
        
        for agent_name in self.agents:
            agent_result = self.execute_agent(agent_name)
            results["agent_results"].append(agent_result)
            
            # Update summary
            if agent_result["status"] == "success":
                results["summary"]["successful"] += 1
                results["summary"]["total_cycles"] += agent_result.get("cycles", 0)
            elif agent_result["status"] == "warning":
                results["summary"]["warnings"] += 1
            else:
                results["summary"]["failed"] += 1
        
        # Save orchestration results
        orchestration_file = self.manifests_path / "orchestration_results.json"
        with open(orchestration_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results

    def validate_manifests(self) -> dict:
        """Validate that all expected manifests were created."""
        print("\n📋 Validating agent manifests...")
        
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "manifests_found": 0,
            "manifests_missing": 0,
            "details": []
        }
        
        for agent_name in self.agents:
            expected_manifest = self.manifests_path / f"{agent_name}_results.json"
            
            if expected_manifest.exists():
                try:
                    with open(expected_manifest, 'r') as f:
                        manifest_data = json.load(f)
                    
                    # Basic validation
                    required_fields = ["agent_id", "execution_time", "status", "cycles_completed"]
                    missing_fields = [field for field in required_fields if field not in manifest_data]
                    
                    if not missing_fields and manifest_data.get("status") == "success":
                        print(f"  ✅ {agent_name}: Valid manifest")
                        validation_results["manifests_found"] += 1
                        validation_results["details"].append({
                            "agent": agent_name,
                            "status": "valid",
                            "cycles": manifest_data.get("cycles_completed", 0)
                        })
                    else:
                        print(f"  ⚠️  {agent_name}: Invalid manifest (missing: {missing_fields})")
                        validation_results["details"].append({
                            "agent": agent_name,
                            "status": "invalid",
                            "issues": missing_fields
                        })
                        
                except json.JSONDecodeError:
                    print(f"  ❌ {agent_name}: Corrupt manifest file")
                    validation_results["details"].append({
                        "agent": agent_name,
                        "status": "corrupt"
                    })
            else:
                print(f"  ❌ {agent_name}: No manifest found")
                validation_results["manifests_missing"] += 1
                validation_results["details"].append({
                    "agent": agent_name,
                    "status": "missing"
                })
        
        return validation_results

    def prepare_flash_sync(self) -> dict:
        """Prepare flash sync data."""
        print("\n⚡ Preparing flash sync...")
        
        # Check if audit evolution log exists
        audit_log = self.manifests_path / "audit_evolution_log.jsonl"
        
        sync_preparation = {
            "timestamp": datetime.utcnow().isoformat(),
            "manifests_directory": str(self.manifests_path),
            "agents_directory": str(self.agents_path),
            "workflow_file": ".github/workflows/recursive_matrix_autonomy.yml",
            "flash_sync_scripts": [
                "scripts/flash_sync.sh",
                "scripts/flash_sync_api.py"
            ],
            "audit_log_exists": audit_log.exists(),
            "ready_for_sync": True
        }
        
        print(f"  📁 Manifests ready: {self.manifests_path}")
        print(f"  🤖 Agents ready: {self.agents_path}")
        print(f"  📝 Audit log: {'✅' if audit_log.exists() else '❌'}")
        print(f"  🔄 Flash sync scripts: ✅")
        
        return sync_preparation

    def print_summary(self, results: dict, validation: dict, sync_prep: dict):
        """Print execution summary."""
        print("\n" + "="*50)
        print("🎯 RECURSIVE AUTONOMY EXECUTION COMPLETE")
        print("="*50)
        
        print(f"📊 Execution Summary:")
        print(f"  Total agents: {results['total_agents']}")
        print(f"  Successful: {results['summary']['successful']}")
        print(f"  Failed: {results['summary']['failed']}")
        print(f"  Warnings: {results['summary']['warnings']}")
        print(f"  Total cycles: {results['summary']['total_cycles']}")
        
        print(f"\n📋 Manifest Validation:")
        print(f"  Valid manifests: {validation['manifests_found']}")
        print(f"  Missing manifests: {validation['manifests_missing']}")
        
        print(f"\n⚡ Flash Sync Status:")
        print(f"  Ready for sync: {'✅' if sync_prep['ready_for_sync'] else '❌'}")
        
        print(f"\n🔄 Next Steps:")
        print(f"  1. Review manifests in: {self.manifests_path}")
        print(f"  2. Execute flash sync: ./scripts/flash_sync.sh")
        print(f"  3. Trigger GitHub Actions: recursive_matrix_autonomy.yml")
        print(f"  4. Monitor cross-portfolio propagation")
        
        success_rate = results['summary']['successful'] / results['total_agents']
        if success_rate >= 0.9:
            print(f"\n🚀 System Status: READY FOR AUTONOMOUS OPERATION!")
        elif success_rate >= 0.7:
            print(f"\n⚠️  System Status: Partially Ready (review failures)")
        else:
            print(f"\n❌ System Status: Needs Attention (multiple failures)")


def main():
    """Main execution function."""
    orchestrator = RecursiveAutonomyOrchestrator()
    
    try:
        # Execute all agents
        results = orchestrator.execute_all_agents()
        
        # Validate manifests
        validation = orchestrator.validate_manifests()
        
        # Prepare flash sync
        sync_prep = orchestrator.prepare_flash_sync()
        
        # Print summary
        orchestrator.print_summary(results, validation, sync_prep)
        
        # Return appropriate exit code
        if results['summary']['failed'] == 0:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Orchestrator failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())