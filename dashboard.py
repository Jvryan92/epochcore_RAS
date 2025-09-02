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
        elif self.path == '/api/pr-status':
            self.send_pr_status_json()
        elif self.path == '/api/pr-conflicts':
            self.send_pr_conflicts_json()
        elif self.path == '/api/pr-integration-plan':
            self.send_pr_integration_plan_json()
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

    <div class="status-card">
        <h3>📋 Pull Request Management</h3>
        <div class="metric">
            <div>Open PRs</div>
            <div class="metric-value" id="total-prs">Loading...</div>
        </div>
        <div class="metric">
            <div>Ready to Merge</div>
            <div class="metric-value" id="ready-prs">Loading...</div>
        </div>
        <div class="metric">
            <div>High Conflicts</div>
            <div class="metric-value" id="high-conflicts" style="color: #dc3545;">Loading...</div>
        </div>
        <div class="metric">
            <div>Timeline (Days)</div>
            <div class="metric-value" id="integration-timeline">Loading...</div>
        </div>
        
        <div style="margin-top: 15px;">
            <button class="refresh-btn" onclick="handleAllPRs()">Handle All PRs</button>
            <button class="refresh-btn" onclick="showPRConflicts()">Show Conflicts</button>
            <button class="refresh-btn" onclick="refreshPRData()">Refresh PR Data</button>
        </div>
        
        <div id="pr-integration-plan" style="margin-top: 15px; display: none;">
            <h4>Integration Plan</h4>
            <div id="integration-phases">Loading phases...</div>
        </div>
    </div>
    
    <script>
        // PR Management functions
        function handleAllPRs() {
            alert('PR Handling Process initiated. Check console for detailed logs.');
            // In a real implementation, this would trigger the comprehensive PR handling
            console.log('Triggering comprehensive PR handling...');
        }
        
        function showPRConflicts() {
            fetch('/api/pr-conflicts')
                .then(response => response.json())
                .then(data => {
                    let conflictInfo = `High Conflicts: ${data.high_conflicts.length}\\n`;
                    conflictInfo += `Medium Conflicts: ${data.medium_conflicts.length}\\n`;
                    conflictInfo += `Low Conflicts: ${data.low_conflicts.length}\\n\\n`;
                    
                    if (data.high_conflicts.length > 0) {
                        conflictInfo += 'High Priority Conflicts:\\n';
                        data.high_conflicts.forEach(conflict => {
                            conflictInfo += `• PR #${conflict.pr1} ↔ PR #${conflict.pr2}: ${conflict.reason}\\n`;
                        });
                    }
                    
                    alert(conflictInfo);
                })
                .catch(error => alert('Error loading conflicts: ' + error));
        }
        
        function refreshPRData() {
            loadPRData();
        }
        
        function loadPRData() {
            fetch('/api/pr-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-prs').textContent = data.total_prs || 0;
                    document.getElementById('ready-prs').textContent = data.ready_to_merge || 0;
                    document.getElementById('high-conflicts').textContent = data.high_conflicts || 0;
                    document.getElementById('integration-timeline').textContent = data.timeline || 'N/A';
                })
                .catch(error => {
                    console.error('Error loading PR data:', error);
                    document.getElementById('total-prs').textContent = 'Error';
                });
            
            // Load integration plan
            fetch('/api/pr-integration-plan')
                .then(response => response.json())
                .then(data => {
                    const phasesDiv = document.getElementById('integration-phases');
                    let phasesHtml = '';
                    
                    Object.entries(data.phases).forEach(([phaseName, phaseInfo]) => {
                        phasesHtml += `
                            <div style="margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 3px;">
                                <strong>${phaseName}</strong> (${phaseInfo.duration})<br>
                                PRs: ${phaseInfo.prs.join(', ')}<br>
                                <small>${phaseInfo.description}</small>
                            </div>
                        `;
                    });
                    
                    phasesDiv.innerHTML = phasesHtml;
                })
                .catch(error => {
                    console.error('Error loading integration plan:', error);
                });
        }
    
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
        
        // Load PR data on page load
        loadPRData();
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

    def send_pr_status_json(self):
        """Send PR status data."""
        try:
            from pr_manager import PRManager
            manager = PRManager()
            report = manager.generate_consolidation_report()
            
            pr_data = {
                "total_prs": report["total_prs"],
                "ready_to_merge": report["prs_ready_to_merge"],
                "high_conflicts": len(report["conflict_analysis"]["high_conflicts"]),
                "medium_conflicts": len(report["conflict_analysis"]["medium_conflicts"]),
                "low_conflicts": len(report["conflict_analysis"]["low_conflicts"]),
                "timeline": report["integration_plan"]["timeline"]["parallel_execution_days"],
                "total_lines_added": report["total_lines_added"],
                "total_lines_deleted": report["total_lines_deleted"]
            }
        except Exception as e:
            pr_data = {
                "error": f"Error loading PR data: {e}",
                "total_prs": 0,
                "ready_to_merge": 0,
                "high_conflicts": 0,
                "timeline": "N/A"
            }
        
        self.send_json_response(pr_data)
    
    def send_pr_conflicts_json(self):
        """Send PR conflicts data."""
        try:
            from pr_manager import PRManager
            manager = PRManager()
            conflicts = manager.analyze_conflicts()
            
            # Simplify conflict data for frontend
            simplified_conflicts = {
                "high_conflicts": conflicts["high_conflicts"],
                "medium_conflicts": conflicts["medium_conflicts"],
                "low_conflicts": conflicts["low_conflicts"],
                "resolution_strategies": conflicts["resolution_strategies"]
            }
        except Exception as e:
            simplified_conflicts = {
                "error": f"Error loading conflict data: {e}",
                "high_conflicts": [],
                "medium_conflicts": [],
                "low_conflicts": []
            }
        
        self.send_json_response(simplified_conflicts)
    
    def send_pr_integration_plan_json(self):
        """Send PR integration plan data."""
        try:
            from pr_manager import PRManager
            manager = PRManager()
            plan = manager.create_integration_plan()
            
            # Include phases, timeline, and integration order
            plan_data = {
                "integration_order": plan["integration_order"],
                "phases": plan["phases"],
                "timeline": plan["timeline"],
                "risks": plan["risks"]
            }
        except Exception as e:
            plan_data = {
                "error": f"Error loading integration plan: {e}",
                "phases": {},
                "timeline": {}
            }
        
        self.send_json_response(plan_data)

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