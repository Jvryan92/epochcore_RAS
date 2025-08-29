"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
"""Tests for pattern generation system with unified block testing methodology."""

import pytest
from pathlib import Path
import sys
from typing import List, Dict, Any
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.agents.patterns import (
    fractal_task_generator,
    adaptive_split_generator,
    quantum_state_generator,
    complexity_analyzer,
    pattern_optimizer
)
from ai_agent.agents.strategy_agent import StrategyTask, TaskType, TaskPattern


class TestPatternGeneration:
    """Test cases for pattern generation using unified block testing."""
    
    def test_fractal_pattern_unified(self):
        """
        Unified block test for fractal pattern generation.
        Tests pattern attributes, task generation, and recursive properties.
        """
        # Setup - Create a base task with fractal pattern
        base_task = StrategyTask(
            name="test_fractal",
            task_type=TaskType.RECURSIVE,
            metadata={
                'size': 2.0,
                'rotation': 0,
                'max_depth': 3,
                'branches': 4,
                'scale_factor': 0.5
            }
        )
        
        # Block 1: Test initial fractal generation
        tasks_depth0 = fractal_task_generator(base_task, None)
        assert len(tasks_depth0) == 4  # Should match branches
        for task in tasks_depth0:
            assert task.task_type == TaskType.RECURSIVE
            assert task.metadata['size'] == 1.0  # Original size * scale_factor
            assert 0 <= task.metadata['rotation'] < 360
            
        # Block 2: Test recursive generation and scaling
        task_depth1 = tasks_depth0[0]  # Take first subtask
        tasks_depth1 = fractal_task_generator(task_depth1, None)
        assert len(tasks_depth1) == 4
        for task in tasks_depth1:
            assert task.metadata['size'] == 0.5  # Should scale again
            assert "_fractal_" in task.name  # Pattern naming is less strict
            
        # Block 3: Test depth limiting
        deep_task = StrategyTask(
            name="test_fractal_deep",
            task_type=TaskType.RECURSIVE,
            depth=5,
            metadata={'max_depth': 4}
        )
        tasks_too_deep = fractal_task_generator(deep_task, None)
        assert len(tasks_too_deep) == 0  # Should not generate beyond max_depth

    def test_adaptive_pattern_unified(self):
        """
        Unified block test for adaptive pattern generation.
        Tests complexity adjustment, success rate influence, and task adaptation.
        """
        # Setup - Create base task with different complexity scenarios
        base_task = StrategyTask(
            name="test_adaptive",
            task_type=TaskType.META,
            metadata={'adaptation_level': 0}
        )
        
        # Block 1: Test basic adaptation with neutral results
        neutral_result = {'complexity': 1.0, 'success_rate': 0.5}
        tasks_neutral = adaptive_split_generator(base_task, neutral_result)
        assert 1 <= len(tasks_neutral) <= 5
        for task in tasks_neutral:
            assert task.task_type == TaskType.META
            assert task.metadata['adaptation_level'] == 1
            
        # Block 2: Test adaptation with high complexity/low success
        hard_result = {'complexity': 2.0, 'success_rate': 0.3}
        tasks_hard = adaptive_split_generator(base_task, hard_result)
        assert len(tasks_hard) > len(tasks_neutral)  # Should generate more tasks
        for task in tasks_hard:
            assert task.metadata['parent_complexity'] == 2.0
            assert task.metadata['parent_success'] == 0.3
            
        # Block 3: Test adaptation with invalid/missing results
        tasks_no_result = adaptive_split_generator(base_task, None)
        assert len(tasks_no_result) == 0
        tasks_invalid = adaptive_split_generator(base_task, "invalid")
        assert len(tasks_invalid) == 0

    def test_quantum_pattern_unified(self):
        """
        Unified block test for quantum pattern generation.
        Tests state generation, probability handling, and bulk operations.
        """
        # Setup - Create base task with quantum properties
        base_task = StrategyTask(
            name="test_quantum",
            task_type=TaskType.COMPOUND,
            metadata={
                'bulk_factor': 3,
                'analyze_probability': 0.3,
                'optimize_probability': 0.2,
                'transform_probability': 0.4,
                'validate_probability': 0.1,
                'max_depth': 2
            }
        )
        
        # Block 1: Test bulk task generation
        tasks = quantum_state_generator(base_task, None)
        states_count = {'analyze': 0, 'optimize': 0, 'transform': 0, 'validate': 0}
        for task in tasks:
            state = task.metadata['state']
            states_count[state] += 1
            assert task.task_type == TaskType.COMPOUND
            assert not task.metadata['collapsed']
            assert len(task.metadata['superposition']) == 4
            
        # Should generate more tasks for higher probability states
        assert states_count['transform'] >= states_count['validate']
        
        # Block 2: Test depth limiting
        deep_task = StrategyTask(
            name="test_quantum_deep",
            task_type=TaskType.COMPOUND,
            depth=3,
            metadata={'max_depth': 2, 'bulk_factor': 1}
        )
        deep_tasks = quantum_state_generator(deep_task, None)
        assert len(deep_tasks) == 0
        
        # Block 3: Test probability thresholds
        low_prob_task = StrategyTask(
            name="test_quantum_low_prob",
            task_type=TaskType.COMPOUND,
            metadata={
                'bulk_factor': 1,
                'analyze_probability': 0.05,  # Below threshold
                'optimize_probability': 0.05,
                'transform_probability': 0.05,
                'validate_probability': 0.05
            }
        )
        low_prob_tasks = quantum_state_generator(low_prob_task, None)
        assert len(low_prob_tasks) == 0  # Should not generate tasks below threshold

    def test_meta_handlers_unified(self):
        """
        Unified block test for meta-task handlers.
        Tests complexity analysis and pattern optimization together.
        """
        # Setup - Create tasks for both handlers
        complexity_task = StrategyTask(
            name="test_complexity",
            task_type=TaskType.META,
            metadata={
                'complexity': 1.0,
                'execution_history': [
                    {'success_rate': 0.8},
                    {'success_rate': 0.6}
                ]
            }
        )
        
        optimize_task = StrategyTask(
            name="test_optimize",
            task_type=TaskType.RECURSIVE,
            metadata={
                'branches': 3,
                'optimization_level': 1
            },
            patterns=[
                TaskPattern(
                    pattern_type='fractal',
                    generator=fractal_task_generator
                )
            ]
        )
        
        # Block 1: Test complexity analysis
        complexity_result = complexity_analyzer(complexity_task)
        assert 'analyzed_complexity' in complexity_result
        assert complexity_result['analyzed_complexity'] > 0.7  # Should reflect average success rate
        assert complexity_result['history_length'] == 2
        assert complexity_result['recommended_subtasks'] >= 1
        
        # Block 2: Test pattern optimization
        optimized_tasks = pattern_optimizer(optimize_task)
        assert len(optimized_tasks) >= 1
        for task in optimized_tasks:
            assert task.task_type == TaskType.RECURSIVE
            assert task.metadata['optimization_level'] == 2
            
        # Block 3: Test handler interaction
        # Create a task that will be processed by both handlers
        hybrid_task = StrategyTask(
            name="test_hybrid",
            task_type=TaskType.COMPOUND,
            metadata={
                'complexity': 1.5,
                'execution_history': [{'success_rate': 0.7}],
                'optimization_level': 1
            },
            patterns=[
                TaskPattern(
                    pattern_type='fractal',
                    generator=fractal_task_generator
                )
            ]
        )
        
        complexity_update = complexity_analyzer(hybrid_task)
        assert complexity_update['analyzed_complexity'] > 0
        
        optimized = pattern_optimizer(hybrid_task)
        assert len(optimized) >= 1
        assert all(t.metadata['optimization_level'] > 1 for t in optimized)
