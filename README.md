# EpochCore RAS (Recursive Autonomous Software)

A comprehensive autonomous software syste- Run the integrated agent system demo
python integrated_demo.py
```

Available agents:
- **project_monitor**: Tracks project status and generates reports
- **asset_manager**: Automates icon generation and asset management
- **workflow_optimizer**: Analyzes and optimizes GitHub Actions workflows
- **kids_friendly_guide**: Provides child-friendly explanations about AI as a helper
- **epoch_audit**: Provides secure audit logging and verification
- **mesh_trigger**: Manages secure triggers for the agent mesh network

## 🏢 Enhanced Ceiling Management System

The EPOCH5 Enhanced Ceiling Management System provides comprehensive dynamic resource limit management with revenue-focused optimization. This system automatically adjusts performance "ceilings" (resource limits) based on real-time metrics and provides clear upgrade paths to maximize revenue.

```bash
# Initialize the system with sample configurations
python integration.py setup-demo

# Launch the real-time web dashboard
python ceiling_dashboard.py

# Interactive launcher with user-friendly menu
./ceiling_launcher.sh

# Create a new ceiling configuration
python integration.py ceilings create user_123 --tier professional

# Adjust ceilings based on performance
python ceiling_manager.py adjust user_123 --success-rate 0.98 --latency 45.0 --budget 80.0
```

### Key Components

- **Dynamic Ceiling Adjustment**: Automatically scales resource limits based on performance scores
- **Multi-Tier Service Model**: Freemium ($0), Professional ($49.99), and Enterprise ($199.99) tiers with clear differentiation
- **Real-time Dashboard**: Web-based monitoring interface at http://localhost:8080
- **Revenue Optimization**: AI-driven upgrade recommendations based on actual usage patterns

### Architecture

- **CeilingManager (`ceiling_manager.py`)**: Core resource management with dynamic adjustment algorithms
- **Dashboard (`ceiling_dashboard.py`)**: Real-time visual analytics and monitoring interface
- **Performance Scoring**: Calculates scores based on success rate, latency, and budget efficiency
- **Automatic Adjustments**: High performers receive increased limits (+25-50%), while poor performers see reductions (-20-30%)

### Business Value

- **Clear Upgrade Path**: Transparent pricing with demonstrated ROI (2.5-3.0x)
- **Performance Incentives**: High-performing users get better limits, encouraging engagement
- **Data-Driven Recommendations**: AI suggests upgrades based on actual usage patterns
- **Revenue Maximization**: Optimizes resource allocation to maximize average revenue per user

## 🧒 Kids Friendly AI Guidees the capabilities of StrategyDECK's intelligent asset management with EpochCore5's advanced agent architecture. This system features recursive self-improvement, ethical decision-making, and adaptive learning capabilities.

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

# Generate icons
python scripts/generate_icons.py
# Or use the enhanced generator
python scripts/enhanced_icon_generator.py --all

# Clean and rebuild all assets
./clean_rebuild_assets.sh
```

## 🚀 Features

- **Enhanced Icon Generation**: Comprehensive SVG/PNG/WebP icon generation with parallel processing, custom palettes, and framework exports
- **AI Agent System**: Dedicated agents for project automation and optimization
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Issue Management**: Auto-labeling and assignment based on keywords
- **PR Management**: Automated reviewer assignment and notifications
- **Documentation**: Auto-generated API docs and usage guides
- **Kids Friendly AI Guide**: Educational resources explaining AI as a helpful tool, not something to fear
- **Integrated Agent System**: Connects Kids Friendly AI Guide, Epoch Audit System, and Mesh Trigger Core with the existing agent architecture
- **Epoch Audit System**: Secure audit logging, verification, and Alpha Ceiling enforcement
- **Mesh Trigger Core**: Secure trigger management and activation for the agent mesh network
- **Enhanced Ceiling Management System**: Dynamic resource limit management with revenue-focused optimization and automatic performance-based adjustments

## 📦 Generated Assets

The system generates icon variants with:
- Multiple color schemes (light/dark modes)
- Various finishes (flat, matte, copper, neon, pastel, metallic)
- Different sizes (16px to 128px)
- Context-specific outputs (web, print, game, saas)
- Multiple formats (SVG, PNG, WebP, AVIF)
- Framework-specific components (React, Vue, Angular, Svelte)

## 🔧 Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate all icon variants (basic)
python scripts/generate_icons.py

# Generate with enhanced options
python scripts/enhanced_icon_generator.py --all

# Use the unified CLI
python scripts/strategydeck_cli.py generate --all

# Or use the Makefile for common operations
make generate        # Basic generation
make generate-enhanced  # Enhanced generation
make export-react    # Export React components
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

# Run the integrated agent system
python integrated_agent_system.py

# Run the integrated agent system demo
python integrated_demo.py
```

Available agents:
- **project_monitor**: Tracks project status and generates reports
- **asset_manager**: Automates icon generation and asset management
- **workflow_optimizer**: Analyzes and optimizes GitHub Actions workflows
- **kids_friendly_guide**: Provides child-friendly explanations about AI as a helper
- **epoch_audit**: Provides secure audit logging and verification
- **mesh_trigger**: Manages secure triggers for the agent mesh network

## 🧒 Kids Friendly AI Guide

The Kids Friendly AI Guide is designed to help explain AI concepts to children in a positive, educational way:

```bash
# Run the Kids AI Guide demo
python scripts/kids_ai_guide_demo.py

# Generate child-friendly AI explanations
python scripts/kids_friendly_ai_guide.py
```

Features:
- Age-appropriate explanations (ages 3-14)
- Kid-friendly metaphors ("AI helps dig the hole, doesn't take the shovel")
- Interactive stories and activities
- Resources for parents and educators
- Positive framing of AI as a helpful tool, not something to fear

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
│   ├── generate_icons.py   # Basic generation script
│   ├── enhanced_icon_generator.py  # Enhanced generation
│   ├── palette_manager.py          # Color palette manager
│   ├── icon_framework_exporter.py  # Framework exporter
│   ├── strategydeck_cli.py         # Unified CLI
│   ├── kids_friendly_ai_guide.py   # Kids AI education module
│   ├── kids_ai_guide_demo.py       # Interactive demo for kids
│   ├── epoch_audit.py      # Secure audit system
│   ├── mesh/               # Mesh network components
│   │   └── trigger_core.py # Secure trigger system
│   └── run_agents.py       # AI agent runner
├── integrated_agent_system.py  # Integrated system connector
├── integrated_demo.py          # Integration demo
├── ceiling_manager.py          # Dynamic resource limit manager
├── ceiling_dashboard.py        # Real-time monitoring interface
├── ceiling_launcher.sh         # Interactive launcher script
├── tests/
│   ├── test_generate_icons.py
│   ├── test_enhanced_generation.py
│   ├── test_palette_manager.py
│   ├── test_framework_exporter.py
│   ├── test_ai_agent.py
│   ├── test_epoch_audit.py
│   ├── test_mesh_trigger_core.py
│   └── test_integrated_agent_system.py
├── docs/
│   ├── api/                # Auto-generated docs
│   ├── AI_AGENT.md         # AI agent documentation
│   ├── ICON_GENERATION.md  # Basic icon generation docs
│   ├── ICON_GENERATION_ENHANCED.md  # Enhanced icon system
│   ├── KIDS_FRIENDLY_AI_GUIDE.md    # Kids guide documentation
│   └── INTEGRATED_AGENT_SYSTEM.md   # Integration documentation
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

## 🎬 Animation System

The StrategyDECK Animation System provides sophisticated animation capabilities for SVG icons and procedurally generated glyphs:

```bash
# Apply animation to standard icons
python animate_icons.py --mode light --finish flat-orange --animation pulse --demo --open

# Apply animation sequence to glyphs
python scripts/glyph_animation_bridge.py --theme cosmic --sequence cosmic-pulsar --demo --open

# Create complete animation showcase
python animation_showcase.py --open

# Launch interactive animation designer
python scripts/animation_designer.py --open
```

### Animation Features
- **Multiple Animation Types**: Pulse, rotate, bounce, fade, color-shift, morph, and more
- **Interactive Demos**: HTML demos with animation controls for easy preview
- **Theme-Specific Animations**: Optimized animations for each glyph theme
- **Animation Sequences**: Combine multiple animations for complex effects
- **Visual Designer**: Interactive tool for creating custom animations
- **Browser Preview**: Live preview of animations with controls
- **Export Capabilities**: Save animations as standalone SVGs for web use

### Integration with Glyph System
The Animation System integrates seamlessly with the Endless Glyph Generator:
- Theme-specific animations optimized for each glyph type
- Complex animation sequences tailored to glyph themes
- Interactive demos showcasing themed glyph animations
- Advanced SVG effects like morphing, color transitions, and transformations

### Animation Designer
The interactive Animation Designer provides a visual interface for:
- Browsing all available SVG icons and glyphs
- Applying multiple animations with customizable parameters
- Previewing animations in real-time with playback controls
- Adjusting animation timing, colors, and transforms
- Exporting animated SVGs for use in web applications
- Copying generated SVG code for direct embedding

## 🔍 Diagnostic & Reporting Tools

The StrategyDECK system includes several diagnostic and reporting tools:

```bash
# Debug SVG baking (color replacement) process
python debug_bake_svg.py --gui
# CLI version (no GUI required)
python debug_bake_svg_cli.py --svg assets/masters/strategy_icon_micro.svg --mode light --finish flat-orange

# Debug PNG conversion issues
python debug_png_conversion.py

# Generate comprehensive PNG conversion report
python debug_png_conversion.py --report

# Test specific SVG to PNG conversion
python debug_png_conversion.py --test-file assets/icons/light/flat-orange/16px/web/icon.svg

# Clean and rebuild all assets
./clean_rebuild_assets.sh

# Generate comprehensive icon report
python icon_report.py --verbose --quality

# Generate HTML visualization of report
./generate_icon_report.sh --verbose --quality --open
```

### Diagnostic Tools
These tools help diagnose and fix common issues with:
- SVG color replacement problems
- PNG conversion failures
- CairoSVG dependency issues
- System-level dependency problems

### Reporting Tools
The reporting tools provide comprehensive analysis of the icon generation system:
- Generation statistics (SVG/PNG counts, variant coverage)
- Quality validation (file integrity, dimensions)
- Dependency verification
- Master file validation
- Endless Glyph System validation
- HTML visualization with progress indicators

For detailed information, see the [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

## 📖 Documentation

- [API Documentation](docs/api/generate_icons.md)
- [Usage Examples](docs/api/examples.md)
- [Basic Icon Generation](docs/ICON_GENERATION.md)
- [Enhanced Icon System](docs/ICON_GENERATION_ENHANCED.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Workflow Configuration](.github/workflows/)
- [AI Agent System](docs/AI_AGENT.md)
- [Kids Friendly AI Guide](docs/KIDS_FRIENDLY_AI_GUIDE.md)
- [Integrated Agent System](docs/INTEGRATED_AGENT_SYSTEM.md)
- [Enhanced Ceiling Management System](docs/CEILING_FEATURES.md)

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

