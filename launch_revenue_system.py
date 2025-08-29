"""
Launch Script for Complete Revenue System
"""

import asyncio
from datetime import datetime

from agent_task_distribution import initialize_revenue_agents
from payment_processor import PaymentProcessor
from penny_challenge import PennyChallenge
from revenue_monitor import RevenueMonitor
from revenue_sources import RevenueSourceManager


async def launch_complete_system():
    """Launch the complete revenue generation system."""

    # Initialize all components
    challenge = PennyChallenge()
    monitor = RevenueMonitor()
    processor = PaymentProcessor()
    sources = RevenueSourceManager()
    agents = initialize_revenue_agents()

    # Start monitoring
    monitor_task = asyncio.create_task(monitor.monitor_transactions())

    # Display available products
    print("\nAvailable Products for Purchase:")
    print("-------------------------------")
    for product in sources.get_lowest_price_products().values():
        print(f"\n{product.name} - ${product.usd_price} or {product.mesh_price} MESH")
        print(f"Description: {product.description}")
        print("\nPayment Options:")
        for method, details in processor.payment_methods.items():
            if details.get("enabled", True):
                currencies = ", ".join(details["currencies"])
                print(f"- {method.title()}: ({currencies})")

    print("\nReady to accept payments!")
    print("Send to: jryan2k19@gmail.com")
    print("Monitoring for first revenue...")

    try:
        # Keep system running
        await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        monitor_task.cancel()
        agents.stop_all_agents()

if __name__ == "__main__":
    # Launch everything
    print("Launching Complete Revenue System...")
    asyncio.run(launch_complete_system())
