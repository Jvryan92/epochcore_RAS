# StrategyDECK Icon Generation System

StrategyDECK is a Python-based icon generation system that creates multiple variants of StrategyDECK brand icons in different modes, finishes, sizes, and contexts. The system generates both SVG and PNG formats automatically.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt` -- completes in ~10 seconds
- Verify installation by generating icons: `python scripts/generate_icons.py` -- completes in < 1 second

### Build and Test Workflow
- **Icon generation**: `python scripts/generate_icons.py` -- generates 10 SVG + 10 PNG files in < 1 second
- **Unit tests**: `pytest tests/ -v` -- runs 6 tests in < 1 second  
- **Linting**: `flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics` -- < 1 second
- **Style check**: `flake8 scripts/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics` -- < 1 second
- **Format check**: `black --check scripts/ tests/` -- < 1 second
- **Apply formatting**: `black scripts/ tests/` -- < 1 second (REQUIRED if format check fails)

### Complete Validation Sequence
Always run this sequence before committing changes:
```bash
pip install -r requirements.txt
python scripts/generate_icons.py
pytest tests/ -v
flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 scripts/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
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
   - Check `assets/icons/light/flat-orange/16px/web/` contains both SVG and PNG
   - Check `assets/icons/dark/copper-foil/32px/web/` contains expected variants
   - Verify file sizes are reasonable (SVG ~200 bytes, PNG varies by size)

## Key Project Structure

```
StrategyDECK/
├── .github/
│   ├── workflows/          # GitHub Actions (ci.yml, cd.yml, etc.)
│   └── issue-labeler.yml   # Issue labeling rules
├── assets/
│   ├── masters/            # Master SVG files (strategy_icon_micro.svg, strategy_icon_standard.svg)
│   └── icons/              # Generated variants (created by script)
├── scripts/
│   └── generate_icons.py   # Main generation script
├── tests/
│   └── test_generate_icons.py  # Unit tests (6 test cases)
├── docs/
│   └── api/                # Auto-generated docs
├── strategy_icon_variant_matrix.csv  # Configuration matrix (10 variants)
└── requirements.txt        # Python dependencies (cairosvg, pytest, flake8, black)
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

### Other Workflows
- `issue-management.yml`: Auto-labels and assigns issues
- `pr-management.yml`: Auto-assigns reviewers, labels PR size  
- `docs.yml`: Auto-generates documentation

## Common Tasks

### Adding New Icon Variants
1. Edit `strategy_icon_variant_matrix.csv` to add new rows
2. Run `python scripts/generate_icons.py` to generate new icons
3. Verify output with validation commands above
4. Run full test suite: `pytest tests/ -v`
5. Format code: `black scripts/ tests/` (if needed)
6. Commit changes

### Modifying Color System
1. Edit color tokens or finish mappings in `scripts/generate_icons.py`
2. Run generation and tests to verify changes work
3. Check that existing tests still pass or update test expectations
4. Ensure code formatting with `black scripts/ tests/`

### Testing Icon Generation Functions
All core functions have unit tests in `tests/test_generate_icons.py`:
- `test_pick_master_*`: Verifies correct master SVG selection
- `test_bake_svg_*`: Verifies color replacement logic  
- `test_*_defined`: Verifies color configuration completeness

## Dependencies and Requirements

### Core Dependencies
- **cairosvg >= 2.5.2**: Required for PNG export functionality
- **pytest >= 7.0.0**: Unit testing framework
- **flake8 >= 5.0.0**: Python linting 
- **black >= 22.0.0**: Code formatting

### Python Version Support
- Tested on Python 3.8, 3.9, 3.10, 3.11
- Primary development on Python 3.11

### System Requirements
- Linux/macOS/Windows compatible
- No special system dependencies beyond Python packages
- Cairo graphics library (installed automatically with cairosvg)

## Troubleshooting

### Icon Generation Issues
- **Missing CSV error**: Ensure `strategy_icon_variant_matrix.csv` exists in repo root
- **Missing master SVG**: Check `assets/masters/` contains both micro and standard SVG files
- **PNG export failures**: Verify cairosvg is properly installed, SVGs will still generate

### Test Failures
- **Import errors**: Run `pip install -r requirements.txt` to ensure dependencies
- **Path issues**: Tests assume script is run from repository root directory
- **Color test failures**: Check that color token definitions match test expectations

### Formatting Issues  
- **Black check failures**: Run `black scripts/ tests/` to auto-format code
- **Line length**: Black enforces automatic line wrapping, no manual adjustment needed
- **Import sorting**: Black handles import organization automatically

### CI/CD Issues
- **Workflow permissions**: GitHub Actions needs write permissions for assets and pages
- **Secret access**: Only GITHUB_TOKEN is required (automatically provided)
- **Artifact upload**: Generated icons are saved as workflow artifacts for debugging

## Quick Reference Commands

```bash
# Full validation workflow
pip install -r requirements.txt && python scripts/generate_icons.py && pytest tests/ -v && flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics && black --check scripts/ tests/

# Generate icons only  
python scripts/generate_icons.py

# Run tests only
pytest tests/ -v

# Format code
black scripts/ tests/

# Clean regeneration
rm -rf assets/icons/* && python scripts/generate_icons.py
```