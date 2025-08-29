"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)

## Basic Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StategyDECK.git
cd StategyDECK
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development Installation

For development, install additional dependencies:

```bash
pip install -r requirements-dev.txt
```

This includes:
- Testing tools (pytest)
- Linting tools (pylint, flake8)
- Code formatting (black, isort)
- Type checking (mypy)
- Documentation tools (mkdocs)

## Docker Installation

1. Build the Docker image:
```bash
docker build -t strategydeck .
```

2. Run the container:
```bash
docker run -it strategydeck
```

## Verification

Run tests to verify installation:
```bash
pytest
```
