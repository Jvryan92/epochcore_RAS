#!/bin/bash
# EpochCore RAS Python Repository Setup Script

set -e

echo "🐍 Setting up EpochCore RAS for Python repository..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install EpochCore RAS dependencies
echo "📥 Installing EpochCore RAS dependencies..."
if [ -f "requirements.txt" ]; then
    # Backup existing requirements
    cp requirements.txt requirements.backup.txt
    
    # Merge with EpochCore requirements
    cat >> requirements.txt << EOF

# EpochCore RAS Dependencies
pyyaml>=6.0.2
psutil>=5.9.5
pytest>=8.0.0
pytest-cov>=4.0.0
flake8>=6.0.0
black>=23.0.0
rich>=13.0.0
schedule>=1.2.0
EOF
else
    # Create new requirements file
    cat > requirements.txt << EOF
# EpochCore RAS Core Dependencies
pyyaml>=6.0.2
psutil>=5.9.5
pytest>=8.0.0
pytest-cov>=4.0.0
flake8>=6.0.0
black>=23.0.0
rich>=13.0.0
schedule>=1.2.0
EOF
fi

pip install -r requirements.txt

# Create basic Python project structure if needed
echo "📁 Setting up Python project structure..."
mkdir -p tests
mkdir -p src
mkdir -p docs
mkdir -p config

# Create pytest configuration
if [ ! -f "pytest.ini" ]; then
    cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# EpochCore RAS
logs/
backups/
.epochcore/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
fi

# Test EpochCore RAS integration
echo "🧪 Testing EpochCore RAS integration..."
if python integration.py validate; then
    echo "✅ EpochCore RAS integration successful!"
else
    echo "⚠️  EpochCore RAS validation warnings - check the output above"
fi

echo "🎉 Python repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run tests: python -m pytest"
echo "3. Initialize recursive improvements: python integration.py init-recursive"
echo "4. Check system status: python integration.py status"