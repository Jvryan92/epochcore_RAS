import pytest
import asyncio
import time
from strategydeck_agent import StrategyDeckAgent, TaskResult, TaskExecutionError

@pytest.fixture
def agent():
    return StrategyDeckAgent(name="test_agent")

def test_task_success():
    def sample_task(x: int, y: int) -> int:
        return x + y
        
    agent = StrategyDeckAgent()
    result = agent.execute_task(sample_task, 2, 3)
    
    assert result.success
    assert result.result == 5
    assert isinstance(result.execution_time, float)
    assert result.error is None
    
def test_task_failure():
    def failing_task():
        raise ValueError("Test error")
        
    agent = StrategyDeckAgent()
    result = agent.execute_task(failing_task)
    
    assert not result.success
    assert result.result is None
    assert "Test error" in str(result.error)
    
@pytest.mark.asyncio
async def test_async_execution():
    async def async_task():
        await asyncio.sleep(0.1)
        return "async result"
        
    agent = StrategyDeckAgent()
    result = await agent.execute_task_async(async_task)
    
    assert result.success
    assert result.result == "async result"
    
def test_caching():
    call_count = 0
    
    def cached_task():
        nonlocal call_count
        call_count += 1
        return call_count
        
    agent = StrategyDeckAgent()
    
    # First call
    result1 = agent.execute_task(cached_task, cache_ttl=1)
    assert result1.result == 1
    
    # Should hit cache
    result2 = agent.execute_task(cached_task, cache_ttl=1)
    assert result2.result == 1
    assert call_count == 1  # Function was only called once
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Should miss cache
    result3 = agent.execute_task(cached_task, cache_ttl=1)
    assert result3.result == 2
    assert call_count == 2
    
def test_performance_metrics():
    def quick_task():
        return "done"
        
    def slow_task():
        time.sleep(0.1)
        return "done"
        
    def failing_task():
        raise ValueError("fail")
        
    agent = StrategyDeckAgent()
    
    # Execute mix of tasks
    agent.execute_task(quick_task)
    agent.execute_task(slow_task)
    agent.execute_task(failing_task)
    
    metrics = agent.get_performance_metrics()
    
    assert "success_rate" in metrics
    assert "avg_execution_time" in metrics
    assert metrics["total_tasks"] == 3
    assert metrics["successful_tasks"] == 2
    assert 0.5 < metrics["success_rate"] < 0.8
