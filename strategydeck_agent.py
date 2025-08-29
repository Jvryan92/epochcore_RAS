"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import logging
import json
import asyncio
import hashlib
import time
import numpy as np
import networkx as nx
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from strategy_intelligence import StrategyIntelligence, TaskMetrics
from strategy_resilience import StrategyResilience, SystemState
from strategy_collaboration import StrategyCollaboration, AgentCapability, KnowledgePacket
from strategy_evolution import AutonomousEvolution
from strategy_quantum import QuantumArchitecture
from strategy_cognitive import CognitiveArchitecture, CognitiveState, CognitiveDecision
from strategy_temporal import TemporalProcessor, TimeSeriesData, TemporalPrediction
from strategy_ethical import EthicalEngine, EthicalAssessment, Impact

from agent_management import AgentManager
from dag_management import DAGManager
from cycle_execution import CycleExecutor
from policy_grants import PolicyManager, PolicyType
from integration import EPOCH5Integration
from ceiling_manager import CeilingManager, ServiceTier

# Mesh automation enhancements
@dataclass
class MeshMetrics:
    success_rate: float
    execution_time: float
    resource_utilization: float
    mesh_stability: float
    optimization_score: float
    quantum_efficiency: float
    ethical_alignment: float
    cognitive_coherence: float
from ethical_reflection import EthicalReflectionEngine
class MeshNode:
    """Represents a node in the automation mesh"""
    def __init__(
        self,
        node_id: str,
        node_type: str,
        capabilities: List[str],
        resources: Dict[str, Any]
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.capabilities = capabilities
        self.resources = resources
        self.connections: List[str] = []
        self.health_score = 1.0
        self.last_heartbeat = datetime.now(timezone.utc)

    def add_connection(self, node_id: str):
        """Add connection to another node"""
        if node_id not in self.connections:
            self.connections.append(node_id)

    def remove_connection(self, node_id: str):
        """Remove connection to another node"""
        if node_id in self.connections:
            self.connections.remove(node_id)

    def update_health(self, score: float):
        """Update node health score"""
        self.health_score = score
        self.last_heartbeat = datetime.now(timezone.utc)

class AutomationMesh:
    """Manages the mesh network of automation nodes"""
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.integration = EPOCH5Integration()
        self.agent_manager = AgentManager()
        self.dag_manager = DAGManager()
        self.cycle_executor = CycleExecutor()
        self.policy_manager = PolicyManager()
        self.ceiling_manager = CeilingManager()

    async def add_node(
        self,
        node_type: str,
        capabilities: List[str],
        resources: Dict[str, Any]
    ) -> str:
        """Add a new node to the mesh"""
        node_id = f"node_{hashlib.sha256(f'{node_type}_{time.time()}'.encode()).hexdigest()[:8]}"
        node = MeshNode(node_id, node_type, capabilities, resources)
        self.nodes[node_id] = node

        # Create agent for node
        agent = self.agent_manager.create_agent(capabilities, f"mesh_{node_type}")
        self.agent_manager.register_agent(agent)

        # Setup node policies
        policy = self.policy_manager.create_policy(
            f"{node_id}_policy",
            PolicyType.TRUST_THRESHOLD,
            {"min_reliability": 0.8}
        )
        self.policy_manager.add_policy(policy)

        return node_id

    def remove_node(self, node_id: str):
        """Remove a node from the mesh"""
        if node_id in self.nodes:
            # Remove connections to this node
            node = self.nodes[node_id]
            for other_id in node.connections:
                self.nodes[other_id].remove_connection(node_id)
            del self.nodes[node_id]

    def optimize_mesh(self) -> MeshMetrics:
        """Optimize mesh configuration and return metrics"""
        metrics = MeshMetrics(
            success_rate=0.0,
            execution_time=0.0,
            resource_utilization=0.0,
            mesh_stability=0.0,
            optimization_score=0.0,
            quantum_efficiency=0.0,
            ethical_alignment=0.0,
            cognitive_coherence=0.0
        )

        try:
            # Calculate mesh metrics
            total_health = sum(node.health_score for node in self.nodes.values())
            avg_health = total_health / len(self.nodes) if self.nodes else 0.0

            total_connections = sum(len(node.connections) for node in self.nodes.values())
            max_connections = len(self.nodes) * (len(self.nodes) - 1)
            connectivity = total_connections / max_connections if max_connections > 0 else 0.0

            metrics.mesh_stability = (avg_health + connectivity) / 2
            metrics.optimization_score = avg_health

            # Optimize connections
            self._optimize_connections()

            # Adjust resource allocation
            self._optimize_resources()

            # Update metrics
            metrics.success_rate = avg_health
            metrics.resource_utilization = self._calculate_resource_utilization()
            metrics.quantum_efficiency = self._calculate_quantum_efficiency()
            metrics.ethical_alignment = self._calculate_ethical_alignment()
            metrics.cognitive_coherence = self._calculate_cognitive_coherence()

        except Exception as e:
            logging.error(f"Mesh optimization error: {str(e)}")

        return metrics

    def _optimize_connections(self):
        """Optimize mesh connections"""
        for node in self.nodes.values():
            # Remove connections to unhealthy nodes
            for conn_id in node.connections[:]:
                if self.nodes[conn_id].health_score < 0.5:
                    node.remove_connection(conn_id)

            # Add connections to high-performing nodes
            for other_id, other_node in self.nodes.items():
                if (
                    other_id != node.node_id
                    and other_id not in node.connections
                    and other_node.health_score > 0.8
                ):
                    node.add_connection(other_id)

    def _optimize_resources(self):
        """Optimize resource allocation"""
        for node in self.nodes.values():
            if node.health_score < 0.7:
                # Increase resources for underperforming nodes
                node.resources["compute"] = node.resources.get("compute", 1) * 1.5
                node.resources["memory"] = node.resources.get("memory", 1) * 1.5
            elif node.health_score > 0.9:
                # Decrease resources for overprovisioned nodes
                node.resources["compute"] = node.resources.get("compute", 1) * 0.8
                node.resources["memory"] = node.resources.get("memory", 1) * 0.8

    def _calculate_resource_utilization(self) -> float:
        """Calculate overall resource utilization"""
        if not self.nodes:
            return 0.0

        total_allocated = sum(
            sum(resources.values())
            for node in self.nodes.values()
            for resources in [node.resources]
        )

        total_capacity = len(self.nodes) * 10  # Assuming base capacity of 10 per node
        return min(total_allocated / total_capacity, 1.0)

    def _calculate_quantum_efficiency(self) -> float:
        """Calculate quantum system efficiency"""
        # Simplified quantum efficiency calculation
        total_efficiency = 0.0
        active_nodes = [node for node in self.nodes.values() if node.health_score > 0.5]
        
        if not active_nodes:
            return 0.0
            
        for node in active_nodes:
            # Calculate quantum-inspired metrics
            coherence = len(node.connections) / (len(self.nodes) - 1) if len(self.nodes) > 1 else 0
            entanglement = node.health_score
            superposition = len(node.capabilities) / 10  # Assuming max 10 capabilities
            
            # Combine quantum metrics
            node_efficiency = (coherence + entanglement + superposition) / 3
            total_efficiency += node_efficiency
            
        return min(total_efficiency / len(active_nodes), 1.0)

    def _calculate_ethical_alignment(self) -> float:
        """Calculate ethical alignment score"""
        total_alignment = 0.0
        active_nodes = [node for node in self.nodes.values() if node.health_score > 0.5]
        
        if not active_nodes:
            return 0.0
            
        for node in active_nodes:
            # Get agent for this node
            agent_did = f"mesh_{node.node_type}"
            agent = self.agent_manager.get_agent(agent_did)
            
            if agent and "ethical_metrics" in agent:
                metrics = agent["ethical_metrics"]
                node_alignment = (
                    metrics["ethical_score"] * 0.4 +
                    metrics["constraint_satisfaction_rate"] * 0.3 +
                    metrics["reflection_confidence"] * 0.3
                )
                total_alignment += node_alignment
                
        return min(total_alignment / len(active_nodes), 1.0)

    def _calculate_cognitive_coherence(self) -> float:
        """Calculate cognitive system coherence"""
        total_coherence = 0.0
        active_nodes = [node for node in self.nodes.values() if node.health_score > 0.5]
        
        if not active_nodes:
            return 0.0
            
        for node in active_nodes:
            # Calculate cognitive metrics
            skill_diversity = len(node.capabilities) / 10
            connection_density = len(node.connections) / (len(self.nodes) - 1) if len(self.nodes) > 1 else 0
            resource_balance = min(
                node.resources.get("compute", 1) / 10,
                node.resources.get("memory", 1) / 10
            )
            
            # Combine cognitive metrics
            node_coherence = (
                skill_diversity * 0.4 +
                connection_density * 0.3 +
                resource_balance * 0.3
            )
            total_coherence += node_coherence
            
        return min(total_coherence / len(active_nodes), 1.0)

@dataclass
class TaskResult:
    """Structured task execution result"""
    success: bool
    result: Any
    execution_time: float
    task_id: str
    timestamp: str
    error: Optional[str] = None

class StrategyError(Exception):
    """Base exception for strategy-related errors"""
    pass

class TaskExecutionError(StrategyError):
    """Raised when task execution fails"""
    pass

class StrategyDeckAgent:
    """
    Enhanced AI Agent for automating strategic tasks in the StrategyDECK project.
    Features:
    - Async task execution
    - Performance monitoring
    - Task result caching
    - Concurrent task handling
    - Comprehensive logging
    - Automated mesh orchestration
    - Dynamic resource optimization
    - Quantum-enhanced decision making
    - Ethical alignment monitoring
    - Cognitive coherence analysis
    """
    def __init__(
        self, 
        name: str = "StrategyDeckAgent",
        max_workers: int = 4,
        cache_dir: Optional[str] = None,
        enable_intelligence: bool = True,
        enable_resilience: bool = True,
        enable_collaboration: bool = True,
        enable_evolution: bool = True,
        enable_quantum: bool = True,
        enable_cognitive: bool = True,
        enable_temporal: bool = True,
        enable_ethical: bool = True,
        enable_mesh: bool = True
    ):
        self.name = name
        self.cache_dir = Path(cache_dir or ".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced logging setup
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
        )
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
            
        # File handler for persistent logging
        file_handler = logging.FileHandler(self.cache_dir / f"{name}.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize automation mesh
        if enable_mesh:
            self.logger.info("Initializing automation mesh...")
            self.mesh = AutomationMesh()
            self._init_mesh_nodes()
        else:
            self.mesh = None
            self.logger.info("Automation mesh disabled")

        # Task execution setup
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._task_history: List[TaskResult] = []
        self._cache: Dict[str, Any] = {}
        
        # Initialize enhanced layers
        if enable_intelligence:
            self.intelligence = StrategyIntelligence(str(self.cache_dir / "models"))
            self.logger.info("Intelligence layer initialized")
            
        if enable_resilience:
            self.resilience = StrategyResilience(str(self.cache_dir / "checkpoints"))
            self.logger.info("Resilience layer initialized")
            
        if enable_collaboration:
            self.collaboration = StrategyCollaboration(
                self.name,
                str(self.cache_dir / "network")
            )
            self.logger.info("Collaboration layer initialized")
            
            # Register agent capabilities
            self.collaboration.register_capability(
                AgentCapability(
                    name=self.name,
                    version="1.0",
                    performance_score=1.0,
                    specializations=["task_execution", "resource_optimization"],
                    last_updated=datetime.now()
                )
            )
            
        # Initialize evolution layer
        if enable_evolution:
            self.evolution = AutonomousEvolution(str(self.cache_dir / "evolution"))
            self.logger.info("Evolution layer initialized")
            
            # Initialize base capabilities
            self.evolution.initialize_capability("task_optimization")
            self.evolution.initialize_capability("resource_management")
            
        # Initialize quantum layer
        if enable_quantum:
            self.quantum = QuantumArchitecture(str(self.cache_dir / "quantum"))
            self.logger.info("Quantum layer initialized")
            
            # Create initial quantum circuits
            self.quantum.create_superposition_circuit(num_qubits=5)
            self.quantum.create_optimization_circuit(nx.complete_graph(4))
            
        # Initialize cognitive layer
        if enable_cognitive:
            self.cognitive = CognitiveArchitecture()
            self.logger.info("Cognitive layer initialized")
            
            # Initialize emotional state
            self.cognitive.update_emotional_state(
                valence=0.5,    # Neutral valence
                arousal=0.3,    # Calm arousal
                dominance=0.7   # Confident dominance
            )
            
        # Initialize temporal layer
        if enable_temporal:
            self.temporal = TemporalProcessor(str(self.cache_dir / "temporal"))
            self.logger.info("Temporal layer initialized")
            
            # Initialize performance tracking with initial data point
            self.temporal.add_time_series(
                "task_performance",
                np.array([1.0]),  # Initial performance score
                metadata={"type": "performance_metric"}
            )
            
        # Initialize self-improvement components
        self.meta_learner = None  # To be implemented
        self.self_improver = None  # To be implemented
        self.logger.info("Self-improvement layer initialized")

        # Initialize ethical layer
        if enable_ethical:
            self.ethical = EthicalEngine(str(self.cache_dir / "ethical"))
            self.logger.info("Ethical layer initialized")
            
            # Register agent as stakeholder
            self.ethical.register_stakeholder(
                stakeholder_id=self.name,
                interests={
                    "task_success": 1.0,
                    "system_stability": 0.8,
                    "resource_efficiency": 0.7,
                    "collaboration_quality": 0.9
                }
            )
        
    def _cache_key(self, task_callable: Callable, args: tuple, kwargs: dict) -> str:
        """Generate cache key for task arguments"""
        task_str = f"{task_callable.__name__}:{str(args)}:{str(kwargs)}"
        return hashlib.sha256(task_str.encode()).hexdigest()
        
    def _save_result(self, result: TaskResult) -> None:
        """Save task result to persistent storage"""
        self._task_history.append(result)
        result_path = self.cache_dir / f"task_{result.task_id}.json"
        with open(result_path, 'w') as f:
            json.dump(result.__dict__, f, indent=2)
            
    def _init_mesh_nodes(self):
        """Initialize the automation mesh nodes"""
        async def setup_nodes():
            try:
                # Create intelligence node
                await self.mesh.add_node(
                    "intelligence",
                    ["analysis", "prediction", "optimization"],
                    {"compute": 2, "memory": 4}
                )

                # Create resilience node
                await self.mesh.add_node(
                    "resilience",
                    ["monitoring", "recovery", "fault_tolerance"],
                    {"compute": 2, "memory": 2}
                )

                # Create collaboration node
                await self.mesh.add_node(
                    "collaboration",
                    ["coordination", "knowledge_sharing", "consensus"],
                    {"compute": 1, "memory": 2}
                )

                # Create quantum node
                await self.mesh.add_node(
                    "quantum",
                    ["quantum_simulation", "quantum_optimization"],
                    {"compute": 4, "memory": 8}
                )

                # Create ethical node
                await self.mesh.add_node(
                    "ethical",
                    ["ethical_assessment", "impact_analysis", "compliance"],
                    {"compute": 1, "memory": 2}
                )

                # Create cognitive node
                await self.mesh.add_node(
                    "cognitive",
                    ["reasoning", "learning", "decision_making"],
                    {"compute": 2, "memory": 4}
                )

                self.logger.info("Automation mesh initialized successfully")

            except Exception as e:
                self.logger.error(f"Failed to initialize mesh nodes: {str(e)}")
                raise

        # Run setup
        asyncio.run(setup_nodes())

    async def optimize_mesh_async(self) -> MeshMetrics:
        """
        Optimize the automation mesh and return performance metrics
        """
        if not self.mesh:
            raise StrategyError("Automation mesh is not enabled")

        try:
            # Get current mesh metrics
            metrics = self.mesh.optimize_mesh()

            # Log optimization results
            self.logger.info(
                f"Mesh optimization results:\n"
                f"- Success Rate: {metrics.success_rate:.2%}\n"
                f"- Resource Utilization: {metrics.resource_utilization:.2%}\n"
                f"- Mesh Stability: {metrics.mesh_stability:.2%}\n"
                f"- Quantum Efficiency: {metrics.quantum_efficiency:.2%}\n"
                f"- Ethical Alignment: {metrics.ethical_alignment:.2%}\n"
                f"- Cognitive Coherence: {metrics.cognitive_coherence:.2%}"
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Mesh optimization failed: {str(e)}")
            raise

    async def execute_task_async(
        self, 
        task_callable: Callable, 
        *args, 
        cache_ttl: int = 3600,
        require_consensus: bool = False,
        share_results: bool = True,
        cognitive_processing: bool = True,
        use_mesh: bool = True,
        **kwargs
    ) -> TaskResult:
        """
        Execute a strategic task asynchronously with enhanced capabilities
        """
        task_id = str(int(time.time() * 1000))
        cache_key = self._cache_key(task_callable, args, kwargs)
        
        # Check cache
        if cache_key in self._cache:
            cached_result, expiry = self._cache[cache_key]
            if time.time() < expiry:
                self.logger.info(f"Cache hit for task: {task_callable.__name__}")
                return cached_result
                
        # Ethical assessment of task
        if hasattr(self, 'ethical'):
            ethical_assessment = self.ethical.assess_action(
                action_id=f"task_{task_id}",
                context={
                    "task_name": task_callable.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "previous_executions": len(self._task_history),
                    "system_load": len(self._cache)
                }
            )
            
            if not ethical_assessment.constraints_satisfied:
                self.logger.warning(f"Task {task_id} failed ethical assessment")
                raise TaskExecutionError(
                    f"Task execution blocked: {', '.join(ethical_assessment.reasoning)}"
                )
                
            # Impact prediction
            impact = self.ethical.predict_impact(
                action_id=f"task_{task_id}",
                context={
                    "task": task_callable.__name__,
                    "system_state": "stable",
                    "stakeholders": list(self._cache.keys())
                }
            )
            
            if impact.uncertainty > 0.8:
                self.logger.warning(
                    f"Task {task_id} has high uncertainty impact: {impact.uncertainty:.2f}"
                )
        
        # Cognitive processing of task context
        if cognitive_processing and hasattr(self, 'cognitive'):
            cognitive_state = self.cognitive.process_input(
                {
                    "task_name": task_callable.__name__,
                    "args": args,
                    "kwargs": kwargs
                },
                context={
                    "previous_executions": len(self._task_history),
                    "cache_status": "miss",
                    "system_load": len(self._cache),
                    "ethical_assessment": ethical_assessment if hasattr(self, 'ethical') else None
                }
            )
            
            # Make cognitive decision about task execution
            decision = self.cognitive.make_decision(
                cognitive_state,
                options=[
                    {"execute": "normal", "priority": "medium"},
                    {"execute": "optimized", "priority": "high"},
                    {"execute": "careful", "priority": "low"}
                ]
            )
            
            self.logger.info(f"Cognitive decision: {decision.reasoning_path}")
            
            # Update emotional state based on decision confidence
            self.cognitive.update_emotional_state(
                valence=decision.confidence,
                arousal=0.5,
                dominance=0.6
            )
                
        # Predict task performance
        if hasattr(self, 'intelligence'):
            predicted_time = self.intelligence.predict_performance(
                memory_usage=0.5,  # Placeholder
                cpu_usage=0.5,     # Placeholder
                complexity_score=1.0
            )
            self.logger.info(f"Predicted execution time: {predicted_time:.2f}s")
            
        # Check system health
        if hasattr(self, 'resilience'):
            health_report = self.resilience.get_health_report()
            if health_report["status"] != "Healthy":
                self.logger.warning(f"System health degraded: {health_report}")
                
        # Reach consensus if required
        if require_consensus and hasattr(self, 'collaboration'):
            consensus = await self.collaboration.reach_consensus(
                f"task_execution_{task_id}",
                {
                    "task": task_callable.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "cognitive_state": cognitive_state if cognitive_processing else None
                }
            )
            if not consensus["consensus_reached"]:
                raise ValueError("Failed to reach consensus for task execution")
                
        # Temporal analysis and prediction
        if hasattr(self, 'temporal'):
            # Update task performance time series
            performance_history = np.array([t.execution_time for t in self._task_history])
            if len(performance_history) > 0:
                self.temporal.add_time_series(
                    "task_performance",
                    performance_history,
                    timestamps=np.array([t.timestamp for t in self._task_history])
                )
                
                # Predict future performance
                prediction = self.temporal.forecast(
                    "task_performance",
                    horizon=5  # Predict next 5 executions
                )
                
                # Log prediction insights
                self.logger.info(
                    f"Predicted future performance: "
                    f"mean={prediction.predictions.mean():.2f}s, "
                    f"confidence={prediction.model_performance['rmse']:.2f}"
                )
                
                # Detect temporal patterns
                patterns = self.temporal.detect_temporal_patterns(
                    "task_performance"
                )
                if patterns.get("seasonality", {}).get("strongest_period"):
                    self.logger.info(
                        f"Detected performance cycle: "
                        f"{patterns['seasonality']['strongest_period']:.1f} tasks"
                    )
                
        start_time = time.time()
        self.logger.info(f"Executing task {task_id}: {task_callable.__name__}")
        
        try:
            # Execute task in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                task_callable,
                *args,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            task_result = TaskResult(
                success=True,
                result=result,
                execution_time=execution_time,
                task_id=task_id,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Cache successful results
            self._cache[cache_key] = (task_result, time.time() + cache_ttl)
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_result = TaskResult(
                success=False,
                result=None,
                execution_time=execution_time,
                task_id=task_id,
                timestamp=datetime.utcnow().isoformat(),
                error=str(e)
            )
            self.logger.error(f"Task {task_id} failed: {e}")
            
        self._save_result(task_result)
        return task_result
            
    def execute_task(
        self, 
        task_callable: Callable, 
        *args, 
        **kwargs
    ) -> TaskResult:
        """
        Synchronous wrapper for task execution
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.execute_task_async(task_callable, *args, **kwargs)
            )
        finally:
            loop.close()
            
    def get_task_history(
        self, 
        limit: Optional[int] = None,
        success_only: bool = False
    ) -> List[TaskResult]:
        """Get execution history with filtering"""
        history = self._task_history
        if success_only:
            history = [r for r in history if r.success]
        if limit:
            history = history[-limit:]
        return history
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate agent performance metrics including ethical metrics"""
        if not self._task_history:
            return {}
            
        successful_tasks = [t for t in self._task_history if t.success]
        total_tasks = len(self._task_history)
        success_rate = len(successful_tasks) / total_tasks if total_tasks > 0 else 0
        
        execution_times = [t.execution_time for t in self._task_history]
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        metrics = {
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "total_tasks": total_tasks,
            "successful_tasks": len(successful_tasks)
        }
        
        # Add ethical metrics if available
        if hasattr(self, 'ethical'):
            ethical_metrics = self.ethical.get_ethical_metrics()
            metrics.update({
                "ethical_score": ethical_metrics.get("average_score", 0.0),
                "constraint_satisfaction": ethical_metrics.get("constraint_satisfaction_rate", 0.0),
                "impact_uncertainty": ethical_metrics.get("impact_metrics", {}).get("average_uncertainty", 0.0),
                "impact_reversibility": ethical_metrics.get("impact_metrics", {}).get("average_reversibility", 1.0)
            })
            
        return metrics
        
    def clear_cache(self) -> None:
        """Clear task cache"""
        self._cache.clear()
        self.logger.info("Task cache cleared")
