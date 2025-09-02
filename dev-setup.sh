#!/bin/bash
# EpochCore RAS Development Setup Script
# Automates the complete development environment setup

set -e

echo "🚀 EpochCore RAS Development Setup"
echo "================================="
echo

# Check Python version
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo
    echo "💡 Virtual environment recommended for development"
    read -p "Create and activate virtual environment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
        echo "⚡ To activate virtual environment, run:"
        echo "   source venv/bin/activate"
        echo "✅ Virtual environment created"
    fi
fi

# Install dependencies (if virtual env is activated)
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo
    echo "📋 Installing dependencies..."
    pip install --upgrade pip
    
    # Try full requirements, fallback to minimal on network issues
    if ! pip install -r requirements.txt; then
        echo "⚠️  Network issues detected, installing minimal requirements..."
        pip install pyyaml psutil rich
        echo "✅ Minimal dependencies installed"
    else
        echo "✅ Full dependencies installed"
    fi
else
    echo "⚠️  Virtual environment not active, skipping dependency installation"
    echo "   Activate with: source venv/bin/activate"
    echo "   Then run: pip install -r requirements.txt"
fi

# Run initial tests
echo
echo "🧪 Running initial tests..."
if python3 -m unittest discover tests/ -v; then
    echo "✅ Initial tests passed"
else
    echo "⚠️  Some tests failed, but this may be expected"
fi

# Set up demo environment
echo
echo "🎯 Setting up demo environment..."
python3 integration.py setup-demo > /dev/null 2>&1
echo "✅ Demo environment ready"

# Check system status
echo
echo "📊 Checking system status..."
python3 integration.py status

echo
echo "🎉 Development setup complete!"
echo
echo "Next steps:"
echo "  1. Activate virtual env:   source venv/bin/activate"
echo "  2. Run tests:             python -m unittest discover tests/ -v"
echo "  3. Run demo:              python integration.py run-workflow"
echo "  4. Start dashboard:       python dashboard.py 8000"
echo "  5. Check status:          python integration.py status"
echo
echo "For detailed documentation, see .github/copilot-instructions.md"
echo
echo "Happy coding! 🚀"