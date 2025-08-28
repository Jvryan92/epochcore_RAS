# EpochCore RAS (Recursive Autonomous Software)

EpochCore RAS is a Python-based autonomous software system that combines icon generation capabilities with advanced AI agent architecture. The system features recursive self-improvement, ethical decision-making, and adaptive learning capabilities.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt` -- takes ~65 seconds. NEVER CANCEL.
- Install additional ML dependencies: `pip install scikit-learn croniter torch` -- takes ~90 seconds. NEVER CANCEL.
- Verify installation by generating icons: `python scripts/generate_icons.py` -- completes in <1 second
- Verify system status: `python integration.py status` -- completes in ~1.5 seconds

### Build and Test Workflow
- **Icon generation**: `python scripts/generate_icons.py` -- generates 10 SVG + 10 PNG files in <1 second
- **Unit tests**: `pytest tests/test_generate_icons.py -v` -- runs 6 core icon tests in <1 second
- **Core system tests**: `pytest tests/test_capsule_metadata.py tests/test_dag_management.py -v` -- runs in ~1 second (some tests may fail due to API changes, but core functionality works)
- **Linting (critical errors)**: `flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics` -- <1 second
- **Linting (full check)**: `flake8 scripts/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics` -- <1 second
- **Format check**: `black --check scripts/ tests/` -- takes ~3 seconds, will show many files need reformatting
- **Apply formatting**: `black scripts/ tests/` -- REQUIRED if format check fails, takes ~3 seconds

### Complete Validation Sequence
Always run this sequence before committing changes:
```bash
pip install -r requirements.txt
pip install scikit-learn croniter torch  # Additional ML dependencies needed
python scripts/generate_icons.py
pytest tests/test_generate_icons.py -v
flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
black --check scripts/ tests/
```
If black check fails, run: `black scripts/ tests/` to auto-format code.

## Validation Scenarios

### Manual Icon Generation Testing
After making changes to the icon generation system, always verify:

1. **Clean generation**:
   ```bash
   rm -rf assets/icons/*
   python scripts/generate_icons.py
   ```
   Expected output: `[done] Generated 10 SVG variants. PNG exports: 10 (requires cairosvg).`

2. **Verify directory structure**:
   ```bash
   test -d assets/icons/light
   test -d assets/icons/dark  
   find assets/icons -name "*.svg" | wc -l | grep -q "10"
   find assets/icons -name "*.png" | wc -l | grep -q "10"
   ```

3. **Inspect sample files**:
   - Check `assets/icons/light/flat-orange/` contains expected variants
   - Check `assets/icons/dark/copper-foil/` contains expected variants
   - Verify file sizes are reasonable (SVG ~200 bytes, PNG varies by size)

### Manual AI Agent Testing
After making changes to the AI agent system, always verify:

1. **List available agents**:
   ```bash
   python scripts/run_agents.py --list
   ```
   Expected output: Lists asset_manager and ledger_agent

2. **Test agent execution**:
   ```bash
   python scripts/run_agents.py --agent asset_manager
   ```
   Expected output: SUCCESS message with CSV config validation

3. **Test system integration**:
   ```bash
   python integration.py status
   ```
   Should show system components status (agents, policies, etc.)

### Manual System Integration Testing
After making changes to the integration system, always verify:

1. **System status check**:
   ```bash
   python integration.py status
   ```
   Should display comprehensive system status without errors

2. **Help system verification**:
   ```bash
   python integration.py --help
   ```
   Should show all available commands (setup-demo, run-workflow, status, etc.)

## Key Project Structure

```
epochcore_RAS/
├── .github/
│   ├── workflows/          # GitHub Actions (ci.yml, cd.yml, etc.)
│   └── issue-labeler.yml   # Issue labeling rules
├── assets/
│   ├── masters/            # Master SVG files (strategy_icon_micro.svg, strategy_icon_standard.svg)
│   └── icons/              # Generated variants (created by script)
├── scripts/
│   ├── ai_agent/           # AI agent system
│   ├── generate_icons.py   # Main generation script
│   └── run_agents.py       # AI agent runner
├── tests/                  # Unit tests (45+ test files)
├── integration.py          # Main system integration script
├── ceiling_launcher.sh     # Interactive ceiling management dashboard
├── strategydeck_agent.py   # Core agent implementation
├── Makefile                # Common development tasks
└── requirements.txt        # Python dependencies
```

## Understanding the Icon Generation System

### Master SVG Files
- **Micro**: `assets/masters/strategy_icon_micro.svg` (128x128) - used for icons ≤ 32px
- **Standard**: `assets/masters/strategy_icon_standard.svg` (256x256) - used for icons > 32px

### Color System
The system uses token-based colors defined in `scripts/generate_icons.py`:
- **Background colors**: Determined by mode (light = white #FFFFFF, dark = slate #060607)
- **Foreground colors**: Determined by finish (flat-orange, matte-carbon, satin-black, etc.)
- **Color replacement**: Script replaces #FF6A00 (background) and #FFFFFF (foreground) in masters

### Configuration Matrix
The `strategy_icon_variant_matrix.csv` defines 10 icon variants with columns:
- Mode: light, dark
- Finish: flat-orange, matte-carbon, satin-black, burnt-orange, copper-foil, embossed-paper  
- Size (px): 16, 32, 48
- Context: web, print
- Filename: auto-generated or custom

## AI Agent System

### Available Agents
- **asset_manager**: Manages and automates icon generation tasks
- **ledger_agent**: Handles ledger and blockchain-related operations

### Agent Commands
- `python scripts/run_agents.py --list` - List available agents
- `python scripts/run_agents.py --agent [name]` - Run specific agent
- `python scripts/run_agents.py` - Run all agents

## Integration System Commands

### Main Integration Commands
- `python integration.py status` - Get comprehensive system status
- `python integration.py setup-demo` - Set up demo environment (may have issues with EthicalPrinciple serialization)
- `python integration.py run-workflow` - Run complete integrated workflow
- `python integration.py validate` - Validate system integrity
- `python integration.py agents list` - List agents
- `python integration.py policies list` - List policies
- `python integration.py ceilings list` - List ceiling configurations

### Makefile Commands
- `make status` - Show system status (uses integration.py)
- `make test` - Run all tests with coverage (~5 seconds, timeout 60 seconds)
- `make lint` - Run linting checks (<1 second)
- `make format` - Format code with Black (~3 seconds)
- `make clean` - Clean up generated files
- `make install` - Install dependencies (~65 seconds, timeout 120 seconds)
- `make demo` - Run demo workflow
- `make all-checks` - Run format, lint, security, and test

## GitHub Actions Workflows

### CI Workflow (.github/workflows/ci.yml)
- **Triggers**: Push to main, Pull requests
- **Tests**: Multi-version Python testing (3.8-3.11), linting, formatting, icon generation
- **Duration**: ~2-3 minutes total
- **Artifacts**: Saves generated icons for 7 days

### CD Workflow (.github/workflows/cd.yml)  
- **Triggers**: Push to main, Manual dispatch
- **Actions**: Generates icons, commits assets, creates releases, deploys to GitHub Pages
- **Duration**: ~3-5 minutes total

### Key Workflow Commands
- Icon generation validation: `python scripts/generate_icons.py`
- Directory validation: `test -d assets/icons/light && test -d assets/icons/dark`
- File count validation: `find assets/icons -name "*.svg" | wc -l | grep -q "10"`

## Common Tasks

### Adding New Icon Variants
1. Edit `strategy_icon_variant_matrix.csv` to add new rows
2. Run `python scripts/generate_icons.py` to generate new icons
3. Verify output with validation commands above
4. Run core test suite: `pytest tests/test_generate_icons.py -v`
5. Format code: `black scripts/ tests/` (if needed)
6. Commit changes

### Working with AI Agents
1. List available agents: `python scripts/run_agents.py --list`
2. Test agent functionality: `python scripts/run_agents.py --agent asset_manager`
3. Check system integration: `python integration.py status`
4. Test agent changes: `pytest tests/test_asset_manager.py -v` (if tests work)

### Modifying Color System
1. Edit color tokens or finish mappings in `scripts/generate_icons.py`
2. Run generation and tests to verify changes work: `python scripts/generate_icons.py && pytest tests/test_generate_icons.py -v`
3. Check that existing tests still pass or update test expectations
4. Ensure code formatting with `black scripts/ tests/`

### Testing Icon Generation Functions
All core functions have unit tests in `tests/test_generate_icons.py`:
- `test_pick_master_*`: Verifies correct master SVG selection
- `test_bake_svg_*`: Verifies color replacement logic  
- `test_*_defined`: Verifies color configuration completeness

## Dependencies and Requirements

### Core Dependencies
- **cairosvg >= 2.8.2**: Required for PNG export functionality
- **scikit-learn**: Machine learning functionality (install separately)
- **croniter**: Scheduling functionality (install separately)  
- **torch**: Deep learning functionality (install separately)
- **pytest >= 8.4.1**: Unit testing framework
- **flake8 >= 7.3.0**: Python linting 
- **black >= 25.1.0**: Code formatting

### Python Version Support
- Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12
- Primary development on Python 3.12

### System Requirements
- Linux/macOS/Windows compatible
- No special system dependencies beyond Python packages
- Cairo graphics library (installed automatically with cairosvg)

## Common Issues and Workarounds

### Dependency Issues
- **Missing sklearn**: Use `pip install scikit-learn` not `pip install sklearn`
- **Missing croniter/torch**: Install with `pip install croniter torch`
- **Requirements.txt conflicts**: Clean up merge conflict markers manually

### Test Issues
- **Some tests fail**: This is expected due to API changes. Focus on core functionality tests like `test_generate_icons.py`
- **Import errors**: Ensure all dependencies are installed including ML libraries
- **Conftest syntax errors**: Check for extra closing braces or merge conflicts

### Formatting Issues  
- **Black check failures**: Run `black scripts/ tests/` to auto-format code
- **Many files need formatting**: This is expected, the codebase needs formatting cleanup
- **Line length issues**: Black handles this automatically

### Integration System Issues
- **Demo setup fails**: Known issue with EthicalPrinciple serialization, but core system works
- **Agent import errors**: Ensure all ML dependencies are installed

## Quick Reference Commands

```bash
# Full validation workflow
pip install -r requirements.txt && pip install scikit-learn croniter torch && python scripts/generate_icons.py && pytest tests/test_generate_icons.py -v && flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics && black --check scripts/ tests/

# Generate icons only  
python scripts/generate_icons.py

# Run core tests only
pytest tests/test_generate_icons.py -v

# Format code
black scripts/ tests/

# Check system status
python integration.py status

# List AI agents
python scripts/run_agents.py --list

# Run specific agent
python scripts/run_agents.py --agent asset_manager

# Clean regeneration
rm -rf assets/icons/* && python scripts/generate_icons.py

# Use Makefile shortcuts
make status  # System status
make test    # Run tests  
make format  # Format code
make lint    # Run linting
```

## Critical Timing Information

**NEVER CANCEL COMMANDS** - Wait for completion:
- Dependency installation: 65-90 seconds (timeout: 120+ seconds)
- Full test suite: 2-5 seconds for core tests (timeout: 60 seconds) 
- Icon generation: <1 second (timeout: 10 seconds)
- System status: 1-2 seconds (timeout: 30 seconds)
- Code formatting: 3 seconds (timeout: 30 seconds)
- ML library installation (torch): 90+ seconds (timeout: 180+ seconds)

Always set appropriate timeouts and wait for commands to complete. Build times are generally fast but dependency installation can be slow.