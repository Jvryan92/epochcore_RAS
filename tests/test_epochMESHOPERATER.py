"""
Test suite for epochMESHOPERATER - Comprehensive Mesh Operations Management System
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

try:
    import pytest
    from unittest.mock import patch, MagicMock
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock classes for basic testing when pytest is not available
    class patch:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return lambda *args, **kwargs: {"roi": 1.5, "capsule_id": "test", "goal": "test"}
        def __exit__(self, *args):
            pass
    
    class MagicMock:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return {"roi": 1.5, "capsule_id": "test", "goal": "test"}

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from epochMESHOPERATER import epochMESHOPERATER, MeshOperationStatus, MeshPerformanceMetrics


class TestEpochMESHOPERATER:
    """Test cases for epochMESHOPERATER functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mesh_operator = epochMESHOPERATER(
            ledger_dir=self.temp_dir,
            enable_analytics=True,
            enable_optimization=True,
            max_concurrent_operations=3
        )
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test epochMESHOPERATER initialization"""
        assert self.mesh_operator.ledger_dir == Path(self.temp_dir)
        assert self.mesh_operator.enable_analytics is True
        assert self.mesh_operator.enable_optimization is True
        assert self.mesh_operator.max_concurrent_operations == 3
        assert len(self.mesh_operator.active_operations) == 0
        assert len(self.mesh_operator.operation_history) == 0
    
    def test_single_goal_execution(self):
        """Test single mesh goal execution"""
        # Mock the underlying mesh network execution
        mock_result = {
            "capsule_id": "test-capsule",
            "goal": "drip.signal",
            "roi": 1.5,
            "revenue": 1000.0,
            "cost": 400.0,
            "margin": 600.0
        }
        
        with patch.object(self.mesh_operator.mesh_network, 'execute_mesh_goal', return_value=mock_result):
            result = self.mesh_operator.execute_single_goal("drip.signal")
            
            assert "operation_id" in result
            assert result["goal"] == "drip.signal"
            assert result["roi"] == 1.5
            assert "performance_metrics" in result
            assert "execution_time" in result
    
    def test_batch_goal_execution_sequential(self):
        """Test batch mesh goal execution in sequential mode"""
        mock_result = {
            "capsule_id": "test-capsule",
            "goal": "test-goal",
            "roi": 1.5,
            "revenue": 1000.0,
            "cost": 400.0,
            "margin": 600.0
        }
        
        with patch.object(self.mesh_operator.mesh_network, 'execute_mesh_goal', return_value=mock_result):
            goals = ["drip.signal", "pulse.sync"]
            result = self.mesh_operator.execute_batch_goals(goals, parallel=False)
            
            assert "batch_id" in result
            assert result["goals"] == goals
            assert len(result["results"]) == 2
            assert result["success_count"] == 2
            assert result["failure_count"] == 0
    
    def test_batch_goal_execution_parallel(self):
        """Test batch mesh goal execution in parallel mode"""
        mock_result = {
            "capsule_id": "test-capsule",
            "goal": "test-goal",
            "roi": 1.5,
            "revenue": 1000.0,
            "cost": 400.0,
            "margin": 600.0
        }
        
        with patch.object(self.mesh_operator.mesh_network, 'execute_mesh_goal', return_value=mock_result):
            goals = ["drip.signal", "pulse.sync", "weave.bind"]
            result = self.mesh_operator.execute_batch_goals(goals, parallel=True)
            
            assert "batch_id" in result
            assert result["goals"] == goals
            assert len(result["results"]) == 3
            assert result["success_count"] == 3
            assert result["failure_count"] == 0
    
    def test_mesh_health_status(self):
        """Test mesh health status checking"""
        health_status = self.mesh_operator.get_mesh_health_status()
        
        assert "timestamp" in health_status
        assert "overall_health" in health_status
        assert "mesh_health" in health_status
        assert "active_operations" in health_status
        
        # Check individual mesh health
        assert "drip" in health_status["mesh_health"]
        assert "pulse" in health_status["mesh_health"]
        assert "weave" in health_status["mesh_health"]
        
        # Check overall health structure
        overall = health_status["overall_health"]
        assert "score" in overall
        assert "status" in overall
        assert overall["status"] in ["healthy", "degraded", "critical"]
    
    def test_mesh_optimization(self):
        """Test mesh topology optimization"""
        optimization_result = self.mesh_operator.optimize_mesh_topology()
        
        assert "optimization_id" in optimization_result
        assert "current_metrics" in optimization_result
        assert "recommendations" in optimization_result
        assert "applied_optimizations" in optimization_result
        assert "execution_time" in optimization_result
        assert optimization_result["status"] == "completed"
    
    def test_emergency_recovery(self):
        """Test emergency mesh recovery"""
        recovery_result = self.mesh_operator.emergency_mesh_recovery()
        
        assert "recovery_id" in recovery_result
        assert "failed_meshes" in recovery_result
        assert "recovery_results" in recovery_result
        assert "execution_time" in recovery_result
        assert recovery_result["status"] == "completed"
    
    def test_operation_tracking(self):
        """Test operation tracking and status management"""
        # Register an operation
        operation_id = "test-op-123"
        self.mesh_operator._register_operation(operation_id, "test", {"param": "value"})
        
        # Check it's in active operations
        assert operation_id in self.mesh_operator.active_operations
        
        # Get operation status
        status = self.mesh_operator.get_operation_status(operation_id)
        assert status is not None
        assert status["operation_id"] == operation_id
        assert status["operation_type"] == "test"
        
        # Complete the operation
        self.mesh_operator._complete_operation(operation_id, {"result": "success"}, {"metric": 1.0})
        
        # Check it's moved to history
        assert operation_id not in self.mesh_operator.active_operations
        assert len(self.mesh_operator.operation_history) == 1
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        operation_id = "test-metrics"
        mesh_type = "test"
        goal = "test.goal"
        execution_time = 1.5
        result = {"roi": 2.0}
        
        metrics = self.mesh_operator._calculate_performance_metrics(
            operation_id, mesh_type, goal, execution_time, result
        )
        
        assert metrics.operation_id == operation_id
        assert metrics.mesh_type == mesh_type
        assert metrics.goal == goal
        assert metrics.execution_time == execution_time
        assert metrics.roi == 2.0
        assert metrics.success_rate == 1.0
        assert metrics.error_rate == 0.0
    
    def test_batch_metrics_calculation(self):
        """Test batch metrics calculation"""
        batch_id = "test-batch"
        goals = ["goal1", "goal2", "goal3"]
        results = [
            {"status": "success"},
            {"status": "success"}, 
            {"status": "failed"}
        ]
        execution_time = 2.0
        
        metrics = self.mesh_operator._calculate_batch_metrics(
            batch_id, goals, results, execution_time
        )
        
        assert metrics["batch_id"] == batch_id
        assert metrics["total_goals"] == 3
        assert metrics["successful_goals"] == 2
        assert metrics["failed_goals"] == 1
        assert metrics["success_rate"] == 2/3
        assert metrics["execution_time"] == execution_time
    
    def test_optimization_recommendations(self):
        """Test optimization recommendation generation"""
        # Test metrics below thresholds
        poor_metrics = {
            "avg_success_rate": 0.5,  # Below 0.85 threshold
            "avg_latency_p95": 600,   # Above 500 threshold
            "avg_roi": 1.0            # Below 1.5 threshold
        }
        
        recommendations = self.mesh_operator._generate_optimization_recommendations(poor_metrics)
        
        assert len(recommendations) == 3  # Should have 3 recommendations
        
        rec_types = [rec["type"] for rec in recommendations]
        assert "improve_reliability" in rec_types
        assert "reduce_latency" in rec_types
        assert "improve_efficiency" in rec_types
    
    def test_analytics_storage(self):
        """Test analytics data storage"""
        metrics = MeshPerformanceMetrics(
            operation_id="test-analytics",
            mesh_type="test",
            goal="test.goal",
            execution_time=1.0,
            success_rate=1.0,
            throughput=1.0,
            resource_efficiency=1.5,
            error_rate=0.0,
            latency_p95=100.0,
            roi=1.8,
            timestamp="2025-08-31T00:00:00"
        )
        
        # Store analytics
        self.mesh_operator._store_analytics(metrics)
        
        # Check file was created and contains data
        assert self.mesh_operator.analytics_file.exists()
        
        with open(self.mesh_operator.analytics_file, "r") as f:
            data = json.loads(f.read().strip())
            assert data["operation_id"] == "test-analytics"
            assert data["roi"] == 1.8


if __name__ == "__main__":
    # Run basic functionality test if pytest is not available
    print("🧪 Running epochMESHOPERATER tests...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        mesh_operator = epochMESHOPERATER(ledger_dir=temp_dir)
        
        # Test basic functionality
        print("✅ Initialization test passed")
        
        # Test health check
        health = mesh_operator.get_mesh_health_status()
        assert "overall_health" in health
        print("✅ Health check test passed")
        
        # Test optimization
        opt_result = mesh_operator.optimize_mesh_topology()
        assert "optimization_id" in opt_result
        print("✅ Optimization test passed")
        
        # Test analytics
        analytics = mesh_operator.get_performance_analytics()
        print("✅ Analytics test passed")
        
        print("🎉 All basic tests passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)