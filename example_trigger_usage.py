"""Example usage of the Agentic Trigger System"""

import asyncio

from trigger_system import AgenticTrigger, TriggerSystem


async def main():
    # Initialize trigger system
    ts = TriggerSystem()
    await ts.initialize()

    # Create a sample trigger
    sample_trigger = AgenticTrigger(
        id=4,
        key="LEGION-SEED-001",
        title="Deployment Framework",
        family="LEGION",
        exec_command="initialize_deployment",
        comp_base="deployment_system",
        scale_command="scale_deployment_nodes",
        recur_command="optimize_deployment",
        full_execution="deploy_full_framework",
        dep_from=0.3,
        dep_to=1.0,
        deps_list=[1, 2, 3]  # Depends on ASTRA, CRUX, and AETHER SEED triggers
    )

    # Register the trigger
    await ts.register_trigger(sample_trigger)

    # Check tier status
    seed_status = await ts.get_tier_status("SEED")
    print("SEED Tier Status:", seed_status)

    # Check family status
    legion_status = await ts.get_family_status("LEGION")
    print("LEGION Family Status:", legion_status)

    # Execute triggers in sequence
    context = {}

    # Execute ASTRA-SEED-001
    print("\nExecuting ASTRA-SEED-001...")
    result = await ts.execute_trigger("ASTRA-SEED-001", context)
    print(f"Status: {result['command_result']['status']}")

    # Execute CRUX-SEED-001
    print("\nExecuting CRUX-SEED-001...")
    result = await ts.execute_trigger("CRUX-SEED-001", context)
    print(f"Status: {result['command_result']['status']}")

    # Execute AETHER-SEED-001
    print("\nExecuting AETHER-SEED-001...")
    result = await ts.execute_trigger("AETHER-SEED-001", context)
    print(f"Status: {result['command_result']['status']}")

    # Execute LEGION-SEED-001
    print("\nExecuting LEGION-SEED-001...")
    result = await ts.execute_trigger("LEGION-SEED-001", context)
    print(f"Status: {result['command_result']['status']}")

    print("\nTrigger execution sequence completed!")

if __name__ == "__main__":
    asyncio.run(main())
