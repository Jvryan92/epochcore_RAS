#!/usr/bin/env python3
"""
EPOCH Core - Agent Fleet Commander
Integrated dashboard for the entire agent ecosystem with epochALPHA as coordinator
"""

import datetime
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

# Try to import optional dependencies
try:
    import matplotlib
    import numpy as np
    import pandas as pd

    matplotlib.use("Agg")  # Use non-interactive backend
    import base64
    from io import BytesIO

    import matplotlib.pyplot as plt
    from flask import Flask, jsonify, render_template, request, send_from_directory

    HAS_DEPENDENCIES = True
except ImportError:
    print("WARNING: Some dependencies are missing. Installing required packages...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "flask", "matplotlib", "pandas"],
            check=True,
        )
        import matplotlib
        import numpy as np
        import pandas as pd

        matplotlib.use("Agg")  # Use non-interactive backend
        import base64
        from io import BytesIO

        import matplotlib.pyplot as plt
        from flask import Flask, jsonify, render_template, request, send_from_directory

        HAS_DEPENDENCIES = True
        print("Dependencies installed successfully!")
    except Exception as e:
        print(f"ERROR: Could not install dependencies: {e}")
        print("\nPlease install manually with:")
        print("    pip install flask matplotlib pandas\n")
        HAS_DEPENDENCIES = False


# Configuration
BASE_DIR = Path(".")
EPOCHALPHA_DIR = BASE_DIR / "epochALPHA"
FLEET_DIR = BASE_DIR / "fleet"
SYNC_DIR = BASE_DIR / "sync"
LEDGER_DIR = BASE_DIR / "ledger"
DASHBOARD_DIR = BASE_DIR / "dashboard"
REPORTS_DIR = DASHBOARD_DIR / "reports"

# Ensure directories exist
for directory in [EPOCHALPHA_DIR, FLEET_DIR, SYNC_DIR, DASHBOARD_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# Timestamp utilities


def get_timestamp():
    """Get current ISO format timestamp"""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Flask app
app = Flask(
    __name__,
    static_folder=str(DASHBOARD_DIR / "static"),
    template_folder=str(DASHBOARD_DIR / "templates"),
)

# Generate CSS


def generate_css():
    """Generate CSS for the dashboard"""
    css_dir = DASHBOARD_DIR / "static" / "css"
    css_dir.mkdir(exist_ok=True, parents=True)

    with open(css_dir / "styles.css", "w") as f:
        f.write(
            """
:root {
    --primary: #2d3748;
    --secondary: #4a5568;
    --accent: #4299e1;
    --success: #48bb78;
    --warning: #ed8936;
    --danger: #f56565;
    --light: #f7fafc;
    --dark: #1a202c;
    --quantum: #805ad5;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: var(--dark);
    background-color: #f7fafc;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 1rem;
}

.header {
    background-color: var(--primary);
    color: white;
    padding: 1rem 0;
    margin-bottom: 2rem;
}

.header h1 {
    margin: 0;
    font-size: 1.5rem;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.dashboard-full {
    grid-column: 1 / -1;
}

.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.card-header {
    padding: 1rem;
    background-color: var(--primary);
    color: white;
    font-weight: 600;
}

.card-header.alpha {
    background-color: var(--quantum);
}

.card-body {
    padding: 1rem;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}

.metric-box {
    background: var(--light);
    padding: 1rem;
    border-radius: 6px;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.metric-value.success {
    color: var(--success);
}

.metric-value.warning {
    color: var(--warning);
}

.metric-value.danger {
    color: var(--danger);
}

.metric-name {
    font-size: 0.875rem;
    color: var(--secondary);
}

.agent-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.agent-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}

.agent-item:last-child {
    border-bottom: none;
}

.agent-name {
    font-weight: 600;
}

.agent-status {
    font-size: 0.875rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
}

.status-active {
    background-color: #c6f6d5;
    color: #22543d;
}

.status-syncing {
    background-color: #bee3f8;
    color: #2c5282;
}

.status-warning {
    background-color: #feebc8;
    color: #7b341e;
}

.status-error {
    background-color: #fed7d7;
    color: #822727;
}

.chart-container {
    width: 100%;
    height: 300px;
}

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.btn-primary {
    background-color: var(--accent);
    color: white;
}

.btn-primary:hover {
    background-color: #3182ce;
}

.btn-quantum {
    background-color: var(--quantum);
    color: white;
}

.btn-quantum:hover {
    background-color: #6b46c1;
}

.tab-container {
    margin-bottom: 1.5rem;
}

.tabs {
    display: flex;
    border-bottom: 1px solid #e2e8f0;
}

.tab {
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    font-weight: 600;
}

.tab.active {
    border-bottom: 2px solid var(--accent);
    color: var(--accent);
}

.tab-content {
    display: none;
    padding: 1rem 0;
}

.tab-content.active {
    display: block;
}

.anomaly-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 0.25rem;
    background-color: #fff5f5;
    border-left: 4px solid var(--danger);
}

.task-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 0.25rem;
    background-color: var(--light);
    border-left: 4px solid var(--accent);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-primary {
    background-color: var(--accent);
    color: white;
}

.badge-success {
    background-color: var(--success);
    color: white;
}

.badge-warning {
    background-color: var(--warning);
    color: white;
}

.badge-danger {
    background-color: var(--danger);
    color: white;
}

.footer {
    margin-top: 2rem;
    padding: 1rem 0;
    border-top: 1px solid #e2e8f0;
    color: var(--secondary);
    font-size: 0.875rem;
}

.quantum-box {
    background-color: #f8f4ff;
    border: 1px solid #e9d8fd;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
}

.quantum-state {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}

.quantum-state-indicator {
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background-color: var(--quantum);
    margin-right: 0.5rem;
    opacity: 0.7;
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.1); opacity: 1; }
    100% { transform: scale(1); opacity: 0.7; }
}

.quantum-state-indicator.active {
    animation: pulse 2s infinite;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr 1fr;
    }
    
    .header-content {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .header-content h1 {
        margin-bottom: 1rem;
    }
}
        """
        )


# Generate HTML


def generate_html():
    """Generate HTML template for the dashboard"""
    templates_dir = DASHBOARD_DIR / "templates"
    templates_dir.mkdir(exist_ok=True, parents=True)

    with open(templates_dir / "index.html", "w") as f:
        f.write(
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPOCH Core - Agent Fleet Commander</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header class="header">
        <div class="container header-content">
            <h1>EPOCH Core - Agent Fleet Commander</h1>
            <div>
                <span id="last-updated">Last updated: {{ last_updated }}</span>
                <a href="/sync/alpha" class="btn btn-quantum">Sync epochALPHA</a>
                <a href="/sync/fleet" class="btn btn-primary">Sync Fleet</a>
            </div>
        </div>
    </header>
    
    <main class="container">
        <!-- Alpha Agent Status -->
        <div class="dashboard-grid">
            <div class="card dashboard-full">
                <div class="card-header alpha">
                    epochALPHA Status (Quantum Horizon)
                </div>
                <div class="card-body">
                    <div class="metrics-grid">
                        <div class="metric-box">
                            <div class="metric-value {{ 'success' if alpha_agent.health_score >= 0.9 else ('warning' if alpha_agent.health_score >= 0.7 else 'danger') }}">
                                {{ "%.2f"|format(alpha_agent.health_score*100) }}%
                            </div>
                            <div class="metric-name">Health Score</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">
                                {{ alpha_agent.latency_ms }} ms
                            </div>
                            <div class="metric-name">Latency</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value {{ 'success' if alpha_agent.sync_success_rate >= 0.9 else ('warning' if alpha_agent.sync_success_rate >= 0.7 else 'danger') }}">
                                {{ "%.0f"|format(alpha_agent.sync_success_rate*100) }}%
                            </div>
                            <div class="metric-name">Sync Success</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value {{ 'success' if alpha_agent.anomalies == 0 else ('warning' if alpha_agent.anomalies < 3 else 'danger') }}">
                                {{ alpha_agent.anomalies }}
                            </div>
                            <div class="metric-name">Anomalies</div>
                        </div>
                    </div>
                    
                    <div class="quantum-box">
                        <h3>Quantum Bridge Status</h3>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                            <div>
                                <strong>Status:</strong> {{ alpha_agent.quantum_bridge.bridge_status }}
                            </div>
                            <div>
                                <strong>Entanglement Quality:</strong> {{ "%.2f"|format(alpha_agent.quantum_bridge.entanglement_quality*100) }}%
                            </div>
                            <div>
                                <strong>Decoherence Estimate:</strong> {{ "%.2f"|format(alpha_agent.quantum_bridge.decoherence_estimate_us/1000) }} ms
                            </div>
                        </div>
                        
                        <h4>Quantum States</h4>
                        <div style="display: flex; flex-wrap: wrap;">
                            {% for state in alpha_agent.quantum_bridge.quantum_states %}
                            <div class="quantum-state">
                                <div class="quantum-state-indicator {{ 'active' if state.entangled_with else '' }}"></div>
                                <div>
                                    <strong>{{ state.q_id }}</strong>
                                    {% if state.entangled_with %}
                                    <span class="badge badge-primary">Entangled with {{ state.entangled_with }}</span>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Agent Fleet Status -->
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    Agent Fleet Status
                </div>
                <div class="card-body">
                    <ul class="agent-list">
                        {% for agent in fleet_agents %}
                        <li class="agent-item">
                            <div class="agent-name">{{ agent.id }}</div>
                            <div class="agent-status {{ agent.status_class }}">{{ agent.status }}</div>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    Fleet Metrics
                </div>
                <div class="card-body">
                    <canvas id="fleetMetricsChart" class="chart-container"></canvas>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    Sync History
                </div>
                <div class="card-body">
                    <canvas id="syncHistoryChart" class="chart-container"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Strategic Directives -->
        <div class="dashboard-grid">
            <div class="card dashboard-full">
                <div class="card-header">
                    Strategic Directives
                </div>
                <div class="card-body">
                    <div class="tab-container">
                        <div class="tabs">
                            <div class="tab active" data-tab="priorities">Priorities</div>
                            <div class="tab" data-tab="tasks">Active Tasks</div>
                            <div class="tab" data-tab="contingency">Contingency Plans</div>
                        </div>
                        
                        <div class="tab-content active" id="priorities">
                            <div style="max-width: 600px; margin: 0 auto;">
                                <canvas id="prioritiesChart"></canvas>
                            </div>
                        </div>
                        
                        <div class="tab-content" id="tasks">
                            {% for task in alpha_agent.strategic_directives.directives %}
                            <div class="task-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <h3 style="margin: 0 0 0.5rem 0;">{{ task.name }}</h3>
                                    <span class="badge badge-{{ 'danger' if task.priority == 'high' else ('warning' if task.priority == 'medium' else 'primary') }}">
                                        {{ task.priority }}
                                    </span>
                                </div>
                                <p>{{ task.description }}</p>
                                <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
                                    <div>
                                        <strong>Assigned to:</strong> {{ ", ".join(task.assigned_to) }}
                                    </div>
                                    <div>
                                        <strong>Deadline:</strong> {{ task.deadline }}
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="tab-content" id="contingency">
                            {% for plan in alpha_agent.strategic_directives.contingency_plans %}
                            <div class="task-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong>Trigger:</strong> {{ plan.trigger }}
                                </div>
                                <div style="margin-top: 0.5rem;">
                                    <strong>Action:</strong> {{ plan.action }}
                                </div>
                                <div style="margin-top: 0.5rem; font-size: 0.875rem;">
                                    <strong>Authorized by:</strong> {{ plan.authorized_by }}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Anomalies and System Health -->
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    Recent Anomalies
                </div>
                <div class="card-body">
                    {% if anomalies %}
                        {% for anomaly in anomalies %}
                        <div class="anomaly-item">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>{{ anomaly.agent_id }}</strong>
                                <span>{{ anomaly.timestamp }}</span>
                            </div>
                            <div style="margin-top: 0.5rem;">
                                {{ anomaly.description }}
                            </div>
                            <div style="margin-top: 0.5rem; display: flex; justify-content: space-between; font-size: 0.875rem;">
                                <span class="badge badge-{{ 'danger' if anomaly.severity == 'high' else ('warning' if anomaly.severity == 'medium' else 'primary') }}">
                                    {{ anomaly.severity }}
                                </span>
                                <span>{{ anomaly.status }}</span>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p>No recent anomalies detected.</p>
                    {% endif %}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    System Health
                </div>
                <div class="card-body">
                    <canvas id="systemHealthChart" class="chart-container"></canvas>
                </div>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>EPOCH Core - Agent Fleet Commander | {{ version }} | &copy; 2025</p>
        </div>
    </footer>
    
    <script>
        // Tab functionality
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });
        
        // Charts
        document.addEventListener('DOMContentLoaded', () => {
            // Fleet Metrics Chart
            const fleetMetricsCtx = document.getElementById('fleetMetricsChart').getContext('2d');
            new Chart(fleetMetricsCtx, {
                type: 'bar',
                data: {
                    labels: {{ fleet_metrics.labels|tojson }},
                    datasets: [
                        {
                            label: 'Reliability',
                            data: {{ fleet_metrics.reliability|tojson }},
                            backgroundColor: '#4299e1',
                        },
                        {
                            label: 'Latency (ms)',
                            data: {{ fleet_metrics.latency|tojson }},
                            backgroundColor: '#f6ad55',
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // Sync History Chart
            const syncHistoryCtx = document.getElementById('syncHistoryChart').getContext('2d');
            new Chart(syncHistoryCtx, {
                type: 'line',
                data: {
                    labels: {{ sync_history.labels|tojson }},
                    datasets: [
                        {
                            label: 'Success Rate',
                            data: {{ sync_history.success_rate|tojson }},
                            borderColor: '#48bb78',
                            backgroundColor: 'rgba(72, 187, 120, 0.2)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Anomalies',
                            data: {{ sync_history.anomalies|tojson }},
                            borderColor: '#f56565',
                            backgroundColor: 'rgba(245, 101, 101, 0.2)',
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // Priorities Chart
            const prioritiesCtx = document.getElementById('prioritiesChart').getContext('2d');
            new Chart(prioritiesCtx, {
                type: 'doughnut',
                data: {
                    labels: {{ priorities.labels|tojson }},
                    datasets: [{
                        data: {{ priorities.values|tojson }},
                        backgroundColor: [
                            '#4299e1',
                            '#48bb78',
                            '#f6ad55',
                            '#f56565',
                            '#805ad5'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                        }
                    }
                }
            });
            
            // System Health Chart
            const systemHealthCtx = document.getElementById('systemHealthChart').getContext('2d');
            new Chart(systemHealthCtx, {
                type: 'line',
                data: {
                    labels: {{ system_health.labels|tojson }},
                    datasets: [{
                        label: 'System Health Score',
                        data: {{ system_health.values|tojson }},
                        borderColor: '#805ad5',
                        backgroundColor: 'rgba(128, 90, 213, 0.2)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 50,
                            max: 100
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>"""
        )


# Load or simulate epochALPHA data


def load_alpha_agent():
    """Load or simulate epochALPHA agent data"""
    latest_sync_file = None

    # Look for actual sync results
    sync_files = list(EPOCHALPHA_DIR.glob("sync/*_result.json"))
    if sync_files:
        latest_sync_file = max(sync_files, key=os.path.getmtime)

    if latest_sync_file and latest_sync_file.exists():
        try:
            with open(latest_sync_file, "r") as f:
                data = json.load(f)
                return {
                    "id": data.get("agent", {}).get("id", "agent://epochALPHA"),
                    "version": data.get("agent", {}).get("version", "6.3.2"),
                    "codename": data.get("agent", {}).get(
                        "codename", "Quantum Horizon"
                    ),
                    "health_score": data.get("metrics", {}).get("health_score", 0.95),
                    "latency_ms": data.get("metrics", {}).get("network_latency_ms", 75),
                    "sync_success_rate": data.get("metrics", {}).get(
                        "sync_success_rate", 0.9
                    ),
                    "anomalies": data.get("metrics", {}).get("anomalies_detected", 0),
                    "quantum_bridge": data.get(
                        "quantum_bridge",
                        {
                            "bridge_status": "operational",
                            "entanglement_quality": 0.92,
                            "decoherence_estimate_us": 100000,
                            "quantum_states": [],
                        },
                    ),
                    "strategic_directives": data.get(
                        "strategic_directives",
                        {"priorities": [], "directives": [], "contingency_plans": []},
                    ),
                    "last_updated": data.get("timestamp", get_timestamp()),
                }
        except Exception as e:
            print(f"Error loading alpha agent data: {e}")

    # Fallback to simulated data
    return {
        "id": "agent://epochALPHA",
        "version": "6.3.2",
        "codename": "Quantum Horizon",
        "health_score": 0.95,
        "latency_ms": 75,
        "sync_success_rate": 0.9,
        "anomalies": 0,
        "quantum_bridge": {
            "bridge_status": "operational",
            "entanglement_quality": 0.92,
            "decoherence_estimate_us": 100000,
            "quantum_states": [
                {"q_id": "q0", "entangled_with": "q1", "coherence": 0.95},
                {"q_id": "q1", "entangled_with": "q0", "coherence": 0.95},
                {"q_id": "q2", "entangled_with": None, "coherence": 0.88},
                {"q_id": "q3", "entangled_with": "q4", "coherence": 0.91},
                {"q_id": "q4", "entangled_with": "q3", "coherence": 0.91},
            ],
        },
        "strategic_directives": {
            "priorities": [
                {"name": "system_integrity", "weight": 0.35},
                {"name": "data_consistency", "weight": 0.25},
                {"name": "anomaly_detection", "weight": 0.20},
                {"name": "resource_optimization", "weight": 0.15},
                {"name": "quantum_readiness", "weight": 0.05},
            ],
            "directives": [
                {
                    "id": "d1",
                    "name": "Enhance mesh resilience",
                    "description": "Improve fault tolerance and recovery mechanisms",
                    "assigned_to": ["agent://bravo", "agent://delta"],
                    "priority": "high",
                    "deadline": (
                        datetime.datetime.now() + datetime.timedelta(days=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "id": "d2",
                    "name": "Optimize data consensus",
                    "description": "Fine-tune PBFT parameters for faster convergence",
                    "assigned_to": ["agent://gamma"],
                    "priority": "medium",
                    "deadline": (
                        datetime.datetime.now() + datetime.timedelta(days=5)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "id": "d3",
                    "name": "Quantum channel preparation",
                    "description": "Prepare secure quantum channels for next-gen protocols",
                    "assigned_to": ["agent://alpha", "agent://epsilon"],
                    "priority": "low",
                    "deadline": (
                        datetime.datetime.now() + datetime.timedelta(days=14)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            ],
            "contingency_plans": [
                {
                    "trigger": "reliability_below_90",
                    "action": "activate_backup_nodes",
                    "authorized_by": "agent://epochALPHA",
                },
                {
                    "trigger": "anomalies_exceed_5",
                    "action": "initiate_security_audit",
                    "authorized_by": "agent://epochALPHA",
                },
            ],
        },
        "last_updated": get_timestamp(),
    }


# Load fleet agents


def load_fleet_agents():
    """Load or simulate fleet agent data"""
    agents = []

    # Check for sync results
    snapshot_files = list(SYNC_DIR.glob("*_snapshots.json"))

    if snapshot_files:
        try:
            # Get the most recent snapshot
            latest_snapshot = max(snapshot_files, key=os.path.getmtime)
            with open(latest_snapshot, "r") as f:
                data = json.load(f)

                for snapshot in data:
                    agent_id = snapshot.get("agent_id", "unknown")
                    latency = snapshot.get("latency_ms", 0)
                    reliability = snapshot.get("reliability", 0)

                    # Determine status based on metrics
                    if reliability < 0.7:
                        status = "Error"
                        status_class = "status-error"
                    elif latency > 350:
                        status = "Warning"
                        status_class = "status-warning"
                    else:
                        status = "Active"
                        status_class = "status-active"

                    agents.append(
                        {
                            "id": agent_id,
                            "status": status,
                            "status_class": status_class,
                            "reliability": reliability,
                            "latency_ms": latency,
                            "last_updated": snapshot.get("ts", get_timestamp()),
                        }
                    )

                return agents
        except Exception as e:
            print(f"Error loading fleet agents: {e}")

    # Fallback to default agents
    return [
        {
            "id": "agent://alpha",
            "status": "Active",
            "status_class": "status-active",
            "reliability": 0.94,
            "latency_ms": 210,
        },
        {
            "id": "agent://bravo",
            "status": "Active",
            "status_class": "status-active",
            "reliability": 0.92,
            "latency_ms": 250,
        },
        {
            "id": "agent://gamma",
            "status": "Active",
            "status_class": "status-active",
            "reliability": 0.90,
            "latency_ms": 300,
        },
        {
            "id": "agent://delta",
            "status": "Active",
            "status_class": "status-active",
            "reliability": 0.91,
            "latency_ms": 230,
        },
        {
            "id": "agent://epsilon",
            "status": "Active",
            "status_class": "status-active",
            "reliability": 0.89,
            "latency_ms": 275,
        },
    ]


# Generate metrics for charts


def generate_metrics():
    """Generate metrics for dashboard charts"""
    fleet_agents = load_fleet_agents()

    # Fleet metrics
    fleet_metrics = {
        "labels": [agent["id"].replace("agent://", "") for agent in fleet_agents],
        "reliability": [agent["reliability"] * 100 for agent in fleet_agents],
        "latency": [agent["latency_ms"] for agent in fleet_agents],
    }

    # Sync history
    sync_history = {
        "labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "success_rate": [92, 95, 89, 94, 97],
        "anomalies": [3, 1, 5, 2, 0],
    }

    # Priorities
    alpha_agent = load_alpha_agent()
    priorities = {
        "labels": [
            p["name"] for p in alpha_agent["strategic_directives"]["priorities"]
        ],
        "values": [
            p["weight"] * 100 for p in alpha_agent["strategic_directives"]["priorities"]
        ],
    }

    # System health over time
    system_health = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4", "Current"],
        "values": [88, 92, 86, 91, 95],
    }

    return {
        "fleet_metrics": fleet_metrics,
        "sync_history": sync_history,
        "priorities": priorities,
        "system_health": system_health,
    }


# Generate anomalies


def generate_anomalies():
    """Generate simulated anomalies"""
    anomalies = []

    # Check if epochALPHA has anomalies
    alpha_agent = load_alpha_agent()
    if alpha_agent["anomalies"] > 0:
        for i in range(alpha_agent["anomalies"]):
            anomalies.append(
                {
                    "agent_id": alpha_agent["id"],
                    "timestamp": get_timestamp(),
                    "description": random.choice(
                        [
                            "Quantum decoherence rate exceeded threshold",
                            "Unexpected latency spike during fleet coordination",
                            "Security audit failed for mesh topology verification",
                        ]
                    ),
                    "severity": random.choice(["low", "medium", "high"]),
                    "status": "Investigating",
                }
            )

    # Add some fleet anomalies if any agent has warning/error status
    fleet_agents = load_fleet_agents()
    for agent in fleet_agents:
        if agent["status"] in ["Warning", "Error"]:
            anomalies.append(
                {
                    "agent_id": agent["id"],
                    "timestamp": get_timestamp(),
                    "description": random.choice(
                        [
                            f"Agent reliability dropped below threshold ({agent['reliability']*100:.1f}%)",
                            f"Latency spike detected ({agent['latency_ms']} ms)",
                            "Failed to complete assigned tasks",
                            "Communication interruption detected",
                        ]
                    ),
                    "severity": "medium" if agent["status"] == "Warning" else "high",
                    "status": "Active",
                }
            )

    return anomalies


# Routes


@app.route("/")
def index():
    """Main dashboard page"""
    alpha_agent = load_alpha_agent()
    fleet_agents = load_fleet_agents()
    metrics = generate_metrics()
    anomalies = generate_anomalies()

    return render_template(
        "index.html",
        alpha_agent=alpha_agent,
        fleet_agents=fleet_agents,
        fleet_metrics=metrics["fleet_metrics"],
        sync_history=metrics["sync_history"],
        priorities=metrics["priorities"],
        system_health=metrics["system_health"],
        anomalies=anomalies,
        last_updated=get_timestamp(),
        version="v1.0.0",
    )


@app.route("/sync/alpha")
def sync_alpha():
    """Trigger epochALPHA sync"""
    try:
        result = subprocess.run(
            [sys.executable, "sync_epochALPHA.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        return jsonify(
            {
                "success": True,
                "message": "epochALPHA sync completed",
                "output": result.stdout,
            }
        )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error syncing epochALPHA: {str(e)}"}
        )


@app.route("/sync/fleet")
def sync_fleet():
    """Trigger fleet sync"""
    try:
        result = subprocess.run(
            [sys.executable, "flash_sync_agents.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        return jsonify(
            {
                "success": True,
                "message": "Fleet sync completed",
                "output": result.stdout,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error syncing fleet: {str(e)}"})


@app.route("/static/<path:path>")
def serve_static(path):
    """Serve static files"""
    return send_from_directory(DASHBOARD_DIR / "static", path)


# Main function


def main():
    """Main entry point"""
    print("🚀 Initializing EPOCH Core - Agent Fleet Commander")

    # Generate static files
    generate_css()
    generate_html()

    print("✅ Dashboard template files generated")
    print("🔄 Starting web server...")

    # Start the server
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
