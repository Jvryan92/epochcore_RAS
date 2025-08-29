"""
PROTECTED FILE - EPOCHCORE RAS PAYMENT GATEWAY CONFIG
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from pathlib import Path

import yaml

# Base payment gateway configuration
PAYMENT_CONFIG = {
    "gateways": {
        "stripe": {
            "enabled": True,
            "mode": "live",
            "auto_payout": True,
            "payout_schedule": "2_days",
            "currency": "USD",
            "methods": ["card", "ach", "wire"],
            "webhook_url": "/api/webhooks/stripe"
        },
        "paypal": {
            "enabled": True,
            "mode": "live",
            "auto_payout": True,
            "payout_schedule": "instant",
            "currency": "USD",
            "methods": ["paypal", "card"],
            "webhook_url": "/api/webhooks/paypal"
        },
        "wire": {
            "enabled": True,
            "mode": "manual",
            "auto_payout": False,
            "payout_schedule": "3_5_days",
            "currency": "USD",
            "methods": ["wire"],
            "webhook_url": "/api/webhooks/wire"
        },
        "ach": {
            "enabled": True,
            "mode": "live",
            "auto_payout": True,
            "payout_schedule": "3_days",
            "currency": "USD",
            "methods": ["ach"],
            "webhook_url": "/api/webhooks/ach"
        }
    },

    "payout_rules": {
        "minimum_payout": "100.00",
        "maximum_payout": "50000.00",
        "hold_period": "0",  # Instant release
        "verification_required": True
    },

    "revenue_rules": {
        "game_sales": {
            "share": "1.00",  # 100%
            "instant_settlement": True,
            "reserve_percentage": "0.00"
        },
        "in_app": {
            "share": "0.70",  # 70%
            "instant_settlement": True,
            "reserve_percentage": "0.00"
        },
        "creator_platform": {
            "share": "0.90",  # 90%
            "instant_settlement": True,
            "reserve_percentage": "0.00"
        },
        "enterprise": {
            "share": "1.00",  # 100%
            "instant_settlement": False,
            "payment_terms": "net30",
            "reserve_percentage": "0.00"
        }
    },

    "security": {
        "require_2fa": True,
        "ip_whitelist": True,
        "max_daily_payout": "100000.00",
        "suspicious_activity_threshold": "10000.00"
    },

    "notifications": {
        "payment_received": True,
        "payout_initiated": True,
        "payout_completed": True,
        "balance_low": True,
        "suspicious_activity": True
    },

    "reporting": {
        "daily_summary": True,
        "weekly_report": True,
        "monthly_statement": True,
        "annual_tax_docs": True,
        "export_formats": ["csv", "pdf", "json"]
    }
}


def save_config():
    """Save payment gateway configuration"""
    config_path = Path("config/payment_gateway.yml")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        yaml.dump(PAYMENT_CONFIG, f, default_flow_style=False)

    print(f"Payment gateway configuration saved to {config_path}")
    print("\nPayment Methods Configured:")
    print("----------------------------")
    print("✓ Stripe (Direct Deposit/Card)")
    print("✓ PayPal (Digital Wallet)")
    print("✓ Wire Transfer (Bank)")
    print("✓ ACH (Direct Bank)")
    print("\nPayout Schedules:")
    print("----------------")
    print("• Direct Deposit: Every 2 days")
    print("• PayPal: Instant available")
    print("• Wire: 3-5 business days")
    print("• ACH: 3 business days")
    print("\nRevenue Shares:")
    print("--------------")
    print("• Game Sales: 100%")
    print("• In-App Purchases: 70%")
    print("• Creator Platform: 90%")
    print("• Enterprise: 100%")


if __name__ == "__main__":
    save_config()
