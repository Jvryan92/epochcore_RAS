import os
import unittest
from unittest.mock import patch
from scripts.ai_agent.core.system_optimizer import SystemOptimizer, OptimizationMesh


class TestSystemOptimizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_cas"
        os.makedirs(self.test_dir, exist_ok=True)
        self.optimizer = SystemOptimizer(self.test_dir)

    def tearDown(self):
        # Clean up test files
        for root, _, files in os.walk(self.test_dir):
            for f in files:
                os.remove(os.path.join(root, f))
        os.rmdir(self.test_dir)

    def test_component_registration(self):
        """Test component registration."""
        self.optimizer.register_component("test_component")
        self.assertIn("test_component", self.optimizer.components)

    def test_improvement_tracking(self):
        """Test improvement tracking with proofs."""
        self.optimizer.register_component("mesh_network")

        metrics = {
            "latency": {"before": 100, "after": 80},
            "throughput": {"before": 1000, "after": 1200},
        }

        changes = [
            {
                "type": "optimization",
                "target": "connection_pool",
                "action": "increase_capacity",
                "params": {"old": 100, "new": 150},
            }
        ]

        root = self.optimizer.improve_component("mesh_network", metrics, changes)

        self.assertIsNotNone(root)
        self.assertIn(root, self.optimizer.improvement_roots)

    def test_merkle_verification(self):
        """Test merkle root verification."""
        self.optimizer.register_component("cache")

        metrics = {"hit_rate": {"before": 0.75, "after": 0.85}}

        changes = [
            {
                "type": "parameter",
                "target": "ttl",
                "action": "update",
                "params": {"old": 300, "new": 600},
            }
        ]

        # Make multiple improvements
        roots = []
        for _ in range(3):
            root = self.optimizer.improve_component("cache", metrics, changes)
            roots.append(root)

        # Verify final system root
        system_root = self.optimizer.get_system_root()
        self.assertIsNotNone(system_root)

        # Verify roots are in improvement history
        for root in roots:
            self.assertIn(root, self.optimizer.improvement_roots)

    def test_invalid_component(self):
        """Test handling of unregistered component."""
        metrics = {"test": {"before": 1, "after": 2}}
        changes = [{"type": "test"}]

        root = self.optimizer.improve_component("invalid", metrics, changes)
        self.assertIsNone(root)


if __name__ == "__main__":
    unittest.main()
