"""
Environment Configuration Loader
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def load_env(env_file: Optional[str] = None) -> Dict[str, str]:
    """Load environment variables from .env file."""
    if env_file is None:
        env_file = Path("/workspaces/epochcore_RAS/.env")

    if not env_file.exists():
        raise FileNotFoundError(f"Environment file not found: {env_file}")

    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')
                # Also set in environment
                os.environ[key.strip()] = value.strip().strip('"\'')

    return env_vars


def get_secrets() -> Dict[str, str]:
    """Get payment processing secrets."""
    try:
        env_vars = load_env()
        required_keys = [
            'COINBASE_EMAIL',
            'COINBASE_API_KEY',
            'STRIPE_API_KEY',
            'MESH_ADDRESS'
        ]

        missing = [key for key in required_keys if key not in env_vars]
        if missing:
            print(f"Warning: Missing environment variables: {', '.join(missing)}")

        return env_vars
    except Exception as e:
        print(f"Error loading environment: {e}")
        return {}
