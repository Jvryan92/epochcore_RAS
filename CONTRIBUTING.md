"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

# Contributing to StrategyDECK

Thank you for considering contributing to StrategyDECK! We appreciate your help in making this project better.

## Development Setup

Before contributing, please set up your development environment:

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/yourusername/StategyDECK.git
   cd StategyDECK
   pip install -r requirements.txt
   ```

2. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run tests to ensure everything works**
   ```bash
   pytest tests/ -v --cov=. --cov-report=html
   ```

## Contributor Guidelines

1. **Communication and Conduct**
   - Be respectful and considerate in your interactions
   - Be open to feedback and engage in constructive discussions
   - Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

2. **Development Process**
   - **Fork the repository**: Create your own fork to make changes
   - **Create a branch**: Always create a new branch for your feature or bug fix:
     ```bash
     git checkout -b feature/your-feature-name
     ```
   - **Write tests**: Ensure your contributions are covered by tests
   - **Follow code style**: Run formatting and linting before committing:
     ```bash
     black scripts/ tests/
     flake8 scripts/
     ```
   - **Commit changes**: Write clear and concise commit messages
   - **Submit PR**: Submit a pull request with detailed description

## Code Standards

- Follow **PEP8** standards for Python code
- Use **Black** for automatic code formatting (88-character line limit)
- Use **Flake8** for linting
- Add **type hints** where appropriate
- Write clear **docstrings** for public functions and classes
- Use meaningful variable and function names
- Keep code clean and well-organized

## Test Requirements

- Ensure **>80% test coverage** for new code
- Write both positive and negative test cases
- Use fixtures for test data setup (see `tests/conftest.py`)
- Run the full test suite before submitting:
  ```bash
  pytest tests/ -v --cov=. --cov-report=html
  ```

## Security Guidelines

- Never commit secrets, credentials, or sensitive data
- Use `secrets` module instead of `random` for cryptography
- Validate all user inputs and handle edge cases
- Run security scans before submitting:
  ```bash
  bandit -r scripts/ tests/
  ```

## Pull Request Process

1. **Before Creating**
   - Search existing issues/PRs to avoid duplicates
   - Ensure code passes all tests and checks
   - Update documentation if needed
   
2. **Pull Request Content**
   - Clearly describe changes and motivation
   - Reference any related issues
   - Include test coverage information
   - List any breaking changes
   
3. **Review Process**
   - Address reviewer feedback promptly
   - Keep discussions focused and technical
   - Be willing to make requested changes

## Security Vulnerabilities

If you discover a security vulnerability:

1. DO NOT file a public issue
2. Email security@strategyDECK.com with:
   - Vulnerability description
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

## Recognition

Contributors who make significant improvements will be recognized in:
- The project's README
- Release notes
- Contributors list

Thank you for contributing to StrategyDECK! Together, we can make this project even better!

## Reporting Issues

When reporting bugs or requesting features, please:

1. **Use the appropriate issue template**
2. **Provide detailed information**:
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (Python version, OS)
   - Error logs or stack traces
3. **Search existing issues** to avoid duplicates

## Security Vulnerabilities

If you discover a security vulnerability, please DO NOT file a public issue. Instead, email the maintainer directly at jryan2k19@gmail.com with:

- A description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Any suggested fixes

## Respectful Communication

- Be respectful and constructive in your comments and discussions.
- We welcome diverse perspectives and experiences, and we value inclusivity in our community.
- If you disagree with a suggestion or critique, please respond with respect and an open mind.
- Focus on the code and technical aspects, not personal attributes.

## Recognition

Contributors who make significant improvements to the project will be recognized in:
- The project's README
- Release notes
- Special recognition in the repository

Thank you for contributing to the Epoch5 Template! Together, we can make this project even better!
>>>>>>> epoch5/main
