# StrategyDECK

A comprehensive icon generation system for the StrategyDECK brand, featuring automated CI/CD workflows and asset management.

## 🚀 Features

- **Icon Generation**: Automated SVG/PNG icon generation with multiple variants
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
```

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
│   └── generate_icons.py   # Main generation script
├── tests/
│   └── test_generate_icons.py
├── docs/
│   └── api/                # Auto-generated docs
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