# EpochCore RAS (Recursive Autonomous Software)
EpochCore RAS is a comprehensive autonomous software system that combines multi-agent orchestration, ethical decision-making, DAG workflow management, and capsule-based asset management with recursive self-improvement capabilities.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Environment Setup
**NEVER CANCEL: Environment setup takes 3-5 minutes. Set timeout to 10+ minutes.**
```bash
# Create virtual environment (takes ~3 seconds)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip (takes ~2 seconds)  
pip install --upgrade pip

# Install dependencies (takes 5-15 minutes depending on network)
# NEVER CANCEL: This step may take up to 15 minutes due to large dependencies
pip install -r requirements.txt
```

**Alternative minimal setup if network issues occur:**
```bash
# Install only essential packages for basic functionality
pip install pyyaml psutil rich
```

### Build and Test System
**NEVER CANCEL: Testing takes 1-5 minutes. Set timeout to 10+ minutes.**
```bash
# Run all tests using unittest (takes ~1 second)
python -m unittest discover tests/ -v

# Run integration tests (takes ~1 second)  
python integration.py validate

# Run system demo (takes ~1 second)
python integration.py setup-demo
python integration.py run-workflow
```

**If pytest is available:**
```bash
# NEVER CANCEL: Full test suite takes 2-5 minutes
pytest --cov=. --cov-report=html --cov-report=term-missing

# Fast test run (takes ~30 seconds)
pytest -x -v
```

### Run the Applications

#### Main Integration System
```bash
# Setup demo environment (takes <1 second)
python integration.py setup-demo

# Run complete workflow (takes <1 second) 
python integration.py run-workflow

# Check system status (takes <1 second)
python integration.py status

# Validate system integrity (takes <1 second)
python integration.py validate
```

#### Web Dashboard
```bash
# Start dashboard server (starts immediately)
python dashboard.py 8000
# Access at http://localhost:8000
# Press Ctrl+C to stop
```

#### Using Makefile Commands
```bash
# Run demo workflow (takes ~1 second)
make demo

# Check system status (takes <1 second)
make status  

# Validate system (takes <1 second)
make validate

# Format code (takes 1-3 seconds)
make format

# Run linting (takes 2-5 seconds) 
make lint

# Clean build artifacts (takes <1 second)
make clean
```

## Validation

### Manual Testing Scenarios
**Always test these scenarios after making changes:**

1. **Basic System Health Check:**
   ```bash
   python integration.py status
   # Verify: Shows operational status with agent/DAG/capsule counts
   ```

2. **Complete Workflow Execution:**
   ```bash
   python integration.py setup-demo
   python integration.py run-workflow
   # Verify: Both complete successfully without errors
   ```

3. **System Validation:**
   ```bash
   python integration.py validate
   # Verify: All integrity checks pass
   ```

4. **Web Dashboard Access:**
   ```bash
   python dashboard.py 8000 &
   curl http://localhost:8000/api/status
   # Verify: Returns JSON status data
   kill %1  # Stop background server
   ```

### Automated Testing
**NEVER CANCEL: Always run the complete test suite before committing changes.**
```bash
# Run all automated tests (takes 1-5 minutes total)
python -m unittest discover tests/ -v
make validate
```

### Code Quality Checks  
**Always run these before committing (combined takes 3-10 seconds):**
```bash
# Format code
make format

# Check linting  
make lint
```

## Common Tasks and Timing Expectations

### Environment Operations
- Virtual environment creation: **~3 seconds**
- Basic package installation: **30 seconds - 5 minutes**
- Full dependency installation: **NEVER CANCEL - may take 5-15 minutes**
- Environment cleanup: **<1 second**

### System Operations  
- Demo setup: **<1 second**
- Workflow execution: **<1 second**
- System status check: **<1 second**
- System validation: **<1 second**
- Dashboard startup: **immediate**

### Development Operations
- Test suite (unittest): **<1 second** 
- Test suite (pytest): **NEVER CANCEL - 2-5 minutes for full coverage**
- Code formatting: **1-3 seconds**
- Linting checks: **2-5 seconds**
- Build artifact cleanup: **<1 second**

### **CRITICAL TIMEOUT WARNINGS:**
- **NEVER CANCEL** pip install operations - they may take 15+ minutes
- **NEVER CANCEL** full pytest runs - they may take 5+ minutes  
- **NEVER CANCEL** any command that appears to hang for less than 60 seconds
- Set minimum timeout of **600 seconds (10 minutes)** for dependency installation
- Set minimum timeout of **300 seconds (5 minutes)** for testing operations

## Project Structure and Navigation

### Root Directory Contents
```
epochcore_RAS/
├── integration.py          # Main system orchestration script
├── dashboard.py            # Web dashboard for monitoring  
├── requirements.txt        # Python dependencies
├── Makefile               # Development automation
├── README.md              # Project documentation
├── tests/                 # Test suite
│   ├── test_integration.py # Integration tests
│   └── __init__.py        # Test package init
├── venv/                  # Virtual environment (created by setup)
└── .github/               # GitHub workflows and actions
```

### Key System Components (if full project available)
- **agent_management.py**: Multi-agent orchestration and DID management
- **policy_grants.py**: Security policies and access control 
- **dag_management.py**: Directed acyclic graph workflow management
- **cycle_execution.py**: Task execution cycles and consensus
- **capsule_metadata.py**: Asset integrity and storage management
- **ceiling_manager.py**: Dynamic resource management and service tiers
- **meta_capsule.py**: System state capture and archiving
- **ethical_reflection.py**: Ethical decision-making framework

### Dashboard Locations
- **Primary dashboard**: `python dashboard.py` at http://localhost:8000
- **Status API**: http://localhost:8000/api/status
- **Agents API**: http://localhost:8000/api/agents

### Test Locations
- **Integration tests**: `tests/test_integration.py`
- **Run tests**: `python -m unittest discover tests/ -v`
- **Test coverage**: Available with pytest if installed

## Troubleshooting Common Issues

### Network/Installation Issues
**Problem**: `pip install -r requirements.txt` fails with timeout
**Solution**: Use minimal setup: `pip install pyyaml psutil rich`

### Import Errors  
**Problem**: `ImportError: No module named X`
**Solution**: Ensure virtual environment is activated: `source venv/bin/activate`

### Test Failures
**Problem**: Tests fail with missing modules
**Solution**: Install test dependencies or use built-in unittest: `python -m unittest discover tests/ -v`

### Port Conflicts
**Problem**: Dashboard won't start on port 8000
**Solution**: Use different port: `python dashboard.py 8001`

### Permission Errors
**Problem**: Scripts not executable
**Solution**: `chmod +x script_name.sh` for shell scripts

## Advanced Usage

### One-liner System Operations
```bash
# Complete system check
python integration.py setup-demo && python integration.py run-workflow && python integration.py validate

# Quick development cycle  
make demo && make validate && make format

# System monitoring
watch -n 5 "python integration.py status"
```

### API Integration
The system provides programmatic access through the integration.py module:
```python
from integration import setup_demo, run_workflow, get_status, validate_system

# Setup and run workflow programmatically
setup_demo()
result = run_workflow() 
status = get_status()
validation = validate_system()
```

### Configuration
- Environment variables can be set via `.env` file (if present)
- System configuration is managed through the integration.py interface
- Dashboard port and settings configurable via command line arguments

---

**Remember**: This system is designed for autonomous operation. Always validate your changes with the complete test suite and never cancel long-running operations prematurely.