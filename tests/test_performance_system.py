#!/usr/bin/env python3
import os
import tempfile
import unittest
from scripts.ai_agent.core.performance_optimizer import PerformanceOptimizer
from scripts.ai_agent.core.mesh_metrics import MeshMetrics

class TestPerformanceSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_key = os.urandom(32)
        self.optimizer = PerformanceOptimizer(self.test_dir, self.test_key)
        self.metrics = MeshMetrics()

    def test_metrics_collection(self):
        # Test basic metrics recording
        self.metrics.record_latency(100.0)
        self.metrics.record_throughput(1000.0)
        self.metrics.record_error("timeout")
        self.metrics.record_pattern_hit("pattern1")
        
        stats = self.metrics.get_all_metrics()
        self.assertEqual(stats["latency"]["avg"], 100.0)
        self.assertEqual(stats["throughput"]["avg"], 1000.0)
        self.assertEqual(stats["errors"]["total"], 1)
        self.assertEqual(stats["patterns"]["total"], 1)

    def test_optimization_workflow(self):
        # Record some test data
        component = "test_component"
        current_params = {"batch_size": 100, "threads": 4}
        
        # Record multiple data points
        test_metrics = [
            {"batch_size": 100, "threads": 4, "latency": 150},
            {"batch_size": 200, "threads": 4, "latency": 120},
            {"batch_size": 200, "threads": 8, "latency": 90},
        ]
        
        for data in test_metrics:
            params = {"batch_size": data["batch_size"], "threads": data["threads"]}
            metrics = {"latency": data["latency"]}
            self.optimizer.record_parameters(component, params, metrics)
        
        # Test optimization suggestion
        suggested, confidence = self.optimizer.suggest_optimization(
            component, 
            current_params,
            "latency"
        )
        
        self.assertIsNotNone(suggested)
        self.assertGreater(confidence, 0.0)
        
        # Test applying optimization
        opt_id = self.optimizer.apply_optimization(
            component,
            current_params,
            suggested,
            0.2,  # 20% improvement
            confidence
        )
        
        # Verify optimization
        self.assertTrue(self.optimizer.verify_optimization(opt_id))
        
        # Check proof root
        root = self.optimizer.get_proof_root()
        self.assertIsNotNone(root)
        self.assertEqual(len(root), 64)  # SHA256 hex string

    def test_metrics_statistics(self):
        # Add varied latency samples
        latencies = [100, 110, 120, 130, 140, 150, 200, 300]
        for lat in latencies:
            self.metrics.record_latency(float(lat))
            
        stats = self.metrics.get_latency_stats()
        self.assertEqual(stats["min"], 100.0)
        self.assertEqual(stats["max"], 300.0)
        self.assertTrue(100 < stats["avg"] < 300)

    def test_error_tracking(self):
        errors = ["timeout", "timeout", "connection", "memory"]
        for err in errors:
            self.metrics.record_error(err)
            
        summary = self.metrics.get_error_summary()
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["by_type"]["timeout"], 2)

    def test_topology_changes(self):
        old_config = {"nodes": 3, "connections": 2}
        new_config = {"nodes": 4, "connections": 3}
        
        self.metrics.record_topology_change(
            old_config,
            new_config,
            "scale_up"
        )
        
        summary = self.metrics.get_topology_summary()
        self.assertEqual(summary["total_changes"], 1)
        self.assertEqual(summary["by_reason"]["scale_up"], 1)

if __name__ == '__main__':
    unittest.main()
