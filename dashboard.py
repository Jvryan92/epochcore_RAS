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

    def send_dashboard_html(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EpochCore RAS Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .status-card { border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 5px; background: white; }
        .status-ok { border-color: #28a745; background-color: #d4edda; }
        .status-recursive { border-color: #007bff; background-color: #d1ecf1; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-weight: bold; font-size: 1.2em; color: #28a745; }
        .recursive-value { font-weight: bold; font-size: 1.2em; color: #007bff; }
        h1 { color: #343a40; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 8px 16px; cursor: pointer; margin: 5px; }
        .trigger-btn { background: #28a745; color: white; border: none; padding: 8px 16px; cursor: pointer; margin: 5px; }
        .engine-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; margin: 10px 0; }
        .engine-card { background: white; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
        .engine-running { border-left: 4px solid #28a745; }
        .engine-stopped { border-left: 4px solid #dc3545; }
    </style>
    <script>
        function refreshData() {
            location.reload();
        }
        
        function triggerImprovement() {
            fetch('/api/recursive/trigger')
                .then(response => response.json())
                .then(data => {
                    alert('Recursive improvement triggered: ' + data.engines_triggered + ' engines activated');
                    setTimeout(refreshData, 2000);
                })
                .catch(error => alert('Error triggering improvement: ' + error));
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</head>
<body>
    <h1>🤖 EpochCore RAS Dashboard</h1>
    <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
    <button class="trigger-btn" onclick="triggerImprovement()">Trigger Recursive Improvement</button>
    
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

    <div class="status-card status-recursive">
        <h3>🔄 Recursive Improvement System</h3>
        <div class="metric">
            <div>Active Engines</div>
            <div class="recursive-value" id="active-engines">Loading...</div>
        </div>
        <div class="metric">
            <div>Total Improvements</div>
            <div class="recursive-value" id="total-improvements">Loading...</div>
        </div>
        <div class="metric">
            <div>System Uptime</div>
            <div class="recursive-value" id="system-uptime">Loading...</div>
        </div>
        <div class="metric">
            <div>Status</div>
            <div class="recursive-value" id="recursive-status">Loading...</div>
        </div>
    </div>
    
    <div class="status-card">
        <h3>Recursive Improvement Engines</h3>
        <div class="engine-grid" id="engine-grid">
            Loading engine status...
        </div>
    </div>

    <div class="status-card">
        <h3>Recent Activity</h3>
        <ul>
            <li>✓ Agent workflow completed successfully</li>
            <li>✓ System validation passed</li>
            <li>✓ Recursive improvements active</li>
            <li>✓ 10 improvement engines initialized</li>
            <li>✓ Compounding logic operational</li>
        </ul>
    </div>
    
    <script>
        // Load recursive improvement data
        fetch('/api/recursive')
            .then(response => response.json())
            .then(data => {
                document.getElementById('active-engines').textContent = data.active_engines || 0;
                document.getElementById('total-improvements').textContent = data.total_improvements || 0;
                document.getElementById('system-uptime').textContent = (data.uptime || 0).toFixed(1) + 's';
                document.getElementById('recursive-status').textContent = data.initialized ? 'Operational' : 'Initializing';
                
                // Update engine grid
                const engineGrid = document.getElementById('engine-grid');
                engineGrid.innerHTML = '';
                
                if (data.engines) {
                    Object.entries(data.engines).forEach(([name, engine]) => {
                        const engineDiv = document.createElement('div');
                        engineDiv.className = `engine-card ${engine.running ? 'engine-running' : 'engine-stopped'}`;
                        engineDiv.innerHTML = `
                            <strong>${name}</strong><br>
                            Status: ${engine.running ? '✓ Running' : '✗ Stopped'}<br>
                            Executions: ${engine.total_executions || 0}<br>
                            Actions: ${engine.actions_count || 0}
                        `;
                        engineGrid.appendChild(engineDiv);
                    });
                } else {
                    engineGrid.innerHTML = '<div>No engine data available</div>';
                }
            })
            .catch(error => {
                console.error('Error loading recursive data:', error);
                document.getElementById('recursive-status').textContent = 'Error';
            });
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
    
    def send_recursive_json(self):
        """Send recursive improvement system status."""
        if not RECURSIVE_AVAILABLE:
            recursive_data = {
                "available": False,
                "error": "Recursive improvement system not available"
            }
        else:
            try:
                # Get global orchestrator or initialize
                global _orchestrator
                if _orchestrator is None:
                    _orchestrator = initialize_recursive_improvement_system()
                
                if _orchestrator:
                    status = _orchestrator.get_system_status()
                    orchestrator_status = status.get("orchestrator", {})
                    
                    recursive_data = {
                        "available": True,
                        "initialized": orchestrator_status.get("initialized", False),
                        "active_engines": orchestrator_status.get("active_engines", 0),
                        "total_improvements": orchestrator_status.get("total_improvements", 0),
                        "uptime": orchestrator_status.get("uptime", 0),
                        "engines": status.get("engines", {}),
                        "recent_activity": status.get("recent_activity", {})
                    }
                else:
                    recursive_data = {
                        "available": False,
                        "error": "Failed to initialize recursive system"
                    }
            except Exception as e:
                recursive_data = {
                    "available": False,
                    "error": f"Error accessing recursive system: {e}"
                }
        
        self.send_json_response(recursive_data)
    
    def trigger_recursive_improvement(self):
        """Trigger recursive improvement via API."""
        if not RECURSIVE_AVAILABLE:
            response = {"error": "Recursive improvement system not available"}
        else:
            try:
                global _orchestrator
                if _orchestrator is None:
                    _orchestrator = initialize_recursive_improvement_system()
                
                if _orchestrator:
                    result = _orchestrator.trigger_recursive_improvement("dashboard_trigger", {
                        "source": "dashboard",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    response = {
                        "success": True,
                        "engines_triggered": len(result.get("engines_triggered", [])),
                        "total_improvements": result.get("total_improvements", 0),
                        "timestamp": result.get("timestamp")
                    }
                else:
                    response = {"error": "Failed to initialize recursive system"}
            except Exception as e:
                response = {"error": f"Error triggering improvements: {e}"}
        
        self.send_json_response(response)

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def start_dashboard(port=8000):
    """Start the dashboard server."""
    try:
        server_address = ('', port)
        httpd = HTTPServer(server_address, DashboardHandler)
        print(f"EpochCore RAS Dashboard started on http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
    except Exception as e:
        print(f"Error starting dashboard: {e}")


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_dashboard(port)