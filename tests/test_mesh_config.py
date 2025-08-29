"""
Test configuration of StrategyDECK agent and automation mesh
"""

import asyncio
from strategydeck_agent import StrategyDeckAgent


async def test_mesh_configuration():
    # Initialize agent with mesh enabled
    agent = StrategyDeckAgent(
        name="TestAgent",
        enable_mesh=True,
        enable_quantum=True,
        enable_ethical=True,
        enable_cognitive=True,
    )

    # Verify mesh nodes
    if not agent.mesh or not agent.mesh.nodes:
        print("❌ Mesh initialization failed - no nodes found")
        return False

    node_types = [node.node_type for node in agent.mesh.nodes.values()]
    expected_nodes = [
        "intelligence",
        "resilience",
        "collaboration",
        "quantum",
        "ethical",
        "cognitive",
    ]

    missing_nodes = [n for n in expected_nodes if n not in node_types]
    if missing_nodes:
        print(f"❌ Missing mesh nodes: {missing_nodes}")
        return False

    # Test mesh optimization
    try:
        metrics = await agent.optimize_mesh_async()
        print("\n=== Mesh Configuration Status ===")
        print(f"Success Rate: {metrics.success_rate:.2%}")
        print(f"Resource Utilization: {metrics.resource_utilization:.2%}")
        print(f"Mesh Stability: {metrics.mesh_stability:.2%}")
        print(f"Quantum Efficiency: {metrics.quantum_efficiency:.2%}")
        print(f"Ethical Alignment: {metrics.ethical_alignment:.2%}")
        print(f"Cognitive Coherence: {metrics.cognitive_coherence:.2%}")

        # Verify metrics are within acceptable ranges
        if (
            metrics.success_rate < 0.5
            or metrics.mesh_stability < 0.5
            or metrics.resource_utilization < 0.1
        ):
            print("❌ Mesh performance metrics below acceptable thresholds")
            return False

        print("\n✅ Mesh configuration successful!")
        return True

    except Exception as e:
        print(f"❌ Mesh optimization failed: {str(e)}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_mesh_configuration())
