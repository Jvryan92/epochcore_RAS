#!/bin/bash
# EpochCore RAS Setup Script

set -e

echo "Setting up EpochCore RAS..."

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize system
echo "Initializing EpochCore RAS..."
python integration.py setup-demo
python integration.py init-recursive

# Run validation
echo "Validating installation..."
python integration.py validate

# Run agent sync
echo "Synchronizing agent registry..."
python agent_register_sync.py --sync

echo "Setup complete! Run 'source venv/bin/activate' to activate the environment."
echo "Then run 'python dashboard.py 8000' to start the dashboard."
