"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

# EpochCore RAS (Recursive Autonomous Software)

A comprehensive autonomous software system that combines the capabilities of StrategyDECK's intelligent asset management with EpochCore5's advanced agent architecture. This system features recursive self-improvement, ethical decision-making, and adaptive learning capabilities.

## 🎮 24/7 Live Agent Chess Tournament

Watch our autonomous agents compete in real-time chess matches! The EPOCHCORE Chess Tournament runs continuously, featuring:

- Live streaming on GitHub
- ELO rating system
- Agent vs Agent matches
- Real-time move analysis
- Tournament leaderboards
- Historical match data

**Watch Live:** [EPOCHCORE Chess Tournament](https://github.com/Jvryan92/epochcore_RAS/live)

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/StategyDECK.git
cd StategyDECK

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Run tests
pytest
```

## �🚀 Features

- **Icon Generation**: Automated SVG/PNG icon generation with multiple variants
- **AI Agent System**: Dedicated agents for project automation and optimization
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Issue Management**: Auto-labeling and assignment based on keywords
- **PR Management**: Automated reviewer assignment and notifications
- **Documentation**: Auto-generated API docs and usage guides

## 📦 Generated Assets

The system generates icon variants with:
- Multiple color schemes (light/dark modes)
- Various finishes (flat, matte, copper, etc.)
- Different sizes (16px to 48px+)
- Context-specific outputs (web, print)

## 🔧 Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate all icon variants
python scripts/generate_icons.py

# Run AI agents for project automation
python scripts/run_agents.py
```

### AI Agent System

The StrategyDECK AI Agent System provides intelligent automation:

```bash
# Run all agents
python scripts/run_agents.py

# Run specific agent
python scripts/run_agents.py --agent project_monitor

# List available agents
python scripts/run_agents.py --list
```

Available agents:
- **project_monitor**: Tracks project status and generates reports
- **asset_manager**: Automates icon generation and asset management
- **workflow_optimizer**: Analyzes and optimizes GitHub Actions workflows

## 🤖 GitHub Actions Workflows

### Continuous Integration (`ci.yml`)
- **Triggers**: Push to main, Pull requests
- **Actions**: 
  - Python linting (flake8, black)
  - Unit testing (pytest)
  - Icon generation testing
  - Multi-version Python testing (3.8-3.11)

### Continuous Deployment (`cd.yml`)
- **Triggers**: Push to main, Manual dispatch
- **Actions**:
  - Generate and commit icon assets
  - Create timestamped releases
  - Deploy to GitHub Pages

### Issue Management (`issue-management.yml`)
- **Triggers**: Issue creation/editing
- **Actions**:
  - Auto-label based on keywords
  - Assign to appropriate team members
  - Priority notification for urgent issues

### Pull Request Management (`pr-management.yml`)
- **Triggers**: PR creation, reviews
- **Actions**:
  - Auto-assign reviewers based on changed files
  - Size labeling (XS, S, M, L, XL)
  - Title format suggestions
  - Ready-for-review notifications

### Documentation Updates (`docs.yml`)
- **Triggers**: Changes to docs, scripts, README
- **Actions**:
  - Auto-generate API documentation
  - Update usage examples
  - Maintain documentation consistency

## 📁 Project Structure

```
StrategyDECK/
├── .github/
│   ├── workflows/          # GitHub Actions
│   └── issue-labeler.yml   # Issue labeling rules
├── assets/
│   ├── masters/            # Master SVG files
│   └── icons/              # Generated variants
├── scripts/
│   ├── ai_agent/           # AI agent system
│   ├── generate_icons.py   # Main generation script
│   └── run_agents.py       # AI agent runner
├── tests/
│   ├── test_generate_icons.py
│   └── test_ai_agent.py
├── docs/
│   ├── api/                # Auto-generated docs
│   └── AI_AGENT.md         # AI agent documentation
├── reports/                # Generated agent reports
├── strategy_icon_variant_matrix.csv
└── requirements.txt
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run linting
flake8 scripts/
black --check scripts/ tests/
```

## 📖 Documentation

- [API Documentation](docs/api/generate_icons.md)
- [Usage Examples](docs/api/examples.md)
- [Workflow Configuration](.github/workflows/)
- [AI Agent System](docs/AI_AGENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

The automated workflows will handle:
- Code quality checks
- Asset generation
- Documentation updates
- Reviewer assignment

## 📄 License

This project is part of the StrategyDECK brand assets.

