"""
FastAPI-based real-time game dashboard for EpochCore RAS
"""

import asyncio
from datetime import datetime
from typing import Dict, Set

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .launch_orchestrator import GameLaunchOrchestrator

app = FastAPI(
    title="EpochCore RAS Game Dashboard",
    description="Real-time game metrics and status",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
orchestrator = GameLaunchOrchestrator()
active_websockets: Set[WebSocket] = set()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EpochCore RAS - Game Launch Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-900">EpochCore RAS</h1>
                <p class="mt-2 text-lg text-gray-600">Game Launch Status</p>
            </div>
            
            <!-- Game Mode Status Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Characters Mode</h3>
                    <p class="text-3xl font-bold text-green-600" id="characters-status">Live</p>
                    <p class="text-sm text-gray-500" id="characters-players">0 active players</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Meshgear Mode</h3>
                    <p class="text-3xl font-bold text-green-600" id="meshgear-status">Live</p>
                    <p class="text-sm text-gray-500" id="meshgear-transactions">0 transactions</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Governance Mode</h3>
                    <p class="text-3xl font-bold text-green-600" id="governance-status">Live</p>
                    <p class="text-sm text-gray-500" id="governance-votes">0 votes</p>
                </div>
            </div>
            
            <!-- Metrics Overview -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Total Players</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="total-players">0</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Matches Played</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="total-matches">0</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">Proof Capsules</h3>
                    <p class="text-3xl font-bold text-indigo-600" id="total-capsules">0</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900">System Health</h3>
                    <p class="text-3xl font-bold text-green-600" id="system-health">100%</p>
                </div>
            </div>
            
            <!-- Charts Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Player Activity Chart -->
                <div class="bg-white rounded-lg shadow">
                    <div class="p-6">
                        <h2 class="text-lg font-medium text-gray-900">Player Activity</h2>
                        <canvas id="player-chart" class="mt-4"></canvas>
                    </div>
                </div>
                
                <!-- Transaction Chart -->
                <div class="bg-white rounded-lg shadow">
                    <div class="p-6">
                        <h2 class="text-lg font-medium text-gray-900">Mesh Transactions</h2>
                        <canvas id="transaction-chart" class="mt-4"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Character Stats -->
            <div class="mt-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">Character Statistics</h2>
                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Character</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pick Rate</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Win Rate</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Score</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200" id="character-stats">
                            <!-- Filled dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            let playerChart, transactionChart;
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            function updateDashboard(data) {
                // Update mode status
                updateModeStatus('characters', data.modes.characters);
                updateModeStatus('meshgear', data.modes.meshgear);
                updateModeStatus('governance', data.modes.governance);
                
                // Update overview metrics
                document.getElementById('total-players').textContent = data.totals.players;
                document.getElementById('total-matches').textContent = data.totals.matches;
                document.getElementById('total-capsules').textContent = data.totals.capsules;
                document.getElementById('system-health').textContent = data.system_health + '%';
                
                // Update charts
                updatePlayerChart(data.charts.players);
                updateTransactionChart(data.charts.transactions);
                
                // Update character stats
                updateCharacterStats(data.characters);
            }
            
            function updateModeStatus(mode, data) {
                document.getElementById(`${mode}-status`).textContent = data.status;
                const metricElem = document.getElementById(`${mode}-${data.metric_type}`);
                if (metricElem) {
                    metricElem.textContent = `${data.metric_value} ${data.metric_type}`;
                }
            }
            
            function updatePlayerChart(data) {
                if (!playerChart) {
                    const ctx = document.getElementById('player-chart').getContext('2d');
                    playerChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Active Players',
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
                
                playerChart.data.labels = data.labels;
                playerChart.data.datasets[0].data = data.values;
                playerChart.update();
            }
            
            function updateTransactionChart(data) {
                if (!transactionChart) {
                    const ctx = document.getElementById('transaction-chart').getContext('2d');
                    transactionChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Transactions/min',
                                data: [],
                                backgroundColor: 'rgb(16, 185, 129)',
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
                
                transactionChart.data.labels = data.labels;
                transactionChart.data.datasets[0].data = data.values;
                transactionChart.update();
            }
            
            function updateCharacterStats(characters) {
                const tbody = document.getElementById('character-stats');
                tbody.innerHTML = '';
                
                for (const char of characters) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                                <div class="text-sm font-medium text-gray-900">${char.name}</div>
                            </div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">${char.pick_rate}%</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">${char.win_rate}%</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">${char.avg_score}</div>
                        </td>
                    `;
                    tbody.appendChild(row);
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
            for mode in orchestrator.game_modes:
                metrics[mode] = orchestrator.get_metrics(mode)

            # Create update message
            message = {
                "modes": {
                    "characters": {
                        "status": "Live",
                        "metric_type": "players",
                        "metric_value": metrics["characters"].active_players if metrics["characters"] else 0
                    },
                    "meshgear": {
                        "status": "Live",
                        "metric_type": "transactions",
                        "metric_value": metrics["meshgear"].mesh_transactions if metrics["meshgear"] else 0
                    },
                    "governance": {
                        "status": "Live",
                        "metric_type": "votes",
                        "metric_value": metrics["governance"].governance_votes if metrics["governance"] else 0
                    }
                },
                "totals": {
                    "players": sum(m.active_players for m in metrics.values() if m),
                    "matches": sum(m.matches_played for m in metrics.values() if m),
                    "capsules": sum(m.proof_capsules for m in metrics.values() if m)
                },
                "system_health": 99.99,
                "charts": {
                    "players": {
                        "labels": [datetime.now().strftime("%H:%M:%S")],
                        "values": [sum(m.active_players for m in metrics.values() if m)]
                    },
                    "transactions": {
                        "labels": ["Characters", "Meshgear", "Governance"],
                        "values": [
                            metrics["characters"].mesh_transactions if metrics["characters"] else 0,
                            metrics["meshgear"].mesh_transactions if metrics["meshgear"] else 0,
                            metrics["governance"].mesh_transactions if metrics["governance"] else 0
                        ]
                    }
                },
                "characters": [
                    {
                        "name": "Eli — The Inheritor",
                        "pick_rate": 35.5,
                        "win_rate": 52.3,
                        "avg_score": 8.7
                    },
                    {
                        "name": "Nara — Bastionkeeper",
                        "pick_rate": 28.9,
                        "win_rate": 49.8,
                        "avg_score": 8.2
                    }
                ]
            }

            await websocket.send_text(json.dumps(message))
            await asyncio.sleep(1)

    except:
        active_websockets.remove(websocket)


@app.on_event("startup")
async def startup_event():
    """Start the orchestrator on server startup"""
    # Launch all game modes
    for mode in orchestrator.game_modes:
        await orchestrator.launch_game_mode(mode)


@app.on_event("shutdown")
async def shutdown_event():
    """Stop all modes on server shutdown"""
    for mode in orchestrator.game_modes:
        await orchestrator.stop_mode(mode)

    # Close all websocket connections
    for ws in active_websockets:
        await ws.close()
