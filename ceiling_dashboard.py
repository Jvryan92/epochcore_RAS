#!/usr/bin/env python3
"""
Ceiling Dashboard - Real-time web interface for monitoring ceiling performance
Provides visual analytics and management interface for EPOCH5 ceiling system
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Simple HTTP server for the dashboard
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

try:
    from ceiling_manager import CeilingManager, ServiceTier, CeilingType
    from integration import EPOCH5Integration

    CEILING_AVAILABLE = True
except ImportError:
    CEILING_AVAILABLE = False


class CeilingDashboardHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, ceiling_manager=None, integration=None, **kwargs):
        self.ceiling_manager = ceiling_manager
        self.integration = integration
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests for dashboard endpoints"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/" or path == "/dashboard":
            self.serve_dashboard()
        elif path == "/api/status":
            self.serve_api_status()
        elif path == "/api/ceilings":
            self.serve_api_ceilings()
        elif path == "/api/performance":
            self.serve_api_performance()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_api_status(self):
        """Serve system status API"""
        if not self.integration:
            self.send_json_response({"error": "Integration not available"})
            return

        status = self.integration.get_system_status()
        self.send_json_response(status)

    def serve_api_ceilings(self):
        """Serve ceiling configurations API"""
        if not self.ceiling_manager:
            self.send_json_response({"error": "Ceiling manager not available"})
            return

        ceilings_data = self.ceiling_manager.load_ceilings()
        service_tiers = self.ceiling_manager.load_service_tiers()

        response = {
            "configurations": ceilings_data.get("configurations", {}),
            "service_tiers": service_tiers.get("tiers", {}),
            "last_updated": ceilings_data.get("last_updated", ""),
        }
        self.send_json_response(response)

    def serve_api_performance(self):
        """Serve performance history API"""
        if not self.ceiling_manager:
            self.send_json_response({"error": "Ceiling manager not available"})
            return

        # Load performance history from ceiling events log
        performance_data = []
        events_log = self.ceiling_manager.ceiling_events_log

        if events_log.exists():
            try:
                with open(events_log, "r") as f:
                    for line in f:
                        if line.strip():
                            event = json.loads(line)
                            if event.get("event_type") == "DYNAMIC_ADJUSTMENT":
                                performance_data.append(
                                    {
                                        "timestamp": event["timestamp"],
                                        "config_id": event["data"]["config_id"],
                                        "performance_score": event["data"][
                                            "performance_score"
                                        ],
                                        "adjustments": event["data"]["adjustments"],
                                    }
                                )
            except Exception as e:
                performance_data = [
                    {"error": f"Failed to load performance data: {str(e)}"}
                ]

        self.send_json_response(performance_data[-50:])  # Return last 50 entries

    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def generate_dashboard_html(self):
        """Generate the dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPOCH5 Ceiling Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .dashboard-container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #667eea;
        }
        .header h1 {
            color: #4a5568;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #718096;
            font-size: 1.1em;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-2px); }
        .metric-card h3 {
            color: #4a5568;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-change {
            font-size: 0.9em;
            color: #718096;
        }
        .tiers-section, .performance-section {
            margin-bottom: 30px;
        }
        .section-title {
            color: #4a5568;
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
        }
        .tier-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        .tier-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .tier-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #4a5568;
        }
        .tier-price {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .tier-limits {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        .limit-item {
            background: #f7fafc;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        .limit-label {
            font-size: 0.8em;
            color: #718096;
            text-transform: uppercase;
        }
        .limit-value {
            font-size: 1.1em;
            font-weight: bold;
            color: #4a5568;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px;
            transition: background 0.2s;
        }
        .refresh-btn:hover { background: #5a67d8; }
        .performance-chart {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            min-height: 200px;
            text-align: center;
        }
        .loading { 
            color: #718096; 
            font-style: italic; 
            padding: 20px;
        }
        .error { 
            color: #e53e3e; 
            background: #fed7d7; 
            padding: 15px; 
            border-radius: 6px; 
            margin: 10px 0; 
        }
        .success {
            color: #38a169;
            background: #c6f6d5;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .auto-refresh {
            text-align: right;
            margin-bottom: 20px;
            color: #718096;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🏗️ EPOCH5 Ceiling Dashboard</h1>
            <div class="subtitle">Real-time Performance & Revenue Optimization</div>
        </div>
        
        <div class="auto-refresh">
            <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh Data</button>
            Auto-refresh: <span id="countdown">30</span>s
        </div>
        
        <div class="metrics-grid" id="metricsGrid">
            <div class="loading">Loading system metrics...</div>
        </div>
        
        <div class="tiers-section">
            <h2 class="section-title">💰 Service Tier Pricing</h2>
            <div id="tiersContainer">
                <div class="loading">Loading service tiers...</div>
            </div>
        </div>
        
        <div class="performance-section">
            <h2 class="section-title">📊 Performance Monitoring</h2>
            <div class="performance-chart" id="performanceChart">
                <div class="loading">Loading performance data...</div>
            </div>
        </div>
    </div>

    <script>
        let refreshInterval;
        let countdownInterval;
        let secondsLeft = 30;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
            startAutoRefresh();
        });
        
        function startAutoRefresh() {
            refreshInterval = setInterval(refreshAll, 30000);
            countdownInterval = setInterval(updateCountdown, 1000);
        }
        
        function updateCountdown() {
            secondsLeft--;
            document.getElementById('countdown').textContent = secondsLeft;
            if (secondsLeft <= 0) {
                secondsLeft = 30;
            }
        }
        
        async function refreshAll() {
            secondsLeft = 30;
            await Promise.all([
                loadSystemMetrics(),
                loadServiceTiers(),
                loadPerformanceData()
            ]);
        }
        
        async function loadSystemMetrics() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                displaySystemMetrics(data);
            } catch (error) {
                document.getElementById('metricsGrid').innerHTML = 
                    `<div class="error">Error loading metrics: ${error.message}</div>`;
            }
        }
        
        function displaySystemMetrics(data) {
            const components = data.components;
            const html = `
                <div class="metric-card">
                    <h3>Active Agents</h3>
                    <div class="metric-value">${components.agents.active}</div>
                    <div class="metric-change">of ${components.agents.total} total</div>
                </div>
                <div class="metric-card">
                    <h3>Ceiling Configs</h3>
                    <div class="metric-value">${components.ceilings?.total_configurations || 0}</div>
                    <div class="metric-change">Avg Score: ${components.ceilings?.average_performance_score || 'N/A'}</div>
                </div>
                <div class="metric-card">
                    <h3>Active Policies</h3>
                    <div class="metric-value">${components.policies.active_policies}</div>
                    <div class="metric-change">${components.policies.total_grants} grants</div>
                </div>
                <div class="metric-card">
                    <h3>Cycle Status</h3>
                    <div class="metric-value">${components.cycles.completed}</div>
                    <div class="metric-change">of ${components.cycles.total} completed</div>
                </div>
                <div class="metric-card">
                    <h3>Dynamic Adjustments</h3>
                    <div class="metric-value">${components.ceilings?.dynamic_adjustments_active || 0}</div>
                    <div class="metric-change">configurations with active adjustments</div>
                </div>
                <div class="metric-card">
                    <h3>System Status</h3>
                    <div class="metric-value">✅</div>
                    <div class="metric-change">All systems operational</div>
                </div>
            `;
            document.getElementById('metricsGrid').innerHTML = html;
        }
        
        async function loadServiceTiers() {
            try {
                const response = await fetch('/api/ceilings');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                displayServiceTiers(data.service_tiers);
            } catch (error) {
                document.getElementById('tiersContainer').innerHTML = 
                    `<div class="error">Error loading tiers: ${error.message}</div>`;
            }
        }
        
        function displayServiceTiers(tiers) {
            let html = '';
            
            Object.entries(tiers).forEach(([tierKey, tier]) => {
                const ceilings = tier.ceilings;
                html += `
                    <div class="tier-card">
                        <div class="tier-header">
                            <div class="tier-name">${tier.name}</div>
                            <div class="tier-price">$${tier.monthly_cost}/month</div>
                        </div>
                        <div class="tier-limits">
                            <div class="limit-item">
                                <div class="limit-label">Budget</div>
                                <div class="limit-value">$${ceilings.budget}</div>
                            </div>
                            <div class="limit-item">
                                <div class="limit-label">Latency</div>
                                <div class="limit-value">${ceilings.latency}s</div>
                            </div>
                            <div class="limit-item">
                                <div class="limit-label">Rate Limit</div>
                                <div class="limit-value">${ceilings.rate_limit}/hr</div>
                            </div>
                            <div class="limit-item">
                                <div class="limit-label">Success Rate</div>
                                <div class="limit-value">${(ceilings.success_rate * 100).toFixed(1)}%</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('tiersContainer').innerHTML = html;
        }
        
        async function loadPerformanceData() {
            try {
                const response = await fetch('/api/performance');
                const data = await response.json();
                
                if (Array.isArray(data) && data.length > 0) {
                    displayPerformanceChart(data);
                } else {
                    document.getElementById('performanceChart').innerHTML = 
                        '<div class="loading">No performance data available yet</div>';
                }
            } catch (error) {
                document.getElementById('performanceChart').innerHTML = 
                    `<div class="error">Error loading performance data: ${error.message}</div>`;
            }
        }
        
        function displayPerformanceChart(data) {
            // Simple text-based performance display
            let html = '<h3>Recent Performance Adjustments</h3>';
            
            data.slice(-10).forEach(entry => {
                const timestamp = new Date(entry.timestamp).toLocaleString();
                const score = entry.performance_score?.toFixed(2) || 'N/A';
                const adjustments = Object.keys(entry.adjustments || {}).join(', ') || 'None';
                
                html += `
                    <div style="padding: 10px; margin: 5px 0; background: #f7fafc; border-radius: 4px; border-left: 3px solid #667eea;">
                        <strong>${entry.config_id}</strong> - Score: ${score}<br>
                        <small>Time: ${timestamp} | Adjustments: ${adjustments}</small>
                    </div>
                `;
            });
            
            document.getElementById('performanceChart').innerHTML = html;
        }
    </script>
</body>
</html>"""


class CeilingDashboard:
    def __init__(self, base_dir: str = "./archive/EPOCH5", port: int = 8080):
        self.base_dir = base_dir
        self.port = port
        self.ceiling_manager = None
        self.integration = None

        if CEILING_AVAILABLE:
            self.ceiling_manager = CeilingManager(base_dir)
            self.integration = EPOCH5Integration(base_dir)

    def start_server(self):
        """Start the dashboard web server"""

        def handler(*args, **kwargs):
            return CeilingDashboardHandler(
                *args,
                ceiling_manager=self.ceiling_manager,
                integration=self.integration,
                **kwargs,
            )

        httpd = HTTPServer(("localhost", self.port), handler)
        print(f"🌐 EPOCH5 Ceiling Dashboard starting on http://localhost:{self.port}")
        print(f"📊 Real-time ceiling monitoring and analytics available")
        print(f"💰 Service tier revenue optimization dashboard")
        print("Press Ctrl+C to stop the server")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard server stopped")
            httpd.server_close()


def main():
    """CLI interface for ceiling dashboard"""
    import argparse

    parser = argparse.ArgumentParser(description="EPOCH5 Ceiling Dashboard")
    parser.add_argument(
        "--port", type=int, default=8080, help="Port to run the dashboard on"
    )
    parser.add_argument(
        "--base-dir", default="./archive/EPOCH5", help="Base directory for EPOCH5 data"
    )

    args = parser.parse_args()

    if not CEILING_AVAILABLE:
        print("❌ Ceiling management system not available")
        print(
            "   Run 'python3 integration.py setup-demo' first to initialize the system"
        )
        return

    dashboard = CeilingDashboard(args.base_dir, args.port)
    dashboard.start_server()


if __name__ == "__main__":
    main()
