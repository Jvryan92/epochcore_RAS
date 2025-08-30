#!/usr/bin/env python3
"""
Example: Multi-Agent Data Processing Pipeline with Synchronization

This example demonstrates how to use the improved agent synchronization system
for a typical multi-agent processing pipeline where agents need to coordinate
their work at various stages.

Scenario: 
- Data collection agents gather data
- Processing agents analyze the data  
- Storage agents save results
- All agents must coordinate at each phase

Usage:
    python examples/multi_agent_pipeline.py
"""

import sys
import asyncio
import random
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.ai_agent.core.synchronizer import AgentSynchronizer, SynchronizedAgent
from scripts.ai_agent.core.sync_registry import SynchronizedAgentRegistry, AgentStatus


class DataCollectionAgent(SynchronizedAgent):
    """Agent that collects data"""
    
    def __init__(self, name: str, synchronizer: AgentSynchronizer, registry: SynchronizedAgentRegistry):
        super().__init__(name, synchronizer)
        self.registry = registry
        self.data = []
        
    def run(self):
        return {"status": "completed", "data_collected": len(self.data)}
    
    def validate_config(self):
        return True
    
    async def collect_data(self):
        """Simulate data collection"""
        await self.registry.update_agent_status(self.name, AgentStatus.ACTIVE, "collecting_data")
        
        print(f"[{self.name}] Starting data collection...")
        
        # Simulate variable collection time
        collection_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(collection_time)
        
        # Simulate collecting data
        self.data = [f"data_item_{i}" for i in range(random.randint(5, 10))]
        print(f"[{self.name}] Collected {len(self.data)} items")
        
        return self.data


class ProcessingAgent(SynchronizedAgent):
    """Agent that processes data"""
    
    def __init__(self, name: str, synchronizer: AgentSynchronizer, registry: SynchronizedAgentRegistry):
        super().__init__(name, synchronizer)
        self.registry = registry
        self.processed_data = []
        
    def run(self):
        return {"status": "completed", "items_processed": len(self.processed_data)}
    
    def validate_config(self):
        return True
        
    async def process_data(self, input_data):
        """Simulate data processing"""
        await self.registry.update_agent_status(self.name, AgentStatus.ACTIVE, "processing_data")
        
        print(f"[{self.name}] Processing {len(input_data)} items...")
        
        # Simulate variable processing time
        processing_time = random.uniform(0.5, 2.0)
        await asyncio.sleep(processing_time)
        
        # Simulate processing
        self.processed_data = [f"processed_{item}" for item in input_data]
        print(f"[{self.name}] Processed {len(self.processed_data)} items")
        
        return self.processed_data


class StorageAgent(SynchronizedAgent):
    """Agent that stores results"""
    
    def __init__(self, name: str, synchronizer: AgentSynchronizer, registry: SynchronizedAgentRegistry):
        super().__init__(name, synchronizer)
        self.registry = registry
        self.stored_items = []
        
    def run(self):
        return {"status": "completed", "items_stored": len(self.stored_items)}
    
    def validate_config(self):
        return True
        
    async def store_data(self, input_data):
        """Simulate data storage"""
        await self.registry.update_agent_status(self.name, AgentStatus.ACTIVE, "storing_data")
        
        print(f"[{self.name}] Storing {len(input_data)} items...")
        
        # Simulate variable storage time
        storage_time = random.uniform(0.3, 1.0)
        await asyncio.sleep(storage_time)
        
        # Simulate storage
        self.stored_items.extend(input_data)
        print(f"[{self.name}] Stored {len(input_data)} items")
        
        return True


async def run_pipeline():
    """Run the multi-agent processing pipeline with synchronization"""
    print("🚀 Starting Multi-Agent Processing Pipeline")
    print("=" * 60)
    
    # Initialize components
    synchronizer = AgentSynchronizer(timeout=15.0)
    registry = SynchronizedAgentRegistry("/tmp/pipeline_registry.json")
    
    # Create agents
    collectors = [
        DataCollectionAgent(f"collector_{i}", synchronizer, registry)
        for i in range(2)
    ]
    
    processors = [
        ProcessingAgent(f"processor_{i}", synchronizer, registry)  
        for i in range(3)
    ]
    
    storage = StorageAgent("storage_1", synchronizer, registry)
    
    all_agents = collectors + processors + [storage]
    
    # Register agents
    print("📝 Registering agents...")
    for agent in all_agents:
        role = agent.__class__.__name__.replace("Agent", "").lower()
        await registry.register_agent(
            agent_id=agent.name,
            role=role,
            sync_capabilities=["phase_sync", "pipeline_sync"],
            metadata={"pipeline": "data_processing"}
        )
    
    try:
        # PHASE 1: Data Collection
        print("\n📊 PHASE 1: Data Collection")
        print("-" * 40)
        
        collector_tasks = [collector.collect_data() for collector in collectors]
        collected_data = await asyncio.gather(*collector_tasks)
        
        # Sync all agents after data collection
        all_agent_names = {agent.name for agent in all_agents}
        sync_tasks = [
            agent.sync_with_agents("phase1_complete", all_agent_names, 10.0)
            for agent in all_agents
        ]
        sync_results = await asyncio.gather(*sync_tasks)
        
        if not all(sync_results):
            print("❌ Phase 1 synchronization failed!")
            return False
            
        print("✅ Phase 1 synchronization completed")
        
        # PHASE 2: Data Processing
        print("\n⚙️  PHASE 2: Data Processing")
        print("-" * 40)
        
        # Distribute collected data to processors
        all_collected = [item for sublist in collected_data for item in sublist]
        chunk_size = len(all_collected) // len(processors)
        
        processing_tasks = []
        for i, processor in enumerate(processors):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < len(processors) - 1 else len(all_collected)
            chunk = all_collected[start_idx:end_idx]
            processing_tasks.append(processor.process_data(chunk))
        
        processed_data = await asyncio.gather(*processing_tasks)
        
        # Sync all agents after processing
        sync_tasks = [
            agent.sync_with_agents("phase2_complete", all_agent_names, 10.0)
            for agent in all_agents
        ]
        sync_results = await asyncio.gather(*sync_tasks)
        
        if not all(sync_results):
            print("❌ Phase 2 synchronization failed!")
            return False
            
        print("✅ Phase 2 synchronization completed")
        
        # PHASE 3: Data Storage
        print("\n💾 PHASE 3: Data Storage")
        print("-" * 40)
        
        # Storage agent stores all processed data
        all_processed = [item for sublist in processed_data for item in sublist]
        await storage.store_data(all_processed)
        
        # Final sync
        sync_tasks = [
            agent.sync_with_agents("phase3_complete", all_agent_names, 10.0)
            for agent in all_agents
        ]
        sync_results = await asyncio.gather(*sync_tasks)
        
        if not all(sync_results):
            print("❌ Phase 3 synchronization failed!")
            return False
            
        print("✅ Phase 3 synchronization completed")
        
        # Pipeline completed successfully
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"   📊 Data collected: {sum(len(data) for data in collected_data)} items")
        print(f"   ⚙️  Data processed: {sum(len(data) for data in processed_data)} items") 
        print(f"   💾 Data stored: {len(storage.stored_items)} items")
        
        # Show final registry stats
        stats = await registry.get_registry_stats()
        print(f"\n📈 Final Stats:")
        print(f"   Total agents: {stats['total_agents']}")
        print(f"   Active agents: {stats['status_breakdown'].get('active', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        return False


async def main():
    """Main entry point"""
    success = await run_pipeline()
    
    if success:
        print("\n✅ Multi-agent pipeline demonstration completed successfully!")
        print("\nThis example showed:")
        print("  • Agent registration and discovery")
        print("  • Phase-based synchronization")  
        print("  • Concurrent agent coordination")
        print("  • Error handling and recovery")
        print("\nTry the sync diagnostic tool to monitor active sync points:")
        print("  python scripts/ai_agent/sync_diagnostic.py --stats")
    else:
        print("\n❌ Pipeline demonstration failed!")
        print("Check the sync diagnostic tool for troubleshooting:")
        print("  python scripts/ai_agent/sync_diagnostic.py --list")


if __name__ == "__main__":
    asyncio.run(main())