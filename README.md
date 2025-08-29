# EpochCore RAS (Recursive Autonomous Software)

A comprehensive autonomous software system that combines the capabilities of StrategyDECK's intelligent asset management with EpochCore5's advanced agent architecture. This system features recursive self-improvement, ethical decision-making, and adaptive learning capabilities.

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

## 🧬 Capsule System

Capsules are autonomous, self-contained digital assets minted by the EpochCore RAS system. Each capsule represents a unique bundle of value, intent, and metadata, and can be used for revenue, governance, network expansion, or custom business actions.

### Capsule Features
- **Self-contained JSON asset**: Each capsule is a JSON file with unique ID, timestamp, trigger, and metadata.
- **Minting via Strike actions**: Capsules are created using batch scripts or dashboard actions (see Strike Actions below).
- **Ledger integration**: All capsule events are logged for analytics and auditing.
- **Payment options**: Capsules can include payment QR codes for Stripe, PayPal, or CashApp.
- **Asset glyphs**: Each capsule is visually represented by a ranked icon (see Asset Glyphs by Rank).

### Capsule Types (Strike Actions)
1. **Strike 1:** Mint revenue/ROI capsule  
   `./ultra_trigger_pack_batch.sh --batch roi-burst`
2. **Strike 2:** Mint mesh/network expansion capsule  
   `./ultra_trigger_pack_batch.sh --batch mesh-expand`
3. **Strike 3:** Mint governance/security capsule  
   `./ultra_trigger_pack_batch.sh --batch gov-harden`
4. **Strike 4:** Mint all types at once  
   `./ultra_trigger_pack_batch.sh --batch full-send`
5. **Strike 5:** Custom selection (ask Copilot)  
   `./ultra_trigger_pack_batch.sh --pick '1 3 8 10'`

### Asset Glyphs by Rank

**Dark Mode**
- **burnt-orange (Premium)**: 48px/print
    - strategy_icon-dark-burnt-orange-48px.png
    - strategy_icon-dark-burnt-orange-48px.svg
- **copper-foil (Elite)**: 32px/web
    - strategy_icon-dark-copper-foil-32px.png
    - strategy_icon-dark-copper-foil-32px.svg
- **flat-orange (Standard)**: 16px/32px/48px/web
    - strategy_icon-dark-flat-orange-16px.png
    - strategy_icon-dark-flat-orange-16px.svg
    - strategy_icon-dark-flat-orange-32px.png
    - strategy_icon-dark-flat-orange-32px.svg
    - strategy_icon-dark-flat-orange-48px.png
    - strategy_icon-dark-flat-orange-48px.svg

**Light Mode**
- **flat-orange (Standard)**: 16px/32px/48px/web
    - strategy_icon-light-flat-orange-16px.png
    - strategy_icon-light-flat-orange-16px.svg
    - strategy_icon-light-flat-orange-32px.png
    - strategy_icon-light-flat-orange-32px.svg
    - strategy_icon-light-flat-orange-48px.png
    - strategy_icon-light-flat-orange-48px.svg
- **matte-carbon (Executive)**: 16px/32px/print
    - strategy_icon-light-matte-carbon-16px.png
    - strategy_icon-light-matte-carbon-16px.svg
    - strategy_icon-light-matte-carbon-32px.png
    - strategy_icon-light-matte-carbon-32px.svg

---

For more details, see the dashboard sidebar or run `streamlit run capsule_dashboard.py` for interactive capsule management.

