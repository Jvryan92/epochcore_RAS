"""Test suite for EcommerceAgent functionality."""

import os
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.ai_agent.agents.ecommerce_agent import EcommerceAgent


class TestEcommerceAgent(unittest.TestCase):
    """Test cases for EcommerceAgent."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test structure
        (self.test_path / "public").mkdir(parents=True)
        (self.test_path / "src/app/api/products").mkdir(parents=True)
        (self.test_path / "src/app/api/checkout").mkdir(parents=True)
        (self.test_path / "src/lib").mkdir(parents=True)
        (self.test_path / "src/app/pricing").mkdir(parents=True)
        (self.test_path / ".github/workflows").mkdir(parents=True)

        # Create test files
        self._create_test_products()
        self._create_test_env()
        self._create_test_api_routes()
        self._create_test_pricing_page()
        self._create_test_workflows()

        # Initialize agent
        self.agent = EcommerceAgent(
            {"products_path": "public/products.json", "env_path": ".env.local"}
        )

        # Mock project root
        self.original_get_root = self.agent.get_project_root
        self.agent.get_project_root = lambda: self.test_path

    def tearDown(self):
        """Clean up test environment."""
        self.agent.get_project_root = self.original_get_root
        import shutil

        shutil.rmtree(self.test_dir)

    def _create_test_products(self):
        """Create test products.json."""
        products = {
            "products": [
                {
                    "Name": "Test Product",
                    "Price (USD cents)": 9900,
                    "License": "perpetual",
                    "Description": "Test description",
                }
            ]
        }
        with open(self.test_path / "public/products.json", "w") as f:
            json.dump(products, f)

    def _create_test_env(self):
        """Create test .env.local."""
        env_content = """
        STRIPE_SECRET_KEY=sk_test_123
        NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_123
        VERCEL_TOKEN=vercel_test_token
        VERCEL_ORG_ID=org_123
        VERCEL_PROJECT_ID=proj_123
        """
        with open(self.test_path / ".env.local", "w") as f:
            f.write(env_content)

    def _create_test_api_routes(self):
        """Create test API routes."""
        # Products route
        products_route = """
        import { NextResponse } from "next/server";
        export async function GET() {
            return NextResponse.json({ products: [] });
        }
        """
        with open(self.test_path / "src/app/api/products/route.ts", "w") as f:
            f.write(products_route)

        # Checkout route
        checkout_route = """
        import { stripe } from "@/lib/stripe";
        export async function POST() {
            const session = await stripe.checkout.sessions.create({});
            return NextResponse.json({ url: session.url });
        }
        """
        with open(self.test_path / "src/app/api/checkout/route.ts", "w") as f:
            f.write(checkout_route)

        # Stripe lib
        stripe_lib = """
        import Stripe from "stripe";
        export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "");
        """
        with open(self.test_path / "src/lib/stripe.ts", "w") as f:
            f.write(stripe_lib)

    def _create_test_pricing_page(self):
        """Create test pricing page."""
        pricing_page = """
        export default function Pricing() {
            fetch("/api/products");
            fetch("/api/checkout");
            location.href=j.url;
            return <div>Price (USD cents)</div>;
        }
        """
        with open(self.test_path / "src/app/pricing/page.tsx", "w") as f:
            f.write(pricing_page)

    def _create_test_workflows(self):
        """Create test GitHub workflows."""
        workflow = """
        name: Deploy
        env:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
          NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: ${{ secrets.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY }}
        jobs:
          deploy:
            runs-on: ubuntu-latest
            steps:
              - run: vercel deploy
        """
        with open(self.test_path / ".github/workflows/deploy-vercel.yml", "w") as f:
            f.write(workflow)

    def test_validate_config(self):
        """Test configuration validation."""
        self.assertTrue(self.agent.validate_config())

        # Test with missing files
        os.remove(self.test_path / "public/products.json")
        self.assertFalse(self.agent.validate_config())

    def test_check_product_catalog(self):
        """Test product catalog validation."""
        result = self.agent._check_product_catalog(self.test_path)
        self.assertTrue(result["exists"])
        self.assertEqual(result["products"], 1)
        self.assertTrue(result["has_required_fields"])
        self.assertEqual(len(result["issues"]), 0)

    def test_check_api_routes(self):
        """Test API routes validation."""
        result = self.agent._check_api_routes(self.test_path)
        self.assertTrue(result["products_route"]["exists"])
        self.assertTrue(result["checkout_route"]["exists"])
        self.assertTrue(result["stripe_lib"]["exists"])

    def test_check_environment(self):
        """Test environment configuration validation."""
        result = self.agent._check_environment(self.test_path)
        self.assertTrue(result["exists"])
        self.assertTrue(result["has_stripe_keys"])
        self.assertTrue(result["has_vercel_config"])
        self.assertEqual(len(result["issues"]), 0)

    def test_check_pricing_page(self):
        """Test pricing page validation."""
        result = self.agent._check_pricing_page(self.test_path)
        self.assertTrue(result["exists"])
        self.assertTrue(result["implements_required"])
        self.assertTrue(result["has_checkout_flow"])

    def test_check_ci_cd(self):
        """Test CI/CD configuration validation."""
        result = self.agent._check_ci_cd(self.test_path)
        self.assertTrue(result["workflows_exist"])
        self.assertTrue(result["has_vercel_deploy"])
        self.assertTrue(result["has_stripe_secrets"])
        self.assertEqual(len(result["issues"]), 0)

    def test_full_run(self):
        """Test complete agent run."""
        result = self.agent.run()
        self.assertIn("product_catalog", result)
        self.assertIn("api_routes", result)
        self.assertIn("environment", result)
        self.assertIn("pricing_page", result)
        self.assertIn("ci_cd", result)
        self.assertIn("timestamp", result)
