# StrategyDECK AI Agent System

A dedicated AI agent system for automating strategic tasks and processes within the StrategyDECK project. This system provides intelligent automation capabilities to enhance development efficiency, improve consistency, and enable smart workflow optimization.

## 🤖 Overview

The StrategyDECK AI Agent System consists of multiple specialized agents that work together to automate various aspects of project management:

- **Project Monitor Agent**: Tracks project status and generates comprehensive reports
- **Asset Manager Agent**: Automates icon generation and asset management tasks
- **Workflow Optimizer Agent**: Analyzes and suggests improvements for GitHub Actions workflows

## 🏗️ Architecture

```
scripts/ai_agent/
├── __init__.py              # Main module exports
├── core/                    # Core framework components
│   ├── __init__.py
│   ├── agent_manager.py     # Agent coordination and management
│   ├── base_agent.py        # Abstract base class for all agents
│   └── logger.py           # Centralized logging configuration
├── agents/                  # Individual agent implementations
│   ├── __init__.py
│   ├── project_monitor.py   # Project monitoring and reporting
│   ├── asset_manager.py     # Asset generation and management
│   └── workflow_optimizer.py # Workflow analysis and optimization
└── config/                  # Configuration files
    └── default.json         # Default agent configuration
```

## 🚀 Quick Start

### Installation

Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run all agents
python scripts/run_agents.py

# Run a specific agent
python scripts/run_agents.py --agent project_monitor

# List available agents
python scripts/run_agents.py --list

# Use custom configuration
python scripts/run_agents.py --config custom.json
```

## 🔧 Agent Details

### Project Monitor Agent

**Purpose**: Provides comprehensive project health monitoring and status reporting.

**Features**:
- Analyzes project structure and organization
- Monitors GitHub Actions workflows
- Tracks asset generation status
- Evaluates test coverage
- Checks documentation completeness
- Generates timestamped reports

**Output**: JSON reports saved to `reports/` directory with detailed project metrics.

### Asset Manager Agent

**Purpose**: Automates and optimizes icon generation and asset management processes.

**Features**:
- Validates master SVG files and CSV configuration
- Monitors asset generation status
- Provides optimization suggestions
- Can automatically trigger asset generation
- Tracks PNG export availability

**Configuration Options**:
- `auto_generate`: Whether to automatically run icon generation (default: false)

### Workflow Optimizer Agent

**Purpose**: Analyzes GitHub Actions workflows and suggests performance improvements.

**Features**:
- Analyzes workflow structure and complexity
- Identifies optimization opportunities
- Checks adherence to best practices
- Provides performance insights
- Suggests security improvements

**Analysis Areas**:
- Trigger configuration
- Job and step organization
- Action version pinning
- Caching strategies
- Security practices

## ⚙️ Configuration

The system uses JSON configuration files to customize agent behavior. Create a configuration file based on the default template:

```json
{
  "logging": {
    "level": "INFO",
    "console": true,
    "file": "logs/ai_agent.log"
  },
  "agents": {
    "project_monitor": {
      "enabled": true,
      "save_report": true
    },
    "asset_manager": {
      "enabled": true,
      "auto_generate": false
    },
    "workflow_optimizer": {
      "enabled": true
    }
  }
}
```

### Configuration Options

#### Logging
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `console`: Enable console output
- `file`: Log file path (optional)

#### Agent Configuration
Each agent can be individually configured with:
- `enabled`: Whether the agent should be loaded and available
- Agent-specific options as documented above

## 🔄 Integration with Existing Workflows

### GitHub Actions Integration

Add the AI agent system to your GitHub Actions workflows:

```yaml
- name: Run AI Agents
  run: |
    python scripts/run_agents.py
    
- name: Upload Agent Reports
  uses: actions/upload-artifact@v3
  with:
    name: ai-agent-reports
    path: reports/
```

### Manual Execution

Run agents manually for development and debugging:

```bash
# Monitor project status
python scripts/run_agents.py --agent project_monitor

# Check asset management
python scripts/run_agents.py --agent asset_manager

# Analyze workflows
python scripts/run_agents.py --agent workflow_optimizer
```

## 📊 Output and Reports

### Project Monitor Reports

Generated reports include:
- **Project Structure**: File counts, directory organization
- **Workflow Status**: GitHub Actions workflow analysis
- **Asset Status**: Icon generation and master file status
- **Test Coverage**: Test file analysis and coverage ratios
- **Documentation**: Documentation completeness check

Reports are saved as timestamped JSON files in the `reports/` directory.

### Agent Execution Results

All agents return structured results with:
- Execution status (success/error)
- Detailed analysis data
- Actionable recommendations
- Timestamp and metadata

## 🧪 Testing

The AI agent system includes comprehensive validation:

```bash
# Test agent functionality
python -c "
from scripts.ai_agent.core.agent_manager import AgentManager
manager = AgentManager()
print('Agent system loaded successfully')
"
```

## 📈 Extending the System

### Creating Custom Agents

1. Inherit from `BaseAgent`:

```python
from scripts.ai_agent.core.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("custom_agent", config)
    
    def validate_config(self):
        # Validate agent configuration
        return True
    
    def run(self):
        # Implement agent logic
        return {"status": "completed"}
```

2. Register with the agent manager:

```python
from scripts.run_agents import main
# Add your agent to the agents list in main()
```

### Adding New Capabilities

The modular architecture supports easy extension:
- Add new agent types in `agents/`
- Extend base functionality in `core/`
- Add configuration options in `config/`

## 🛡️ Error Handling and Logging

The system includes robust error handling:
- **Comprehensive Logging**: All operations are logged with timestamps
- **Graceful Failure**: Agents fail safely without affecting others
- **Detailed Error Messages**: Clear error reporting for debugging
- **Timeout Protection**: Long-running operations have timeout limits

## 🔮 Future Enhancements

Planned improvements for the AI agent system:

- **Scheduled Execution**: Cron-style scheduling for automatic runs
- **Web Dashboard**: Real-time monitoring and control interface
- **Notification Integration**: Slack, email, or webhook notifications
- **Machine Learning**: Predictive analytics for project health
- **Multi-Repository Support**: Manage multiple StrategyDECK projects
- **Custom Metrics**: User-defined KPIs and monitoring targets

## 📝 Contributing

To contribute to the AI agent system:

1. Follow the existing architecture patterns
2. Add comprehensive tests for new agents
3. Update documentation for new features
4. Ensure proper error handling and logging
5. Maintain backward compatibility

## 🆘 Troubleshooting

### Common Issues

**Agent Not Found**: Check that the agent is enabled in configuration and properly registered.

**Configuration Errors**: Validate JSON syntax and ensure all required fields are present.

**Permission Issues**: Ensure the script has read/write access to required directories.

**Import Errors**: Verify all dependencies are installed and Python path is correct.

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python scripts/run_agents.py --verbose
```

Or set log level in configuration:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📄 License

This AI agent system is part of the StrategyDECK project and follows the same licensing terms.