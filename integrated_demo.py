#!/usr/bin/env python3
"""
Integrated Agent System Demo

This script demonstrates the use of the Integrated Agent System
that connects the Kids Friendly AI Guide, Epoch Audit System,
and Mesh Trigger Core with the existing EpochCore RAS agent architecture.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path

# Import the integrated system
from integrated_agent_system import (
    EpochAuditAdapter,
    IntegratedAgentSystem,
    KidsFriendlyAgentAdapter,
    MeshTriggerAdapter,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("IntegratedDemo")


async def demo_kids_friendly_guide(system):
    """Demonstrate the Kids Friendly AI Guide."""
    logger.info("=== Demonstrating Kids Friendly AI Guide ===")

    # Get explanations for different ages
    ages = [4, 7, 10, 12]
    for age in ages:
        explanation = await system.get_child_friendly_explanation(age)
        logger.info(f"\nExplanation for {age}-year-old:")
        logger.info(explanation)

    # Get content for a specific age
    if system.kids_friendly:
        content = system.kids_friendly.get_content_for_child(8)
        logger.info("\nContent for 8-year-old:")
        logger.info(f"Metaphor: {content['metaphor']}")
        logger.info(f"Stories count: {len(content['stories'])}")
        logger.info(f"Activities count: {len(content['activities'])}")

        # Get interactive dialog
        dialog = system.kids_friendly.get_dialog_for_child(6)
        logger.info("\nInteractive dialog for 6-year-old:")
        for exchange in dialog[:2]:  # Show just the first 2 exchanges
            logger.info(f"{exchange['speaker']}: {exchange['text']}")

    # Broadcast an activity
    if system.kids_friendly:
        success = await system.kids_friendly.broadcast_activity(
            age_range=[6, 8],
            activity_type="story"
        )
        logger.info(f"\nActivity broadcast success: {success}")


async def demo_epoch_audit(system):
    """Demonstrate the Epoch Audit System."""
    logger.info("\n=== Demonstrating Epoch Audit System ===")

    # Log various events
    if system.epoch_audit:
        # Log standard event
        entry = system.epoch_audit.log_agent_event(
            agent_id="demo_agent",
            event="demo_started",
            note="Demo of audit system started",
            demo_timestamp=datetime.now().isoformat()
        )
        logger.info(f"Logged event: {entry['event']} ({entry['ts']})")

        # Create a seal for data
        data = f"Demo data created at {datetime.now().isoformat()}"
        seal = system.epoch_audit.create_agent_seal("demo_agent", data)
        logger.info(f"Created seal: {seal['file']}")

        # Verify the seal
        valid = system.epoch_audit.verify_agent_seal(Path(seal["file"]), data)
        logger.info(f"Seal verification: {valid}")

        # Test Alpha Ceiling
        original = 150
        capped = system.epoch_audit.enforce_resource_limit(
            original, "memory", ceiling=100)
        logger.info(f"Alpha Ceiling: {original} capped to {capped}")

        # Create Phone Audit Scroll
        audit_info = system.epoch_audit.create_phone_audit_scroll()
        logger.info(f"Created Phone Audit Scroll: {audit_info['file']}")

        # Broadcast an alert
        success = await system.epoch_audit.broadcast_audit_alert(
            alert_type="test_alert",
            details={"source": "demo", "level": "info"}
        )
        logger.info(f"Alert broadcast success: {success}")


async def demo_mesh_trigger(system):
    """Demonstrate the Mesh Trigger Core."""
    logger.info("\n=== Demonstrating Mesh Trigger Core ===")

    if system.mesh_trigger:
        # Register a custom trigger
        trigger_info = system.mesh_trigger.register_agent_trigger(
            trigger_id="demo_trigger",
            description="A demonstration trigger",
            resource_requirement=30,
            trigger_type="standard"
        )
        logger.info(f"Registered trigger: {trigger_info['id']}")

        # Register a handler
        def demo_handler(context):
            logger.info(f"Demo handler called with context: {context}")
            return {"status": "processed", "timestamp": datetime.now().isoformat()}

        success = system.mesh_trigger.register_handler("demo_trigger", demo_handler)
        logger.info(f"Handler registration: {success}")

        # Create a trigger seal
        context = {"demo": True, "timestamp": datetime.now().isoformat()}
        seal = system.mesh_trigger.create_trigger_seal("demo_trigger", context)
        logger.info(f"Created trigger seal: {seal}")

        # Verify the seal
        valid = system.mesh_trigger.verify_trigger_seal(seal)
        logger.info(f"Trigger seal verification: {valid}")

        # Activate the trigger
        activation = system.mesh_trigger.activate_trigger("demo_trigger", context)
        logger.info(f"Trigger activation: {activation}")

        # Broadcast the trigger
        success = await system.mesh_trigger.broadcast_trigger_activation(
            "demo_trigger",
            context
        )
        logger.info(f"Trigger broadcast success: {success}")


async def demo_integrated_features(system):
    """Demonstrate integrated system features."""
    logger.info("\n=== Demonstrating Integrated Features ===")

    # System optimization
    logger.info("Running system optimization...")
    results = await system.optimize_system()
    if results.get("success"):
        if "mesh_metrics" in results:
            metrics = results["mesh_metrics"]
            logger.info(f"Success Rate: {metrics.get('success_rate', 0):.2%}")
            logger.info(
                f"Resource Utilization: {metrics.get('resource_utilization', 0):.2%}")
            logger.info(f"Mesh Stability: {metrics.get('mesh_stability', 0):.2%}")
    else:
        logger.info(f"Optimization failed: {results.get('error', 'Unknown error')}")

    # Create system audit
    try:
        logger.info("Creating system audit...")
        audit_info = system.create_system_audit()
        logger.info(f"Audit timestamp: {audit_info.get('timestamp')}")
        logger.info(f"Audit scroll: {audit_info.get('audit_scroll', {}).get('file')}")
    except Exception as e:
        logger.error(f"Audit creation failed: {e}")

    # Activate a system trigger
    try:
        logger.info("Activating system heartbeat trigger...")
        activation = await system.activate_system_trigger(
            "system_heartbeat",
            {"source": "demo", "timestamp": datetime.now().isoformat()}
        )
        logger.info(f"Activation status: {activation.get('status')}")
    except Exception as e:
        logger.error(f"Trigger activation failed: {e}")


async def run_simulated_workload(system, duration=60):
    """
    Run a simulated workload for the specified duration.

    Args:
        system: The integrated system
        duration: Duration in seconds to run the simulation
    """
    logger.info(f"\n=== Running Simulated Workload ({duration}s) ===")

    start_time = time.time()
    events = 0

    # Possible ages for kids content
    ages = [3, 5, 7, 9, 11, 13]

    # Possible triggers to activate
    triggers = ["system_heartbeat", "mesh_optimize"]

    # Create a tasks list
    tasks = []

    # Run until duration expires
    while time.time() - start_time < duration:
        # Choose a random action
        action = random.choice([
            "kids_explanation",
            "kids_content",
            "audit_log",
            "trigger_activation",
            "system_audit"
        ])

        if action == "kids_explanation":
            age = random.choice(ages)
            tasks.append(asyncio.create_task(
                system.get_child_friendly_explanation(age)
            ))

        elif action == "kids_content" and system.kids_friendly:
            age = random.choice(ages)
            system.kids_friendly.get_content_for_child(age)

        elif action == "audit_log" and system.epoch_audit:
            system.epoch_audit.log_agent_event(
                agent_id=f"sim_agent_{random.randint(1, 10)}",
                event=f"simulated_event_{random.randint(1, 5)}",
                note="Simulated workload event",
                simulation_id=events
            )

        elif action == "trigger_activation":
            trigger = random.choice(triggers)
            tasks.append(asyncio.create_task(
                system.activate_system_trigger(
                    trigger,
                    {"simulation": True, "event_id": events}
                )
            ))

        elif action == "system_audit" and random.random() < 0.1:  # 10% chance
            try:
                system.create_system_audit()
            except Exception:
                pass

        # Clean up completed tasks
        new_tasks = []
        for task in tasks:
            if task.done():
                try:
                    task.result()  # Get result to prevent warning about not retrieving result
                except Exception:
                    pass
            else:
                new_tasks.append(task)
        tasks = new_tasks

        events += 1

        # Sleep a bit to prevent overwhelming the system
        await asyncio.sleep(0.1)

    # Wait for any remaining tasks
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.info(f"Simulated workload completed with {events} events")

    # Create final audit
    logger.info("Creating final system audit...")
    try:
        audit_info = system.create_system_audit()
        logger.info(
            f"Final audit created: {audit_info.get('audit_scroll', {}).get('file')}")
    except Exception as e:
        logger.error(f"Final audit failed: {e}")


async def main():
    """Main demonstration function."""
    logger.info("Starting Integrated Agent System Demo")

    # Create demo directory
    demo_dir = Path("./demo_data")
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Create integrated system
    system = IntegratedAgentSystem(
        name="IntegratedDemo",
        data_dir=str(demo_dir)
    )

    try:
        # Run demos
        await demo_kids_friendly_guide(system)
        await demo_epoch_audit(system)
        await demo_mesh_trigger(system)
        await demo_integrated_features(system)

        # Run simulated workload (shorter for demo)
        await run_simulated_workload(system, duration=10)

    finally:
        # Clean shutdown
        system.shutdown()
        logger.info("Demo completed")


if __name__ == "__main__":
    asyncio.run(main())
