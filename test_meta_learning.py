#!/usr/bin/env python3
"""
Test suite for EpochCore RAS Meta-Learning Components
"""

import unittest
import numpy as np
from datetime import datetime
import json
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import meta-learning components
try:
    from meta_learning_engine import (
        MetaLearningEngine, MAMLEngine, MetaRLAgent, SimpleMetaModel,
        setup_meta_learning, run_meta_experiment, get_meta_status
    )
    from meta_optimizer import (
        MetaOptimizer, RecursiveImprovementEngine, ImprovementStrategy,
        setup_meta_optimizer, run_meta_optimization, get_meta_optimizer_status
    )
    from automl_zero import (
        AutoMLZeroEngine, ProgramGenerator, FitnessEvaluator, OperationType,
        setup_automl_zero, run_automl_zero_experiment, get_automl_zero_status
    )
    from experiment_manager import (
        ExperimentManager, ExperimentType, ExperimentStatus, TriggerCondition,
        setup_experiment_manager, get_experiment_manager_status
    )
    from feature_adaptor import (
        AdaptationEngine, FeatureSelector, FeatureScaler, AdaptationType,
        setup_feature_adaptor, get_feature_adaptor_status
    )
    META_LEARNING_AVAILABLE = True
except ImportError as e:
    print(f"Meta-learning components not available: {e}")
    META_LEARNING_AVAILABLE = False


class TestMetaLearningEngine(unittest.TestCase):
    """Test meta-learning engine functionality"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
        self.engine = MetaLearningEngine()
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine.maml_engine)
        self.assertIsNotNone(self.engine.meta_rl_agent)
        self.assertEqual(len(self.engine.task_registry), 0)
    
    def test_synthetic_task_creation(self):
        """Test synthetic task creation"""
        task = self.engine.create_synthetic_task("regression")
        self.assertEqual(task.task_type, "regression")
        self.assertIn('X', task.support_data)
        self.assertIn('y', task.support_data)
    
    def test_task_registration(self):
        """Test task registration"""
        task = self.engine.create_synthetic_task("regression")
        self.engine.register_task(task)
        self.assertEqual(len(self.engine.task_registry), 1)
        self.assertIn(task.task_id, self.engine.task_registry)
    
    def test_meta_learning_cycle(self):
        """Test complete meta-learning cycle"""
        result = self.engine.run_meta_learning_cycle(num_tasks=3)
        
        self.assertIn('num_tasks', result)
        self.assertEqual(result['num_tasks'], 3)
        self.assertIsNotNone(result['maml_loss'])
        self.assertGreater(len(self.engine.performance_history), 0)
    
    def test_status_retrieval(self):
        """Test status retrieval"""
        status = self.engine.get_meta_learning_status()
        
        self.assertEqual(status['status'], 'operational')
        self.assertIn('registered_tasks', status)
        self.assertIn('maml_model_parameters', status)


class TestMetaOptimizer(unittest.TestCase):
    """Test meta-optimizer functionality"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
        self.optimizer = MetaOptimizer()
    
    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly"""
        self.assertIsNotNone(self.optimizer.recursive_engine)
        self.assertEqual(len(self.optimizer.optimization_history), 0)
    
    def test_improvement_proposal_generation(self):
        """Test improvement proposal generation"""
        engine = self.optimizer.recursive_engine
        proposals = engine.generate_improvement_proposals([ImprovementStrategy.HYPERPARAMETER_OPTIMIZATION])
        
        self.assertGreater(len(proposals), 0)
        for proposal in proposals:
            self.assertIsNotNone(proposal.proposal_id)
            self.assertIsNotNone(proposal.description)
            self.assertLessEqual(proposal.risk_level, engine.max_risk_threshold)
    
    def test_safety_checks(self):
        """Test safety check mechanisms"""
        engine = self.optimizer.recursive_engine
        
        # Test safety check initialization
        self.assertGreater(len(engine.safety_checks), 0)
        
        # All safety checks should be callable
        for check in engine.safety_checks:
            self.assertTrue(callable(check.check_function))
    
    def test_meta_optimization_cycle(self):
        """Test complete meta-optimization cycle"""
        result = self.optimizer.run_meta_optimization()
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('improvement_cycle_result', result)
        self.assertGreater(len(self.optimizer.optimization_history), 0)


class TestAutoMLZero(unittest.TestCase):
    """Test AutoML-Zero functionality"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
        self.engine = AutoMLZeroEngine(population_size=10, max_generations=5)  # Small for testing
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertEqual(self.engine.population_size, 10)
        self.assertEqual(self.engine.max_generations, 5)
        self.assertIsNotNone(self.engine.generator)
        self.assertIsNotNone(self.engine.evaluator)
    
    def test_program_generation(self):
        """Test program generation"""
        program = self.engine.generator.generate_random_program(input_size=5, output_size=1)
        
        self.assertIsNotNone(program.program_id)
        self.assertEqual(program.input_size, 5)
        self.assertEqual(program.output_size, 1)
        self.assertGreater(len(program.operations), 0)
    
    def test_population_initialization(self):
        """Test population initialization"""
        self.engine.initialize_population(input_size=5, output_size=1)
        
        self.assertEqual(len(self.engine.population), self.engine.population_size)
        for program in self.engine.population:
            self.assertEqual(program.input_size, 5)
            self.assertEqual(program.output_size, 1)
    
    def test_synthetic_data_generation(self):
        """Test synthetic data generation"""
        train_data, test_data = self.engine.generate_synthetic_data(n_samples=50)
        
        train_x, train_y = train_data
        test_x, test_y = test_data
        
        self.assertEqual(train_x.shape[0], 25)  # Half for train
        self.assertEqual(test_x.shape[0], 25)   # Half for test
        self.assertEqual(train_x.shape[1], 10)  # Default input size


class TestExperimentManager(unittest.TestCase):
    """Test experiment manager functionality"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
        self.manager = ExperimentManager()
    
    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        self.assertIsNotNone(self.manager.triggers)
        self.assertIsNotNone(self.manager.performance_monitor)
        self.assertIsNotNone(self.manager.experiment_runner)
    
    def test_default_triggers(self):
        """Test default triggers are set up"""
        self.assertGreater(len(self.manager.triggers), 0)
        
        # Check specific triggers exist
        trigger_conditions = [t.condition for t in self.manager.triggers.values()]
        self.assertIn(TriggerCondition.PERFORMANCE_THRESHOLD, trigger_conditions)
        self.assertIn(TriggerCondition.SCHEDULE, trigger_conditions)
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        # Record some metrics
        self.manager.record_performance_metrics({
            'accuracy': 0.85,
            'loss': 0.15,
            'fitness': 0.8
        })
        
        self.assertGreater(len(self.manager.performance_monitor.metrics_history), 0)
    
    def test_manual_experiment_trigger(self):
        """Test manual experiment triggering"""
        exp_id = self.manager.trigger_experiment(
            ExperimentType.PERFORMANCE_BENCHMARK,
            {'test_param': 'value'}
        )
        
        self.assertIsNotNone(exp_id)
        # Give experiment time to start
        import time
        time.sleep(1)
        
        # Check experiment exists
        result = self.manager.get_experiment_by_id(exp_id)
        self.assertIsNotNone(result)


class TestFeatureAdaptor(unittest.TestCase):
    """Test feature adaptor functionality"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
        self.adaptor = AdaptationEngine()
    
    def test_adaptor_initialization(self):
        """Test adaptor initializes correctly"""
        self.assertIsNotNone(self.adaptor.selector)
        self.assertIsNotNone(self.adaptor.scaler)
        self.assertIsNotNone(self.adaptor.reducer)
        self.assertIsNotNone(self.adaptor.engineer)
    
    def test_feature_analysis(self):
        """Test feature analysis"""
        X = np.random.randn(100, 20)
        analysis = self.adaptor.analyze_features(X)
        
        self.assertEqual(analysis['feature_count'], 20)
        self.assertEqual(analysis['sample_count'], 100)
        self.assertIn('suggested_adaptations', analysis)
    
    def test_feature_selection(self):
        """Test feature selection"""
        X = np.random.randn(50, 15)
        y = (np.sum(X[:, :3], axis=1) > 0).astype(int)  # Binary classification target
        
        X_selected, selected_indices = self.adaptor.selector.select_features(X, y, k=5)
        
        self.assertEqual(X_selected.shape[1], 5)
        self.assertEqual(len(selected_indices), 5)
    
    def test_feature_scaling(self):
        """Test feature scaling"""
        X = np.random.randn(50, 10) * 100  # Large scale
        
        X_scaled, scaler = self.adaptor.scaler.scale_features(X)
        
        self.assertEqual(X_scaled.shape, X.shape)
        # Should be roughly normalized
        self.assertLess(abs(np.mean(X_scaled)), 0.1)
    
    def test_adaptation_experiment(self):
        """Test complete adaptation experiment"""
        result = self.adaptor.run_adaptation_experiment()
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('performance_evaluation', result)
        self.assertGreater(result['transformations_applied'], 0)


class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def setUp(self):
        if not META_LEARNING_AVAILABLE:
            self.skipTest("Meta-learning components not available")
    
    def test_setup_functions(self):
        """Test all setup functions work"""
        result1 = setup_meta_learning()
        self.assertEqual(result1['status'], 'success')
        
        result2 = setup_meta_optimizer()
        self.assertEqual(result2['status'], 'success')
        
        result3 = setup_automl_zero()
        self.assertEqual(result3['status'], 'success')
        
        result4 = setup_experiment_manager()
        self.assertEqual(result4['status'], 'success')
        
        result5 = setup_feature_adaptor()
        self.assertEqual(result5['status'], 'success')
    
    def test_status_functions(self):
        """Test all status functions work"""
        status1 = get_meta_status()
        self.assertIn('status', status1)
        
        status2 = get_meta_optimizer_status()
        self.assertIn('status', status2)
        
        status3 = get_automl_zero_status()
        self.assertIn('status', status3)
        
        status4 = get_experiment_manager_status()
        self.assertIn('status', status4)
        
        status5 = get_feature_adaptor_status()
        self.assertIn('status', status5)
    
    def test_experiment_functions(self):
        """Test experiment execution functions"""
        # Test meta-learning experiment
        result1 = run_meta_experiment(num_tasks=2)
        self.assertIn('tasks_processed', result1)
        
        # Test meta-optimization
        result2 = run_meta_optimization()
        self.assertEqual(result2['status'], 'completed')
        
        # Test AutoML-Zero (very small scale)
        result3 = run_automl_zero_experiment(input_size=3, output_size=1)
        self.assertEqual(result3['status'], 'completed')


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    if META_LEARNING_AVAILABLE:
        suite.addTest(unittest.makeSuite(TestMetaLearningEngine))
        suite.addTest(unittest.makeSuite(TestMetaOptimizer))
        suite.addTest(unittest.makeSuite(TestAutoMLZero))
        suite.addTest(unittest.makeSuite(TestExperimentManager))
        suite.addTest(unittest.makeSuite(TestFeatureAdaptor))
        suite.addTest(unittest.makeSuite(TestIntegration))
    else:
        print("⚠️ Meta-learning components not available - skipping tests")
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    exit(0 if result.wasSuccessful() else 1)