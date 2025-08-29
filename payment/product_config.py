"""
PROTECTED FILE - EPOCHCORE RAS PRODUCT CONFIGURATION
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List


@dataclass
class ProductTier:
    name: str
    price: Decimal
    features: List[str]
    billing: str
    description: str


@dataclass
class GameProduct:
    name: str
    type: str
    tiers: Dict[str, ProductTier]
    category: str


class ProductConfiguration:
    def __init__(self):
        # Core Game Products
        self.game_products = {
            "BASE_GAME": GameProduct(
                name="EpochCore Game",
                type="one_time",
                tiers={
                    "STANDARD": ProductTier(
                        name="Standard Edition",
                        price=Decimal("29.99"),
                        features=[
                            "Full Game Access",
                            "Basic Character Customization",
                            "Standard Gameplay Modes",
                            "Community Access"
                        ],
                        billing="one_time",
                        description="Enter the EpochCore universe with our standard edition"
                    ),
                    "DELUXE": ProductTier(
                        name="Deluxe Edition",
                        price=Decimal("49.99"),
                        features=[
                            "All Standard Features",
                            "Exclusive Character Skins",
                            "Digital Soundtrack",
                            "Digital Artbook",
                            "Bonus In-Game Currency"
                        ],
                        billing="one_time",
                        description="Enhanced gaming experience with exclusive digital content"
                    ),
                    "ULTIMATE": ProductTier(
                        name="Ultimate Edition",
                        price=Decimal("79.99"),
                        features=[
                            "All Deluxe Features",
                            "Season 1 Pass Included",
                            "Exclusive Ultimate Skins",
                            "Priority Server Queue",
                            "Special Title: 'Founder'",
                            "Early Access to New Features"
                        ],
                        billing="one_time",
                        description="The complete EpochCore experience with all benefits"
                    )
                },
                category="game"
            ),

            # Season Pass Products
            "SEASON_PASS": GameProduct(
                name="EpochCore Season Pass",
                type="recurring",
                tiers={
                    "BASIC": ProductTier(
                        name="Battle Pass",
                        price=Decimal("9.99"),
                        features=[
                            "Seasonal Rewards Track",
                            "Basic Seasonal Items",
                            "XP Boosters",
                            "Season Challenges"
                        ],
                        billing="seasonal",
                        description="Access seasonal content and rewards"
                    ),
                    "PREMIUM": ProductTier(
                        name="Premium Pass",
                        price=Decimal("14.99"),
                        features=[
                            "All Battle Pass Features",
                            "Premium Seasonal Items",
                            "Exclusive Challenges",
                            "Bonus XP Boosters",
                            "Premium Season Title"
                        ],
                        billing="seasonal",
                        description="Enhanced seasonal rewards and exclusive items"
                    ),
                    "ANNUAL": ProductTier(
                        name="Annual Pass",
                        price=Decimal("49.99"),
                        features=[
                            "Access to All Season Passes",
                            "Exclusive Annual Items",
                            "20% Bonus XP Year-Round",
                            "Special Annual Title",
                            "Priority Support"
                        ],
                        billing="annual",
                        description="Year-round access to all seasonal content"
                    )
                },
                category="subscription"
            ),

            # Creator Platform Products
            "CREATOR": GameProduct(
                name="EpochCore Creator Platform",
                type="recurring",
                tiers={
                    "BASIC": ProductTier(
                        name="Creator Basic",
                        price=Decimal("19.99"),
                        features=[
                            "Basic Asset Creation Tools",
                            "Community Market Access",
                            "Basic Analytics",
                            "Standard Support"
                        ],
                        billing="monthly",
                        description="Start your journey as a content creator"
                    ),
                    "PRO": ProductTier(
                        name="Creator Pro",
                        price=Decimal("49.99"),
                        features=[
                            "Advanced Creation Tools",
                            "Priority Market Placement",
                            "Advanced Analytics",
                            "Priority Support",
                            "Marketing Tools",
                            "Custom Storefront"
                        ],
                        billing="monthly",
                        description="Professional tools for serious creators"
                    ),
                    "ENTERPRISE": ProductTier(
                        name="Creator Enterprise",
                        price=Decimal("199.99"),
                        features=[
                            "All Pro Features",
                            "Custom API Access",
                            "Dedicated Support",
                            "Revenue Share Benefits",
                            "Early Feature Access",
                            "Custom Integration Options"
                        ],
                        billing="monthly",
                        description="Enterprise-level creation and integration tools"
                    )
                },
                category="creator"
            ),

            # In-Game Currency Packages
            "CURRENCY": GameProduct(
                name="EpochCore Credits",
                type="one_time",
                tiers={
                    "STARTER": ProductTier(
                        name="Starter Pack",
                        price=Decimal("4.99"),
                        features=[
                            "500 Credits",
                            "1 Basic Loot Box"
                        ],
                        billing="one_time",
                        description="Start your collection with basic credits"
                    ),
                    "PREMIUM": ProductTier(
                        name="Premium Pack",
                        price=Decimal("9.99"),
                        features=[
                            "1100 Credits",
                            "3 Premium Loot Boxes",
                            "1 Exclusive Item"
                        ],
                        billing="one_time",
                        description="Best value for regular players"
                    ),
                    "WHALE": ProductTier(
                        name="Whale Pack",
                        price=Decimal("49.99"),
                        features=[
                            "6000 Credits",
                            "15 Premium Loot Boxes",
                            "5 Exclusive Items",
                            "Special Profile Badge"
                        ],
                        billing="one_time",
                        description="Ultimate value pack for dedicated players"
                    )
                },
                category="currency"
            )
        }

    def get_product_details(self, product_key: str, tier: str = None) -> Dict:
        """Get detailed information about a product"""
        if product_key not in self.game_products:
            raise ValueError(f"Invalid product key: {product_key}")

        product = self.game_products[product_key]

        if tier and tier not in product.tiers:
            raise ValueError(f"Invalid tier: {tier}")

        if tier:
            return {
                "product": product.name,
                "type": product.type,
                "category": product.category,
                "tier": product.tiers[tier].__dict__
            }

        return {
            "product": product.name,
            "type": product.type,
            "category": product.category,
            "tiers": {k: v.__dict__ for k, v in product.tiers.items()}
        }

    def get_price(self, product_key: str, tier: str) -> Decimal:
        """Get price for a specific product tier"""
        return self.game_products[product_key].tiers[tier].price

    def list_all_products(self) -> Dict:
        """List all available products and their tiers"""
        return {
            k: {
                "name": v.name,
                "type": v.type,
                "category": v.category,
                "tiers": list(v.tiers.keys())
            }
            for k, v in self.game_products.items()
        }


# Example usage:
if __name__ == "__main__":
    config = ProductConfiguration()

    # List all products
    products = config.list_all_products()
    print("Available Products:")
    print(products)

    # Get specific product details
    game_details = config.get_product_details("BASE_GAME", "ULTIMATE")
    print("\nUltimate Edition Details:")
    print(game_details)
