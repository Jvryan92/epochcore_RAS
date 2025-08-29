"""
Simple business metrics tracking system for EpochCore RAS
"""

import csv
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class BusinessMetrics:
    def __init__(self, data_dir: str = "business_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def log_customer(self,
                     customer_id: str,
                     plan: str,
                     mrr: float,
                     source: str = "organic",
                     notes: str = "") -> None:
        """Log new customer acquisition"""
        with open(f"{self.data_dir}/customers.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                customer_id,
                plan,
                mrr,
                source,
                notes
            ])

    def log_revenue(self,
                    amount: float,
                    type: str,
                    customer_id: str,
                    notes: str = "") -> None:
        """Log revenue entry"""
        with open(f"{self.data_dir}/revenue.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                amount,
                type,
                customer_id,
                notes
            ])

    def log_metric(self,
                   metric: str,
                   value: float,
                   tags: Dict[str, str] = None) -> None:
        """Log business metric"""
        with open(f"{self.data_dir}/metrics.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                metric,
                value,
                json.dumps(tags or {})
            ])

    def get_mrr(self) -> float:
        """Calculate current MRR"""
        try:
            mrr = 0
            with open(f"{self.data_dir}/customers.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    mrr += float(row[3])  # MRR column
            return mrr
        except FileNotFoundError:
            return 0

    def get_customer_count(self, plan: Optional[str] = None) -> int:
        """Get total customer count, optionally filtered by plan"""
        try:
            count = 0
            with open(f"{self.data_dir}/customers.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not plan or row[2] == plan:  # Plan column
                        count += 1
            return count
        except FileNotFoundError:
            return 0

    def get_metrics_report(self) -> Dict:
        """Generate business metrics report"""
        return {
            "mrr": self.get_mrr(),
            "total_customers": self.get_customer_count(),
            "by_plan": {
                "community": self.get_customer_count("community"),
                "startup": self.get_customer_count("startup"),
                "business": self.get_customer_count("business"),
                "enterprise": self.get_customer_count("enterprise")
            },
            "generated_at": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    metrics = BusinessMetrics()

    # Log a new customer
    metrics.log_customer(
        "cust_123",
        "startup",
        49.0,
        "github",
        "Found through GitHub Stars"
    )

    # Log revenue
    metrics.log_revenue(
        588.0,  # $49 * 12
        "annual_subscription",
        "cust_123",
        "Annual prepay with 12 months"
    )

    # Log some metrics
    metrics.log_metric(
        "system_uptime",
        99.99,
        {"region": "us-east-1"}
    )

    # Get a report
    report = metrics.get_metrics_report()
    print(json.dumps(report, indent=2))
