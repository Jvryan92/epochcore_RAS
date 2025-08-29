"""E-commerce Integration Agent for managing pricing and payment systems."""

import os
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from collections import defaultdict
from ..core.base_agent import BaseAgent
from ..core.performance_optimizer import PerformanceOptimizer


class EcommerceAgent(BaseAgent):
    """Agent for managing e-commerce integrations and monitoring."""

    def __init__(self, config: Dict[str, Any] | None = None):
        """Initialize the E-commerce Agent.

        Args:
            config: Agent configuration with optional settings:
                   - products_path: Path to products.json
                   - env_path: Path to .env.local
                   - stripe_enabled: Whether Stripe integration is enabled
                   - vercel_enabled: Whether Vercel deployment is enabled
                   - performance_monitoring: Enable performance tracking
                   - pricing_history_path: Path to store pricing history
        """
        super().__init__("ecommerce_agent", config)
        self.products_path = self.config.get("products_path", "public/products.json")
        self.env_path = self.config.get("env_path", ".env.local")
        self.stripe_enabled = self.config.get("stripe_enabled", True)
        self.vercel_enabled = self.config.get("vercel_enabled", True)

        # Performance monitoring
        if self.config.get("performance_monitoring", True):
            self.performance_optimizer = PerformanceOptimizer()

        # Pricing history tracking
        self.pricing_history_path = self.config.get(
            "pricing_history_path", "data/pricing_history.json"
        )
        self._load_pricing_history()

        # Metrics tracking
        self.metrics: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            True if configuration is valid
        """
        project_root = self.get_project_root()

        # Check for required files
        products_exists = (project_root / self.products_path).exists()
        env_exists = (project_root / self.env_path).exists()

        # Check for required API routes
        api_routes = [
            "src/app/api/products/route.ts",
            "src/app/api/checkout/route.ts",
            "src/lib/stripe.ts",
        ]
        routes_exist = all((project_root / route).exists() for route in api_routes)

        return products_exists and env_exists and routes_exist

    def run(self) -> Dict[str, Any]:
        """Run e-commerce system checks and monitoring.

        Returns:
            Status report of e-commerce system
        """
        project_root = self.get_project_root()

        report = {
            "timestamp": datetime.now().isoformat(),
            "product_catalog": self._check_product_catalog(project_root),
            "api_routes": self._check_api_routes(project_root),
            "environment": self._check_environment(project_root),
            "pricing_page": self._check_pricing_page(project_root),
            "ci_cd": self._check_ci_cd(project_root),
        }

        # Add performance metrics
        if hasattr(self, "performance_optimizer"):
            report["performance"] = self.performance_optimizer.get_metrics()

        # Add pricing analytics
        report["pricing"] = self._analyze_pricing_trends()

        return report

    def track_metrics(self, category: str, metric: str, value: float) -> None:
        """Track a metric value for monitoring.

        Args:
            category: Metric category (e.g. 'sales', 'performance')
            metric: Name of the specific metric
            value: Metric value to record
        """
        self.metrics[category][metric] = value

    def _analyze_pricing_trends(self) -> Dict[str, Any]:
        """Analyze pricing trends and coordinate with other agents."""
        if not self.pricing_history:
            return {"status": "no_history"}

        analysis = {
            "changes": [],
            "volatility": {},
            "recommendations": [],
            "metrics": {},
            "compound_features": {},
        }

        total_volatility = 0
        high_volatility_products = 0

        # Notify performance agent about analysis start
        if hasattr(self, "performance_optimizer"):
            self.send_message(
                recipient="performance_optimizer",
                topic="pricing_analysis",
                data={"action": "start_analysis"},
                priority="normal",
            )

        # Analyze price changes
        for product_id, history in self.pricing_history.items():
            if len(history) > 1:
                # Calculate price volatility
                prices = [entry["price"] for entry in history]
                avg_price = sum(prices) / len(prices)
                volatility = (max(prices) - min(prices)) / avg_price

                analysis["volatility"][product_id] = volatility
                total_volatility += volatility

                if volatility > 0.2:  # High volatility threshold
                    high_volatility_products += 1

                # Track significant changes
                recent_changes = []
                for i in range(1, len(history)):
                    pct_change = (
                        history[i]["price"] - history[i - 1]["price"]
                    ) / history[i - 1]["price"]
                    if abs(pct_change) > 0.1:  # 10% threshold
                        change_info = {
                            "product_id": product_id,
                            "date": history[i]["date"],
                            "change": pct_change * 100,
                        }
                        analysis["changes"].append(change_info)
                        recent_changes.append(pct_change)

                # Analyze recent pricing patterns
                if recent_changes:
                    avg_change = sum(recent_changes) / len(recent_changes)
                    if avg_change > 0.15:
                        analysis["recommendations"].append(
                            {
                                "type": "price_trend",
                                "product_id": product_id,
                                "message": "Consider price optimization review",
                                "confidence": 0.8,
                            }
                        )

        # Calculate overall metrics
        num_products = len(self.pricing_history)
        if num_products > 0:
            analysis["metrics"] = {
                "avg_volatility": total_volatility / num_products,
                "high_volatility_ratio": high_volatility_products / num_products,
                "price_change_frequency": len(analysis["changes"]) / num_products,
            }

            # Add compound feature data
            analysis["compound_features"] = {
                "price_optimization": {
                    "needs_review": analysis["metrics"]["high_volatility_ratio"] > 0.3,
                    "confidence": min(
                        1.0, analysis["metrics"]["price_change_frequency"] * 2
                    ),
                    "impact_score": analysis["metrics"]["avg_volatility"] * 100,
                },
                "market_stability": {
                    "stable": analysis["metrics"]["avg_volatility"] < 0.15,
                    "confidence": 0.7,
                    "trend": (
                        "volatile"
                        if analysis["metrics"]["high_volatility_ratio"] > 0.3
                        else "stable"
                    ),
                },
            }

            # Request performance data for high-volatility products
            if high_volatility_products > 0 and hasattr(self, "performance_optimizer"):
                self.send_message(
                    recipient="performance_optimizer",
                    topic="performance_check",
                    data={
                        "high_volatility_products": list(
                            pid
                            for pid, vol in analysis["volatility"].items()
                            if vol > 0.2
                        ),
                        "metrics": analysis["metrics"],
                    },
                    priority="high",
                )

                # Wait for performance data
                messages = self.get_messages("performance_data")
                if messages:
                    latest_perf = messages[-1]["data"]
                    analysis["performance_correlation"] = latest_perf

                    # Add joint recommendations
                    if latest_perf.get("high_load_correlation", False):
                        analysis["recommendations"].append(
                            {
                                "type": "performance_pricing",
                                "message": "High price volatility correlates with system load",
                                "confidence": 0.9,
                                "action": "Review pricing strategy during peak hours",
                            }
                        )

        # Notify analysis completion
        if hasattr(self, "performance_optimizer"):
            self.send_message(
                recipient="performance_optimizer",
                topic="pricing_analysis",
                data={
                    "action": "complete",
                    "metrics": analysis["metrics"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                priority="normal",
            )

        return analysis

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming messages from other agents.

        Args:
            message: The message to process
        """
        topic = message["topic"]
        data = message["data"]

        if topic == "performance_alert":
            # Handle performance warnings that might affect pricing
            if data.get("severity") == "high":
                self.logger.warning(
                    f"High severity performance alert received: {data.get('message')}"
                )
                # Trigger immediate pricing review if needed
                if data.get("affects_pricing", False):
                    self._analyze_pricing_trends()

        elif topic == "system_health":
            # Monitor system health metrics that could impact e-commerce
            health_score = data.get("health_score", 0)
            if health_score < 0.7:  # Below acceptable threshold
                self.logger.warning(f"Poor system health detected: {health_score}")
                # Could trigger defensive pricing strategies

        elif topic == "resource_utilization":
            # Track resource usage that might affect pricing decisions
            if data.get("cpu_usage", 0) > 80 or data.get("memory_usage", 0) > 80:
                self.logger.info("High resource utilization detected")
                # Could adjust pricing strategies during high load

    def _load_pricing_history(self) -> None:
        """Load pricing history from disk or initialize if not exists."""
        try:
            if os.path.exists(self.pricing_history_path):
                with open(self.pricing_history_path, "r") as f:
                    self.pricing_history = json.load(f)
            else:
                # Initialize empty history
                os.makedirs(os.path.dirname(self.pricing_history_path), exist_ok=True)
                self.pricing_history = {}
                self._save_pricing_history()
        except Exception as e:
            self.logger.error(f"Failed to load pricing history: {e}")
            self.pricing_history = {}

    def _save_pricing_history(self) -> None:
        """Save current pricing history to disk."""
        try:
            with open(self.pricing_history_path, "w") as f:
                json.dump(self.pricing_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save pricing history: {e}")

    def _check_product_catalog(self, root: Path) -> Dict[str, Any]:
        """Check product catalog configuration."""
        catalog = {
            "exists": False,
            "products": 0,
            "has_required_fields": True,
            "issues": [],
        }

        products_file = root / self.products_path
        if not products_file.exists():
            catalog["issues"].append("Products file missing")
            return catalog

        catalog["exists"] = True
        try:
            with open(products_file) as f:
                data = json.load(f)
                products = data.get("products", [])
                catalog["products"] = len(products)

                # Validate required fields
                required_fields = ["Name", "Price (USD cents)", "License"]
                for product in products:
                    missing = [f for f in required_fields if f not in product]
                    if missing:
                        catalog["has_required_fields"] = False
                        catalog["issues"].append(
                            f"Product {product.get('Name', 'Unknown')} missing fields: {missing}"
                        )
        except Exception as e:
            catalog["issues"].append(f"Error reading products: {e}")

        # Update pricing history when checking catalog
        try:
            if catalog["exists"] and catalog["products"] > 0:
                products_file = root / self.products_path
                with open(products_file, "r") as f:
                    data = json.load(f)
                    products = data.get("products", [])

                timestamp = datetime.now(timezone.utc).isoformat()

                for product in products:
                    product_id = str(
                        product.get("id")
                        or hashlib.md5(
                            str(product.get("Name", "")).encode()
                        ).hexdigest()
                    )

                    if product_id not in self.pricing_history:
                        self.pricing_history[product_id] = []

                    self.pricing_history[product_id].append(
                        {
                            "date": timestamp,
                            "price": product.get("Price (USD cents)", 0),
                        }
                    )

                self._save_pricing_history()

        except Exception as e:
            self.logger.error(f"Failed to update pricing history: {e}")

        return catalog

    def _check_api_routes(self, root: Path) -> Dict[str, Any]:
        """Check API route implementations."""
        routes = {
            "products_route": {"exists": False, "implements_required": False},
            "checkout_route": {"exists": False, "implements_required": False},
            "stripe_lib": {"exists": False, "configured": False},
        }

        # Check products route
        products_route = root / "src/app/api/products/route.ts"
        if products_route.exists():
            routes["products_route"]["exists"] = True
            with open(products_route) as f:
                content = f.read()
                routes["products_route"]["implements_required"] = all(
                    term in content for term in ["GET", "NextResponse", "products.json"]
                )

        # Check checkout route
        checkout_route = root / "src/app/api/checkout/route.ts"
        if checkout_route.exists():
            routes["checkout_route"]["exists"] = True
            with open(checkout_route) as f:
                content = f.read()
                routes["checkout_route"]["implements_required"] = all(
                    term in content
                    for term in ["POST", "stripe.checkout.sessions.create"]
                )

        # Check Stripe lib
        stripe_lib = root / "src/lib/stripe.ts"
        if stripe_lib.exists():
            routes["stripe_lib"]["exists"] = True
            with open(stripe_lib) as f:
                content = f.read()
                routes["stripe_lib"]["configured"] = all(
                    term in content for term in ["Stripe", "STRIPE_SECRET_KEY"]
                )

        return routes

    def _check_environment(self, root: Path) -> Dict[str, Any]:
        """Check environment configuration."""
        env = {
            "exists": False,
            "has_stripe_keys": False,
            "has_vercel_config": False,
            "issues": [],
        }

        env_file = root / self.env_path
        if not env_file.exists():
            env["issues"].append(".env.local file missing")
            return env

        env["exists"] = True
        try:
            with open(env_file) as f:
                content = f.read()
                env["has_stripe_keys"] = all(
                    key in content
                    for key in [
                        "STRIPE_SECRET_KEY",
                        "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
                    ]
                )
                env["has_vercel_config"] = all(
                    key in content
                    for key in ["VERCEL_TOKEN", "VERCEL_ORG_ID", "VERCEL_PROJECT_ID"]
                )
        except Exception as e:
            env["issues"].append(f"Error reading .env.local: {e}")

        return env

    def _check_pricing_page(self, root: Path) -> Dict[str, Any]:
        """Check pricing page implementation."""
        pricing = {
            "exists": False,
            "implements_required": False,
            "has_checkout_flow": False,
        }

        pricing_page = root / "src/app/pricing/page.tsx"
        if not pricing_page.exists():
            return pricing

        pricing["exists"] = True
        with open(pricing_page) as f:
            content = f.read()
            pricing["implements_required"] = all(
                term in content
                for term in ['fetch("/api/products")', "Price (USD cents)", "License"]
            )
            pricing["has_checkout_flow"] = all(
                term in content
                for term in ['fetch("/api/checkout")', "location.href=j.url"]
            )

        return pricing

    def _check_ci_cd(self, root: Path) -> Dict[str, Any]:
        """Check CI/CD configuration."""
        cicd = {
            "workflows_exist": False,
            "has_vercel_deploy": False,
            "has_stripe_secrets": False,
            "issues": [],
        }

        workflows_dir = root / ".github/workflows"
        if not workflows_dir.exists():
            cicd["issues"].append("GitHub workflows directory missing")
            return cicd

        cicd["workflows_exist"] = True

        # Check Vercel deployment workflow
        deploy_file = workflows_dir / "deploy-vercel.yml"
        if deploy_file.exists():
            with open(deploy_file) as f:
                content = f.read()
                cicd["has_vercel_deploy"] = "vercel deploy" in content
                cicd["has_stripe_secrets"] = all(
                    secret in content
                    for secret in [
                        "STRIPE_SECRET_KEY",
                        "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
                    ]
                )

        return cicd
