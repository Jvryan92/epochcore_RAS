# Cross-Repository Automation - Usage Guide

## Overview

The EpochCore RAS Cross-Repository Automation system provides comprehensive automated fixes and improvements across multiple repositories. This system integrates with the existing recursive autonomy engines to deliver "automate fix all" functionality.

## Features

### 🚀 Automated Fix Types

1. **AI Code Review** - Automated code analysis and security improvements
2. **Auto Refactoring** - Code quality improvements and optimization
3. **Dependency Health** - Security updates and version management
4. **Workflow Auditing** - CI/CD pipeline optimization and security
5. **Documentation Sync** - Automated documentation updates

### 🎯 Target Repositories

- `epochcore_RAS` - Main recursive autonomy system
- `EpochCore_OS` - Operating system components
- `epoch5_template` - Project templates and scaffolding

## Quick Start

### 1. Initialize the System

```bash
# Initialize cross-repository automation
python integration.py init-recursive
python cross_repository_automation.py init
```

### 2. Check System Status

```bash
# Check all monitored repositories
python integration.py cross-repo-status

# Check recursive improvement system
python integration.py recursive-status
```

### 3. Execute Automated Fixes

```bash
# Fix all repositories with all fix types
python integration.py automate-fix-all

# Fix specific repositories and types
python integration.py automate-fix-all --repos epochcore_RAS EpochCore_OS --fix-types code_review refactor

# Create PRs but don't auto-merge
python integration.py automate-fix-all --create-prs --no-auto-merge

# Auto-merge safe fixes (documentation, minor dependencies)
python integration.py automate-fix-all --auto-merge
```

## Advanced Usage

### Command Line Options

```bash
python integration.py automate-fix-all [options]

Options:
  --repos REPO [REPO ...]        Target repositories (default: all)
  --fix-types TYPE [TYPE ...]     Fix types to apply (default: all)
  --create-prs                   Create pull requests (default: true)
  --auto-merge                   Auto-merge safe fixes (default: false)

Fix Types:
  code_review     - AI-powered code analysis and security fixes
  refactor        - Code quality improvements and optimization
  dependencies    - Security updates and dependency management
  workflows       - CI/CD pipeline optimization
  documentation   - Documentation synchronization and updates
```

### Direct Script Usage

```bash
# Use the cross-repository automation script directly
python cross_repository_automation.py automate-fix-all --repos epochcore_RAS --fix-types code_review --create-prs

# Get repository status
python cross_repository_automation.py status

# Initialize system
python cross_repository_automation.py init
```

## GitHub Actions Integration

### Manual Workflow Dispatch

1. Go to GitHub Actions in any monitored repository
2. Select "Cross-Repository Automated Fixes" workflow
3. Configure parameters:
   - **Target Repositories**: `all` or specific repos
   - **Fix Types**: `all` or specific types
   - **Create PRs**: `true/false`
   - **Auto Merge**: `true/false` (for safe fixes only)
   - **Urgency**: `low/medium/high/critical`

### Scheduled Automation

The system runs automatically:
- **Weekly**: Sundays at 3:00 AM UTC with comprehensive fixes
- **Event-driven**: Triggered by repository dispatch events

### Workflow Examples

```bash
# Trigger via GitHub CLI
gh workflow run cross-repository-automation.yml \
  -f target_repositories="epochcore_RAS,EpochCore_OS" \
  -f fix_types="code_review,dependencies" \
  -f create_prs=true \
  -f auto_merge=false \
  -f urgency=high

# Repository dispatch trigger
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/Jvryan92/epochcore_RAS/dispatches \
  -d '{"event_type":"cross-repo-automation","client_payload":{"urgency":"high"}}'
```

## Safety Features

### Auto-Merge Safety

Only the following fixes are eligible for auto-merge:
- Documentation updates (≤5 changes)
- Minor dependency updates (≤5 packages)
- Whitespace and formatting fixes
- Simple refactoring (high safety rating)

### Fix Application Safety

The system applies fixes based on safety ratings:
- **High Safety**: Applied automatically
- **Medium Safety**: Applied with verification
- **Low Safety**: Suggested only, requires manual review

## Monitoring and Reporting

### Real-time Status

```bash
# Monitor system status
python integration.py status

# Monitor cross-repository status
python integration.py cross-repo-status

# View detailed recursive engine status
python integration.py recursive-status
```

### Automation Reports

After running automation, check the generated reports:

```bash
# View latest automation report
cat cross_repository_automation_report.json | jq .

# View summary
python -c "
import json
with open('cross_repository_automation_report.json') as f:
    report = json.load(f)
    summary = report['summary']
    print(f'Repos: {summary[\"successful_repos\"]}/{summary[\"total_repos\"]}')
    print(f'Fixes: {summary[\"total_fixes_applied\"]}')
    print(f'PRs: {summary[\"prs_created\"]} created, {summary[\"prs_merged\"]} merged')
"
```

### Logs

Check system logs for detailed execution information:

```bash
# View recursive improvement logs
tail -f logs/recursive_improvements.log

# View automation execution
tail -f logs/actions.json
```

## Integration Examples

### Bash Script Integration

```bash
#!/bin/bash
set -e

echo "🚀 Starting comprehensive repository automation..."

# Initialize system
python integration.py init-recursive

# Check status
python integration.py cross-repo-status

# Apply fixes based on urgency
if [ "$URGENCY" = "high" ]; then
    python integration.py automate-fix-all --auto-merge
else
    python integration.py automate-fix-all --create-prs
fi

# Generate report
echo "✅ Automation completed. Check cross_repository_automation_report.json"
```

### Python Integration

```python
#!/usr/bin/env python3
import sys
from cross_repository_automation import CrossRepositoryAutomator
from integration import initialize_recursive_improvement_system

def main():
    # Initialize systems
    initialize_recursive_improvement_system()
    
    automator = CrossRepositoryAutomator()
    if not automator.initialize():
        print("Failed to initialize automation system")
        return 1
    
    # Execute targeted automation
    results = automator.automate_fix_all(
        target_repos=["epochcore_RAS"],
        fix_types=["code_review", "dependencies"],
        create_prs=True,
        auto_merge=False
    )
    
    print(f"✅ Applied {results['summary']['total_fixes_applied']} fixes")
    print(f"📝 Created {results['summary']['prs_created']} PRs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Troubleshooting

### Common Issues

1. **Initialization Fails**
   ```bash
   # Check dependencies
   pip install -r requirements.txt
   
   # Verify system status
   python integration.py validate
   ```

2. **No Fixes Applied**
   ```bash
   # Check engine status
   python integration.py recursive-status
   
   # Verify repository access
   python integration.py cross-repo-status
   ```

3. **PR Creation Fails**
   - Verify GitHub permissions
   - Check branch protection rules
   - Review workflow logs

### Debug Mode

```bash
# Enable verbose logging
export PYTHONPATH=.
export DEBUG=1
python integration.py automate-fix-all --repos epochcore_RAS --fix-types code_review
```

## Best Practices

### Development Workflow

1. **Test First**: Run automation on individual repositories before bulk operations
2. **Staged Rollout**: Start with low-risk fix types (documentation, dependencies)
3. **Review PRs**: Even auto-generated PRs should be reviewed for complex changes
4. **Monitor Impact**: Check automation reports and system metrics

### Production Usage

1. **Schedule Wisely**: Run comprehensive automation during low-activity periods
2. **Safety First**: Enable auto-merge only for well-tested repositories
3. **Monitor Continuously**: Set up alerts for automation failures
4. **Backup Strategy**: Ensure repository backups before major automation runs

## Configuration

### Environment Variables

```bash
# System configuration
export RECURSIVE_IMPROVEMENT_LOG_LEVEL=INFO
export CROSS_REPO_AUTO_MERGE_ENABLED=false
export CROSS_REPO_DEFAULT_URGENCY=medium

# GitHub integration
export GITHUB_TOKEN=your_token_here
export GITHUB_API_URL=https://api.github.com
```

### Repository-Specific Settings

Create `.epochcore-automation.yml` in each repository:

```yaml
# Repository automation configuration
automation:
  enabled: true
  auto_merge_safe_fixes: true
  fix_types_enabled:
    - code_review
    - refactor
    - dependencies
    - workflows
    - documentation
  
  safety_thresholds:
    min_safety_for_auto_apply: medium
    max_fixes_for_auto_merge: 5
    
  notifications:
    pr_created: true
    fixes_applied: true
    errors: true
```

This comprehensive automation system provides the "automate fix all" functionality requested, with safety controls, monitoring, and extensive customization options.