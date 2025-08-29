#!/usr/bin/env python3
"""Unified block tests for the WorkflowOptimizerAgent class."""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, mock_open
import tempfile
import json
import os


class TestWorkflowOptimizerUnified:
    """Test cases for WorkflowOptimizerAgent using unified block testing."""

    def setup_method(self):
        """Set up test fixtures."""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from ai_agent.agents import WorkflowOptimizerAgent

        self.WorkflowOptimizerAgent = WorkflowOptimizerAgent

    def test_workflow_analysis_unified(self):
        """
        Unified block test for workflow analysis capabilities.
        Tests workflow parsing, metrics calculation, and bottleneck detection.
        """
        # Block 1: Test workflow parsing
        workflow_data = {
            "tasks": [
                {
                    "id": "task1",
                    "name": "Process Images",
                    "dependencies": [],
                    "duration": 60,
                    "resources": ["cpu", "memory"],
                },
                {
                    "id": "task2",
                    "name": "Generate Metadata",
                    "dependencies": ["task1"],
                    "duration": 30,
                    "resources": ["cpu"],
                },
                {
                    "id": "task3",
                    "name": "Update Database",
                    "dependencies": ["task2"],
                    "duration": 45,
                    "resources": ["io"],
                },
            ]
        }

        optimizer = self.WorkflowOptimizerAgent()
        analysis = optimizer.analyze_workflow(workflow_data)

        assert analysis["total_duration"] == 135
        assert analysis["critical_path"] == ["task1", "task2", "task3"]
        assert analysis["bottlenecks"] == ["task1"]  # Longest task

        # Block 2: Test resource analysis
        resource_usage = optimizer.analyze_resource_usage(workflow_data)
        assert "cpu" in resource_usage
        assert "memory" in resource_usage
        assert "io" in resource_usage
        assert resource_usage["cpu"] == 90  # task1 + task2
        assert resource_usage["memory"] == 60  # task1
        assert resource_usage["io"] == 45  # task3

        # Block 3: Test optimization suggestions
        suggestions = optimizer.get_optimization_suggestions(workflow_data)
        assert len(suggestions) > 0
        assert any(
            "parallel" in s.lower() for s in suggestions
        )  # Should suggest parallelization
        assert any(
            "resource" in s.lower() for s in suggestions
        )  # Should mention resource optimization

    def test_workflow_optimization_unified(self):
        """
        Unified block test for workflow optimization strategies.
        Tests optimization algorithms, parallel execution, and resource allocation.
        """
        # Block 1: Test parallel optimization
        workflow_data = {
            "tasks": [
                {
                    "id": "task1",
                    "name": "Task 1",
                    "dependencies": [],
                    "duration": 30,
                    "resources": ["cpu"],
                },
                {
                    "id": "task2",
                    "name": "Task 2",
                    "dependencies": [],
                    "duration": 45,
                    "resources": ["memory"],
                },
                {
                    "id": "task3",
                    "name": "Task 3",
                    "dependencies": ["task1", "task2"],
                    "duration": 20,
                    "resources": ["io"],
                },
            ]
        }

        optimizer = self.WorkflowOptimizerAgent()
        optimized = optimizer.optimize_parallel_execution(workflow_data)

        assert optimized["total_duration"] < 95  # Original sequential duration
        assert len(optimized["parallel_groups"]) >= 2  # Should identify parallel tasks
        assert optimized["parallel_duration"] == 65  # max(task1,task2) + task3

        # Block 2: Test resource optimization
        resource_constraints = {
            "cpu": 2,  # 2 CPU cores
            "memory": "4GB",
            "io": "100MB/s",
        }

        resource_optimized = optimizer.optimize_resource_allocation(
            workflow_data, resource_constraints
        )

        assert "allocations" in resource_optimized
        assert all(
            task["id"] in resource_optimized["allocations"]
            for task in workflow_data["tasks"]
        )
        assert resource_optimized[
            "feasible"
        ]  # Should be possible with given constraints

        # Block 3: Test cost optimization
        cost_factors = {"cpu_hour": 1.0, "memory_gb_hour": 0.5, "io_gb": 0.1}

        cost_optimized = optimizer.optimize_cost(workflow_data, cost_factors)

        assert "total_cost" in cost_optimized
        assert "cost_breakdown" in cost_optimized
        assert all(
            resource in cost_optimized["cost_breakdown"]
            for resource in ["cpu", "memory", "io"]
        )
        assert cost_optimized["cost_reduction_suggestions"]

    def test_workflow_monitoring_unified(self):
        """
        Unified block test for workflow monitoring and adaptation.
        Tests performance tracking, dynamic adjustment, and reporting.
        """
        # Block 1: Test performance monitoring
        workflow_data = {
            "tasks": [
                {"id": "task1", "name": "Task 1", "duration": 30, "dependencies": []}
            ]
        }

        optimizer = self.WorkflowOptimizerAgent()

        # Simulate task execution with timing
        with patch("time.time", side_effect=[0, 35]):  # 35 seconds actual duration
            stats = optimizer.monitor_task_execution("task1", workflow_data["tasks"][0])

        assert stats["planned_duration"] == 30
        assert stats["actual_duration"] == 35
        assert stats["deviation"] == 5
        assert not stats["within_expected"]

        # Block 2: Test adaptive optimization
        execution_history = [
            {"task_id": "task1", "planned": 30, "actual": 35},
            {"task_id": "task1", "planned": 30, "actual": 32},
            {"task_id": "task1", "planned": 30, "actual": 34},
        ]

        adapted = optimizer.adapt_workflow(workflow_data, execution_history)
        assert adapted["tasks"][0]["duration"] > 30  # Should increase duration estimate
        assert "confidence_factor" in adapted["tasks"][0]
        assert adapted["adaptation_reason"]

        # Block 3: Test reporting and analytics
        workflow_metrics = {
            "completed_tasks": 10,
            "failed_tasks": 2,
            "total_duration": 500,
            "resource_usage": {"cpu": 80, "memory": 70, "io": 45},
        }

        report = optimizer.generate_workflow_report(workflow_metrics)

        assert "success_rate" in report
        assert report["success_rate"] == 0.8  # 10/(10+2)
        assert "efficiency_metrics" in report
        assert "recommendations" in report
        assert report["resource_utilization"]
        assert all(
            metric in report["resource_utilization"]
            for metric in ["cpu", "memory", "io"]
        )
