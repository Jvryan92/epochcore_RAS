"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class SecureConfig:
    """Secure configuration management for MeshCredit system."""

    def __init__(self):
        self.config_dir = Path.home() / '.meshcredit'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self._load_config()

    def _load_config(self) -> None:
        """Load or create configuration."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "wallets": {},
                "integrations": {
                    "coinbase": {
                        "enabled": False,
                        "api_key_env": "COINBASE_API_KEY",
                        "api_secret_env": "COINBASE_API_SECRET"
                    }
                }
            }
            self._save_config()

    def _save_config(self) -> None:
        """Save configuration securely."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
        # Set secure permissions
        self.config_file.chmod(0o600)

    def setup_coinbase(self) -> bool:
        """Configure Coinbase integration using environment variables."""
        print("\n=== Coinbase Integration Setup ===")
        print("\nFor security, add these lines to your ~/.bashrc or ~/.zshrc:")
        print('export COINBASE_API_KEY="your_api_key"')
        print('export COINBASE_API_SECRET="your_api_secret"')
        print("\nOr set them for the current session:")
        print('export COINBASE_API_KEY="your_api_key"')
        print('export COINBASE_API_SECRET="your_api_secret"')

        # Check if environment variables are set
        api_key = os.getenv("COINBASE_API_KEY")
        api_secret = os.getenv("COINBASE_API_SECRET")

        if not api_key or not api_secret:
            print("\n❌ Environment variables not found!")
            print("Please set COINBASE_API_KEY and COINBASE_API_SECRET")
            return False

        # Update config
        self.config["integrations"]["coinbase"]["enabled"] = True
        self._save_config()

        print("\n✅ Coinbase integration configured!")
        print("Credentials will be loaded securely from environment")
        return True

    def get_coinbase_credentials(self) -> Optional[Dict[str, str]]:
        """Securely retrieve Coinbase credentials."""
        if not self.config["integrations"]["coinbase"]["enabled"]:
            return None

        api_key = os.getenv("COINBASE_API_KEY")
        api_secret = os.getenv("COINBASE_API_SECRET")

        if not api_key or not api_secret:
            return None

        return {
            "api_key": api_key,
            "api_secret": api_secret
        }

    def reset_coinbase(self) -> None:
        """Reset Coinbase integration configuration."""
        self.config["integrations"]["coinbase"]["enabled"] = False
        self._save_config()
        print("\n🔄 Coinbase integration reset")
        print("Environment variables should be unset manually")


def main():
    """Main execution function."""
    config = SecureConfig()

    print("\n=== MeshCredit Secure Configuration ===")
    print("\nCurrent Status:")
    print(f"Config Location: {config.config_file}")
    print(f"Coinbase Enabled: {config.config['integrations']['coinbase']['enabled']}")

    # Setup example
    if config.setup_coinbase():
        creds = config.get_coinbase_credentials()
        if creds:
            print("\nCredentials loaded successfully!")
            print("API Key length:", len(creds["api_key"]))
            # Never print actual credentials!

    # How to reset if needed
    # config.reset_coinbase()


if __name__ == "__main__":
    main()
