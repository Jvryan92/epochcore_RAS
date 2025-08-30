#!/usr/bin/env python3
"""
Agent Synchronization System for EpochCore RAS

This module provides mechanisms for synchronizing agents, handling message passing,
state sharing, and coordination between different agent instances. It supports
both asynchronous communication and synchronized execution cycles.
"""

import asyncio
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Set
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("AgentSync")

@dataclass
class SyncMessage:
    """Message for agent synchronization"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    priority: int = 0
    ttl: int = 3600  # Time-to-live in seconds
    is_acknowledged: bool = False
    thread_id: Optional[str] = None
    parent_id: Optional[str] = None
    
    @staticmethod
    def create(
        sender_id: str,
        receiver_id: str,
        message_type: str,
        content: Dict[str, Any],
        priority: int = 0,
        thread_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> 'SyncMessage':
        """Create a new message"""
        return SyncMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            priority=priority,
            is_acknowledged=False,
            thread_id=thread_id,
            parent_id=parent_id
        )

@dataclass
class AgentState:
    """State information for an agent"""
    agent_id: str
    status: str
    last_updated: str
    current_tasks: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    collaboration_status: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SyncPoint:
    """Synchronization point for coordinating agent activities"""
    sync_id: str
    name: str
    participants: List[str]
    ready_agents: Set[str] = field(default_factory=set)
    is_complete: bool = False
    timeout: float = 30.0  # seconds
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    
    def is_ready(self) -> bool:
        """Check if all agents are ready"""
        return set(self.participants) == self.ready_agents
    
    def mark_agent_ready(self, agent_id: str) -> bool:
        """Mark an agent as ready"""
        if agent_id in self.participants:
            self.ready_agents.add(agent_id)
            return True
        return False
    
    def complete(self) -> None:
        """Mark the sync point as complete"""
        self.is_complete = True
        self.completed_at = datetime.now(timezone.utc).isoformat()

class MessageQueue:
    """Thread-safe message queue"""
    def __init__(self, max_size: int = 1000):
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.lock = threading.Lock()
        
    def put(self, message: SyncMessage) -> None:
        """Add a message to the queue"""
        with self.lock:
            # Priority queue sorts by first element of tuple
            # Negative priority to make higher values more important
            self.queue.put((-message.priority, message))
    
    def get(self) -> Optional[SyncMessage]:
        """Get the next message from the queue"""
        try:
            _, message = self.queue.get(block=False)
            return message
        except queue.Empty:
            return None
            
    def size(self) -> int:
        """Get the current size of the queue"""
        return self.queue.qsize()

class AgentSynchronizer:
    """
    Core synchronization system for coordinating multiple agents.
    Provides message passing, state synchronization, and coordination points.
    """
    def __init__(self, 
                data_dir: str = ".sync", 
                enable_persistence: bool = True,
                message_ttl: int = 3600):
        self.data_dir = Path(data_dir)
        if enable_persistence:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
        self.enable_persistence = enable_persistence
        self.message_ttl = message_ttl
        
        # Message queues for each agent
        self.message_queues: Dict[str, MessageQueue] = {}
        
        # Agent states
        self.agent_states: Dict[str, AgentState] = {}
        
        # Sync points
        self.sync_points: Dict[str, SyncPoint] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Locks for thread safety
        self.state_lock = threading.Lock()
        self.sync_lock = threading.Lock()
        
        # Event for sync completion notification
        self.sync_event = threading.Event()
        
        # Start cleanup thread
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_task)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
        logger.info("Agent synchronizer initialized")
        
    def register_agent(self, 
                    agent_id: str, 
                    capabilities: List[str] = None) -> bool:
        """Register an agent with the synchronizer"""
        try:
            with self.state_lock:
                # Create message queue for agent
                if agent_id not in self.message_queues:
                    self.message_queues[agent_id] = MessageQueue()
                
                # Create or update agent state
                if agent_id not in self.agent_states:
                    self.agent_states[agent_id] = AgentState(
                        agent_id=agent_id,
                        status="registered",
                        last_updated=datetime.now(timezone.utc).isoformat(),
                        capabilities=capabilities or []
                    )
                else:
                    self.agent_states[agent_id].status = "registered"
                    self.agent_states[agent_id].last_updated = datetime.now(timezone.utc).isoformat()
                    if capabilities:
                        self.agent_states[agent_id].capabilities = capabilities
                
                if self.enable_persistence:
                    self._save_agent_state(agent_id)
                    
                logger.info(f"Agent registered: {agent_id}")
                return True
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the synchronizer"""
        try:
            with self.state_lock:
                if agent_id in self.agent_states:
                    self.agent_states[agent_id].status = "unregistered"
                    self.agent_states[agent_id].last_updated = datetime.now(timezone.utc).isoformat()
                    
                    if self.enable_persistence:
                        self._save_agent_state(agent_id)
                        
                    logger.info(f"Agent unregistered: {agent_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False
    
    def update_agent_state(self, 
                        agent_id: str, 
                        status: Optional[str] = None,
                        tasks: Optional[List[str]] = None,
                        metrics: Optional[Dict[str, Any]] = None,
                        resources: Optional[Dict[str, Any]] = None) -> bool:
        """Update an agent's state"""
        try:
            with self.state_lock:
                if agent_id not in self.agent_states:
                    logger.warning(f"Cannot update state for unknown agent: {agent_id}")
                    return False
                
                state = self.agent_states[agent_id]
                
                if status:
                    state.status = status
                if tasks is not None:
                    state.current_tasks = tasks
                if metrics:
                    state.metrics.update(metrics)
                if resources:
                    state.resources.update(resources)
                
                state.last_updated = datetime.now(timezone.utc).isoformat()
                
                if self.enable_persistence:
                    self._save_agent_state(agent_id)
                
                return True
        except Exception as e:
            logger.error(f"Error updating agent state for {agent_id}: {e}")
            return False
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get an agent's current state"""
        with self.state_lock:
            return self.agent_states.get(agent_id)
    
    def send_message(self, message: SyncMessage) -> bool:
        """Send a message to an agent"""
        try:
            receiver_id = message.receiver_id
            
            # Check if receiver exists
            if receiver_id not in self.message_queues:
                logger.warning(f"Cannot send message to unknown agent: {receiver_id}")
                return False
            
            # Add message to receiver's queue
            self.message_queues[receiver_id].put(message)
            
            # Persist message if enabled
            if self.enable_persistence:
                self._save_message(message)
            
            logger.debug(f"Message sent: {message.message_id} from {message.sender_id} to {message.receiver_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def get_messages(self, 
                  agent_id: str, 
                  max_count: int = 10) -> List[SyncMessage]:
        """Get messages for an agent"""
        if agent_id not in self.message_queues:
            logger.warning(f"Cannot get messages for unknown agent: {agent_id}")
            return []
        
        messages = []
        queue = self.message_queues[agent_id]
        
        for _ in range(min(max_count, queue.size())):
            message = queue.get()
            if message:
                messages.append(message)
        
        return messages
    
    def acknowledge_message(self, message_id: str, agent_id: str) -> bool:
        """Acknowledge receipt of a message"""
        try:
            if self.enable_persistence:
                message_file = self.data_dir / "messages" / f"{message_id}.json"
                if message_file.exists():
                    with open(message_file, 'r') as f:
                        message_data = json.load(f)
                    
                    message_data["is_acknowledged"] = True
                    
                    with open(message_file, 'w') as f:
                        json.dump(message_data, f, indent=2)
            
            logger.debug(f"Message acknowledged: {message_id} by {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error acknowledging message {message_id}: {e}")
            return False
    
    def create_sync_point(self, 
                       name: str, 
                       participants: List[str],
                       timeout: float = 30.0) -> Optional[str]:
        """Create a synchronization point for coordinating agents"""
        try:
            with self.sync_lock:
                # Validate participants
                for agent_id in participants:
                    if agent_id not in self.agent_states:
                        logger.warning(f"Cannot create sync point with unknown agent: {agent_id}")
                        return None
                
                sync_id = str(uuid.uuid4())
                
                sync_point = SyncPoint(
                    sync_id=sync_id,
                    name=name,
                    participants=participants,
                    timeout=timeout
                )
                
                self.sync_points[sync_id] = sync_point
                
                # Notify participants
                for agent_id in participants:
                    message = SyncMessage.create(
                        sender_id="system",
                        receiver_id=agent_id,
                        message_type="sync_request",
                        content={
                            "sync_id": sync_id,
                            "name": name,
                            "timeout": timeout
                        },
                        priority=10  # High priority for sync messages
                    )
                    self.send_message(message)
                
                logger.info(f"Sync point created: {sync_id} ({name}) with {len(participants)} participants")
                return sync_id
        except Exception as e:
            logger.error(f"Error creating sync point: {e}")
            return None
    
    def agent_ready_for_sync(self, sync_id: str, agent_id: str) -> bool:
        """Mark an agent as ready for a sync point"""
        try:
            with self.sync_lock:
                if sync_id not in self.sync_points:
                    logger.warning(f"Unknown sync point: {sync_id}")
                    return False
                
                sync_point = self.sync_points[sync_id]
                
                if agent_id not in sync_point.participants:
                    logger.warning(f"Agent {agent_id} not a participant in sync point {sync_id}")
                    return False
                
                sync_point.mark_agent_ready(agent_id)
                
                # Check if all agents are ready
                if sync_point.is_ready():
                    sync_point.complete()
                    
                    # Notify participants
                    for participant_id in sync_point.participants:
                        message = SyncMessage.create(
                            sender_id="system",
                            receiver_id=participant_id,
                            message_type="sync_complete",
                            content={
                                "sync_id": sync_id,
                                "name": sync_point.name,
                                "completed_at": sync_point.completed_at
                            },
                            priority=10  # High priority for sync messages
                        )
                        self.send_message(message)
                    
                    # Set event to notify waiting threads
                    self.sync_event.set()
                    
                    logger.info(f"Sync point completed: {sync_id} ({sync_point.name})")
                
                return True
        except Exception as e:
            logger.error(f"Error marking agent ready for sync: {e}")
            return False
    
    def wait_for_sync(self, sync_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a sync point to complete"""
        if sync_id not in self.sync_points:
            logger.warning(f"Unknown sync point: {sync_id}")
            return False
        
        sync_point = self.sync_points[sync_id]
        
        if sync_point.is_complete:
            return True
        
        # Wait for sync completion
        self.sync_event.clear()
        start_time = time.time()
        actual_timeout = timeout or sync_point.timeout
        
        while not sync_point.is_complete:
            if self.sync_event.wait(timeout=1.0):  # Short timeout for responsiveness
                return True
                
            # Check for timeout
            elapsed = time.time() - start_time
            if elapsed > actual_timeout:
                logger.warning(f"Timeout waiting for sync point: {sync_id}")
                return False
                
            # Check if complete again (might have been set by another thread)
            if sync_point.is_complete:
                return True
        
        return sync_point.is_complete
    
    def register_message_handler(self, 
                              message_type: str, 
                              handler: Callable[[SyncMessage], None]) -> None:
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")
    
    def process_message(self, message: SyncMessage) -> bool:
        """Process a message using the registered handler"""
        try:
            message_type = message.message_type
            
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                handler(message)
                return True
            else:
                logger.warning(f"No handler registered for message type: {message_type}")
                return False
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {e}")
            return False
    
    def broadcast_message(self, 
                       sender_id: str, 
                       message_type: str, 
                       content: Dict[str, Any],
                       exclude_agents: List[str] = None) -> bool:
        """Broadcast a message to all registered agents"""
        try:
            exclude = exclude_agents or []
            recipients = [agent_id for agent_id in self.agent_states 
                         if agent_id != sender_id and agent_id not in exclude]
            
            success = True
            
            for recipient in recipients:
                message = SyncMessage.create(
                    sender_id=sender_id,
                    receiver_id=recipient,
                    message_type=message_type,
                    content=content
                )
                
                if not self.send_message(message):
                    success = False
            
            logger.info(f"Broadcast message from {sender_id} to {len(recipients)} agents")
            return success
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return False
    
    def _save_agent_state(self, agent_id: str) -> None:
        """Save agent state to persistent storage"""
        try:
            states_dir = self.data_dir / "states"
            states_dir.mkdir(parents=True, exist_ok=True)
            
            state = self.agent_states[agent_id]
            state_file = states_dir / f"{agent_id}.json"
            
            with open(state_file, 'w') as f:
                # Convert dataclass to dict for serialization
                state_dict = {
                    "agent_id": state.agent_id,
                    "status": state.status,
                    "last_updated": state.last_updated,
                    "current_tasks": state.current_tasks,
                    "capabilities": state.capabilities,
                    "metrics": state.metrics,
                    "collaboration_status": state.collaboration_status,
                    "resources": state.resources
                }
                json.dump(state_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving agent state for {agent_id}: {e}")
    
    def _save_message(self, message: SyncMessage) -> None:
        """Save message to persistent storage"""
        try:
            messages_dir = self.data_dir / "messages"
            messages_dir.mkdir(parents=True, exist_ok=True)
            
            message_file = messages_dir / f"{message.message_id}.json"
            
            with open(message_file, 'w') as f:
                # Convert dataclass to dict for serialization
                message_dict = {
                    "message_id": message.message_id,
                    "sender_id": message.sender_id,
                    "receiver_id": message.receiver_id,
                    "message_type": message.message_type,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "priority": message.priority,
                    "ttl": message.ttl,
                    "is_acknowledged": message.is_acknowledged,
                    "thread_id": message.thread_id,
                    "parent_id": message.parent_id
                }
                json.dump(message_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving message {message.message_id}: {e}")
    
    def _cleanup_task(self) -> None:
        """Background task for cleaning up expired messages"""
        while self.running:
            try:
                # Only perform cleanup if persistence is enabled
                if self.enable_persistence:
                    messages_dir = self.data_dir / "messages"
                    if messages_dir.exists():
                        now = datetime.now(timezone.utc)
                        
                        for message_file in messages_dir.glob("*.json"):
                            try:
                                with open(message_file, 'r') as f:
                                    message_data = json.load(f)
                                
                                # Parse message timestamp
                                timestamp = datetime.fromisoformat(message_data["timestamp"].replace("Z", "+00:00"))
                                ttl = message_data.get("ttl", self.message_ttl)
                                
                                # Check if message has expired
                                age = (now - timestamp).total_seconds()
                                if age > ttl:
                                    # Delete expired message
                                    message_file.unlink()
                                    logger.debug(f"Deleted expired message: {message_data['message_id']}")
                            except Exception as e:
                                logger.error(f"Error processing message file {message_file}: {e}")
                
                # Sleep for a while before next cleanup
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                time.sleep(60)  # Sleep even on error
    
    def shutdown(self) -> None:
        """Shutdown the synchronizer"""
        self.running = False
        
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5.0)
        
        logger.info("Agent synchronizer shut down")

# Thread-safe singleton instance
_INSTANCE = None
_INSTANCE_LOCK = threading.Lock()

def get_synchronizer() -> AgentSynchronizer:
    """Get the singleton instance of the synchronizer"""
    global _INSTANCE
    
    if _INSTANCE is None:
        with _INSTANCE_LOCK:
            if _INSTANCE is None:
                _INSTANCE = AgentSynchronizer()
    
    return _INSTANCE

# Async API for the synchronizer
class AsyncAgentSynchronizer:
    """Asynchronous wrapper for the agent synchronizer"""
    def __init__(self):
        self.sync = get_synchronizer()
        self.loop = asyncio.get_event_loop()
    
    async def register_agent(self, 
                           agent_id: str, 
                           capabilities: List[str] = None) -> bool:
        """Register an agent asynchronously"""
        return await self.loop.run_in_executor(
            None, 
            lambda: self.sync.register_agent(agent_id, capabilities)
        )
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.unregister_agent(agent_id)
        )
    
    async def update_agent_state(self, 
                               agent_id: str, 
                               status: Optional[str] = None,
                               tasks: Optional[List[str]] = None,
                               metrics: Optional[Dict[str, Any]] = None,
                               resources: Optional[Dict[str, Any]] = None) -> bool:
        """Update an agent's state asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.update_agent_state(agent_id, status, tasks, metrics, resources)
        )
    
    async def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get an agent's state asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.get_agent_state(agent_id)
        )
    
    async def send_message(self, message: SyncMessage) -> bool:
        """Send a message asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.send_message(message)
        )
    
    async def get_messages(self, 
                         agent_id: str, 
                         max_count: int = 10) -> List[SyncMessage]:
        """Get messages for an agent asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.get_messages(agent_id, max_count)
        )
    
    async def create_sync_point(self, 
                              name: str, 
                              participants: List[str],
                              timeout: float = 30.0) -> Optional[str]:
        """Create a sync point asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.create_sync_point(name, participants, timeout)
        )
    
    async def agent_ready_for_sync(self, sync_id: str, agent_id: str) -> bool:
        """Mark an agent as ready for sync asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.agent_ready_for_sync(sync_id, agent_id)
        )
    
    async def wait_for_sync(self, 
                          sync_id: str, 
                          timeout: Optional[float] = None) -> bool:
        """Wait for a sync point to complete asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.wait_for_sync(sync_id, timeout)
        )
    
    async def broadcast_message(self, 
                              sender_id: str, 
                              message_type: str, 
                              content: Dict[str, Any],
                              exclude_agents: List[str] = None) -> bool:
        """Broadcast a message asynchronously"""
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync.broadcast_message(sender_id, message_type, content, exclude_agents)
        )

def get_async_synchronizer() -> AsyncAgentSynchronizer:
    """Get the async wrapper for the synchronizer"""
    return AsyncAgentSynchronizer()

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Synchronization System")
    parser.add_argument("--register", help="Register an agent")
    parser.add_argument("--send", help="Send a message (format: sender:receiver:type:content)")
    parser.add_argument("--sync", help="Create a sync point (format: name:agent1,agent2,...)")
    parser.add_argument("--list", action="store_true", help="List registered agents")
    parser.add_argument("--monitor", action="store_true", help="Monitor sync events")
    
    args = parser.parse_args()
    
    sync = get_synchronizer()
    
    if args.register:
        agent_id = args.register
        capabilities = ["messaging", "synchronization"]
        success = sync.register_agent(agent_id, capabilities)
        print(f"Agent registration {'successful' if success else 'failed'}: {agent_id}")
    
    elif args.send:
        try:
            sender, receiver, msg_type, content_str = args.send.split(":", 3)
            content = json.loads(content_str)
            
            message = SyncMessage.create(
                sender_id=sender,
                receiver_id=receiver,
                message_type=msg_type,
                content=content
            )
            
            success = sync.send_message(message)
            print(f"Message send {'successful' if success else 'failed'}: {message.message_id}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    elif args.sync:
        try:
            name, participants_str = args.sync.split(":", 1)
            participants = participants_str.split(",")
            
            sync_id = sync.create_sync_point(name, participants)
            if sync_id:
                print(f"Sync point created: {sync_id}")
                
                # Simulate participants checking in
                for agent_id in participants:
                    success = sync.agent_ready_for_sync(sync_id, agent_id)
                    print(f"Agent {agent_id} ready: {'yes' if success else 'no'}")
                
                # Wait for sync completion
                completed = sync.wait_for_sync(sync_id)
                print(f"Sync point {'completed' if completed else 'timed out'}: {sync_id}")
            else:
                print("Failed to create sync point")
        except Exception as e:
            print(f"Error creating sync point: {e}")
    
    elif args.list:
        print("Registered Agents:")
        for agent_id, state in sync.agent_states.items():
            print(f"  {agent_id}: {state.status}, {len(state.capabilities)} capabilities")
    
    elif args.monitor:
        print("Monitoring sync events (Ctrl+C to exit)...")
        try:
            while True:
                time.sleep(1)
                
                # Print current sync points
                with sync.sync_lock:
                    for sync_id, point in sync.sync_points.items():
                        status = "complete" if point.is_complete else f"{len(point.ready_agents)}/{len(point.participants)} ready"
                        print(f"Sync point {sync_id} ({point.name}): {status}")
                
                print("\033[F" * (len(sync.sync_points) or 1))  # Move cursor up
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    else:
        parser.print_help()
