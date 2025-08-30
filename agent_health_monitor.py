#!/usr/bin/env python3
"""
Agent Health Monitor - Continuously monitors agent health metrics
Integrates with flash sync to provide real-time agent status tracking
"""

import argparse
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import random
import statistics
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_health.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AgentHealthMonitor")

# Constants and configuration
MONITOR_DIR = "./monitor"
LEDGER_DIR = "./ledger"
SYNC_DIR = "./sync"
DASHBOARD_DIR = "./dashboard"
ALERTS_FILE = f"{MONITOR_DIR}/alerts.jsonl"
HEALTH_LOG = f"{MONITOR_DIR}/health_metrics.jsonl"
AGENT_CONFIG = f"{MONITOR_DIR}/monitor_config.json"

# Ensure directories exist
for directory in [MONITOR_DIR, DASHBOARD_DIR]:
    os.makedirs(directory, exist_ok=True)

# Default monitoring configuration
DEFAULT_CONFIG = {
    "monitoring_interval_seconds": 60,
    "alert_thresholds": {
        "latency_ms": 400,
        "reliability": 0.85,
        "memory_usage_mb": 500,
        "heartbeat_missing_minutes": 5
    },
    "anomaly_detection": {
        "z_score_threshold": 2.0,
        "min_samples": 10,
        "learning_rate": 0.1
    },
    "sync_schedule": {
        "interval_minutes": 60,
        "force_sync_on_anomalies": True
    }
}

# Load or create configuration


def load_config():
    if os.path.exists(AGENT_CONFIG):
        with open(AGENT_CONFIG, 'r') as f:
            return json.load(f)
    with open(AGENT_CONFIG, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return DEFAULT_CONFIG

# Utility functions


def timestamp_utc():
    """Generate ISO-8601 UTC timestamp"""
    return dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_timestamp(ts_str):
    """Parse ISO-8601 timestamp string to datetime"""
    return dt.datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%SZ')


def hash_string(s):
    """SHA-256 hash of string"""
    return hashlib.sha256(s.encode()).hexdigest()

# Agent state tracking


class AgentHealthMonitor:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.agent_states = {}
        self.historical_metrics = {
            "latency": {},
            "reliability": {},
            "memory": {},
            "task_success": {}
        }
        self.alert_history = []
        self.running = False
        self.last_sync_time = dt.datetime.utcnow() - dt.timedelta(days=1)

        # Load initial agent states from registry
        self._load_agent_states()

        # Load historical metrics if available
        if os.path.exists(HEALTH_LOG):
            self._load_historical_metrics()

    def _load_agent_states(self):
        """Load agent states from latest registry"""
        registry_path = f"{LEDGER_DIR}/mesh_registry_latest.json"
        if not os.path.exists(registry_path):
            # Try to find any registry file
            registry_files = [f for f in os.listdir(
                LEDGER_DIR) if "registry" in f and f.endswith(".json")]
            if registry_files:
                registry_path = f"{LEDGER_DIR}/{registry_files[0]}"
            else:
                logger.warning(
                    "No registry file found. Starting with empty agent states.")
                return

        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)

            # Process agent data
            for agent in registry.get("agents", []):
                agent_id = agent.get("agent_id")
                if not agent_id:
                    continue

                self.agent_states[agent_id] = {
                    "id": agent_id,
                    "did": agent.get("did", ""),
                    "skills": agent.get("skills", []),
                    "reliability": agent.get("reliability", 0.0),
                    "latency_ms": agent.get("latency_ms", 0),
                    "status": agent.get("status", "unknown"),
                    "last_seen": agent.get("last_seen", timestamp_utc()),
                    "health_score": 1.0,
                    "alerts": []
                }

            logger.info(f"Loaded {len(self.agent_states)} agents from registry")
        except Exception as e:
            logger.error(f"Error loading agent states: {e}")

    def _load_historical_metrics(self):
        """Load historical metrics from health log"""
        try:
            with open(HEALTH_LOG, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        timestamp = entry.get("ts")
                        if not timestamp:
                            continue

                        metrics = entry.get("metrics", {})
                        for agent_id, agent_metrics in metrics.items():
                            # Initialize if not exists
                            for metric_type in self.historical_metrics:
                                if agent_id not in self.historical_metrics[metric_type]:
                                    self.historical_metrics[metric_type][agent_id] = []

                            # Add data points
                            if "latency_ms" in agent_metrics:
                                self.historical_metrics["latency"][agent_id].append(
                                    (timestamp, agent_metrics["latency_ms"])
                                )
                            if "reliability" in agent_metrics:
                                self.historical_metrics["reliability"][agent_id].append(
                                    (timestamp, agent_metrics["reliability"])
                                )
                            if "memory_usage_mb" in agent_metrics:
                                self.historical_metrics["memory"][agent_id].append(
                                    (timestamp, agent_metrics["memory_usage_mb"])
                                )
                            if "task_success_rate" in agent_metrics:
                                self.historical_metrics["task_success"][agent_id].append(
                                    (timestamp, agent_metrics["task_success_rate"])
                                )
                    except json.JSONDecodeError:
                        continue

            # Count loaded metrics
            total_points = sum(len(points) for metric_type in self.historical_metrics
                               for agent_id, points in self.historical_metrics[metric_type].items())
            logger.info(f"Loaded {total_points} historical metric points")
        except Exception as e:
            logger.error(f"Error loading historical metrics: {e}")

    def start_monitoring(self):
        """Start monitoring thread"""
        if self.running:
            logger.warning("Monitoring already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Agent health monitoring started")

    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5.0)
        logger.info("Agent health monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect current metrics
                self._collect_metrics()

                # Check for anomalies and generate alerts
                alerts = self._check_anomalies()
                if alerts:
                    self._record_alerts(alerts)

                # Check if it's time for a flash sync
                self._check_sync_schedule(force=bool(alerts) and
                                          self.config["sync_schedule"]["force_sync_on_anomalies"])

                # Generate health dashboard
                self._generate_dashboard()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            # Sleep until next interval
            time.sleep(self.config["monitoring_interval_seconds"])

    def _collect_metrics(self):
        """Collect current metrics for all agents"""
        # Get latest flash sync data if available
        sync_files = sorted(Path(SYNC_DIR).glob("*_snapshots.json"),
                            key=lambda p: p.stat().st_mtime, reverse=True)

        if not sync_files:
            logger.warning("No sync snapshot files found")
            return

        # Load latest snapshot
        latest_snapshots = None
        try:
            with open(sync_files[0], 'r') as f:
                latest_snapshots = json.load(f)
        except Exception as e:
            logger.error(f"Error loading latest snapshots: {e}")
            return

        # Process snapshot metrics
        current_metrics = {"ts": timestamp_utc(), "metrics": {}}

        for snapshot in latest_snapshots:
            agent_id = snapshot.get("agent_id")
            if not agent_id or agent_id not in self.agent_states:
                continue

            # Update agent state
            self.agent_states[agent_id].update({
                "latency_ms": snapshot.get("latency_ms", 0),
                "reliability": snapshot.get("reliability", 0.0),
                "last_seen": snapshot.get("ts", timestamp_utc()),
                "memory_usage_mb": snapshot.get("memory_usage_mb", 0),
                "skills_active": snapshot.get("skills_active", [])
            })

            # Add to current metrics
            current_metrics["metrics"][agent_id] = {
                "latency_ms": snapshot.get("latency_ms", 0),
                "reliability": snapshot.get("reliability", 0.0),
                "memory_usage_mb": snapshot.get("memory_usage_mb", 0),
                "skills_active": len(snapshot.get("skills_active", [])),
                "health_score": self._calculate_health_score(agent_id)
            }

            # Update historical metrics
            ts = timestamp_utc()
            if agent_id not in self.historical_metrics["latency"]:
                self.historical_metrics["latency"][agent_id] = []
            self.historical_metrics["latency"][agent_id].append(
                (ts, snapshot.get("latency_ms", 0))
            )

            if agent_id not in self.historical_metrics["reliability"]:
                self.historical_metrics["reliability"][agent_id] = []
            self.historical_metrics["reliability"][agent_id].append(
                (ts, snapshot.get("reliability", 0.0))
            )

            if agent_id not in self.historical_metrics["memory"]:
                self.historical_metrics["memory"][agent_id] = []
            self.historical_metrics["memory"][agent_id].append(
                (ts, snapshot.get("memory_usage_mb", 0))
            )

        # Save metrics to health log
        with open(HEALTH_LOG, 'a') as f:
            f.write(json.dumps(current_metrics) + '\n')

    def _calculate_health_score(self, agent_id):
        """Calculate overall health score for an agent"""
        if agent_id not in self.agent_states:
            return 0.0

        agent = self.agent_states[agent_id]

        # Calculate health score based on reliability and latency
        reliability_score = min(1.0, agent.get("reliability", 0.0))

        # Latency score (lower is better)
        latency_threshold = self.config["alert_thresholds"]["latency_ms"]
        latency_ms = agent.get("latency_ms", 0)
        latency_score = max(0.0, min(1.0, 1.0 - (latency_ms / latency_threshold)))

        # Heartbeat score (recent heartbeats are better)
        last_seen = agent.get("last_seen", "")
        if last_seen:
            try:
                time_diff = dt.datetime.utcnow() - parse_timestamp(last_seen)
                max_missing = self.config["alert_thresholds"]["heartbeat_missing_minutes"]
                heartbeat_score = max(
                    0.0, min(1.0, 1.0 - (time_diff.total_seconds() / (max_missing * 60))))
            except:
                heartbeat_score = 0.5
        else:
            heartbeat_score = 0.5

        # Overall score (weighted average)
        health_score = (reliability_score * 0.4) + \
            (latency_score * 0.4) + (heartbeat_score * 0.2)
        return round(health_score, 2)

    def _check_anomalies(self):
        """Check for anomalies in agent metrics"""
        alerts = []

        for agent_id, agent in self.agent_states.items():
            # Check latency threshold
            if agent.get("latency_ms", 0) > self.config["alert_thresholds"]["latency_ms"]:
                alerts.append({
                    "ts": timestamp_utc(),
                    "agent_id": agent_id,
                    "alert_type": "high_latency",
                    "value": agent.get("latency_ms", 0),
                    "threshold": self.config["alert_thresholds"]["latency_ms"],
                    "severity": "warning"
                })

            # Check reliability threshold
            if agent.get("reliability", 1.0) < self.config["alert_thresholds"]["reliability"]:
                alerts.append({
                    "ts": timestamp_utc(),
                    "agent_id": agent_id,
                    "alert_type": "low_reliability",
                    "value": agent.get("reliability", 0.0),
                    "threshold": self.config["alert_thresholds"]["reliability"],
                    "severity": "warning"
                })

            # Check memory usage
            if agent.get("memory_usage_mb", 0) > self.config["alert_thresholds"]["memory_usage_mb"]:
                alerts.append({
                    "ts": timestamp_utc(),
                    "agent_id": agent_id,
                    "alert_type": "high_memory",
                    "value": agent.get("memory_usage_mb", 0),
                    "threshold": self.config["alert_thresholds"]["memory_usage_mb"],
                    "severity": "warning"
                })

            # Check heartbeat
            last_seen = agent.get("last_seen", "")
            if last_seen:
                try:
                    time_diff = dt.datetime.utcnow() - parse_timestamp(last_seen)
                    max_missing = self.config["alert_thresholds"]["heartbeat_missing_minutes"]
                    if time_diff.total_seconds() > (max_missing * 60):
                        alerts.append({
                            "ts": timestamp_utc(),
                            "agent_id": agent_id,
                            "alert_type": "missing_heartbeat",
                            "value": int(time_diff.total_seconds() / 60),
                            "threshold": max_missing,
                            "severity": "critical"
                        })
                except:
                    pass

            # Check for statistical anomalies in latency
            if agent_id in self.historical_metrics["latency"]:
                latency_history = [point[1]
                                   for point in self.historical_metrics["latency"][agent_id]]
                if len(latency_history) >= self.config["anomaly_detection"]["min_samples"]:
                    mean = statistics.mean(latency_history)
                    stdev = statistics.stdev(latency_history) if len(
                        latency_history) > 1 else 1.0
                    current = agent.get("latency_ms", 0)
                    z_score = (current - mean) / stdev if stdev > 0 else 0

                    if abs(z_score) > self.config["anomaly_detection"]["z_score_threshold"]:
                        alerts.append({
                            "ts": timestamp_utc(),
                            "agent_id": agent_id,
                            "alert_type": "latency_anomaly",
                            "value": current,
                            "mean": mean,
                            "z_score": round(z_score, 2),
                            "threshold": self.config["anomaly_detection"]["z_score_threshold"],
                            "severity": "warning"
                        })

        return alerts

    def _record_alerts(self, alerts):
        """Record alerts to alert log"""
        self.alert_history.extend(alerts)

        # Trim alert history to recent alerts
        max_alerts = 1000
        if len(self.alert_history) > max_alerts:
            self.alert_history = self.alert_history[-max_alerts:]

        # Write to alerts file
        with open(ALERTS_FILE, 'a') as f:
            for alert in alerts:
                f.write(json.dumps(alert) + '\n')

        # Update agent state with alerts
        for alert in alerts:
            agent_id = alert.get("agent_id")
            if agent_id in self.agent_states:
                if "alerts" not in self.agent_states[agent_id]:
                    self.agent_states[agent_id]["alerts"] = []
                self.agent_states[agent_id]["alerts"].append(alert)

                # Keep only recent alerts
                self.agent_states[agent_id]["alerts"] = self.agent_states[agent_id]["alerts"][-10:]

        # Log alerts
        for alert in alerts:
            logger.warning(
                f"Alert: {alert['alert_type']} for {alert['agent_id']} - {alert.get('value')} (threshold: {alert.get('threshold')})")

    def _check_sync_schedule(self, force=False):
        """Check if it's time for a flash sync"""
        now = dt.datetime.utcnow()
        minutes_since_sync = (now - self.last_sync_time).total_seconds() / 60

        if force or minutes_since_sync >= self.config["sync_schedule"]["interval_minutes"]:
            self._trigger_flash_sync()
            self.last_sync_time = now

    def _trigger_flash_sync(self):
        """Trigger a flash sync process"""
        logger.info("Triggering flash sync...")
        try:
            # Call the flash sync script
            import subprocess
            result = subprocess.run(["python3", "flash_sync_agents.py"],
                                    capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Flash sync completed successfully")
            else:
                logger.error(f"Flash sync failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error triggering flash sync: {e}")

    def _generate_dashboard(self):
        """Generate health dashboard visualization"""
        try:
            # Generate dashboard for each metric type
            self._generate_latency_chart()
            self._generate_reliability_chart()
            self._generate_memory_chart()
            self._generate_health_score_chart()

            # Generate summary dashboard
            self._generate_summary_dashboard()

            # Generate HTML dashboard
            self._generate_html_dashboard()

        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")

    def _generate_latency_chart(self):
        """Generate latency chart"""
        plt.figure(figsize=(10, 6))

        for agent_id, data_points in self.historical_metrics["latency"].items():
            if len(data_points) < 2:
                continue

            timestamps = [parse_timestamp(point[0]) for point in data_points[-50:]]
            values = [point[1] for point in data_points[-50:]]

            plt.plot(timestamps, values, label=agent_id.split('://')[-1])

        plt.title('Agent Latency Over Time')
        plt.xlabel('Time')
        plt.ylabel('Latency (ms)')
        plt.grid(True)
        plt.legend()
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        plt.tight_layout()
        plt.savefig(f"{DASHBOARD_DIR}/latency_chart.png")
        plt.close()

    def _generate_reliability_chart(self):
        """Generate reliability chart"""
        plt.figure(figsize=(10, 6))

        for agent_id, data_points in self.historical_metrics["reliability"].items():
            if len(data_points) < 2:
                continue

            timestamps = [parse_timestamp(point[0]) for point in data_points[-50:]]
            values = [point[1] for point in data_points[-50:]]

            plt.plot(timestamps, values, label=agent_id.split('://')[-1])

        plt.title('Agent Reliability Over Time')
        plt.xlabel('Time')
        plt.ylabel('Reliability Score')
        plt.grid(True)
        plt.legend()
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        plt.tight_layout()
        plt.savefig(f"{DASHBOARD_DIR}/reliability_chart.png")
        plt.close()

    def _generate_memory_chart(self):
        """Generate memory usage chart"""
        plt.figure(figsize=(10, 6))

        for agent_id, data_points in self.historical_metrics["memory"].items():
            if len(data_points) < 2:
                continue

            timestamps = [parse_timestamp(point[0]) for point in data_points[-50:]]
            values = [point[1] for point in data_points[-50:]]

            plt.plot(timestamps, values, label=agent_id.split('://')[-1])

        plt.title('Agent Memory Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('Memory Usage (MB)')
        plt.grid(True)
        plt.legend()
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        plt.tight_layout()
        plt.savefig(f"{DASHBOARD_DIR}/memory_chart.png")
        plt.close()

    def _generate_health_score_chart(self):
        """Generate health score chart"""
        labels = [agent_id.split('://')[-1] for agent_id in self.agent_states.keys()]
        values = [self._calculate_health_score(agent_id)
                  for agent_id in self.agent_states.keys()]

        plt.figure(figsize=(10, 6))
        colors = ['green' if score >= 0.9 else 'orange' if score >=
                  0.7 else 'red' for score in values]
        plt.bar(labels, values, color=colors)
        plt.title('Agent Health Scores')
        plt.xlabel('Agent')
        plt.ylabel('Health Score (0-1)')
        plt.grid(True, axis='y')
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(f"{DASHBOARD_DIR}/health_score_chart.png")
        plt.close()

    def _generate_summary_dashboard(self):
        """Generate a summary dashboard"""
        plt.figure(figsize=(12, 10))

        # Define grid layout
        gs = plt.GridSpec(2, 2, figure=plt.gcf())

        # Plot latency
        ax1 = plt.subplot(gs[0, 0])
        for agent_id, data_points in self.historical_metrics["latency"].items():
            if len(data_points) < 2:
                continue
            timestamps = [parse_timestamp(point[0]) for point in data_points[-20:]]
            values = [point[1] for point in data_points[-20:]]
            ax1.plot(timestamps, values, label=agent_id.split('://')[-1])
        ax1.set_title('Latency (ms)')
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        # Plot reliability
        ax2 = plt.subplot(gs[0, 1])
        for agent_id, data_points in self.historical_metrics["reliability"].items():
            if len(data_points) < 2:
                continue
            timestamps = [parse_timestamp(point[0]) for point in data_points[-20:]]
            values = [point[1] for point in data_points[-20:]]
            ax2.plot(timestamps, values, label=agent_id.split('://')[-1])
        ax2.set_title('Reliability')
        ax2.grid(True)
        ax2.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        # Plot health score
        ax3 = plt.subplot(gs[1, 0])
        labels = [agent_id.split('://')[-1] for agent_id in self.agent_states.keys()]
        values = [self._calculate_health_score(agent_id)
                  for agent_id in self.agent_states.keys()]
        colors = ['green' if score >= 0.9 else 'orange' if score >=
                  0.7 else 'red' for score in values]
        ax3.bar(labels, values, color=colors)
        ax3.set_title('Health Score')
        ax3.set_ylim(0, 1)
        ax3.grid(True, axis='y')

        # Plot alert count
        ax4 = plt.subplot(gs[1, 1])
        alert_counts = {}
        for alert in self.alert_history[-100:]:
            agent_id = alert.get("agent_id", "unknown")
            alert_counts[agent_id] = alert_counts.get(agent_id, 0) + 1

        if alert_counts:
            alert_labels = [agent_id.split('://')[-1]
                            for agent_id in alert_counts.keys()]
            alert_values = list(alert_counts.values())
            ax4.bar(alert_labels, alert_values)
            ax4.set_title('Recent Alerts')
            ax4.grid(True, axis='y')
        else:
            ax4.text(0.5, 0.5, "No Recent Alerts",
                     horizontalalignment='center', verticalalignment='center')
            ax4.set_title('Recent Alerts')

        plt.tight_layout()
        plt.savefig(f"{DASHBOARD_DIR}/summary_dashboard.png")
        plt.close()

    def _generate_html_dashboard(self):
        """Generate HTML dashboard"""
        # Create HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Agent Health Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 10px 20px; }}
                .summary {{ display: flex; flex-wrap: wrap; justify-content: space-between; margin: 20px 0; }}
                .card {{ background-color: #f0f0f0; padding: 15px; margin: 10px; border-radius: 5px; min-width: 200px; }}
                .metric {{ font-size: 24px; font-weight: bold; }}
                .charts {{ display: flex; flex-wrap: wrap; justify-content: center; }}
                .chart {{ margin: 15px; text-align: center; }}
                .chart img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
                .alerts {{ margin: 20px 0; }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .warning {{ background-color: #fff3cd; }}
                .critical {{ background-color: #f8d7da; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .danger {{ color: red; }}
                .refresh {{ text-align: center; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>Agent Health Dashboard</h1>
                    <p>Last updated: {timestamp_utc()}</p>
                </div>
                
                <div class="summary">
        """

        # Add agent summary cards
        for agent_id, agent in self.agent_states.items():
            health_score = self._calculate_health_score(agent_id)
            health_class = "good" if health_score >= 0.9 else "warning" if health_score >= 0.7 else "danger"

            html_content += f"""
                    <div class="card">
                        <h3>{agent_id.split('://')[-1]}</h3>
                        <div class="metric {health_class}">{health_score * 100:.0f}%</div>
                        <p>Latency: {agent.get('latency_ms', 0)} ms</p>
                        <p>Reliability: {agent.get('reliability', 0.0):.2f}</p>
                        <p>Status: {agent.get('status', 'unknown')}</p>
                        <p>Last seen: {agent.get('last_seen', 'unknown')}</p>
                    </div>
            """

        html_content += """
                </div>
                
                <div class="charts">
                    <div class="chart">
                        <h3>Summary Dashboard</h3>
                        <img src="summary_dashboard.png" alt="Summary Dashboard">
                    </div>
                    <div class="chart">
                        <h3>Latency Over Time</h3>
                        <img src="latency_chart.png" alt="Latency Chart">
                    </div>
                    <div class="chart">
                        <h3>Reliability Over Time</h3>
                        <img src="reliability_chart.png" alt="Reliability Chart">
                    </div>
                    <div class="chart">
                        <h3>Memory Usage</h3>
                        <img src="memory_chart.png" alt="Memory Chart">
                    </div>
                    <div class="chart">
                        <h3>Health Scores</h3>
                        <img src="health_score_chart.png" alt="Health Score Chart">
                    </div>
                </div>
                
                <div class="alerts">
                    <h2>Recent Alerts</h2>
        """

        # Add recent alerts
        if self.alert_history:
            html_content += """
                    <table>
                        <tr>
                            <th>Time</th>
                            <th>Agent</th>
                            <th>Type</th>
                            <th>Value</th>
                            <th>Threshold</th>
                            <th>Severity</th>
                        </tr>
            """

            for alert in self.alert_history[-10:]:
                alert_class = "critical" if alert.get(
                    "severity") == "critical" else "warning"
                html_content += f"""
                        <tr class="{alert_class}">
                            <td>{alert.get('ts', '')}</td>
                            <td>{alert.get('agent_id', '').split('://')[-1]}</td>
                            <td>{alert.get('alert_type', '')}</td>
                            <td>{alert.get('value', '')}</td>
                            <td>{alert.get('threshold', '')}</td>
                            <td>{alert.get('severity', '')}</td>
                        </tr>
                """

            html_content += """
                    </table>
            """
        else:
            html_content += """
                    <p>No recent alerts. All systems normal.</p>
            """

        html_content += """
                </div>
                
                <div class="refresh">
                    <p>This dashboard auto-refreshes every 5 minutes. Last refresh: {timestamp_utc()}</p>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 5 minutes
                setTimeout(function() {{
                    location.reload();
                }}, 300000);
            </script>
        </body>
        </html>
        """

        # Write HTML file
        with open(f"{DASHBOARD_DIR}/index.html", 'w') as f:
            f.write(html_content)


def main():
    """Command line interface for agent health monitor"""
    parser = argparse.ArgumentParser(description="Agent Health Monitoring System")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--dashboard", action="store_true", help="Generate dashboard")
    parser.add_argument("--alerts", action="store_true", help="Show recent alerts")
    parser.add_argument("--sync", action="store_true", help="Trigger flash sync")

    args = parser.parse_args()

    # Initialize monitor
    monitor = AgentHealthMonitor()

    if args.start:
        monitor.start_monitoring()
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("Monitoring stopped")

    elif args.stop:
        monitor.stop_monitoring()
        print("Monitoring stopped")

    elif args.dashboard:
        monitor._generate_dashboard()
        print(f"Dashboard generated in {DASHBOARD_DIR}/index.html")

    elif args.alerts:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = [json.loads(line) for line in f if line.strip()]

            print(f"Recent Alerts ({len(alerts)}):")
            for alert in alerts[-10:]:
                print(f"[{alert.get('ts', '')}] {alert.get('agent_id', '')}: {alert.get('alert_type', '')} - {alert.get('value', '')} (threshold: {alert.get('threshold', '')})")
        else:
            print("No alerts found")

    elif args.sync:
        monitor._trigger_flash_sync()
        print("Flash sync triggered")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
