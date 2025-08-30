#!/usr/bin/env python3
"""
Agent Flash Sync Dashboard
Displays the results and statistics from scheduled flash syncs
"""

import datetime
import glob
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Configuration
SYNC_RESULTS_DIR = Path("./sync_results")
SYNC_DIR = Path("./sync")
REPORTS_DIR = Path("./dashboard/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_sync_results():
    """Load all sync results from the results directory"""
    results = []

    for result_file in sorted(SYNC_RESULTS_DIR.glob("*.json")):
        try:
            with open(result_file, "r") as f:
                data = json.load(f)

                # Add the filename info
                filename = result_file.name
                parts = filename.split("_")
                if len(parts) >= 3:
                    data["schedule_name"] = parts[1]
                    timestamp_str = "_".join(parts[2:]).replace(".json", "")
                    try:
                        data["timestamp"] = datetime.datetime.strptime(
                            timestamp_str, "%Y%m%d_%H%M%S"
                        )
                    except ValueError:
                        data["timestamp"] = datetime.datetime.fromtimestamp(
                            result_file.stat().st_mtime
                        )
                else:
                    data["schedule_name"] = "unknown"
                    data["timestamp"] = datetime.datetime.fromtimestamp(
                        result_file.stat().st_mtime
                    )

                results.append(data)
        except Exception as e:
            print(f"Error loading {result_file}: {e}")
            continue

    # Sort by timestamp
    results.sort(key=lambda x: x["timestamp"])
    return results


def load_agent_states():
    """Load the most recent agent states from sync snapshots"""
    agents = {}

    # Find the most recent snapshot file
    snapshot_files = sorted(SYNC_DIR.glob("*_snapshots.json"))
    if not snapshot_files:
        return agents

    latest_snapshot = snapshot_files[-1]

    try:
        with open(latest_snapshot, "r") as f:
            snapshots = json.load(f)

            for snapshot in snapshots:
                agent_id = snapshot.get("agent_id", "unknown")
                agents[agent_id] = {
                    "latency_ms": snapshot.get("latency_ms", 0),
                    "reliability": snapshot.get("reliability", 0),
                    "state_hash": snapshot.get("state_hash", ""),
                    "skills_active": snapshot.get("skills_active", []),
                    "memory_usage_mb": snapshot.get("memory_usage_mb", 0),
                    "timestamp": snapshot.get("ts", "")
                }
    except Exception as e:
        print(f"Error loading agent states: {e}")

    return agents


def generate_reports():
    """Generate dashboard reports and visualizations"""
    results = load_sync_results()
    if not results:
        return

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)

    # Ensure timestamp is datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Generate consensus trend
    if "consensus_achieved" in df.columns:
        plt.figure(figsize=(10, 6))
        df["consensus_int"] = df["consensus_achieved"].astype(int)
        df.plot(x="timestamp", y="consensus_int", kind="line",
                title="Consensus Achievement Over Time")
        plt.ylabel("Consensus Achieved (1=Yes, 0=No)")
        plt.savefig(REPORTS_DIR / "consensus_trend.png")
        plt.close()

    # Generate anomaly trend
    if "anomalies" in df.columns:
        plt.figure(figsize=(10, 6))
        df.plot(x="timestamp", y="anomalies", kind="line",
                title="Anomalies Detected Over Time")
        plt.ylabel("Number of Anomalies")
        plt.savefig(REPORTS_DIR / "anomaly_trend.png")
        plt.close()

    # Generate sync time distribution by schedule
    if "schedule_name" in df.columns and df["schedule_name"].nunique() > 1:
        plt.figure(figsize=(10, 6))
        df.groupby("schedule_name")["anomalies"].mean().plot(
            kind="bar", title="Average Anomalies by Schedule"
        )
        plt.ylabel("Average Anomalies")
        plt.savefig(REPORTS_DIR / "anomalies_by_schedule.png")
        plt.close()

    # Save summary stats
    summary = {
        "total_syncs": len(df),
        "success_rate": df["consensus_achieved"].mean() if "consensus_achieved" in df.columns else None,
        "total_anomalies": df["anomalies"].sum() if "anomalies" in df.columns else None,
        "last_sync": df["timestamp"].max().isoformat() if "timestamp" in df.columns else None,
    }

    with open(REPORTS_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)


@app.route("/")
def index():
    """Main dashboard page"""
    generate_reports()

    # Load the latest data
    results = load_sync_results()
    agents = load_agent_states()

    # Get summary statistics
    summary = {}
    if os.path.exists(REPORTS_DIR / "summary.json"):
        with open(REPORTS_DIR / "summary.json", "r") as f:
            summary = json.load(f)

    # Get the latest sync result
    latest_sync = results[-1] if results else {}

    return render_template(
        "index.html",
        agents=agents,
        summary=summary,
        latest_sync=latest_sync,
        results=results[-10:],  # Last 10 results
    )


@app.route("/api/agents")
def api_agents():
    """API endpoint for agent data"""
    return jsonify(load_agent_states())


@app.route("/api/syncs")
def api_syncs():
    """API endpoint for sync results"""
    return jsonify(load_sync_results())


def create_template_directory():
    """Create the templates directory and HTML file for the dashboard"""
    templates_dir = Path("./dashboard/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    with open(templates_dir / "index.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Agent Flash Sync Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 20px; }
        .agent-card { margin-bottom: 20px; }
        .anomaly { color: #dc3545; }
        .healthy { color: #198754; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Agent Flash Sync Dashboard</h1>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Sync Summary</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Total Syncs:</strong> {{ summary.total_syncs }}</p>
                        <p><strong>Success Rate:</strong> {{ "%.2f"|format(summary.success_rate*100) }}%</p>
                        <p><strong>Total Anomalies:</strong> {{ summary.total_anomalies }}</p>
                        <p><strong>Last Sync:</strong> {{ summary.last_sync }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Latest Sync Result</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Sync ID:</strong> {{ latest_sync.sync_id }}</p>
                        <p><strong>Time:</strong> {{ latest_sync.ts }}</p>
                        <p><strong>Consensus:</strong> 
                            <span class="{% if latest_sync.consensus_achieved %}healthy{% else %}anomaly{% endif %}">
                                {{ "Achieved" if latest_sync.consensus_achieved else "Failed" }}
                            </span>
                        </p>
                        <p><strong>Anomalies:</strong> 
                            <span class="{% if latest_sync.anomalies > 0 %}anomaly{% else %}healthy{% endif %}">
                                {{ latest_sync.anomalies }}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <h2 class="mb-3">Agent States</h2>
        <div class="row">
            {% for agent_id, agent in agents.items() %}
            <div class="col-md-4">
                <div class="card agent-card">
                    <div class="card-header">
                        <h5>{{ agent_id }}</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Latency:</strong> 
                            <span class="{% if agent.latency_ms > 300 %}anomaly{% else %}healthy{% endif %}">
                                {{ agent.latency_ms }} ms
                            </span>
                        </p>
                        <p><strong>Reliability:</strong> 
                            <span class="{% if agent.reliability < 0.85 %}anomaly{% else %}healthy{% endif %}">
                                {{ "%.2f"|format(agent.reliability*100) }}%
                            </span>
                        </p>
                        <p><strong>Memory:</strong> {{ agent.memory_usage_mb }} MB</p>
                        <p><strong>Active Skills:</strong> {{ agent.skills_active|length }}</p>
                        <p><strong>Last Updated:</strong> {{ agent.timestamp }}</p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <h2 class="mb-3">Recent Sync History</h2>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Schedule</th>
                    <th>Sync ID</th>
                    <th>Consensus</th>
                    <th>Anomalies</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                <tr>
                    <td>{{ result.timestamp }}</td>
                    <td>{{ result.schedule_name }}</td>
                    <td>{{ result.sync_id }}</td>
                    <td class="{% if result.consensus_achieved %}healthy{% else %}anomaly{% endif %}">
                        {{ "Achieved" if result.consensus_achieved else "Failed" }}
                    </td>
                    <td class="{% if result.anomalies > 0 %}anomaly{% else %}healthy{% endif %}">
                        {{ result.anomalies }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2 class="mb-3">Trend Reports</h2>
        <div class="row">
            <div class="col-md-6 mb-4">
                <img src="/dashboard/reports/consensus_trend.png" class="img-fluid" alt="Consensus Trend">
            </div>
            <div class="col-md-6 mb-4">
                <img src="/dashboard/reports/anomaly_trend.png" class="img-fluid" alt="Anomaly Trend">
            </div>
            <div class="col-md-6 mb-4">
                <img src="/dashboard/reports/anomalies_by_schedule.png" class="img-fluid" alt="Anomalies by Schedule">
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")


def main():
    """Main entry point for the dashboard"""
    create_template_directory()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
