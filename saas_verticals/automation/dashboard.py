"""
Real-time dashboard showing automated demonstrations across all verticals
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .launch_orchestrator import AutomatedLaunchOrchestrator

app = FastAPI(
    title="EpochCore RAS Automation Demo",
    description="Real-time demonstration of automated security and verification",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
orchestrator = AutomatedLaunchOrchestrator()
active_websockets: Set[WebSocket] = set()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EpochCore RAS - Live Automation Demo</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-900">EpochCore RAS</h1>
                <p class="mt-2 text-lg text-gray-600">Live Automation Demonstration</p>
            </div>
            
            <!-- Metrics Overview -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Active Verticals</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="active-verticals">0</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Total Events</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="total-events">0</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Avg Response Time</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="avg-response">0ms</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">System Health</h3>
                    <p class="text-3xl font-bold text-green-600" id="system-health">100%</p>
                </div>
            </div>
            
            <!-- Live Activity Feed -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-white rounded-lg shadow">
                    <div class="p-6">
                        <h2 class="text-lg font-medium text-gray-900">Live Activity</h2>
                        <div class="mt-4 h-96 overflow-y-auto" id="activity-feed"></div>
                    </div>
                </div>
                
                <!-- Metrics Chart -->
                <div class="bg-white rounded-lg shadow">
                    <div class="p-6">
                        <h2 class="text-lg font-medium text-gray-900">Performance Metrics</h2>
                        <canvas id="metrics-chart" class="mt-4"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Vertical Status Grid -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="vertical-grid">
            </div>
        </div>

        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            let metricsChart;
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            function updateDashboard(data) {
                // Update overview metrics
                document.getElementById('active-verticals').textContent = data.active_verticals;
                document.getElementById('total-events').textContent = data.total_events;
                document.getElementById('avg-response').textContent = `${data.avg_response_time}ms`;
                document.getElementById('system-health').textContent = `${data.system_health}%`;
                
                // Update activity feed
                const feed = document.getElementById('activity-feed');
                const entry = document.createElement('div');
                entry.className = 'py-2 border-b border-gray-200';
                entry.innerHTML = `
                    <p class="text-sm text-gray-600">${data.latest_event.timestamp}</p>
                    <p class="font-medium">${data.latest_event.message}</p>
                `;
                feed.insertBefore(entry, feed.firstChild);
                
                // Update metrics chart
                updateChart(data.metrics);
                
                // Update vertical grid
                updateVerticalGrid(data.verticals);
            }
            
            function updateChart(metrics) {
                if (!metricsChart) {
                    const ctx = document.getElementById('metrics-chart').getContext('2d');
                    metricsChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Events/sec',
                                data: [],
                                borderColor: 'rgb(99, 102, 241)',
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
                
                metricsChart.data.labels.push(new Date().toLocaleTimeString());
                metricsChart.data.datasets[0].data.push(metrics.events_per_second);
                
                if (metricsChart.data.labels.length > 20) {
                    metricsChart.data.labels.shift();
                    metricsChart.data.datasets[0].data.shift();
                }
                
                metricsChart.update();
            }
            
            function updateVerticalGrid(verticals) {
                const grid = document.getElementById('vertical-grid');
                grid.innerHTML = '';
                
                for (const [name, data] of Object.entries(verticals)) {
                    const card = document.createElement('div');
                    card.className = 'bg-white rounded-lg shadow p-6';
                    card.innerHTML = `
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">${name}</h3>
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${
                                data.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }">${data.status}</span>
                        </div>
                        <dl class="mt-4 grid grid-cols-2 gap-4">
                            <div>
                                <dt class="text-sm text-gray-500">Events</dt>
                                <dd class="text-lg font-medium text-gray-900">${data.events}</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Latency</dt>
                                <dd class="text-lg font-medium text-gray-900">${data.latency}ms</dd>
                            </div>
                        </dl>
                    `;
                    grid.appendChild(card);
                }
            }
        </script>
    </body>
    </html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_websockets.add(websocket)

    try:
        while True:
            # Collect metrics from orchestrator
            metrics = {}
            for vertical in orchestrator.verticals:
                metrics[vertical] = orchestrator.get_metrics(vertical)

            # Create update message
            message = {
                "active_verticals": len(orchestrator.active_demos),
                "total_events": sum(m.api_calls for m in metrics.values() if m),
                "avg_response_time": 42,  # Simulated value
                "system_health": 99.99,
                "latest_event": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Processed {len(metrics)} vertical updates"
                },
                "metrics": {
                    "events_per_second": sum(m.api_calls for m in metrics.values() if m) / 60
                },
                "verticals": {
                    name: {
                        "status": "active" if name in orchestrator.active_demos else "inactive",
                        "events": metrics[name].api_calls if metrics[name] else 0,
                        "latency": 42  # Simulated value
                    }
                    for name in orchestrator.verticals
                }
            }

            await websocket.send_text(json.dumps(message))
            await asyncio.sleep(1)

    except:
        active_websockets.remove(websocket)


@app.on_event("startup")
async def startup_event():
    """Start the orchestrator on server startup"""
    # Launch all verticals
    for vertical in orchestrator.verticals:
        await orchestrator.orchestrate_launch(vertical)


@app.on_event("shutdown")
async def shutdown_event():
    """Stop all demos on server shutdown"""
    for vertical in orchestrator.verticals:
        await orchestrator.stop_demos(vertical)

    # Close all websocket connections
    for ws in active_websockets:
        await ws.close()
