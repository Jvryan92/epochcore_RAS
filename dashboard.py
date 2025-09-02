#!/usr/bin/env python3
"""
EpochCore RAS Dashboard
Simple web dashboard for monitoring the system with meta-learning capabilities
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Meta-learning imports
try:
    from meta_learning_engine import get_meta_status
    from meta_optimizer import get_meta_optimizer_status
    from automl_zero import get_automl_zero_status
    from experiment_manager import get_experiment_manager_status
    from feature_adaptor import get_feature_adaptor_status
    META_LEARNING_AVAILABLE = True
except ImportError:
    META_LEARNING_AVAILABLE = False


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard_html()
        elif self.path == '/api/status':
            self.send_status_json()
        elif self.path == '/api/agents':
            self.send_agents_json()
        elif self.path == '/api/meta-learning':
            self.send_meta_learning_json()
        elif self.path == '/api/experiments':
            self.send_experiments_json()
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
        .status-meta { border-color: #007bff; background-color: #cce7ff; }
        .status-warning { border-color: #ffc107; background-color: #fff3cd; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-weight: bold; font-size: 1.2em; color: #28a745; }
        .metric-value-meta { font-weight: bold; font-size: 1.2em; color: #007bff; }
        h1 { color: #343a40; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 8px 16px; cursor: pointer; margin: 2px; }
        .meta-btn { background: #17a2b8; color: white; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .experiment-log { max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; background: #f8f9fa; padding: 10px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🤖 EpochCore RAS Dashboard</h1>
    
    <div class="grid">
        <div>
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
        </div>
        
        <div id="meta-learning-status">
            <!-- Meta-learning status will be loaded here -->
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
        
        <div id="experiment-log" class="experiment-log">
            <!-- Experiment logs will be loaded here -->
        </div>
    </div>

    <div class="status-card">
        <h3>Quick Actions</h3>
        <button class="refresh-btn" onclick="location.reload()">Refresh Status</button>
        <button class="refresh-btn" onclick="runValidation()">Run Validation</button>
        <button class="refresh-btn meta-btn" onclick="runMetaExperiment()">Run Meta-Learning</button>
        <button class="refresh-btn meta-btn" onclick="runAutoMLExperiment()">Run AutoML-Zero</button>
        <button class="refresh-btn meta-btn" onclick="runFeatureAdaptation()">Feature Adaptation</button>
    </div>

    <script>
        async function loadMetaLearningStatus() {
            try {
                const response = await fetch('/api/meta-learning');
                const data = await response.json();
                
                const statusHtml = `
                    <div class="status-card status-meta">
                        <h3>Meta-Learning Status: ${data.status ? 'ACTIVE' : 'INACTIVE'}</h3>
                        <div class="metric">
                            <div>MAML Tasks</div>
                            <div class="metric-value-meta">${data.meta_learning?.registered_tasks || 0}</div>
                        </div>
                        <div class="metric">
                            <div>Model Parameters</div>
                            <div class="metric-value-meta">${data.meta_learning?.maml_model_parameters || 0}</div>
                        </div>
                        <div class="metric">
                            <div>Active Experiments</div>
                            <div class="metric-value-meta">${data.experiments?.running_experiments || 0}</div>
                        </div>
                        <div class="metric">
                            <div>AutoML Population</div>
                            <div class="metric-value-meta">${data.automl_zero?.current_population_count || 0}</div>
                        </div>
                        <div class="metric">
                            <div>Feature Adaptations</div>
                            <div class="metric-value-meta">${data.feature_adaptor?.active_transformations || 0}</div>
                        </div>
                        <div class="metric">
                            <div>Improvements Applied</div>
                            <div class="metric-value-meta">${data.meta_optimizer?.recursive_improvement?.improvement_history_length || 0}</div>
                        </div>
                    </div>
                `;
                
                document.getElementById('meta-learning-status').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('meta-learning-status').innerHTML = `
                    <div class="status-card status-warning">
                        <h3>Meta-Learning Status: UNAVAILABLE</h3>
                        <p>Meta-learning components not accessible</p>
                    </div>
                `;
            }
        }

        async function loadExperimentLog() {
            try {
                const response = await fetch('/api/experiments');
                const data = await response.json();
                
                let logHtml = '<h4>Recent Experiments:</h4>';
                if (data.experiments && data.experiments.length > 0) {
                    data.experiments.slice(0, 5).forEach(exp => {
                        const status = exp.status.toUpperCase();
                        const type = exp.experiment_type;
                        const time = new Date(exp.start_time).toLocaleTimeString();
                        logHtml += `<div>[${time}] ${type}: ${status}</div>`;
                    });
                } else {
                    logHtml += '<div>No recent experiments</div>';
                }
                
                document.getElementById('experiment-log').innerHTML = logHtml;
            } catch (error) {
                document.getElementById('experiment-log').innerHTML = '<div>Failed to load experiment log</div>';
            }
        }

        function runValidation() {
            alert('System validation would be triggered here');
        }

        function runMetaExperiment() {
            alert('Meta-learning experiment would be triggered here');
        }

        function runAutoMLExperiment() {
            alert('AutoML-Zero experiment would be triggered here');
        }

        function runFeatureAdaptation() {
            alert('Feature adaptation would be triggered here');
        }

        // Load dynamic content
        loadMetaLearningStatus();
        loadExperimentLog();
        
        // Refresh every 30 seconds
        setInterval(() => {
            loadMetaLearningStatus();
            loadExperimentLog();
        }, 30000);
    </script>

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

    def send_meta_learning_json(self):
        """Send meta-learning status as JSON"""
        if not META_LEARNING_AVAILABLE:
            meta_data = {
                "status": False,
                "message": "Meta-learning components not available"
            }
        else:
            try:
                meta_data = {
                    "status": True,
                    "meta_learning": get_meta_status(),
                    "meta_optimizer": get_meta_optimizer_status(),
                    "automl_zero": get_automl_zero_status(),
                    "experiments": get_experiment_manager_status(),
                    "feature_adaptor": get_feature_adaptor_status(),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                meta_data = {
                    "status": False,
                    "error": str(e),
                    "message": "Error retrieving meta-learning status"
                }
        
        self.send_json_response(meta_data)
    
    def send_experiments_json(self):
        """Send recent experiments as JSON"""
        if not META_LEARNING_AVAILABLE:
            exp_data = {"experiments": [], "message": "Meta-learning not available"}
        else:
            try:
                from experiment_manager import experiment_manager
                experiments = experiment_manager.get_all_experiments()
                exp_data = {
                    "experiments": [
                        {
                            "experiment_id": exp.experiment_id,
                            "experiment_type": exp.experiment_type.value,
                            "status": exp.status.value,
                            "start_time": exp.start_time.isoformat(),
                            "end_time": exp.end_time.isoformat() if exp.end_time else None,
                            "duration_seconds": exp.duration_seconds,
                            "metrics": exp.metrics
                        } for exp in experiments[:20]  # Last 20 experiments
                    ],
                    "total_experiments": len(experiments)
                }
            except Exception as e:
                exp_data = {"experiments": [], "error": str(e)}
        
        self.send_json_response(exp_data)

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