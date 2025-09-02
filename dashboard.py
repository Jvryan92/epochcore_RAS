#!/usr/bin/env python3
"""
EpochCore RAS Dashboard
Simple web dashboard for monitoring the system
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Import monetization pipeline for metrics
try:
    from monetization_pipeline import create_monetization_workflow
    MONETIZATION_AVAILABLE = True
except ImportError:
    MONETIZATION_AVAILABLE = False


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
        else:
            super().do_GET()

    def send_dashboard_html(self):
        # Get monetization metrics if available
        monetization_section = ""
        if MONETIZATION_AVAILABLE:
            try:
                pipeline = create_monetization_workflow()
                metrics = pipeline.get_pipeline_metrics()
                monetization_section = f"""
    <div class="status-card monetization-card">
        <h3>💰 Monetization Pipeline</h3>
        <div class="metric">
            <div>Monthly Revenue</div>
            <div class="metric-value">${metrics['total_monetary_value']:,.2f}</div>
        </div>
        <div class="metric">
            <div>Compounding Factor</div>
            <div class="metric-value">{metrics['compounding_factor']:.3f}x</div>
        </div>
        <div class="metric">
            <div>Steps Completed</div>
            <div class="metric-value">{metrics['steps_completed']}/10</div>
        </div>
        <div class="metric">
            <div>Automation Level</div>
            <div class="metric-value">{metrics['automation_level']:.1%}</div>
        </div>
        <div class="metric">
            <div>ROI</div>
            <div class="metric-value">{metrics['roi_percentage']:.1f}%</div>
        </div>
    </div>"""
            except:
                monetization_section = """
    <div class="status-card">
        <h3>💰 Monetization Pipeline</h3>
        <p>Pipeline not initialized. Run <code>python integration.py monetize</code> to activate.</p>
    </div>"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EpochCore RAS Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .status-card {{ border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 5px; }}
        .status-ok {{ border-color: #28a745; background-color: #d4edda; }}
        .monetization-card {{ border-color: #ffc107; background-color: #fff3cd; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-weight: bold; font-size: 1.2em; color: #28a745; }}
        h1 {{ color: #343a40; }}
        .refresh-btn {{ background: #007bff; color: white; border: none; padding: 8px 16px; cursor: pointer; margin: 5px; }}
        .monetize-btn {{ background: #ffc107; color: #212529; border: none; padding: 8px 16px; cursor: pointer; margin: 5px; }}
        code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
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

{monetization_section}

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
        <button class="monetize-btn" onclick="alert('Run: python integration.py monetize')">Execute Monetization Pipeline</button>
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

    def send_monetization_json(self):
        if MONETIZATION_AVAILABLE:
            try:
                pipeline = create_monetization_workflow()
                metrics = pipeline.get_pipeline_metrics()
                self.send_json_response(metrics)
            except Exception as e:
                error_data = {
                    "error": "Monetization pipeline not available",
                    "message": str(e),
                    "status": "inactive"
                }
                self.send_json_response(error_data)
        else:
            error_data = {
                "error": "Monetization module not imported",
                "status": "unavailable"
            }
            self.send_json_response(error_data)

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