"""Tests for the monetization engine module."""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monetization_engine import (
        MonetizationEngine,
        TrancheExecutor,
        UserProfile,
        MonetizationMetrics,
        create_monetization_engine,
        create_tranche_executor,
    )

    MONETIZATION_AVAILABLE = True
except ImportError as e:
    MONETIZATION_AVAILABLE = False
    print(f"Monetization engine not available for testing: {e}")


@unittest.skipUnless(MONETIZATION_AVAILABLE, "Monetization engine not available")
class TestMonetizationEngine(unittest.TestCase):
    """Test cases for MonetizationEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_monetization_engine()

    def test_create_engine(self):
        """Test engine creation."""
        self.assertIsInstance(self.engine, MonetizationEngine)
        self.assertEqual(len(self.engine.users), 0)
        self.assertEqual(len(self.engine.metrics), 0)
        self.assertEqual(len(self.engine.tranches_executed), 0)

    def test_user_profile_creation(self):
        """Test user profile creation and retrieval."""
        user_id = "test_user_001"
        user = self.engine.get_user_profile(user_id)

        self.assertIsInstance(user, UserProfile)
        self.assertEqual(user.user_id, user_id)
        self.assertEqual(user.tier, "free")
        self.assertEqual(user.subscription_status, "none")
        self.assertEqual(user.referrals_made, 0)
        self.assertEqual(user.lifetime_value, 0.0)

    def test_analytics_event_tracking(self):
        """Test analytics event tracking."""
        user_id = "test_user_002"
        event_type = "workflow_completed"
        data = {"workflow_type": "test"}

        self.engine.track_analytics_event(event_type, user_id, data)

        # Check event was recorded
        self.assertEqual(len(self.engine.analytics_events), 1)
        event = self.engine.analytics_events[0]
        self.assertEqual(event["event_type"], event_type)
        self.assertEqual(event["user_id"], user_id)
        self.assertEqual(event["data"], data)

        # Check user metrics were updated
        user = self.engine.get_user_profile(user_id)
        self.assertEqual(user.usage_metrics[event_type], 1)

    def test_engagement_score_calculation(self):
        """Test engagement score calculation."""
        user_id = "test_user_003"

        # Track multiple events
        for i in range(5):
            self.engine.track_analytics_event("test_event", user_id, {"count": i})

        score = self.engine.calculate_engagement_score(user_id)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

        user = self.engine.get_user_profile(user_id)
        self.assertEqual(user.engagement_score, score)

    def test_metrics_update(self):
        """Test metrics updating."""
        strategy = "test_strategy"
        tranche = 1

        self.engine.update_metrics(
            strategy,
            tranche,
            conversion_rate=0.25,
            revenue_generated=100.0,
            users_converted=5,
        )

        key = f"{strategy}_tranche_{tranche}"
        self.assertIn(key, self.engine.metrics)

        metric = self.engine.metrics[key]
        self.assertEqual(metric.strategy, strategy)
        self.assertEqual(metric.tranche, tranche)
        self.assertEqual(metric.conversion_rate, 0.25)
        self.assertEqual(metric.revenue_generated, 100.0)
        self.assertEqual(metric.users_converted, 5)

    def test_get_status(self):
        """Test status retrieval."""
        # Add some test data
        self.engine.get_user_profile("user1")
        self.engine.get_user_profile("user2")
        self.engine.update_metrics("test", 1, revenue_generated=50.0)
        self.engine.tranches_executed.add(1)

        status = self.engine.get_status()

        self.assertEqual(status["total_users"], 2)
        self.assertEqual(status["tranches_executed"], [1])
        self.assertEqual(status["total_revenue"], 50.0)
        self.assertIn("last_updated", status)


@unittest.skipUnless(MONETIZATION_AVAILABLE, "Monetization engine not available")
class TestTrancheExecutor(unittest.TestCase):
    """Test cases for TrancheExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_monetization_engine()
        self.executor = create_tranche_executor(self.engine)

    def test_create_executor(self):
        """Test executor creation."""
        self.assertIsInstance(self.executor, TrancheExecutor)
        self.assertIs(self.executor.engine, self.engine)

    def test_tranche_1_execution(self):
        """Test Tranche 1: Scaffold core modules."""
        result = self.executor.execute_tranche_1()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tranche"], 1)
        self.assertEqual(result["modules_initialized"], 5)
        self.assertIn(1, self.engine.tranches_executed)
        self.assertEqual(len(result["strategies_scaffolded"]), 5)

    def test_tranche_2_execution(self):
        """Test Tranche 2: Analytics and event tracking."""
        result = self.executor.execute_tranche_2()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tranche"], 2)
        self.assertGreater(result["events_tracked"], 0)
        self.assertIn(2, self.engine.tranches_executed)

        # Check that analytics events were created
        self.assertGreater(len(self.engine.analytics_events), 0)
        self.assertGreater(len(self.engine.users), 0)

    def test_tranche_3_execution(self):
        """Test Tranche 3: Freemium gating."""
        # Set up some users first
        self.executor.execute_tranche_2()  # Creates users

        result = self.executor.execute_tranche_3()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tranche"], 3)
        self.assertGreaterEqual(result["users_evaluated"], 0)
        self.assertIn(3, self.engine.tranches_executed)

    def test_tranche_sequential_execution(self):
        """Test that tranches can be executed sequentially."""
        # Execute first few tranches
        results = []
        for i in range(1, 4):
            method = getattr(self.executor, f"execute_tranche_{i}")
            result = method()
            results.append(result)
            self.assertEqual(result["status"], "success")

        # Check all tranches were recorded
        for i in range(1, 4):
            self.assertIn(i, self.engine.tranches_executed)

    def test_execute_all_tranches(self):
        """Test executing all tranches."""
        result = self.executor.execute_all_tranches()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tranches_executed"], 10)
        self.assertGreaterEqual(result["total_revenue_generated"], 0)

        # Check all tranches were executed
        for i in range(1, 11):
            self.assertIn(i, self.engine.tranches_executed)

    def test_cross_strategy_triggers(self):
        """Test cross-strategy trigger functionality."""
        # Create user with conditions for triggers
        user = self.engine.get_user_profile("test_trigger_user")
        user.tier = "basic"
        user.subscription_status = "active"
        user.lifetime_value = 100.0
        user.engagement_score = 80.0
        user.referrals_made = 2

        # Test qualification checks
        self.assertTrue(
            self.executor._user_qualifies_for_trigger(user, "subscription", "bundling")
        )
        self.assertTrue(
            self.executor._user_qualifies_for_trigger(user, "referral", "upsell")
        )
        self.assertTrue(
            self.executor._user_qualifies_for_trigger(user, "bundling", "referral")
        )

    def test_revenue_calculation(self):
        """Test cross-strategy revenue calculations."""
        strategies = ["bundling", "upsell", "subscription", "referral", "freemium"]

        for strategy in strategies:
            revenue = self.executor._calculate_cross_strategy_revenue(strategy)
            self.assertGreater(revenue, 0)
            self.assertIsInstance(revenue, float)


@unittest.skipUnless(MONETIZATION_AVAILABLE, "Monetization engine not available")
class TestIntegration(unittest.TestCase):
    """Integration tests for the complete monetization system."""

    def test_full_system_workflow(self):
        """Test complete system workflow from creation to execution."""
        # Create system components
        engine = create_monetization_engine()
        executor = create_tranche_executor(engine)

        # Execute a subset of tranches
        for i in [1, 2, 3]:
            method = getattr(executor, f"execute_tranche_{i}")
            result = method()
            self.assertEqual(result["status"], "success")

        # Check system state
        status = engine.get_status()
        self.assertEqual(len(status["tranches_executed"]), 3)
        self.assertGreater(len(status["active_strategies"]), 0)

    def test_factory_functions(self):
        """Test factory functions work correctly."""
        engine = create_monetization_engine()
        executor = create_tranche_executor(engine)

        self.assertIsInstance(engine, MonetizationEngine)
        self.assertIsInstance(executor, TrancheExecutor)
        self.assertIs(executor.engine, engine)

    def test_config_loading(self):
        """Test configuration loading."""
        engine = create_monetization_engine()

        # Check default config exists
        self.assertIn("freemium", engine.config)
        self.assertIn("bundling", engine.config)
        self.assertIn("subscription", engine.config)
        self.assertIn("referral", engine.config)
        self.assertIn("upsell", engine.config)

        # Check config structure
        self.assertIn("usage_limits", engine.config["freemium"])
        self.assertIn("prices", engine.config["subscription"])


class TestWithoutMonetization(unittest.TestCase):
    """Test cases that should work even without monetization engine."""

    def test_import_protection(self):
        """Test that the system handles missing monetization gracefully."""
        # This test always runs to ensure import protection works
        self.assertTrue(
            True
        )  # Placeholder - the fact we got here means import protection worked


if __name__ == "__main__":
    unittest.main()
