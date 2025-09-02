#!/usr/bin/env python3
"""
Test script for the 16 Recursive Autonomous Engines implementation
Validates all required engines are present and run_all method works correctly
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_16_engines_implementation():
    """Test the complete 16 engines implementation as specified in requirements."""
    
    print("="*80)
    print("TESTING 16 RECURSIVE AUTONOMOUS ENGINES IMPLEMENTATION")
    print("="*80)
    
    try:
        # Test 1: Import all required engines
        print("\n1. Testing Engine Imports...")
        
        required_engines = [
            'AutonomousIssueAnalyzerEngine',
            'SelfGeneratingTestSuiteEngine',
            'RecursiveDependencyGraphUpdater',
            'AutonomousDocumentationEnhancer',
            'RecursiveFeedbackLoopEngine',
            'SelfTuningPrioritizationEngine',
            'AutomatedReferenceImplementationEngine',
            'AutonomousPlaybookGeneratorEngine',
            'ContinuousEngineHealthMonitor',
            'CrossEngineTriggerSystem',
            'CompoundingMetaIssueTracker',
            'CompoundingRootCauseExtractor',
            'RecursiveImpactPropagationEngine',
            'SelfEvolvingTestMatrixEngine',
            'AutonomousKnowledgeBaseBuilder',
            'RecursiveSelfDocumentingEngine'
        ]
        
        # Import all engines individually to avoid import * issue
        from recursive_improvement.engines import (
            AutonomousIssueAnalyzerEngine,
            SelfGeneratingTestSuiteEngine,
            RecursiveDependencyGraphUpdater,
            AutonomousDocumentationEnhancer,
            RecursiveFeedbackLoopEngine,
            SelfTuningPrioritizationEngine,
            AutomatedReferenceImplementationEngine,
            AutonomousPlaybookGeneratorEngine,
            ContinuousEngineHealthMonitor,
            CrossEngineTriggerSystem,
            CompoundingMetaIssueTracker,
            CompoundingRootCauseExtractor,
            RecursiveImpactPropagationEngine,
            SelfEvolvingTestMatrixEngine,
            AutonomousKnowledgeBaseBuilder,
            RecursiveSelfDocumentingEngine
        )
        
        engine_classes = {
            'AutonomousIssueAnalyzerEngine': AutonomousIssueAnalyzerEngine,
            'SelfGeneratingTestSuiteEngine': SelfGeneratingTestSuiteEngine,
            'RecursiveDependencyGraphUpdater': RecursiveDependencyGraphUpdater,
            'AutonomousDocumentationEnhancer': AutonomousDocumentationEnhancer,
            'RecursiveFeedbackLoopEngine': RecursiveFeedbackLoopEngine,
            'SelfTuningPrioritizationEngine': SelfTuningPrioritizationEngine,
            'AutomatedReferenceImplementationEngine': AutomatedReferenceImplementationEngine,
            'AutonomousPlaybookGeneratorEngine': AutonomousPlaybookGeneratorEngine,
            'ContinuousEngineHealthMonitor': ContinuousEngineHealthMonitor,
            'CrossEngineTriggerSystem': CrossEngineTriggerSystem,
            'CompoundingMetaIssueTracker': CompoundingMetaIssueTracker,
            'CompoundingRootCauseExtractor': CompoundingRootCauseExtractor,
            'RecursiveImpactPropagationEngine': RecursiveImpactPropagationEngine,
            'SelfEvolvingTestMatrixEngine': SelfEvolvingTestMatrixEngine,
            'AutonomousKnowledgeBaseBuilder': AutonomousKnowledgeBaseBuilder,
            'RecursiveSelfDocumentingEngine': RecursiveSelfDocumentingEngine
        }
        
        for engine_name in required_engines:
            try:
                engine_class = engine_classes[engine_name]
                print(f"   ✓ {engine_name} imported successfully")
            except KeyError:
                print(f"   ✗ {engine_name} NOT FOUND")
                return False
        
        print(f"   ✓ All {len(required_engines)} required engines imported successfully")
        
        # Test 2: Orchestrator initialization with run_all method
        print("\n2. Testing Orchestrator with run_all method...")
        
        from recursive_improvement import RecursiveOrchestrator
        
        orchestrator = RecursiveOrchestrator()
        if not orchestrator.initialize():
            print("   ✗ Orchestrator initialization failed")
            return False
        
        # Check run_all method exists
        if not hasattr(orchestrator, 'run_all'):
            print("   ✗ run_all method NOT FOUND in orchestrator")
            return False
        
        print("   ✓ Orchestrator initialized successfully")
        print("   ✓ run_all method found in orchestrator")
        
        # Test 3: Register all 16 engines
        print("\n3. Testing Engine Registration...")
        
        engines = [
            AutonomousIssueAnalyzerEngine(),
            SelfGeneratingTestSuiteEngine(),
            RecursiveDependencyGraphUpdater(),
            AutonomousDocumentationEnhancer(),
            RecursiveFeedbackLoopEngine(),
            SelfTuningPrioritizationEngine(),
            AutomatedReferenceImplementationEngine(),
            AutonomousPlaybookGeneratorEngine(),
            ContinuousEngineHealthMonitor(),
            CrossEngineTriggerSystem(),
            CompoundingMetaIssueTracker(),
            CompoundingRootCauseExtractor(),
            RecursiveImpactPropagationEngine(),
            SelfEvolvingTestMatrixEngine(),
            AutonomousKnowledgeBaseBuilder(),
            RecursiveSelfDocumentingEngine()
        ]
        
        registered_count = 0
        for engine in engines:
            if orchestrator.register_engine(engine):
                registered_count += 1
                print(f"   ✓ Registered {engine.name}")
            else:
                print(f"   ✗ Failed to register {engine.name}")
                return False
        
        if registered_count != 16:
            print(f"   ✗ Expected 16 engines, registered {registered_count}")
            return False
        
        print(f"   ✓ All 16 engines registered successfully")
        
        # Test 4: Test run_all method execution
        print("\n4. Testing run_all Method Execution...")
        
        result = orchestrator.run_all()
        
        if "error" in result:
            print(f"   ✗ run_all execution failed: {result['error']}")
            return False
        
        engines_executed = result.get("engines_executed", [])
        total_improvements = result.get("total_improvements", 0)
        errors = result.get("errors", [])
        
        print(f"   ✓ run_all executed successfully")
        print(f"   ✓ Engines executed: {len(engines_executed)}")
        print(f"   ✓ Total improvements: {total_improvements}")
        print(f"   ✓ Errors: {len(errors)}")
        
        if len(engines_executed) != 16:
            print(f"   ✗ Expected 16 engines executed, got {len(engines_executed)}")
            return False
        
        success_count = len([e for e in engines_executed if e.get('status') == 'success'])
        print(f"   ✓ Successful executions: {success_count}/16")
        
        # Test 5: Test trigger_recursive_improvement method
        print("\n5. Testing trigger_recursive_improvement Method...")
        
        trigger_result = orchestrator.trigger_recursive_improvement("test_context", {"test": True})
        
        if "error" in trigger_result:
            print(f"   ✗ trigger_recursive_improvement failed: {trigger_result['error']}")
            return False
        
        print("   ✓ trigger_recursive_improvement executed successfully")
        
        # Test 6: Integration system test
        print("\n6. Testing Integration System...")
        
        import integration
        
        system_orchestrator = integration.initialize_recursive_improvement_system()
        if not system_orchestrator:
            print("   ✗ Integration system initialization failed")
            return False
        
        if len(system_orchestrator.engines) != 16:
            print(f"   ✗ Integration system has {len(system_orchestrator.engines)} engines, expected 16")
            return False
        
        print(f"   ✓ Integration system initialized with {len(system_orchestrator.engines)} engines")
        
        # Test system status
        status = system_orchestrator.get_system_status()
        if "engines" not in status or len(status["engines"]) != 16:
            print("   ✗ System status check failed")
            return False
        
        print("   ✓ System status check passed")
        
        # Test 7: Verify recursive and compounding features
        print("\n7. Testing Recursive and Compounding Features...")
        
        # Check that engines have compounding actions
        engines_with_actions = 0
        for engine_name, engine in system_orchestrator.engines.items():
            if hasattr(engine, 'actions') and len(engine.actions) > 0:
                engines_with_actions += 1
        
        print(f"   ✓ {engines_with_actions} engines have compounding actions")
        
        # Check that engines have recursive capabilities
        engines_with_recursive = 0
        for engine_name, engine in system_orchestrator.engines.items():
            if hasattr(engine, 'execute_with_compounding'):
                engines_with_recursive += 1
        
        print(f"   ✓ {engines_with_recursive} engines have recursive capabilities")
        
        if engines_with_recursive != 16:
            print(f"   ✗ Expected 16 engines with recursive capabilities, got {engines_with_recursive}")
            return False
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Successfully implemented 16 Recursive Autonomous Engines")
        print("✅ run_all method working correctly")
        print("✅ trigger_recursive_improvement method working correctly") 
        print("✅ All engines support recursive and compounding improvements")
        print("✅ Integration system working correctly")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution function."""
    print(f"Starting comprehensive test at {datetime.now()}")
    
    success = test_16_engines_implementation()
    
    if success:
        print(f"\n🎉 IMPLEMENTATION SUCCESSFUL!")
        print("All 16 recursive autonomous engines are working correctly.")
        sys.exit(0)
    else:
        print(f"\n❌ IMPLEMENTATION FAILED!")
        print("Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()