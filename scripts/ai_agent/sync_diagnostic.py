#!/usr/bin/env python3
"""
Agent Synchronization Diagnostic Utility

This utility helps diagnose and resolve synchronization issues in the epochcore RAS 
agentic agent system. It provides real-time monitoring, issue detection, and 
recovery recommendations.

Usage:
    python sync_diagnostic.py [options]
    
    Options:
    --monitor           Monitor sync points in real-time
    --diagnose <id>     Diagnose specific sync point
    --list              List all active sync points  
    --cleanup           Clean up completed sync points
    --stats             Show synchronization statistics
    --registry          Show agent registry status
    --help              Show this help message
"""

import sys
import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append('/home/runner/work/epochcore_RAS/epochcore_RAS')

from scripts.ai_agent.core.synchronizer import AgentSynchronizer
from scripts.ai_agent.core.sync_registry import SynchronizedAgentRegistry, AgentStatus


class SyncDiagnosticTool:
    """Tool for diagnosing agent synchronization issues"""
    
    def __init__(self):
        self.synchronizer = AgentSynchronizer()
        self.registry = SynchronizedAgentRegistry()
        
    async def list_sync_points(self):
        """List all active sync points"""
        print("🔍 Active Synchronization Points:")
        print("=" * 50)
        
        active_syncs = self.synchronizer.list_active_sync_points()
        
        if not active_syncs:
            print("No active sync points found.")
            return
        
        for sync in active_syncs:
            print(f"Sync ID: {sync['id']}")
            print(f"  State: {sync['state']}")
            print(f"  Agents Joined: {sync['agents_joined']}")
            print(f"  Agents Pending: {sync['agents_pending']}")
            print(f"  Start Time: {sync['start_time']}")
            if sync['completion_time']:
                print(f"  Completion Time: {sync['completion_time']}")
            print()
    
    async def diagnose_sync_point(self, sync_id: str):
        """Diagnose a specific sync point"""
        print(f"🔧 Diagnosing Sync Point: {sync_id}")
        print("=" * 50)
        
        try:
            diagnostics = self.synchronizer.diagnose_sync_issues(sync_id)
            
            if "error" in diagnostics:
                print(f"❌ Error: {diagnostics['error']}")
                return
            
            status = diagnostics["status"]
            print(f"Status: {status['state']}")
            print(f"Agents Joined: {', '.join(status['agents_joined'])}")
            print(f"Agents Pending: {', '.join(status['agents_pending'])}")
            
            if diagnostics["issues"]:
                print("\n⚠️  Issues Found:")
                for issue in diagnostics["issues"]:
                    print(f"  - {issue}")
            
            if diagnostics["recommendations"]:
                print("\n💡 Recommendations:")
                for rec in diagnostics["recommendations"]:
                    print(f"  - {rec}")
            
            if not diagnostics["issues"]:
                print("\n✅ No issues detected with this sync point.")
                
        except Exception as e:
            print(f"❌ Failed to diagnose sync point: {e}")
    
    async def monitor_sync_points(self, duration: int = 60):
        """Monitor sync points in real-time"""
        print(f"📊 Monitoring Sync Points for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        print("=" * 50)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while asyncio.get_event_loop().time() - start_time < duration:
                active_syncs = self.synchronizer.list_active_sync_points()
                
                # Clear screen (simple approach)
                print("\033[H\033[J", end="")
                print(f"📊 Sync Monitor - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 50)
                
                if active_syncs:
                    for sync in active_syncs:
                        state_icon = "🟢" if sync['state'] == 'completed' else "🟡" if sync['state'] == 'syncing' else "🔴"
                        print(f"{state_icon} {sync['id']}: {sync['state']} "
                              f"({len(sync['agents_joined'])}/{len(sync['agents_joined']) + len(sync['agents_pending'])})")
                else:
                    print("No active sync points.")
                
                print(f"\nMonitoring... ({int(asyncio.get_event_loop().time() - start_time)}s)")
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
    
    async def cleanup_sync_points(self):
        """Clean up completed sync points"""
        print("🧹 Cleaning Up Sync Points...")
        print("=" * 50)
        
        active_syncs = self.synchronizer.list_active_sync_points()
        completed_syncs = [s for s in active_syncs if s['state'] == 'completed']
        
        if not completed_syncs:
            print("No completed sync points to clean up.")
            return
        
        for sync in completed_syncs:
            self.synchronizer.cleanup_sync_point(sync['id'])
            print(f"✅ Cleaned up sync point: {sync['id']}")
        
        print(f"\n🧹 Cleaned up {len(completed_syncs)} sync points.")
    
    async def show_stats(self):
        """Show synchronization statistics"""
        print("📈 Synchronization Statistics")
        print("=" * 50)
        
        active_syncs = self.synchronizer.list_active_sync_points()
        
        # Sync point stats
        total_syncs = len(active_syncs)
        by_state = {}
        for sync in active_syncs:
            state = sync['state']
            by_state[state] = by_state.get(state, 0) + 1
        
        print("Sync Points:")
        print(f"  Total Active: {total_syncs}")
        for state, count in by_state.items():
            print(f"  {state.title()}: {count}")
        
        # Registry stats
        try:
            registry_stats = await self.registry.get_registry_stats()
            print(f"\nAgent Registry:")
            print(f"  Total Agents: {registry_stats['total_agents']}")
            
            for status, count in registry_stats['status_breakdown'].items():
                if count > 0:
                    print(f"  {status.title()}: {count}")
            
            if registry_stats['sync_capabilities']:
                print(f"\nSync Capabilities:")
                for cap, count in registry_stats['sync_capabilities'].items():
                    print(f"  {cap}: {count} agents")
                    
        except Exception as e:
            print(f"⚠️  Could not retrieve registry stats: {e}")
    
    async def show_registry_status(self):
        """Show agent registry status"""
        print("👥 Agent Registry Status")
        print("=" * 50)
        
        try:
            registry = await self.registry.load_registry()
            
            if not registry:
                print("No agents registered.")
                return
            
            for agent_id, info in registry.items():
                status_icon = "🟢" if info.status == AgentStatus.ACTIVE else "🔴"
                print(f"{status_icon} {agent_id}")
                print(f"  Role: {info.role}")
                print(f"  Status: {info.status.value}")
                print(f"  Last Seen: {info.last_seen.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Last Action: {info.last_action}")
                if info.sync_capabilities:
                    print(f"  Sync Capabilities: {', '.join(info.sync_capabilities)}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to load registry: {e}")

async def main():
    """Main diagnostic tool entry point"""
    parser = argparse.ArgumentParser(
        description="Agent Synchronization Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--monitor", action="store_true", help="Monitor sync points in real-time")
    parser.add_argument("--monitor-duration", type=int, default=60, help="Monitor duration in seconds (default: 60)")
    parser.add_argument("--diagnose", type=str, help="Diagnose specific sync point by ID")
    parser.add_argument("--list", action="store_true", help="List all active sync points")
    parser.add_argument("--cleanup", action="store_true", help="Clean up completed sync points")
    parser.add_argument("--stats", action="store_true", help="Show synchronization statistics")
    parser.add_argument("--registry", action="store_true", help="Show agent registry status")
    
    args = parser.parse_args()
    
    tool = SyncDiagnosticTool()
    
    try:
        if args.monitor:
            await tool.monitor_sync_points(args.monitor_duration)
        elif args.diagnose:
            await tool.diagnose_sync_point(args.diagnose)
        elif args.list:
            await tool.list_sync_points()
        elif args.cleanup:
            await tool.cleanup_sync_points()
        elif args.stats:
            await tool.show_stats()
        elif args.registry:
            await tool.show_registry_status()
        else:
            # Default action - show overview
            print("🔍 Agent Synchronization Overview")
            print("=" * 50)
            await tool.show_stats()
            print()
            await tool.list_sync_points()
            
    except KeyboardInterrupt:
        print("\n⏹️  Diagnostic tool interrupted by user")
    except Exception as e:
        print(f"❌ Diagnostic tool error: {e}")

if __name__ == "__main__":
    asyncio.run(main())