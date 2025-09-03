# Quick Start Guide

Get up and running with EpochCore RAS in minutes.

## 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Initialize System
```bash
python integration.py setup-demo
python integration.py init-recursive
```

## 3. Verify Installation
```bash
python integration.py status
python integration.py validate
```

## 4. Start Dashboard
```bash
python dashboard.py 8000
```

Visit http://localhost:8000 to see the system dashboard.

## Next Steps
- Read the Developer Guide
- Explore the API documentation
- Configure system settings
