"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
Digital Watermarking System for EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ContentWatermark:
    """Digital watermark system for protecting generated content."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize watermark system with secret key."""
        self.secret_key = secret_key or self._generate_secret()
        self._watermark_version = "1.0.0"

    def _generate_secret(self) -> str:
        """Generate a unique secret key."""
        timestamp = str(int(time.time()))
        unique_id = hashlib.sha256(timestamp.encode()).hexdigest()
        return f"epochcore_{unique_id[:16]}"

    def apply_watermark(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply digital watermark to content."""
        # Create watermark data
        watermark = {
            "timestamp": datetime.now().isoformat(),
            "version": self._watermark_version,
            "copyright": "© 2024 John Ryan, EpochCore Business",
            "content_id": content.get("content_id", ""),
            "agent_id": content.get("agent_id", ""),
            "content_type": content.get("content_type", "")
        }

        # Generate HMAC signature
        signature = self._generate_signature(json.dumps(watermark))
        watermark["signature"] = signature

        # Add watermark to content
        content["_watermark"] = watermark
        content["_protected"] = True

        return content

    def verify_watermark(self, content: Dict[str, Any]) -> bool:
        """Verify content watermark authenticity."""
        if not content.get("_watermark"):
            return False

        watermark = content["_watermark"]
        stored_sig = watermark.pop("signature", None)
        if not stored_sig:
            return False

        # Verify signature
        current_sig = self._generate_signature(json.dumps(watermark))
        watermark["signature"] = stored_sig  # Restore signature

        return hmac.compare_digest(stored_sig, current_sig)

    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for watermark."""
        hmac_obj = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        )
        return base64.b64encode(hmac_obj.digest()).decode()
