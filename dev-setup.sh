#!/bin/bash
# EPOCH5 Development Setup Script
# Automates the complete development environment setup

set -e

echo "🚀 EPOCH5 Template Development Setup"
echo "===================================="
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
        echo "⚡ Activating virtual environment..."
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    fi
fi

# Install dependencies
echo
echo "📋 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install pre-commit hooks
echo
echo "🪝 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  Pre-commit not found, skipping hook installation"
fi

# Run initial tests
echo
echo "🧪 Running initial tests..."
if python3 -m pytest tests/ --tb=no -q; then
    echo "✅ Initial tests passed"
else
    echo "⚠️  Some tests failed, but this is expected during development"
fi

# Set up demo environment
echo
echo "🎯 Setting up demo environment..."
python3 integration.py setup-demo > /dev/null 2>&1
echo "✅ Demo environment ready"

# Check system status
echo
echo "📊 Checking system status..."
python3 integration.py status | head -5

echo
echo "🎉 Development setup complete!"
echo
echo "Next steps:"
echo "  1. Run tests:           pytest"
echo "  2. Format code:         black ."
echo "  3. Check linting:       flake8 ."
echo "  4. System demo:         python3 integration.py run-workflow"
echo "  5. Launch dashboard:    bash ceiling_launcher.sh"
echo
echo "For detailed documentation, see DEVELOPMENT.md"
echo
echo "Happy coding! 🚀"