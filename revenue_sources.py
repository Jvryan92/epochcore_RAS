"""
Expanded Revenue Sources System
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict


@dataclass
class RevenueProduct:
    """Product definition for revenue generation."""
    id: str
    name: str
    description: str
    usd_price: Decimal
    mesh_price: Decimal
    category: str
    features: list
    trial_available: bool = False
    subscription: bool = False


class RevenueSourceManager:
    def __init__(self):
        self.categories = {
            "instant": "Instant Access Features",
            "support": "Support Services",
            "early_access": "Early Access Program",
            "api": "API Services",
            "training": "Training & Tutorials",
            "custom": "Custom Solutions"
        }

        self.products = self._initialize_products()

    def _initialize_products(self) -> Dict[str, RevenueProduct]:
        """Initialize all available revenue products."""
        return {
            # Instant Access Products
            "basic_access": RevenueProduct(
                id="basic_access",
                name="Basic Access",
                description="Instant access to core features",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="instant",
                features=["Core functionality", "Basic support"]
            ),

            # Support Services
            "priority_support": RevenueProduct(
                id="priority_support",
                name="Priority Support",
                description="24/7 priority support access",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="support",
                features=["24/7 support", "1-hour response time"]
            ),

            # Early Access
            "beta_access": RevenueProduct(
                id="beta_access",
                name="Beta Access",
                description="Early access to beta features",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="early_access",
                features=["Beta features", "Feedback priority"]
            ),

            # API Access
            "api_basic": RevenueProduct(
                id="api_basic",
                name="API Basic",
                description="Basic API access package",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="api",
                features=["100 API calls", "Basic endpoints"]
            ),

            # Training
            "quick_start": RevenueProduct(
                id="quick_start",
                name="Quick Start Guide",
                description="Essential getting started guide",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="training",
                features=["Setup guide", "Basic tutorials"]
            ),

            # Custom Solutions
            "custom_basic": RevenueProduct(
                id="custom_basic",
                name="Basic Customization",
                description="Basic level customization",
                usd_price=Decimal("0.01"),
                mesh_price=Decimal("1.00"),
                category="custom",
                features=["Minor customization", "Basic branding"]
            ),

            # Bundle Deals
            "starter_bundle": RevenueProduct(
                id="starter_bundle",
                name="Starter Bundle",
                description="Essential features bundle",
                usd_price=Decimal("0.03"),
                mesh_price=Decimal("3.00"),
                category="instant",
                features=[
                    "Basic Access",
                    "Quick Start Guide",
                    "Basic API Access"
                ]
            ),
        }

    def get_product(self, product_id: str) -> RevenueProduct:
        """Get product by ID."""
        return self.products.get(product_id)

    def list_products(self, category: str = None) -> Dict[str, RevenueProduct]:
        """List all products, optionally filtered by category."""
        if category:
            return {
                k: v for k, v in self.products.items()
                if v.category == category
            }
        return self.products

    def get_bundles(self) -> Dict[str, RevenueProduct]:
        """Get all available product bundles."""
        return {
            k: v for k, v in self.products.items()
            if len(v.features) >= 3
        }

    def get_lowest_price_products(self) -> Dict[str, RevenueProduct]:
        """Get products at minimum price point."""
        min_usd = min(p.usd_price for p in self.products.values())
        return {
            k: v for k, v in self.products.items()
            if v.usd_price == min_usd
        }


if __name__ == "__main__":
    # Initialize manager
    manager = RevenueSourceManager()

    # Display all penny products
    print("Available $0.01 Products:")
    print("-----------------------")
    for product_id, product in manager.get_lowest_price_products().items():
        print(f"\n{product.name}")
        print(f"Description: {product.description}")
        print(f"Price: ${product.usd_price} or {product.mesh_price} MESH")
        print(f"Features: {', '.join(product.features)}")
