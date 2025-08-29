"""
PROTECTED FILE - EPOCHCORE RAS PAYMENT CONFIG
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

# Stripe Product Configuration
# IMPORTANT: Replace these IDs with your actual Stripe product and price IDs
# Find these in your Stripe Dashboard after creating products

STRIPE_PRODUCTS = {
    # Game Base
    'game_base': {
        'name': 'EpochCore Game',
        'price_id': 'price_xxxxx',  # Replace with actual price ID
        'product_id': 'prod_xxxxx',  # Replace with actual product ID
        'description': 'EpochCore Base Game Access'
    },

    # Season Pass
    'season_pass': {
        'name': 'Season Pass',
        'price_id': 'price_xxxxx',
        'product_id': 'prod_xxxxx',
        'description': 'Access to seasonal content and features'
    },

    # Creator Platform
    'creator_platform': {
        'name': 'Creator Platform Access',
        'price_id': 'price_xxxxx',
        'product_id': 'prod_xxxxx',
        'description': 'Full access to creator tools and marketplace'
    },

    # Enterprise License
    'enterprise_license': {
        'name': 'Enterprise License',
        'price_id': 'price_xxxxx',
        'product_id': 'prod_xxxxx',
        'description': 'Enterprise-level access and support'
    }
}

# Revenue Share Configuration
REVENUE_SHARES = {
    'GAME_SALE': 1.00,     # 100% to EpochCore
    'IN_APP': 0.70,        # 70% after platform fees
    'CREATOR': 0.90,       # 90% to EpochCore
    'ENTERPRISE': 1.00     # 100% to EpochCore
}

# Webhook Configuration
WEBHOOK_CONFIG = {
    'endpoints': {
        'stripe': '/webhook/stripe',
        'health': '/health'
    },
    'allowed_events': [
        'payment_intent.succeeded',
        'charge.refunded',
        'charge.dispute.created',
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted'
    ]
}

# Payment Processing Configuration
PAYMENT_CONFIG = {
    'currency': 'usd',
    'auto_payout': True,
    'payout_schedule': 'daily',
    'minimum_payout': 1.00,
    'supported_payment_methods': [
        'card',
        'us_bank_account',
        'link'
    ]
}

# Reporting Configuration
REPORTING_CONFIG = {
    'transaction_log': 'transactions',
    'report_formats': ['json', 'csv'],
    'automated_reports': {
        'daily_summary': True,
        'weekly_report': True,
        'monthly_statement': True
    }
}

# Security Configuration
SECURITY_CONFIG = {
    'require_3ds': True,
    'max_retry_attempts': 3,
    'suspicious_amount_threshold': 5000.00,
    'require_billing_address': True
}
