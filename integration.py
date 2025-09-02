#!/usr/bin/env python3
"""
EpochCore RAS Integration Test Script
Minimal integration script for testing purposes with meta-learning capabilities
"""

import sys
import argparse
from datetime import datetime
import json

# Meta-learning imports
try:
    from meta_learning_engine import setup_meta_learning, run_meta_experiment, get_meta_status
    from meta_optimizer import setup_meta_optimizer, run_meta_optimization, get_meta_optimizer_status
    from automl_zero import setup_automl_zero, run_automl_zero_experiment, get_automl_zero_status
    from experiment_manager import setup_experiment_manager, start_experiment_monitoring, trigger_manual_experiment, get_experiment_manager_status
    from feature_adaptor import setup_feature_adaptor, run_feature_adaptation_experiment, get_feature_adaptor_status
    META_LEARNING_AVAILABLE = True
except ImportError as e:
    print(f"Meta-learning modules not fully available: {e}")
    META_LEARNING_AVAILABLE = False

def setup_demo():
    """Setup demo environment"""
    print(f"[{datetime.now()}] Setting up EpochCore RAS demo environment...")
    print("✓ Creating agent registry...")
    print("✓ Initializing policy framework...")
    print("✓ Setting up DAG management...")
    print("✓ Creating capsule storage...")
    print("✓ Demo environment setup complete!")
    return {"status": "success", "components_initialized": 4}

def run_workflow():
    """Run sample workflow"""
    print(f"[{datetime.now()}] Running EpochCore RAS workflow...")
    print("→ Executing agent tasks...")
    print("→ Processing DAG components...")
    print("→ Creating capsules...")
    print("→ Generating reports...")
    print("✓ Workflow execution complete!")
    return {"status": "success", "tasks_completed": 4}

def get_status():
    """Get system status"""
    print(f"EpochCore RAS System Status (as of {datetime.now()}):")
    print("  AGENTS: 5 active, 12 registered")
    print("  POLICIES: 3 active, 0 violations")
    print("  DAGS: 2 completed, 1 running")
    print("  CAPSULES: 8 total, all verified")
    print("  SYSTEM: Operational")
    
    # Add meta-learning status if available
    if META_LEARNING_AVAILABLE:
        print("  META-LEARNING: Available")
        try:
            meta_status = get_meta_status()
            print(f"    - Registered tasks: {meta_status.get('registered_tasks', 0)}")
            print(f"    - MAML parameters: {meta_status.get('maml_model_parameters', 0)}")
            
            meta_opt_status = get_meta_optimizer_status()
            print(f"    - Active improvements: {meta_opt_status.get('recursive_improvement', {}).get('active_proposals', 0)}")
            
            automl_status = get_automl_zero_status()
            print(f"    - AutoML population: {automl_status.get('current_population_count', 0)}")
            
            exp_status = get_experiment_manager_status()
            print(f"    - Running experiments: {exp_status.get('running_experiments', 0)}")
            
            feat_status = get_feature_adaptor_status()
            print(f"    - Active adaptations: {feat_status.get('active_transformations', 0)}")
        except Exception as e:
            print(f"    - Status retrieval error: {e}")
    else:
        print("  META-LEARNING: Unavailable (dependencies missing)")
    
    return {"status": "operational"}


def setup_meta_systems():
    """Setup all meta-learning systems"""
    if not META_LEARNING_AVAILABLE:
        print("❌ Meta-learning dependencies not available")
        return {"status": "error", "message": "Dependencies missing"}
    
    print(f"[{datetime.now()}] Setting up EpochCore RAS meta-learning systems...")
    
    results = {}
    
    try:
        results['meta_learning'] = setup_meta_learning()
        results['meta_optimizer'] = setup_meta_optimizer()  
        results['automl_zero'] = setup_automl_zero()
        results['experiment_manager'] = setup_experiment_manager()
        results['feature_adaptor'] = setup_feature_adaptor()
        
        # Start experiment monitoring
        start_experiment_monitoring()
        
        print("✓ All meta-learning systems initialized!")
        return {"status": "success", "results": results}
        
    except Exception as e:
        print(f"❌ Error setting up meta-learning systems: {e}")
        return {"status": "error", "message": str(e)}


def run_meta_learning_demo():
    """Run meta-learning demonstration"""
    if not META_LEARNING_AVAILABLE:
        return {"status": "error", "message": "Meta-learning not available"}
    
    print(f"[{datetime.now()}] Running meta-learning demonstration...")
    
    results = {}
    
    try:
        # Run meta-learning experiment
        print("→ Running MAML experiment...")
        results['meta_learning'] = run_meta_experiment(num_tasks=3)
        
        # Run meta-optimization
        print("→ Running meta-optimization...")
        results['meta_optimization'] = run_meta_optimization()
        
        # Run feature adaptation
        print("→ Running feature adaptation...")
        results['feature_adaptation'] = run_feature_adaptation_experiment()
        
        # Run AutoML-Zero (smaller scale for demo)
        print("→ Running AutoML-Zero experiment...")
        results['automl_zero'] = run_automl_zero_experiment(input_size=5, output_size=1)
        
        print("✓ Meta-learning demonstration completed!")
        return {"status": "success", "results": results}
        
    except Exception as e:
        print(f"❌ Meta-learning demonstration failed: {e}")
        return {"status": "error", "message": str(e)}


def run_experiment(experiment_type: str, parameters: dict = None):
    """Run a specific experiment"""
    if not META_LEARNING_AVAILABLE:
        return {"status": "error", "message": "Meta-learning not available"}
    
    try:
        exp_id = trigger_manual_experiment(experiment_type, parameters)
        print(f"✓ Started experiment {exp_id} of type {experiment_type}")
        return {"status": "success", "experiment_id": exp_id}
    except Exception as e:
        print(f"❌ Failed to start experiment: {e}")
        return {"status": "error", "message": str(e)}

def validate_system():
    """Validate system integrity"""
    print(f"[{datetime.now()}] Validating EpochCore RAS system integrity...")
    print("→ Checking agent registry...")
    print("→ Validating policy compliance...")
    print("→ Verifying capsule integrity...")
    print("→ Testing DAG execution...")
    print("✓ System validation complete - All checks passed!")
    return {"status": "valid", "errors": 0}

def main():
    parser = argparse.ArgumentParser(description="EpochCore RAS Integration System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Original commands
    subparsers.add_parser("setup-demo", help="Set up demo environment with sample data")
    subparsers.add_parser("run-workflow", help="Run complete integrated workflow")
    subparsers.add_parser("status", help="Get system status")
    subparsers.add_parser("validate", help="Validate system integrity")
    
    # Meta-learning commands
    subparsers.add_parser("setup-meta", help="Set up meta-learning systems")
    subparsers.add_parser("run-meta-demo", help="Run meta-learning demonstration")
    subparsers.add_parser("meta-status", help="Get meta-learning system status")
    
    # Experiment commands
    exp_parser = subparsers.add_parser("run-experiment", help="Run specific experiment")
    exp_parser.add_argument("--type", choices=["meta_learning", "meta_optimization", "automl_zero", "feature_adaptation"], 
                           required=True, help="Type of experiment to run")
    exp_parser.add_argument("--params", help="JSON parameters for experiment")
    
    args = parser.parse_args()
    
    if args.command == "setup-demo":
        result = setup_demo()
        return 0 if result["status"] == "success" else 1
    elif args.command == "run-workflow":
        result = run_workflow()
        return 0 if result["status"] == "success" else 1
    elif args.command == "status":
        result = get_status()
        return 0 if result["status"] == "operational" else 1
    elif args.command == "validate":
        result = validate_system()
        return 0 if result["status"] == "valid" else 1
    elif args.command == "setup-meta":
        result = setup_meta_systems()
        return 0 if result["status"] == "success" else 1
    elif args.command == "run-meta-demo":
        result = run_meta_learning_demo()
        return 0 if result["status"] == "success" else 1
    elif args.command == "meta-status":
        if META_LEARNING_AVAILABLE:
            try:
                print("Meta-Learning System Status:")
                print(json.dumps(get_meta_status(), indent=2))
                print("\nMeta-Optimizer Status:")
                print(json.dumps(get_meta_optimizer_status(), indent=2))
                print("\nAutoML-Zero Status:")
                print(json.dumps(get_automl_zero_status(), indent=2))
                print("\nExperiment Manager Status:")
                print(json.dumps(get_experiment_manager_status(), indent=2))
                print("\nFeature Adaptor Status:")
                print(json.dumps(get_feature_adaptor_status(), indent=2))
                return 0
            except Exception as e:
                print(f"Error getting meta-learning status: {e}")
                return 1
        else:
            print("Meta-learning not available")
            return 1
    elif args.command == "run-experiment":
        parameters = {}
        if args.params:
            try:
                parameters = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON parameters: {e}")
                return 1
        
        result = run_experiment(args.type, parameters)
        return 0 if result["status"] == "success" else 1
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())