#!/usr/bin/env python3
"""
EpochCore RAS Dashboard
Enhanced web dashboard for monitoring the system including recursive improvements
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Import recursive improvement status
try:
    from integration import _orchestrator, initialize_recursive_improvement_system
    RECURSIVE_AVAILABLE = True
except ImportError:
    RECURSIVE_AVAILABLE = False


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard_html()
        elif self.path == '/api/status':
            self.send_status_json()
        elif self.path == '/api/agents':
            self.send_agents_json()
        elif self.path == '/api/recursive':
            self.send_recursive_json()
        elif self.path == '/api/recursive/trigger':
            self.trigger_recursive_improvement()
        else:
            super().do_GET()
            self.send_dashboard_html()
        elif self.path == '/api/status':
            self.send_status_json()
        elif self.path == '/api/agents':
            self.send_agents_json()
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
        <h3>Recent Activity</h3>
        <ul>
            <li>✓ Agent workflow completed successfully</li>
            <li>✓ System validation passed</li>
            <li>✓ Demo environment initialized</li>
            <li>→ Monitoring system health</li>
        </ul>
    </div>

    <div class="status-card">
        <h3>Quick Actions</h3>
        <button class="refresh-btn" onclick="location.reload()">Refresh Status</button>
        <button class="refresh-btn" onclick="alert('Feature not implemented in demo')">Run Validation</button>
        <button class="refresh-btn" onclick="alert('Feature not implemented in demo')">Create Capsule</button>
    </div>

    <p><em>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</em></p>
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