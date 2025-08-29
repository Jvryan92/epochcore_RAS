"""
Admin access management for social media accounts
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional

class AdminAccess:
    def __init__(self):
        self.credentials_file = os.path.join(
            os.path.dirname(__file__),
            "admin_credentials.json"
        )
        self._load_credentials()
    
    def _load_credentials(self):
        """Load admin credentials if they exist"""
        try:
            with open(self.credentials_file, "r") as f:
                self.credentials = json.load(f)
        except FileNotFoundError:
            self.credentials = {
                "admin": {
                    "email": "jryan2k19@gmail.com",
                    "last_login": None
                },
                "platforms": {
                    "twitter": {
                        "last_insights_check": None
                    },
                    "linkedin": {
                        "last_insights_check": None
                    },
                    "discord": {
                        "last_insights_check": None
                    }
                }
            }
            self._save_credentials()
    
    def _save_credentials(self):
        """Save admin credentials"""
        with open(self.credentials_file, "w") as f:
            json.dump(self.credentials, f, indent=4)
    
    def log_insights_check(self, platform: str):
        """Log when admin checks platform insights"""
        if platform in self.credentials["platforms"]:
            self.credentials["platforms"][platform]["last_insights_check"] = \
                datetime.utcnow().isoformat()
            self._save_credentials()
    
    def get_last_insights_check(self, platform: str) -> Optional[str]:
        """Get when admin last checked platform insights"""
        if platform in self.credentials["platforms"]:
            return self.credentials["platforms"][platform]["last_insights_check"]
        return None

    def get_insights_summary(self) -> Dict:
        """Get summary of insights access"""
        return {
            "admin_email": self.credentials["admin"]["email"],
            "platform_checks": {
                platform: data["last_insights_check"]
                for platform, data in self.credentials["platforms"].items()
            }
        }
