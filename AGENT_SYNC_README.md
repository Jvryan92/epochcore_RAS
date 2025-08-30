# Agent Flash Sync System

This system provides automated agent synchronization, monitoring, and visualization tools for your mesh network of agents, with the flash sync serving as the master coordinator.

## Components

1. **Flash Sync Script** (`flash_sync_agents.py`)
   - Synchronizes the state of all agents in the mesh network
   - Validates consensus across agents
   - Detects anomalies in agent performance
   - Creates comprehensive logs and artifacts

2. **Scheduled Sync** (`schedule_flash_sync.py`)
   - Runs the flash sync at scheduled times (9 AM, 2 PM, and 5 PM)
   - Can be run manually with `--now` flag
   - Logs all sync results for historical tracking

3. **Agent Dashboard** (`agent_dashboard.py`)
   - Provides a web-based visualization of agent health and sync results
   - Shows historical trends and anomaly detection
   - Displays detailed agent status information

4. **System Service** (`flash-sync.service`)
   - Systemd service definition for running the scheduler as a background service
   - Ensures the sync process restarts on failure

5. **Cron Job** (`flash-sync-crontab`)
   - Alternative scheduling using cron
   - Runs the sync process at 9 AM, 2 PM, and 5 PM daily

6. **epochALPHA Sync** (`sync_epochALPHA.py`)
   - Specialized sync for the master coordinator agent
   - Features quantum bridge simulation
   - Distributes strategic directives to other agents
   - Creates detailed performance metrics

7. **Fleet Commander** (`fleet_commander.py`)
   - Advanced dashboard for the entire agent ecosystem
   - Visualizes quantum bridge status
   - Displays strategic directives and fleet health
   - Provides anomaly detection and monitoring

## Setup Instructions

### Installing Dependencies

```bash
pip install flask pandas matplotlib
```

### Running a Manual Flash Sync

```bash
python flash_sync_agents.py
```

### Running an epochALPHA Sync

```bash
python sync_epochALPHA.py
```

### Starting the Fleet Commander Dashboard

```bash
python fleet_commander.py
```

Then open your browser to http://localhost:5000 to view the dashboard.

### Setting Up Scheduled Syncs

#### Option 1: Using the Scheduler Daemon

```bash
python schedule_flash_sync.py
```

This will run continuously and perform syncs at the scheduled times.

#### Option 2: Using Cron

```bash
crontab -e
```

Add the contents of `flash-sync-crontab` to your crontab.

#### Option 3: Using Systemd

```bash
sudo cp flash-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flash-sync
sudo systemctl start flash-sync
```

### Running the Dashboard

```bash
python agent_dashboard.py
```

Then open your browser to http://localhost:5000 to view the dashboard.

## The epochALPHA Agent

The epochALPHA agent serves as the master coordinator for your entire agent fleet. It has several unique capabilities:

### Quantum Bridge

The quantum bridge is a simulated quantum computing interface that provides secure communication between agents. It features:

- Entangled quantum states for secure messaging
- Decoherence monitoring for channel stability
- Error correction for reliable transmission

### Strategic Directives

The agent distributes strategic directives to other agents in the fleet, prioritizing tasks based on system needs:

- Task assignment based on agent capabilities
- Priority management for critical operations
- Contingency planning for system failures

### Anomaly Detection

Advanced anomaly detection identifies unusual patterns in the agent mesh:

- Performance anomalies in CPU and memory usage
- Communication anomalies in agent messaging
- Security anomalies in authentication and authorization

## Monitoring and Maintenance

### Checking Sync Status

Recent sync results are stored in the `sync_results` directory and can be viewed either through the dashboard or directly:

```bash
ls -la sync_results/
cat sync_results/latest_sync.json
```

### Log Files

Logs for the scheduled syncs are stored in the `logs` directory:

```bash
tail -f logs/scheduled_sync.log
```

### Troubleshooting

If a sync fails, check the following:

1. Verify all agents are reachable and active
2. Check for anomalies in the agent metrics
3. Examine the detailed sync receipt in the `sync` directory
4. Review the logs for error messages

## Customization

### Adjusting Sync Schedule

Edit the `SCHEDULE` array in `schedule_flash_sync.py` to change sync times.

### Adding New Agents

Update the `AGENTS` array in `flash_sync_agents.py` to add or remove agents from the sync process.

### Modifying Anomaly Detection Thresholds

The `FLASH_THRESHOLD` environment variable controls how sensitive the anomaly detection is. Lower values result in more detected anomalies.

## Integration with StrategyDECK

The agent system integrates with the StrategyDECK icon generation system to provide visual representations for the dashboard.

### Icon Generation

The `generate_icons.py` script in the `scripts` directory creates icon variants based on:

- **Mode**: Light or dark background
- **Finish**: Different visual styles (flat-orange, matte-carbon, etc.)
- **Size**: Various pixel dimensions (16px, 32px, 48px)
- **Context**: Usage context (web, print, app)

To generate the icons:

```bash
python scripts/generate_icons.py
```

### Testing Icon Generation

The system includes tests to verify icon generation:

```bash
pytest tests/test_generate_icons.py
```

## Advanced Usage

### Fleet Commander API

The Fleet Commander dashboard provides an API for programmatic access:

- `/sync/alpha` - Trigger an epochALPHA sync
- `/sync/fleet` - Trigger a full fleet sync

### Quantum Bridge Operations

Advanced users can experiment with the quantum bridge simulation:

```python
from sync_epochALPHA import simulate_quantum_bridge

# Get the current quantum state
quantum_state = simulate_quantum_bridge()
print(quantum_state)
```

### Security Considerations

The system uses HMAC authentication for secure communication:

- All sync operations are authenticated using HMAC signatures
- Ledger entries are cryptographically linked for tamper resistance
- Anomaly detection identifies potential security issues
