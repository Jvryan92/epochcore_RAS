"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
Simple test for StrategyDECK agent initialization
"""
import asyncio
from strategydeck_agent import StrategyDeckAgent

def test_agent():
    print("Creating agent...")
    agent = StrategyDeckAgent(
        name="TestAgent",
        enable_mesh=True,
        enable_quantum=True,
        enable_ethical=True,
        enable_cognitive=True
    )
    
    print("\nVerifying mesh initialization...")
    if agent.mesh and agent.mesh.nodes:
        node_types = [node.node_type for node in agent.mesh.nodes.values()]
        print(f"Found mesh nodes: {node_types}")
        return True
    else:
        print("❌ No mesh nodes found")
        return False

if __name__ == "__main__":
    success = test_agent()
    if success:
        print("\n✅ Agent initialized successfully with mesh enabled")
    else:
        print("\n❌ Agent initialization failed")
