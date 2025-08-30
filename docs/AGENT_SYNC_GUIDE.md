# Agent Synchronization System - Usage Guide

## Overview

The epochcore RAS agent synchronization system provides robust coordination between multiple AI agents working collaboratively. The system has been enhanced to handle common synchronization issues including race conditions, timeouts, and partial failures.

## Key Components

### 1. AgentSynchronizer
The core synchronization coordinator that manages sync points and agent coordination.

### 2. SynchronizedAgent  
Base class for agents that need synchronization capabilities.

### 3. SynchronizedAgentRegistry
Registry system for agent discovery and health monitoring.

### 4. Sync Diagnostic Tool
Utility for monitoring and debugging synchronization issues.

## Quick Start

### Basic Agent Synchronization

```python
import asyncio
from scripts.ai_agent.core.synchronizer import AgentSynchronizer, SynchronizedAgent

# Create synchronizer
synchronizer = AgentSynchronizer(timeout=30.0)

# Create agents
class MyAgent(SynchronizedAgent):
    def run(self):
        return {"status": "completed"}
    
    def validate_config(self):
        return True
    
    async def do_work_then_sync(self):
        # Do some work
        print(f"[{self.name}] Working...")
        await asyncio.sleep(1.0)
        
        # Sync with other agents
        other_agents = {"agent1", "agent2", "agent3"}
        success = await self.sync_with_agents("work_complete", other_agents)
        
        print(f"[{self.name}] Sync result: {success}")
        return success

# Usage
agent1 = MyAgent("agent1", synchronizer)
agent2 = MyAgent("agent2", synchronizer) 
agent3 = MyAgent("agent3", synchronizer)

# Run coordinated work
async def main():
    tasks = [
        agent1.do_work_then_sync(),
        agent2.do_work_then_sync(),
        agent3.do_work_then_sync(),
    ]
    results = await asyncio.gather(*tasks)
    print(f"All agents completed: {all(results)}")

asyncio.run(main())
```

### Using the Agent Registry

```python
from scripts.ai_agent.core.sync_registry import SynchronizedAgentRegistry, AgentStatus

# Create registry
registry = SynchronizedAgentRegistry()

# Register agents
await registry.register_agent(
    agent_id="worker_1",
    role="data_processor", 
    sync_capabilities=["data_sync", "checkpoint_sync"]
)

# Update agent status
await registry.update_agent_status("worker_1", AgentStatus.SYNCING)

# Find agents with specific capabilities
sync_agents = await registry.get_agents_with_sync_capability("data_sync")

# Agent heartbeat
await registry.heartbeat("worker_1")
```

## Synchronization Patterns

### 1. Barrier Synchronization
All agents must reach a sync point before any can proceed:

```python
async def barrier_sync_example():
    agents = ["agent1", "agent2", "agent3"]
    synchronizer = AgentSynchronizer()
    
    # All agents sync at the barrier
    for agent_name in agents:
        agent = SynchronizedAgent(agent_name, synchronizer)
        await agent.sync_with_agents("barrier_point", set(agents))
```

### 2. Phase Synchronization
Agents synchronize at different phases of work:

```python
async def phase_sync_example():
    # Phase 1: Data collection
    await agent.sync_with_agents("phase1_complete", all_agents)
    
    # Phase 2: Data processing  
    await agent.sync_with_agents("phase2_complete", all_agents)
    
    # Phase 3: Result aggregation
    await agent.sync_with_agents("phase3_complete", all_agents)
```

### 3. Subset Synchronization
Only specific agents need to synchronize:

```python
async def subset_sync_example():
    # Only processing agents sync
    processing_agents = {"processor1", "processor2"} 
    await processor_agent.sync_with_agents("processing_done", processing_agents)
    
    # Only storage agents sync
    storage_agents = {"storage1", "storage2"}
    await storage_agent.sync_with_agents("storage_ready", storage_agents)
```

## Monitoring and Diagnostics

### Using the Diagnostic Tool

```bash
# List active sync points
python scripts/ai_agent/sync_diagnostic.py --list

# Show sync statistics
python scripts/ai_agent/sync_diagnostic.py --stats

# Monitor sync points in real-time
python scripts/ai_agent/sync_diagnostic.py --monitor

# Diagnose a specific sync point
python scripts/ai_agent/sync_diagnostic.py --diagnose "my_sync_point"

# Show agent registry status
python scripts/ai_agent/sync_diagnostic.py --registry

# Clean up completed sync points
python scripts/ai_agent/sync_diagnostic.py --cleanup
```

### Programmatic Diagnostics

```python
# Get sync point status
synchronizer = AgentSynchronizer()
status = synchronizer.get_sync_status("my_sync_id")

# Diagnose issues
diagnostics = synchronizer.diagnose_sync_issues("my_sync_id")
print(f"Issues: {diagnostics['issues']}")
print(f"Recommendations: {diagnostics['recommendations']}")

# Force complete stuck sync (emergency recovery)
synchronizer.force_complete_sync("stuck_sync_id")
```

## Error Handling

### Common Issues and Solutions

1. **Sync Timeout**
   - Increase timeout value
   - Check if all required agents are running
   - Use diagnostics to identify missing agents

2. **Race Conditions**
   - The system now handles concurrent sync point creation automatically
   - Agents can join sync points in SYNCING state

3. **Agent Discovery**
   - Use SynchronizedAgentRegistry for dynamic agent discovery
   - Implement heartbeat mechanisms for health monitoring

4. **Partial Failures**
   - Set appropriate timeouts
   - Implement retry logic in agent code
   - Use force completion for recovery

### Best Practices

1. **Timeouts**: Set reasonable timeouts based on expected agent processing time
2. **Heartbeats**: Implement regular heartbeats for long-running agents
3. **Error Handling**: Always handle sync failures gracefully
4. **Monitoring**: Use the diagnostic tool for production monitoring
5. **Cleanup**: Regularly clean up completed sync points

## Configuration

### Synchronizer Settings

```python
synchronizer = AgentSynchronizer(
    timeout=30.0  # Default timeout in seconds
)
```

### Registry Settings

```python
registry = SynchronizedAgentRegistry(
    registry_path="./archive/EPOCH5/agents/registry.json"
)
```

## Troubleshooting

### Sync Points Not Completing

1. Check if all required agents are registered and active
2. Verify agents are using the same sync point ID
3. Check for network connectivity issues
4. Review agent logs for errors

### High Memory Usage

1. Clean up completed sync points regularly
2. Limit the number of concurrent sync points
3. Monitor agent resource usage

### Performance Issues

1. Reduce sync polling interval if needed
2. Optimize agent processing time
3. Use subset synchronization instead of full synchronization

For more help, use the diagnostic tool or check the agent logs for detailed error messages.