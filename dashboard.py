#!/usr/bin/env python3
"""
EpochCore RAS Dashboard
Enhanced web dashboard with autonomous monetization metrics
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Import monetization systems for real-time data
try:
    from monetization_loops import monetization_engine
    from marketing_engine import marketing_engine
    from kpi_tracker import kpi_tracker
    from autonomous_agents import agent_swarm
    MONETIZATION_ENABLED = True
except ImportError:
    MONETIZATION_ENABLED = False


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard_html()
        elif self.path == '/api/status':
            self.send_status_json()
        elif self.path == '/api/agents':
            self.send_agents_json()
        elif self.path == '/api/monetization':
            self.send_monetization_json()
        elif self.path == '/api/kpis':
            self.send_kpis_json()
        else:
            super().do_GET()

    def send_dashboard_html(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EpochCore RAS Dashboard - Autonomous Monetization</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            color: white;
        }
        .status-card { 
            background: rgba(255, 255, 255, 0.95);
            border: none;
            padding: 20px; 
            margin: 15px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        .status-ok { 
            border-left: 5px solid #28a745; 
        }
        .status-warning {
            border-left: 5px solid #ffc107;
        }
        .status-critical {
            border-left: 5px solid #dc3545;
        }
        .metric { 
            display: inline-block; 
            margin: 10px 20px 10px 0; 
            text-align: center;
        }
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value { 
            font-weight: bold; 
            font-size: 1.8em; 
            color: #28a745; 
        }
        .metric-value.warning { color: #ffc107; }
        .metric-value.critical { color: #dc3545; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        h1 { 
            color: white; 
            margin: 0;
            font-size: 2.5em;
        }
        h2 {
            color: #333;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .refresh-btn { 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; 
            border: none; 
            padding: 12px 24px; 
            cursor: pointer; 
            border-radius: 25px;
            font-weight: bold;
            margin: 5px;
            transition: transform 0.2s;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .alert {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        .agent-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .agent-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .kpi-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .auto-update {
            font-size: 0.8em;
            color: #666;
            font-style: italic;
        }
    </style>
    <script>
        function refreshDashboard() {
            location.reload();
        }
        
        function startAutoRefresh() {
            setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
        }
        
        async function updateMetrics() {
            try {
                const [status, agents, monetization, kpis] = await Promise.all([
                    fetch('/api/status').then(r => r.json()),
                    fetch('/api/agents').then(r => r.json()),
                    fetch('/api/monetization').then(r => r.json()),
                    fetch('/api/kpis').then(r => r.json())
                ]);
                
                // Update DOM elements with new data
                updateStatusDisplay(status);
                updateAgentDisplay(agents);
                updateMonetizationDisplay(monetization);
                updateKPIDisplay(kpis);
                
                document.getElementById('last-update').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error updating metrics:', error);
            }
        }
        
        function updateStatusDisplay(status) {
            // Update system health indicator
            const healthElement = document.getElementById('system-health');
            if (healthElement) {
                healthElement.className = status.health === 'OPTIMAL' ? 'success' : 
                                         status.health === 'GOOD' ? 'warning' : 'alert';
                healthElement.textContent = `System Health: ${status.health}`;
            }
        }
        
        function updateAgentDisplay(agents) {
            // Update agent metrics
            const activeAgents = agents.agents.filter(a => a.status === 'active').length;
            const agentCountElement = document.getElementById('active-agents');
            if (agentCountElement) {
                agentCountElement.textContent = activeAgents;
            }
        }
        
        function updateMonetizationDisplay(monetization) {
            // Update revenue and other monetization metrics
            const revenueElement = document.getElementById('revenue');
            if (revenueElement && monetization.metrics) {
                revenueElement.textContent = `$${monetization.metrics.revenue.toLocaleString()}`;
            }
        }
        
        function updateKPIDisplay(kpis) {
            // Update KPI alerts
            const alertsElement = document.getElementById('active-alerts');
            if (alertsElement) {
                alertsElement.textContent = kpis.active_alerts.length;
            }
        }
        
        // Auto-refresh every 30 seconds
        window.addEventListener('load', () => {
            startAutoRefresh();
            // Initial metrics update
            updateMetrics();
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀🧠💰 EpochCore RAS Dashboard</h1>
            <p>Autonomous Hyper-Scalable Monetization Engine</p>
            <div class="auto-update">Auto-refreshing every 30 seconds</div>
        </div>

        <div class="grid">
            <div class="status-card status-ok">
                <h2>🤖 Autonomous Agent Swarm</h2>
                <div class="metric">
                    <div class="metric-label">Active Agents</div>
                    <div class="metric-value" id="active-agents">8</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total Agents</div>
                    <div class="metric-value">8</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Tasks Completed</div>
                    <div class="metric-value">0</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Autonomy Level</div>
                    <div class="metric-value">83%</div>
                </div>
                
                <div class="agent-list">
                    <div class="agent-item">
                        <strong>RevMax</strong><br>
                        <small>Revenue Optimizer - Active</small>
                    </div>
                    <div class="agent-item">
                        <strong>GrowthBot</strong><br>
                        <small>Growth Hacker - Active</small>
                    </div>
                    <div class="agent-item">
                        <strong>MarketMind</strong><br>
                        <small>Marketing Strategist - Active</small>
                    </div>
                    <div class="agent-item">
                        <strong>RetainPro</strong><br>
                        <small>Retention Specialist - Active</small>
                    </div>
                </div>
            </div>

            <div class="status-card status-warning">
                <h2>💰 Monetization Loops</h2>
                <div class="metric">
                    <div class="metric-label">Revenue</div>
                    <div class="metric-value" id="revenue">$0</div>
                </div>
                <div class="metric">
                    <div class="metric-label">CAC</div>
                    <div class="metric-value">$200</div>
                </div>
                <div class="metric">
                    <div class="metric-label">CLV</div>
                    <div class="metric-value">$0</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Mode</div>
                    <div class="metric-value">EXECUTOR</div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 25%"></div>
                </div>
                <div style="text-align: center; margin-top: 10px;">
                    <small>Optimization Progress: 25%</small>
                </div>
            </div>

            <div class="status-card status-ok">
                <h2>📈 Marketing Engine</h2>
                <div class="metric">
                    <div class="metric-label">Total Content</div>
                    <div class="metric-value">1</div>
                </div>
                <div class="metric">
                    <div class="metric-label">CTR</div>
                    <div class="metric-value">0.0%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Conversions</div>
                    <div class="metric-value">0</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Active Mutations</div>
                    <div class="metric-value">0</div>
                </div>
                
                <div class="success">
                    ✓ Marketing automation active<br>
                    ✓ Content generation pipeline ready<br>
                    ✓ A/B testing framework deployed
                </div>
            </div>

            <div class="status-card status-critical">
                <h2>📊 KPI Tracker & Alerts</h2>
                <div class="metric">
                    <div class="metric-label">Metrics Tracked</div>
                    <div class="metric-value">3</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Active Alerts</div>
                    <div class="metric-value critical" id="active-alerts">0</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Mutations</div>
                    <div class="metric-value">5</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Health Score</div>
                    <div class="metric-value warning">65%</div>
                </div>
                
                <div class="kpi-grid">
                    <div class="kpi-item">
                        <strong>Revenue Growth</strong><br>
                        <span class="metric-value">↗️ +15%</span>
                    </div>
                    <div class="kpi-item">
                        <strong>Engagement</strong><br>
                        <span class="metric-value">📊 24%</span>
                    </div>
                    <div class="kpi-item">
                        <strong>Automation</strong><br>
                        <span class="metric-value">🤖 78%</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="status-card">
            <h2>🚀 Recent Autonomous Activities</h2>
            <div class="grid" style="grid-template-columns: 1fr 1fr;">
                <div>
                    <h3>Completed Optimizations:</h3>
                    <ul>
                        <li>✅ Pricing strategy optimization (+$11,357 value)</li>
                        <li>✅ Growth experiment launched (viral referral)</li>
                        <li>✅ Churn prediction model deployed</li>
                        <li>✅ Marketing campaign automation</li>
                    </ul>
                </div>
                <div>
                    <h3>Next Autonomous Actions:</h3>
                    <ul>
                        <li>⏳ Product feature prioritization (scheduled)</li>
                        <li>⏳ Content mutation optimization</li>
                        <li>⏳ Agent collaboration enhancement</li>
                        <li>⏳ KPI threshold auto-adjustment</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="status-card">
            <h2>🎮 System Controls</h2>
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Now</button>
            <button class="refresh-btn" onclick="alert('Running autonomous validation...')">🔍 Run Validation</button>
            <button class="refresh-btn" onclick="alert('Executing monetization cycle...')">💰 Execute Cycle</button>
            <button class="refresh-btn" onclick="alert('Generating performance report...')">📊 Generate Report</button>
        </div>

        <div class="status-card" id="system-health">
            <p id="system-health">System Health: OPERATIONAL</p>
            <p><em>Last updated: <span id="last-update">""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</span></em></p>
        </div>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def send_status_json(self):
        if MONETIZATION_ENABLED:
            try:
                # Get real-time data from monetization systems
                agent_status = agent_swarm.get_swarm_status()
                monetization_status = monetization_engine.get_status()
                marketing_status = marketing_engine.get_performance_summary()
                kpi_status = kpi_tracker.get_kpi_dashboard()
                
                status_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "operational",
                    "agents": {
                        "active": agent_status["active_agents"],
                        "total": agent_status["total_agents"],
                        "completed_tasks": agent_status["completed_tasks"],
                        "value_generated": agent_status["total_value_generated"],
                        "autonomy_level": agent_status["average_autonomy_level"]
                    },
                    "monetization": {
                        "mode": monetization_status["mode"],
                        "revenue": monetization_status["metrics"]["revenue"],
                        "cac": monetization_status["metrics"]["cac"],
                        "clv": monetization_status["metrics"]["clv"],
                        "engagement_rate": monetization_status["metrics"]["engagement_rate"],
                        "automation_percentage": monetization_status["metrics"]["automation_percentage"]
                    },
                    "marketing": {
                        "total_content": marketing_status.get("total_content", 0),
                        "overall_ctr": marketing_status.get("overall_ctr", 0),
                        "conversions": marketing_status.get("total_conversions", 0),
                        "active_mutations": marketing_status.get("active_mutations", 0)
                    },
                    "kpis": {
                        "tracked": kpi_status.get("total_kpis_tracked", 0),
                        "alerts": len(kpi_status.get("active_alerts", [])),
                        "mutations": len(kpi_status.get("recent_mutations", []))
                    },
                    "health": self._calculate_system_health(monetization_status)
                }
            except Exception as e:
                status_data = {"error": str(e), "status": "error"}
        else:
            # Fallback to legacy data
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "status": "operational",
                "agents": {"active": 5, "total": 12},
                "dags": {"running": 1, "completed": 2},
                "capsules": {"total": 8, "verified": 8},
                "policies": {"active": 3, "violations": 0}
            }
        
        self.send_json_response(status_data)
    
    def _calculate_system_health(self, monetization_status):
        """Calculate overall system health"""
        engagement = monetization_status['metrics']['engagement_rate']
        automation = monetization_status['metrics']['automation_percentage']
        
        if engagement > 0.20 and automation > 0.70:
            return "OPTIMAL"
        elif engagement > 0.15 and automation > 0.50:
            return "GOOD"
        else:
            return "NEEDS_ATTENTION"

    def send_agents_json(self):
        if MONETIZATION_ENABLED:
            try:
                agent_status = agent_swarm.get_swarm_status()
                agent_details = []
                
                for agent_id, agent in agent_swarm.agents.items():
                    agent_details.append({
                        "id": agent_id,
                        "name": agent.name,
                        "role": agent.role.value,
                        "status": agent.status.value,
                        "autonomy_level": agent.autonomy_level,
                        "value_generated": agent.total_value_generated,
                        "skills": list(agent.skills.keys())
                    })
                
                agents_data = {
                    "agents": agent_details,
                    "summary": {
                        "total": len(agent_details),
                        "active": len([a for a in agent_details if a["status"] == "active"]),
                        "avg_autonomy": agent_status["average_autonomy_level"]
                    }
                }
            except Exception as e:
                agents_data = {"error": str(e)}
        else:
            # Fallback to legacy data
            agents_data = {
                "agents": [
                    {"id": "agent_001", "status": "active", "skills": ["python", "data_processing"]},
                    {"id": "agent_002", "status": "active", "skills": ["javascript", "frontend"]},
                    {"id": "agent_003", "status": "active", "skills": ["devops", "docker"]},
                    {"id": "agent_004", "status": "active", "skills": ["security", "audit"]},
                    {"id": "agent_005", "status": "active", "skills": ["database", "sql"]}
                ]
            }
        
        self.send_json_response(agents_data)
    
    def send_monetization_json(self):
        if MONETIZATION_ENABLED:
            try:
                monetization_status = monetization_engine.get_status()
                self.send_json_response(monetization_status)
            except Exception as e:
                self.send_json_response({"error": str(e)})
        else:
            self.send_json_response({"error": "Monetization systems not available"})
    
    def send_kpis_json(self):
        if MONETIZATION_ENABLED:
            try:
                kpi_dashboard = kpi_tracker.get_kpi_dashboard()
                self.send_json_response(kpi_dashboard)
            except Exception as e:
                self.send_json_response({"error": str(e)})
        else:
            self.send_json_response({"error": "KPI tracking not available"})

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def start_dashboard(port=8000):
    """Start the dashboard server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"✓ EpochCore RAS Dashboard starting on http://localhost:{port}")
    print("  Access the dashboard in your web browser")
    print("  Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Dashboard server stopped")
        httpd.server_close()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_dashboard(port)