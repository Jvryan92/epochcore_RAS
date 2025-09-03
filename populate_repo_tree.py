#!/usr/bin/env python3
"""
Repository Population Script
EpochCore RAS Repository Automation

Intelligently generates missing repository files and directory structures
with template-based content generation and validation.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging


class RepositoryPopulator:
    """Manages repository file structure population and validation."""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.backup_dir = self.repo_root / "backups" / "repo_structure"
        self.config_dir = self.repo_root / "config"
        self.templates_dir = self.repo_root / "templates"
        
        # Ensure directories exist
        for path in [self.backup_dir, self.config_dir, self.templates_dir]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Expected repository structure
        self.expected_structure = self.define_expected_structure()
        
        # File templates
        self.templates = self.define_file_templates()
    
    def define_expected_structure(self) -> Dict[str, Any]:
        """Define the expected repository structure."""
        return {
            "directories": [
                "config",
                "data",
                "logs",
                "backups",
                "backups/agent_registry",
                "backups/repo_structure",
                "backups/snapshots",
                "templates",
                "docs",
                "docs/api",
                "docs/guides",
                "scripts",
                "scripts/deployment",
                "scripts/maintenance",
                "automation",
                "automation/workflows",
                "tests/unit",
                "tests/integration",
                "tests/performance"
            ],
            "files": {
                # Configuration files
                "config/agent_registry.yaml": "agent_config",
                "config/continuity_ritual.yaml": "continuity_config",
                "config/vault_settings.yaml": "vault_config",
                "config/merge_automation.yaml": "merge_config",
                "config/system_settings.yaml": "system_config",
                
                # Documentation files
                "docs/API.md": "api_docs",
                "docs/DEPLOYMENT.md": "deployment_docs",
                "docs/ARCHITECTURE.md": "architecture_docs",
                "docs/CONTRIBUTING.md": "contributing_docs",
                "docs/CHANGELOG.md": "changelog",
                "docs/guides/quick_start.md": "quick_start_guide",
                "docs/guides/developer_guide.md": "developer_guide",
                "docs/guides/troubleshooting.md": "troubleshooting_guide",
                
                # Script files
                "scripts/setup.sh": "setup_script",
                "scripts/deploy.sh": "deploy_script",
                "scripts/backup.sh": "backup_script",
                "scripts/health_check.sh": "health_check_script",
                "scripts/deployment/docker_build.sh": "docker_build_script",
                "scripts/deployment/kubernetes_deploy.sh": "k8s_deploy_script",
                "scripts/maintenance/log_rotation.sh": "log_rotation_script",
                "scripts/maintenance/cleanup.sh": "cleanup_script",
                
                # Automation files
                "automation/repo_monitor.py": "repo_monitor",
                "automation/performance_tracker.py": "performance_tracker",
                "automation/security_scanner.py": "security_scanner",
                
                # Template files
                "templates/engine_template.py": "engine_template",
                "templates/workflow_template.yml": "workflow_template",
                "templates/test_template.py": "test_template",
                
                # Data structure files
                "data/system_metrics.json": "metrics_data",
                "data/performance_baseline.json": "performance_data",
                
                # Configuration files
                ".gitignore": "gitignore",
                ".env.example": "env_example",
                "pyproject.toml": "pyproject",
                "setup.cfg": "setup_config",
                "MANIFEST.in": "manifest",
                
                # Test configuration
                "pytest.ini": "pytest_config",
                "tox.ini": "tox_config",
                
                # Security and compliance
                ".github/CODEOWNERS": "codeowners",
                ".github/SECURITY.md": "security_policy"
            }
        }
    
    def define_file_templates(self) -> Dict[str, str]:
        """Define templates for different file types."""
        return {
            "agent_config": """# Agent Registry Configuration
# EpochCore RAS Agent Management

registry:
  auto_discovery: true
  health_monitoring: true
  backup_enabled: true
  retention_days: 30

agents:
  recursive_engines:
    count: 15
    health_check_interval: 300  # 5 minutes
    
monitoring:
  enabled: true
  log_level: INFO
  metrics_collection: true
  
backup:
  enabled: true
  schedule: "0 */6 * * *"  # Every 6 hours
  retention: 30
""",
            
            "continuity_config": """# Continuity Ritual Configuration
# EpochCore RAS Maintenance Automation

rituals:
  daily:
    enabled: true
    schedule: "0 2 * * *"  # 2:00 AM daily
    tasks:
      - system_health_check
      - log_rotation
      - temp_cleanup
      - metrics_collection
      
  weekly:
    enabled: true
    schedule: "0 3 * * 1"  # 3:00 AM Monday
    tasks:
      - full_backup
      - dependency_update_check
      - performance_analysis
      - security_scan
      
  monthly:
    enabled: true
    schedule: "0 4 1 * *"  # 4:00 AM 1st of month
    tasks:
      - archive_old_logs
      - cleanup_old_backups
      - system_optimization
      - comprehensive_audit

monitoring:
  resource_thresholds:
    cpu_percent: 80
    memory_percent: 85
    disk_percent: 90
    
notifications:
  enabled: true
  channels:
    - log
    - file
""",
            
            "vault_config": """# Zip Vault Configuration
# EpochCore RAS Snapshot System

profiles:
  full_system:
    description: "Complete system snapshot"
    include:
      - "**/*.py"
      - "**/*.yaml"
      - "**/*.yml" 
      - "**/*.json"
      - "**/*.md"
      - "config/**"
      - "data/**"
      - "docs/**"
    exclude:
      - "**/__pycache__/**"
      - "**/node_modules/**"
      - "**/.git/**"
      - "**/venv/**"
      - "logs/**"
      
  code_only:
    description: "Code and configuration only"
    include:
      - "**/*.py"
      - "**/*.yaml"
      - "**/*.yml"
      - "config/**"
    exclude:
      - "**/__pycache__/**"
      - "logs/**"
      - "backups/**"
      
  config_only:
    description: "Configuration files only"
    include:
      - "config/**"
      - "*.yaml"
      - "*.yml"
      - "requirements.txt"
      - "pyproject.toml"

vault:
  compression_level: 6
  integrity_check: true
  encryption: false  # Enable if needed
  retention_days: 90
  
schedule:
  full_system: "0 1 * * *"  # Daily at 1:00 AM
  code_only: "0 */6 * * *"  # Every 6 hours
  config_only: "0 */3 * * *"  # Every 3 hours
""",
            
            "merge_config": """# Merge Automation Configuration
# EpochCore RAS Automated Merge System

merge_strategies:
  auto_merge:
    enabled: true
    conditions:
      - all_checks_passed
      - no_conflicts
      - approved_by_maintainer
      
  conflict_resolution:
    strategy: "auto"  # auto, manual, skip
    prefer: "incoming"  # incoming, current, manual
    
quality_gates:
  pre_merge:
    - lint_check
    - test_suite
    - security_scan
    - integration_test
    
  post_merge:
    - deployment_test
    - smoke_test
    - rollback_validation
    
notifications:
  success: true
  failure: true
  conflict: true
  
rollback:
  enabled: true
  triggers:
    - test_failure
    - deployment_failure
    - critical_error
    
  strategy: "backup_restore"  # backup_restore, git_revert
""",
            
            "system_config": """# System Settings
# EpochCore RAS Core Configuration

system:
  name: "EpochCore RAS"
  version: "1.0.0"
  environment: "production"
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/system.log"
  rotation:
    max_size: "10MB"
    backup_count: 5
    
performance:
  monitoring: true
  metrics_collection: true
  profiling: false
  
security:
  audit_logging: true
  input_validation: true
  rate_limiting: true
  
integration:
  recursive_improvement: true
  agent_registry: true
  automation: true
""",
            
            "api_docs": """# EpochCore RAS API Documentation

## Overview
The EpochCore RAS provides a comprehensive API for managing recursive autonomous software systems.

## Endpoints

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents/sync` - Synchronize agent registry
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}/health` - Update agent health status

### System Operations
- `GET /api/system/status` - Get system status
- `POST /api/system/validate` - Validate system integrity
- `POST /api/system/backup` - Create system backup

### Recursive Improvement
- `GET /api/recursive/status` - Get recursive improvement status
- `POST /api/recursive/trigger` - Trigger recursive improvements
- `GET /api/recursive/engines` - List all engines

## Authentication
All API endpoints require authentication via API key or OAuth token.

## Rate Limiting
API calls are limited to 1000 requests per hour per authenticated user.
""",
            
            "deployment_docs": """# Deployment Guide

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
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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
""",
            
            "architecture_docs": """# Architecture Documentation

## System Overview
EpochCore RAS is a recursive autonomous software system designed for continuous improvement and automation.

## Core Components

### 1. Recursive Improvement Framework
- 15 autonomous engines
- Compounding logic execution
- Real-time monitoring and adaptation

### 2. Agent Management System
- Dynamic agent discovery
- Health monitoring
- Registry synchronization

### 3. Automation Layer
- Repository population
- Continuous maintenance rituals
- Snapshot and backup management

### 4. Integration Layer
- GitHub Actions workflows
- CI/CD pipeline integration
- External service connectors

## Data Flow
1. System initialization
2. Agent discovery and registration
3. Continuous monitoring and improvement
4. Automated maintenance and backups
5. Reporting and validation

## Security Considerations
- Input validation at all entry points
- Secure credential management
- Audit logging for all operations
- Rate limiting and access control
""",
            
            "contributing_docs": """# Contributing to EpochCore RAS

## Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages

## Code Review Process
All contributions go through automated and manual review:
- Automated testing and linting
- Security scanning
- Manual code review by maintainers

## Recursive Improvement
The system will automatically learn from your contributions and improve itself over time.
""",
            
            "changelog": """# Changelog

## [1.0.0] - 2025-09-03

### Added
- Initial release of EpochCore RAS
- 15 recursive improvement engines
- Agent registry synchronization
- Repository automation system
- Comprehensive documentation

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- Implemented secure authentication
- Added input validation
- Enabled audit logging
""",
            
            "quick_start_guide": """# Quick Start Guide

Get up and running with EpochCore RAS in minutes.

## 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Initialize System
```bash
python integration.py setup-demo
python integration.py init-recursive
```

## 3. Verify Installation
```bash
python integration.py status
python integration.py validate
```

## 4. Start Dashboard
```bash
python dashboard.py 8000
```

Visit http://localhost:8000 to see the system dashboard.

## Next Steps
- Read the Developer Guide
- Explore the API documentation
- Configure system settings
""",
            
            "developer_guide": """# Developer Guide

## Architecture Overview
EpochCore RAS uses a modular architecture with recursive improvement capabilities.

## Adding New Engines
1. Inherit from RecursiveEngine base class
2. Implement required methods
3. Register with orchestrator
4. Add tests

## Configuration Management
All configuration is stored in YAML files in the `config/` directory.

## Testing
Run tests with:
```bash
python -m unittest discover tests/
pytest --cov=.
```

## Debugging
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python integration.py status
```

## Performance Optimization
- Monitor resource usage
- Profile code execution
- Optimize recursive algorithms
- Use caching where appropriate
""",
            
            "troubleshooting_guide": """# Troubleshooting Guide

## Common Issues

### System Won't Start
1. Check Python version (3.12+ required)
2. Verify all dependencies installed
3. Check configuration files
4. Review log files

### Agents Not Registering
1. Verify orchestrator initialization
2. Check agent registry permissions
3. Review agent discovery logs
4. Validate system resources

### Performance Issues
1. Monitor resource usage
2. Check for memory leaks
3. Optimize recursive algorithms
4. Review system logs

### Backup Failures
1. Check disk space
2. Verify backup directory permissions
3. Review backup configuration
4. Check system resources

## Getting Help
- Check log files first
- Review documentation
- Search existing issues
- Create detailed bug reports
""",
            
            "gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/*.log
*.log

# Temporary files
tmp/
temp/
.tmp/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backups and snapshots
backups/
*.bak
*.backup

# Data files
data/*.json
data/*.yaml
!data/*.example.*

# Security
.env
*.key
*.pem
secrets/
""",
            
            "env_example": """# Environment Variables Example
# Copy to .env and update values

# System Configuration
EPOCHCORE_ENV=development
EPOCHCORE_DEBUG=false
LOG_LEVEL=INFO

# Database Configuration (if needed)
DATABASE_URL=sqlite:///data/epochcore.db

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
API_SECRET_KEY=your-secret-key-here

# External Services
GITHUB_TOKEN=your-github-token
NOTIFICATION_WEBHOOK=your-webhook-url

# Resource Limits
MAX_MEMORY_MB=1024
MAX_CPU_PERCENT=80

# Backup Configuration  
BACKUP_RETENTION_DAYS=30
BACKUP_STORAGE_PATH=backups/
""",
            
            "pyproject": """[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "epochcore-ras"
version = "1.0.0"
description = "EpochCore Recursive Autonomous Software System"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "EpochCore Team", email = "team@epochcore.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0.2",
    "psutil>=5.9.5",
    "rich>=13.0.0",
    "schedule>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "flake8>=6.0.0",
    "black>=23.0.0",
]

[project.urls]
Homepage = "https://github.com/epochcore/ras"
Repository = "https://github.com/epochcore/ras.git"
Documentation = "https://epochcore.github.io/ras/"

[tool.setuptools]
packages = ["recursive_improvement", "recursive_improvement.engines"]

[tool.black]
line-length = 88
target-version = ['py312']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--cov=recursive_improvement --cov-report=term-missing"
""",
            
            "setup_script": """#!/bin/bash
# EpochCore RAS Setup Script

set -e

echo "Setting up EpochCore RAS..."

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.12"

if [ "$(printf '%s\\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize system
echo "Initializing EpochCore RAS..."
python integration.py setup-demo
python integration.py init-recursive

# Run validation
echo "Validating installation..."
python integration.py validate

# Run agent sync
echo "Synchronizing agent registry..."
python agent_register_sync.py --sync

echo "Setup complete! Run 'source venv/bin/activate' to activate the environment."
echo "Then run 'python dashboard.py 8000' to start the dashboard."
""",
            
            "repo_monitor": """#!/usr/bin/env python3
\"\"\"
Repository Monitor
EpochCore RAS Automation

Monitors repository health and triggers automated maintenance.
\"\"\"

import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

class RepoMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def monitor_health(self):
        \"\"\"Monitor repository health.\"\"\"
        # Implementation placeholder
        pass
        
    def check_disk_space(self):
        \"\"\"Check available disk space.\"\"\"
        # Implementation placeholder
        pass
        
    def monitor_performance(self):
        \"\"\"Monitor system performance.\"\"\"
        # Implementation placeholder
        pass

if __name__ == "__main__":
    monitor = RepoMonitor()
    monitor.monitor_health()
""",
            
            "engine_template": """#!/usr/bin/env python3
\"\"\"
Engine Template
Template for creating new recursive improvement engines
\"\"\"

from datetime import datetime
from typing import Dict, Any
from ..base import RecursiveEngine, CompoundingAction

class TemplateEngine(RecursiveEngine):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("template_engine", config)
        # Initialize engine-specific data
        
    def execute_main_action(self) -> Dict[str, Any]:
        \"\"\"Execute the main engine action.\"\"\"
        return {"status": "completed", "timestamp": datetime.now().isoformat()}
        
    def execute_pre_action(self) -> Dict[str, Any]:
        \"\"\"Execute pre-action at +0.25 interval.\"\"\"
        return {"status": "pre_completed", "timestamp": datetime.now().isoformat()}
""",
        }
    
    def scan_existing_structure(self) -> Dict[str, Any]:
        """Scan current repository structure."""
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "existing_directories": [],
            "existing_files": [],
            "missing_directories": [],
            "missing_files": [],
            "unexpected_items": []
        }
        
        # Scan directories
        for expected_dir in self.expected_structure["directories"]:
            dir_path = self.repo_root / expected_dir
            if dir_path.exists():
                scan_result["existing_directories"].append(expected_dir)
            else:
                scan_result["missing_directories"].append(expected_dir)
        
        # Scan files
        for expected_file in self.expected_structure["files"]:
            file_path = self.repo_root / expected_file
            if file_path.exists():
                scan_result["existing_files"].append(expected_file)
            else:
                scan_result["missing_files"].append(expected_file)
        
        return scan_result
    
    def create_backup(self) -> str:
        """Create backup of current structure."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"structure_backup_{timestamp}.json"
        
        # Scan current structure
        current_structure = self.scan_existing_structure()
        
        # Save backup
        try:
            with open(backup_file, 'w') as f:
                json.dump(current_structure, f, indent=2)
            
            self.logger.info(f"Created structure backup: {backup_file}")
            return str(backup_file)
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return ""
    
    def populate_missing_directories(self, missing_dirs: List[str]) -> int:
        """Create missing directories."""
        created_count = 0
        
        for dir_path in missing_dirs:
            full_path = self.repo_root / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {dir_path}")
                created_count += 1
            except Exception as e:
                self.logger.error(f"Failed to create directory {dir_path}: {e}")
        
        return created_count
    
    def populate_missing_files(self, missing_files: List[str]) -> int:
        """Create missing files using templates."""
        created_count = 0
        
        for file_path in missing_files:
            full_path = self.repo_root / file_path
            template_key = self.expected_structure["files"][file_path]
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate file content
            content = self.generate_file_content(file_path, template_key)
            
            try:
                with open(full_path, 'w') as f:
                    f.write(content)
                self.logger.info(f"Created file: {file_path}")
                created_count += 1
            except Exception as e:
                self.logger.error(f"Failed to create file {file_path}: {e}")
        
        return created_count
    
    def generate_file_content(self, file_path: str, template_key: str) -> str:
        """Generate content for a file based on its template."""
        if template_key in self.templates:
            return self.templates[template_key]
        
        # Fallback content based on file type
        file_suffix = Path(file_path).suffix.lower()
        
        if file_suffix == '.md':
            return f"# {Path(file_path).stem.replace('_', ' ').title()}\n\nDocumentation for {file_path}\n"
        elif file_suffix == '.py':
            return f'#!/usr/bin/env python3\n"""\n{Path(file_path).stem}\n"""\n\n# Implementation placeholder\n'
        elif file_suffix == '.sh':
            return f'#!/bin/bash\n# {Path(file_path).stem}\n\necho "Script placeholder"\n'
        elif file_suffix in ['.yaml', '.yml']:
            return f'# {Path(file_path).stem} configuration\nversion: "1.0"\n'
        elif file_suffix == '.json':
            return '{\n  "placeholder": true\n}\n'
        else:
            return f"# {Path(file_path).name}\n# Auto-generated placeholder file\n"
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate repository structure."""
        scan = self.scan_existing_structure()
        
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "is_complete": len(scan["missing_directories"]) == 0 and len(scan["missing_files"]) == 0,
            "health_score": 0.0,
            "statistics": {
                "total_expected_dirs": len(self.expected_structure["directories"]),
                "total_expected_files": len(self.expected_structure["files"]),
                "existing_dirs": len(scan["existing_directories"]),
                "existing_files": len(scan["existing_files"]),
                "missing_dirs": len(scan["missing_directories"]),
                "missing_files": len(scan["missing_files"])
            }
        }
        
        # Calculate health score
        total_expected = len(self.expected_structure["directories"]) + len(self.expected_structure["files"])
        total_existing = len(scan["existing_directories"]) + len(scan["existing_files"])
        
        if total_expected > 0:
            validation_result["health_score"] = total_existing / total_expected
        
        return validation_result
    
    def full_population(self) -> Dict[str, Any]:
        """Perform complete repository population."""
        population_result = {
            "timestamp": datetime.now().isoformat(),
            "phase": "starting",
            "success": False,
            "backup_created": False,
            "directories_created": 0,
            "files_created": 0,
            "structure_complete": False
        }
        
        try:
            # Phase 1: Create backup
            population_result["phase"] = "backup"
            backup_file = self.create_backup()
            population_result["backup_created"] = bool(backup_file)
            
            # Phase 2: Scan structure
            population_result["phase"] = "scanning"
            scan = self.scan_existing_structure()
            
            # Phase 3: Create missing directories
            population_result["phase"] = "creating_directories"
            dirs_created = self.populate_missing_directories(scan["missing_directories"])
            population_result["directories_created"] = dirs_created
            
            # Phase 4: Create missing files
            population_result["phase"] = "creating_files"
            files_created = self.populate_missing_files(scan["missing_files"])
            population_result["files_created"] = files_created
            
            # Phase 5: Validate
            population_result["phase"] = "validating"
            validation = self.validate_structure()
            population_result["structure_complete"] = validation["is_complete"]
            
            population_result["phase"] = "complete"
            population_result["success"] = validation["is_complete"]
            
        except Exception as e:
            population_result["error"] = str(e)
            self.logger.error(f"Population failed: {e}")
        
        return population_result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current population status."""
        validation = self.validate_structure()
        
        return {
            "repository_health": "healthy" if validation["health_score"] >= 0.9 else 
                               "warning" if validation["health_score"] >= 0.7 else "critical",
            "structure_complete": validation["is_complete"],
            "completion_percentage": validation["health_score"] * 100,
            "missing_items": validation["statistics"]["missing_dirs"] + validation["statistics"]["missing_files"],
            "backup_available": len(list(self.backup_dir.glob("*.json"))) > 0 if self.backup_dir.exists() else False
        }


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Repository Structure Population")
    parser.add_argument('--populate', action='store_true', help='Populate missing structure')
    parser.add_argument('--validate', action='store_true', help='Validate structure only')
    parser.add_argument('--status', action='store_true', help='Get population status')
    parser.add_argument('--scan', action='store_true', help='Scan current structure')
    
    args = parser.parse_args()
    
    populator = RepositoryPopulator()
    
    if args.populate:
        result = populator.full_population()
        print(json.dumps(result, indent=2))
    elif args.validate:
        result = populator.validate_structure()
        print(json.dumps(result, indent=2))
    elif args.status:
        result = populator.get_status()
        print(json.dumps(result, indent=2))
    elif args.scan:
        result = populator.scan_existing_structure()
        print(json.dumps(result, indent=2))
    else:
        print("Use --populate, --validate, --status, or --scan")


if __name__ == "__main__":
    main()