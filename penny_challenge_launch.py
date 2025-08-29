"""
Agent Configuration for Penny Challenge Revenue Drive
"""

from agent_task_distribution import initialize_revenue_agents
from penny_challenge import REVENUE_SOURCES, PennyChallenge


def configure_penny_challenge():
    """Configure agents for immediate revenue generation focus."""

    # Initialize core systems
    manager = initialize_revenue_agents()
    challenge = PennyChallenge()

    # Configure agent priorities
    strategist = manager.get_agent("strategist")
    if strategist:
        strategist.config.update({
            "priority_tasks": ["real_revenue_generation"],
            "target_metrics": {
                "min_transaction_usd": 0.01,
                "min_transaction_mesh": 1.00
            }
        })

    ecommerce = manager.get_agent("ecommerce")
    if ecommerce:
        ecommerce.config.update({
            "active_products": REVENUE_SOURCES,
            "payment_processors": ["coinbase"],
            "min_transaction": {
                "usd": 0.01,
                "mesh": 1.00
            }
        })

    monitor = manager.get_agent("monitor")
    if monitor:
        monitor.config.update({
            "priority_metrics": [
                "real_transactions",
                "usd_revenue",
                "mesh_revenue"
            ],
            "alert_thresholds": {
                "transaction_success": 1,  # Alert on first success
                "revenue_milestone": 0.01  # Alert on first penny
            }
        })

    # Start revenue tracking
    manager.start_all_agents()

    return {
        "manager": manager,
        "challenge": challenge
    }


if __name__ == "__main__":
    system = configure_penny_challenge()
    print("\nPenny Challenge Activated!")
    print("------------------------")
    print("Target: First $0.01 USD or 1 MESH transaction")
    print("Status: Monitoring for first revenue...")
