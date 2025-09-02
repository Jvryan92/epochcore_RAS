#!/usr/bin/env python3
"""
EpochCore RAS Dashboard
Simple web dashboard for monitoring the system
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard_html()
        elif self.path == '/api/status':
            self.send_status_json()
        elif self.path == '/api/agents':
            self.send_agents_json()
        elif self.path == '/api/improvement':
            self.send_improvement_json()
        else:
            super().do_GET()

    def send_dashboard_html(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EpochCore RAS Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status-card { border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 5px; }
        .status-ok { border-color: #28a745; background-color: #d4edda; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-weight: bold; font-size: 1.2em; color: #28a745; }
        h1 { color: #343a40; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 8px 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🤖 EpochCore RAS Dashboard</h1>
    
    <div class="status-card status-ok">
        <h3>System Status: OPERATIONAL</h3>
        <div class="metric">
            <div>Active Agents</div>
            <div class="metric-value">5</div>
        </div>
        <div class="metric">
            <div>Total Agents</div>
            <div class="metric-value">12</div>
        </div>
        <div class="metric">
            <div>Running DAGs</div>
            <div class="metric-value">1</div>
        </div>
        <div class="metric">
            <div>Completed DAGs</div>
            <div class="metric-value">2</div>
        </div>
        <div class="metric">
            <div>Total Capsules</div>
            <div class="metric-value">8</div>
        </div>
    </div>

    <div class="status-card">
        <h3>Recursive Improvement Status</h3>
        <div id="improvement-status">Loading improvement status...</div>
        <div class="metric">
            <div>Total Improvements</div>
            <div class="metric-value" id="total-improvements">-</div>
        </div>
        <div class="metric">
            <div>Recent Improvements (24h)</div>
            <div class="metric-value" id="recent-improvements">-</div>
        </div>
        <div class="metric">
            <div>Registered Subsystems</div>
            <div class="metric-value" id="subsystem-count">-</div>
        </div>
    </div>

    <div class="status-card">
        <h3>Recent Activity</h3>
        <ul>
            <li>✓ Agent workflow completed successfully</li>
            <li>✓ System validation passed</li>
            <li>✓ Demo environment initialized</li>
            <li>→ Monitoring system health</li>
            <li id="recent-improvement-activity">→ Loading improvement activity...</li>
        </ul>
    </div>

    <div class="status-card">
        <h3>Quick Actions</h3>
        <button class="refresh-btn" onclick="location.reload()">Refresh Status</button>
        <button class="refresh-btn" onclick="alert('Feature not implemented in demo')">Run Validation</button>
        <button class="refresh-btn" onclick="alert('Feature not implemented in demo')">Create Capsule</button>
    </div>

    <p><em>Last updated: <span id="status-timestamp">""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</span></em></p>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status-timestamp').innerText = new Date(data.timestamp).toLocaleString();
                })
                .catch(error => console.error('Error fetching status:', error));
        }

        function updateImprovement() {
            fetch('/api/improvement')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'not_initialized') {
                        document.getElementById('improvement-status').innerText = 'Not Initialized';
                        document.getElementById('total-improvements').innerText = 'N/A';
                        document.getElementById('recent-improvements').innerText = 'N/A';
                        document.getElementById('subsystem-count').innerText = 'N/A';
                        document.getElementById('recent-improvement-activity').innerText = '→ Run setup-demo to initialize';
                    } else if (data.error) {
                        document.getElementById('improvement-status').innerText = 'Error: ' + data.error;
                    } else {
                        const autonomousStatus = data.autonomous_mode ? 'Autonomous Mode: ON' : 'Manual Mode';
                        document.getElementById('improvement-status').innerText = autonomousStatus;
                        document.getElementById('total-improvements').innerText = data.total_improvements || 0;
                        document.getElementById('recent-improvements').innerText = data.recent_improvements || 0;
                        document.getElementById('subsystem-count').innerText = data.registered_subsystems || 0;
                        
                        // Show recent activity
                        if (data.recent_activity && data.recent_activity.length > 0) {
                            const activity = data.recent_activity[data.recent_activity.length - 1];
                            const statusIcon = activity.success ? '✓' : '✗';
                            document.getElementById('recent-improvement-activity').innerText = 
                                `${statusIcon} ${activity.subsystem} ${activity.type} improvement`;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching improvement status:', error);
                    document.getElementById('improvement-status').innerText = 'Status unavailable';
                });
        }

        // Update status every 5 seconds
        updateStatus();
        updateImprovement();
        setInterval(() => {
            updateStatus();
            updateImprovement();
        }, 5000);
    </script>
</body>
</html>
"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def send_status_json(self):
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "operational",
            "agents": {"active": 5, "total": 12},
            "dags": {"running": 1, "completed": 2},
            "capsules": {"total": 8, "verified": 8},
            "policies": {"active": 3, "violations": 0}
        }
        self.send_json_response(status_data)

    def send_agents_json(self):
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

    def send_improvement_json(self):
        """Send recursive improvement status as JSON"""
        try:
            from recursive_improvement import get_framework
            framework = get_framework()
            
            if framework.subsystem_hooks:
                status = framework.get_status()
                metrics = framework.get_metrics()
                
                improvement_data = {
                    "autonomous_mode": status["autonomous_mode"],
                    "registered_subsystems": len(status["registered_subsystems"]),
                    "recent_improvements": len(status["recent_improvements"]),
                    "total_improvements": status["total_improvements"],
                    "subsystems": {},
                    "recent_activity": []
                }
                
                # Subsystem details
                for name, info in status["registered_subsystems"].items():
                    improvement_data["subsystems"][name] = {
                        "enabled": info["enabled"],
                        "last_improvement": info["last_improvement"],
                        "strategies": info["strategies"]
                    }
                
                # Recent improvements
                recent = metrics.get_recent_improvements(6)  # Last 6 hours
                for improvement in recent[-5:]:  # Last 5 improvements
                    improvement_data["recent_activity"].append({
                        "timestamp": improvement["timestamp"],
                        "subsystem": improvement["subsystem"],
                        "type": improvement["improvement_type"],
                        "success": improvement["success"]
                    })
                    
            else:
                improvement_data = {
                    "status": "not_initialized",
                    "message": "Recursive improvement framework not initialized"
                }
                
        except Exception as e:
            improvement_data = {
                "status": "error",
                "error": str(e)
            }
            
        self.send_json_response(improvement_data)

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