# Deployment Guide

## Prerequisites
- Python 3.12+
- Docker (optional)
- Kubernetes (for production)

## Local Development Setup

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Initialize system

```bash
git clone <repository>
cd epochcore_RAS
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python integration.py setup-demo
```

## Production Deployment

### Docker Deployment
```bash
docker build -t epochcore-ras .
docker run -d -p 8000:8000 epochcore-ras
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

## Configuration
Update configuration files in the `config/` directory before deployment.
