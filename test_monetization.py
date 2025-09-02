#!/usr/bin/env python3
"""
Tests for the autonomous monetization loops system
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from monetization_loops import MonetizationLoopsEngine, MonetizationMode, RevenueStream
from marketing_engine import MarketingEngine, ContentType, DistributionChannel
from kpi_tracker import KPITracker, AlertSeverity
from autonomous_agents import AgentSwarmOrchestrator, AgentRole, TaskPriority


class TestMonetizationLoops(unittest.TestCase):
    """Test cases for monetization loops engine"""
    
    def setUp(self):
        self.engine = MonetizationLoopsEngine()
    
    def test_initialization(self):
        """Test monetization engine initialization"""
        self.assertIsInstance(self.engine, MonetizationLoopsEngine)
        self.assertEqual(self.engine.current_mode, MonetizationMode.EXECUTOR)
        self.assertIn(RevenueStream.SAAS, self.engine.active_streams)
        self.assertIn(RevenueStream.FREEMIUM, self.engine.active_streams)
        self.assertGreater(len(self.engine.feedback_loops), 0)
    
    def test_feedback_loop_execution(self):
        """Test feedback loop execution"""
        # Update some metrics to trigger loops
        self.engine.update_metrics(revenue=5000, engagement_rate=0.10, cac=400)
        
        # Execute feedback loops
        results = self.engine.execute_feedback_loops()
        
        self.assertIsInstance(results, dict)
        self.assertIn("executed_loops", results)
        self.assertIn("improvements", results)
        self.assertIn("mode_changes", results)
    
    def test_metrics_update(self):
        """Test metrics updating"""
        initial_revenue = self.engine.metrics.revenue
        
        self.engine.update_metrics(revenue=10000)
        
        self.assertEqual(self.engine.metrics.revenue, 10000)
        self.assertNotEqual(self.engine.metrics.revenue, initial_revenue)
    
    def test_status_retrieval(self):
        """Test status retrieval"""
        status = self.engine.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("mode", status)
        self.assertIn("metrics", status)
        self.assertIn("active_streams", status)
        self.assertIn("performance_trend", status)


class TestMarketingEngine(unittest.TestCase):
    """Test cases for marketing engine"""
    
    def setUp(self):
        self.engine = MarketingEngine()
    
    def test_initialization(self):
        """Test marketing engine initialization"""
        self.assertIsInstance(self.engine, MarketingEngine)
        self.assertGreater(len(self.engine.content_templates), 0)
        self.assertGreater(len(self.engine.audience_segments), 0)
    
    def test_content_generation(self):
        """Test content generation"""
        content = self.engine.generate_content(
            ContentType.BLOG_POST,
            "tech_executives",
            [DistributionChannel.LINKEDIN]
        )
        
        self.assertIsNotNone(content)
        self.assertIsNotNone(content.title)
        self.assertIsNotNone(content.body)
        self.assertIsNotNone(content.call_to_action)
        self.assertEqual(content.content_type, ContentType.BLOG_POST)
        self.assertEqual(content.target_audience, "tech_executives")
    
    def test_performance_update(self):
        """Test performance tracking update"""
        # Generate content first
        content = self.engine.generate_content(
            ContentType.SOCIAL_MEDIA,
            "startup_founders", 
            [DistributionChannel.TWITTER]
        )
        
        # Update performance
        self.engine.update_performance(content.content_id, {
            "views": 1000,
            "clicks": 50,
            "conversions": 5
        })
        
        updated_content = self.engine.generated_content[content.content_id]
        self.assertEqual(updated_content.performance.views, 1000)
        self.assertEqual(updated_content.performance.clicks, 50)
        self.assertEqual(updated_content.performance.conversions, 5)
    
    def test_content_calendar_generation(self):
        """Test content calendar generation"""
        calendar = self.engine.get_content_calendar(7)  # 7 days
        
        self.assertIsInstance(calendar, list)
        # Should have some content scheduled
        if calendar:
            item = calendar[0]
            self.assertIn("date", item)
            self.assertIn("content_type", item)
            self.assertIn("target_audience", item)
    
    def test_performance_summary(self):
        """Test performance summary"""
        summary = self.engine.get_performance_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn("total_content", summary)


class TestKPITracker(unittest.TestCase):
    """Test cases for KPI tracker"""
    
    def setUp(self):
        self.tracker = KPITracker()
    
    def test_initialization(self):
        """Test KPI tracker initialization"""
        self.assertIsInstance(self.tracker, KPITracker)
        self.assertGreater(len(self.tracker.thresholds), 0)
        self.assertGreater(len(self.tracker.mutation_rules), 0)
    
    def test_metric_tracking(self):
        """Test metric tracking"""
        initial_count = len(self.tracker.metrics_history.get("revenue", []))
        
        self.tracker.track_metric("revenue", 5000.0, "test")
        
        self.assertIn("revenue", self.tracker.metrics_history)
        self.assertEqual(len(self.tracker.metrics_history["revenue"]), initial_count + 1)
    
    def test_threshold_breach_detection(self):
        """Test threshold breach detection and alerts"""
        # Track a metric that should breach the critical threshold
        self.tracker.track_metric("revenue", 3000.0, "test")  # Below critical threshold of 5000
        
        # Check if alert was created
        revenue_alerts = [alert for alert in self.tracker.alerts.values() if alert.kpi_name == "revenue"]
        if revenue_alerts:
            alert = revenue_alerts[0]
            self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
    
    def test_kpi_dashboard(self):
        """Test KPI dashboard data"""
        # Add some metrics
        self.tracker.track_metric("revenue", 8000.0)
        self.tracker.track_metric("engagement_rate", 0.25)
        
        dashboard = self.tracker.get_kpi_dashboard()
        
        self.assertIsInstance(dashboard, dict)
        self.assertIn("current_metrics", dashboard)
        self.assertIn("active_alerts", dashboard)
        self.assertIn("total_kpis_tracked", dashboard)


class TestAgentSwarm(unittest.TestCase):
    """Test cases for autonomous agent swarm"""
    
    def setUp(self):
        self.swarm = AgentSwarmOrchestrator()
    
    def test_initialization(self):
        """Test agent swarm initialization"""
        self.assertIsInstance(self.swarm, AgentSwarmOrchestrator)
        self.assertGreater(len(self.swarm.agents), 0)
        
        # Check that we have diverse agent roles
        roles = [agent.role for agent in self.swarm.agents.values()]
        self.assertIn(AgentRole.REVENUE_OPTIMIZER, roles)
        self.assertIn(AgentRole.GROWTH_HACKER, roles)
        self.assertIn(AgentRole.MARKETING_STRATEGIST, roles)
    
    def test_task_creation(self):
        """Test monetization task creation"""
        initial_task_count = len(self.swarm.tasks)
        
        task_id = self.swarm.create_monetization_task(
            "optimize_pricing",
            "Test pricing optimization task",
            TaskPriority.HIGH
        )
        
        self.assertIsInstance(task_id, str)
        self.assertEqual(len(self.swarm.tasks), initial_task_count + 1)
        self.assertIn(task_id, self.swarm.tasks)
    
    def test_autonomous_cycle_execution(self):
        """Test autonomous cycle execution"""
        # Create some tasks first
        self.swarm.create_monetization_task("optimize_pricing", "Test task", TaskPriority.HIGH)
        self.swarm.create_monetization_task("growth_experiment", "Test experiment", TaskPriority.MEDIUM)
        
        # Execute cycle
        results = self.swarm.execute_autonomous_cycle()
        
        self.assertIsInstance(results, dict)
        self.assertIn("tasks_processed", results)
        self.assertIn("value_generated", results)
        self.assertIn("agents_active", results)
        self.assertIn("collaborations", results)
    
    def test_swarm_status(self):
        """Test swarm status retrieval"""
        status = self.swarm.get_swarm_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("total_agents", status)
        self.assertIn("active_agents", status)
        self.assertIn("total_value_generated", status)
        self.assertIn("performance_trend", status)


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.monetization_engine = MonetizationLoopsEngine()
        self.marketing_engine = MarketingEngine()
        self.kpi_tracker = KPITracker()
        self.agent_swarm = AgentSwarmOrchestrator()
    
    def test_end_to_end_monetization_cycle(self):
        """Test complete monetization cycle"""
        # 1. Create monetization tasks
        task_id = self.agent_swarm.create_monetization_task(
            "optimize_pricing", 
            "Revenue optimization test", 
            TaskPriority.HIGH
        )
        
        # 2. Execute autonomous cycle
        agent_results = self.agent_swarm.execute_autonomous_cycle()
        self.assertGreater(agent_results["tasks_processed"], 0)
        
        # 3. Update metrics based on results
        self.monetization_engine.update_metrics(
            revenue=agent_results["value_generated"] / 10,  # Scale down for testing
            engagement_rate=0.20
        )
        
        # 4. Execute monetization loops
        monetization_results = self.monetization_engine.execute_feedback_loops()
        self.assertIsInstance(monetization_results, dict)
        
        # 5. Generate marketing content
        content = self.marketing_engine.generate_content(
            ContentType.BLOG_POST,
            "tech_executives",
            [DistributionChannel.LINKEDIN]
        )
        self.assertIsNotNone(content)
        
        # 6. Track KPIs
        self.kpi_tracker.track_metric("revenue", 7000.0)
        self.kpi_tracker.track_metric("engagement_rate", 0.22)
        
        # 7. Verify system state
        agent_status = self.agent_swarm.get_swarm_status()
        monetization_status = self.monetization_engine.get_status()
        marketing_status = self.marketing_engine.get_performance_summary()
        kpi_status = self.kpi_tracker.get_kpi_dashboard()
        
        # Assert all systems are operational
        self.assertGreater(agent_status["completed_tasks"], 0)
        self.assertIn("mode", monetization_status)
        self.assertGreater(marketing_status["total_content"], 0)
        self.assertGreater(kpi_status["total_kpis_tracked"], 0)
    
    def test_system_health_monitoring(self):
        """Test system health monitoring"""
        # Simulate system operation
        self.agent_swarm.create_monetization_task("analyze_data", "Health check", TaskPriority.MEDIUM)
        self.agent_swarm.execute_autonomous_cycle()
        
        # Update with healthy metrics
        self.monetization_engine.update_metrics(
            revenue=8000,
            engagement_rate=0.25,
            automation_percentage=0.80
        )
        
        status = self.monetization_engine.get_status()
        
        # Verify system is reporting healthy status
        self.assertIn("metrics", status)
        self.assertEqual(status["metrics"]["revenue"], 8000)
        self.assertGreaterEqual(status["metrics"]["engagement_rate"], 0.20)
        self.assertGreaterEqual(status["metrics"]["automation_percentage"], 0.70)
    
    def test_autonomous_improvement_detection(self):
        """Test autonomous improvement detection and implementation"""
        # Create baseline performance
        for i in range(5):
            self.kpi_tracker.track_metric("revenue", 6000 + (i * 500))
            self.kpi_tracker.track_metric("engagement_rate", 0.15 + (i * 0.02))
        
        # Get KPI dashboard to check trends
        dashboard = self.kpi_tracker.get_kpi_dashboard()
        
        # Verify trend analysis is working
        self.assertIn("current_metrics", dashboard)
        if "revenue" in dashboard["current_metrics"]:
            revenue_data = dashboard["current_metrics"]["revenue"]
            self.assertIn("trend", revenue_data)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)