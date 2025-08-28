# Contributing to StrategyDECK

Thank you for considering contributing to StrategyDECK! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following our coding standards:
   - Use Black for code formatting
   - Follow PEP 8 style guidelines
   - Include docstrings and type hints
   - Add tests for new functionality

3. Run tests and checks:
   ```bash
   pytest  # Run tests
   pytest --cov=scripts  # Check coverage
   pre-commit run --all-files  # Run all checks
   ```

4. Update documentation if needed:
   - Add/update docstrings
   - Update relevant .md files
   - Update CHANGELOG.md

5. Submit a pull request:
   - Fill out the PR template completely
   - Link to any related issues
   - Wait for CI checks to pass
   - Request review from maintainers

## Coding Standards

- Use Python 3.8+ features
- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Add type hints to all functions
- Write descriptive docstrings
- Maintain test coverage above 80%

## Testing

- Write unit tests for all new functionality
- Use pytest for testing
- Include both positive and negative test cases
- Mock external dependencies appropriately

## Documentation

- Keep README.md up to date
- Add docstrings to all public functions/classes
- Update CHANGELOG.md for all notable changes
- Use clear commit messages

## Questions or Problems?

- Open an issue for bugs or feature requests
- Join our community discussions
- Contact maintainers directly for security issues

Thank you for contributing!
