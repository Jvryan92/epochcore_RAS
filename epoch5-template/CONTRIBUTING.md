# Contributing to Epoch5 Template

Thank you for your interest in contributing to Epoch5 Template! We appreciate your help in improving this project. Please follow the guidelines below to ensure a smooth contribution process.

## Development Setup

Before contributing, please set up your development environment:

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/EpochCore5/epoch5-template.git
   cd epoch5-template
   pip install -r requirements.txt
   ```

2. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run tests to ensure everything works**
   ```bash
   pytest --cov=. --cov-report=html
   ```

For detailed setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributor Guidelines

1. **Fork the repository**: Create your own fork of the repository to make changes.
2. **Create a branch**: Always create a new branch for your feature or bug fix.
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Write tests**: Ensure your contributions are covered by tests.
4. **Follow code style**: Run formatting and linting before committing.
   ```bash
   black .
   flake8 .
   ```
5. **Commit your changes**: Write clear and concise commit messages describing your changes.
6. **Submit a pull request**: Once your changes are ready, submit a pull request to the main repository for review.

## Code Standards

- We follow **PEP8** standards for Python code. Please ensure your code adheres to these conventions.
- Use **Black** for automatic code formatting with 88-character line limit.
- Use **Flake8** for linting your code.
- Add **type hints** where appropriate to improve code clarity.
- Write clear **docstrings** for all public functions and classes.

## Test Requirements

- Ensure that your contributions are covered by tests.
- Aim for **>80% test coverage** on new code.
- Run the full test suite before submitting:
  ```bash
  pytest --cov=. --cov-report=html
  ```
- Write both positive and negative test cases.
- Use fixtures for test data setup (see `tests/conftest.py`).

## Security Guidelines

- Never commit secrets, credentials, or sensitive data.
- Use the `secrets` module instead of `random` for cryptographic purposes.
- Validate all user inputs and handle edge cases.
- Run security scans before submitting:
  ```bash
  bandit -r . --skip B101
  ```

## Pull Request Process

1. **Update documentation** if you're changing functionality.
2. **Add tests** for new features or bug fixes.
3. **Ensure all checks pass**:
   - All tests pass
   - Code formatting is correct
   - No linting errors
   - Security scans are clean
4. **Write a clear PR description** explaining what changes you made and why.
5. **Link any related issues** in your PR description.

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