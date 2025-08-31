# GitHub Actions Workflows Configuration

This document provides detailed information about the GitHub Actions workflows implemented for the StrategyDECK project.

## Workflow Files Overview

### 1. `ci.yml` - Continuous Integration
**Purpose**: Automated testing and code quality checks
**Triggers**: Push to main branch, Pull requests to main branch
**Jobs**:
- **Multi-version Testing**: Tests across Python 3.8, 3.9, 3.10, 3.11
- **Dependency Installation**: Installs requirements from `requirements.txt`
- **Code Linting**: Uses flake8 for syntax and style checking
- **Code Formatting**: Validates Black formatting compliance
- **Functional Testing**: Runs icon generation script and validates output
- **Unit Testing**: Executes pytest test suite
- **Artifact Upload**: Saves generated icons as workflow artifacts

### 2. `cd.yml` - Continuous Deployment
**Purpose**: Automated asset generation and deployment
**Triggers**: Push to main branch, Manual workflow dispatch
**Jobs**:
- **Asset Generation**: Runs icon generation script with latest changes
- **Automated Commits**: Commits newly generated assets back to repository
- **Release Creation**: Creates timestamped releases with packaged assets
- **GitHub Pages**: Deploys generated icons to GitHub Pages for public access

### 3. `issue-management.yml` - Issue Automation
**Purpose**: Automated issue labeling and assignment
**Triggers**: Issue opened or edited
**Jobs**:
- **Auto-labeling**: Uses keyword matching to apply appropriate labels
- **Auto-assignment**: Assigns issues to team members based on content
- **Priority Detection**: Identifies and flags high-priority issues
- **Team Notification**: Sends notifications for urgent issues

### 4. `pr-management.yml` - Pull Request Automation
**Purpose**: Automated PR review and management
**Triggers**: PR opened, ready for review, review submitted
**Jobs**:
- **Reviewer Assignment**: Auto-assigns reviewers based on changed files
- **Size Labeling**: Categorizes PRs by size (XS, S, M, L, XL)
- **Title Validation**: Suggests conventional commit title formats
- **Ready Notifications**: Notifies team when PR is ready for review

### 5. `docs.yml` - Documentation Automation
**Purpose**: Automated documentation generation and deployment
**Triggers**: Changes to docs/, scripts/, README.md, requirements.txt
**Jobs**:
- **API Documentation**: Auto-generates Python module documentation
- **Usage Examples**: Creates and maintains usage examples
- **Documentation Updates**: Updates README with current project status
- **Docs Deployment**: Deploys documentation to GitHub Pages

## Configuration Files

### `.github/issue-labeler.yml`
Defines keyword-to-label mappings for automatic issue categorization:
- **bug**: error, issue, problem, broken, etc.
- **enhancement**: feature, improvement, request, etc.
- **documentation**: docs, readme, guide, tutorial, etc.
- **design**: ui, ux, interface, style, theme, etc.
- **icon**: svg, png, logo, symbol, graphic, etc.
- **workflow**: action, ci, cd, deploy, github, etc.

## Secrets and Permissions Required

### Repository Settings
- **Actions**: Enabled
- **Pages**: Enabled (for documentation and asset deployment)
- **Issues**: Enabled (for issue management workflows)
- **Pull Requests**: Enabled (for PR management workflows)

### Built-in Secrets Used
- `GITHUB_TOKEN`: Used for repository operations (automatically provided)

### Permissions Required
- **Contents**: Write (for committing generated assets)
- **Issues**: Write (for labeling and assignment)
- **Pull Requests**: Write (for reviewer assignment and labeling)
- **Pages**: Write (for GitHub Pages deployment)

## Customization Guide

### Adding New Labels
Edit `.github/issue-labeler.yml` to add new keyword-to-label mappings.

### Modifying Reviewer Assignment
Update the `reviewRules` object in `pr-management.yml` to change file-based reviewer assignment.

### Changing Test Coverage
Modify the `ci.yml` workflow to add or remove Python versions, linting tools, or test commands.

### Adjusting Deployment Targets
Update `cd.yml` to modify where and how assets are deployed.

## Troubleshooting

### Workflow Failures
1. Check the Actions tab in GitHub for detailed error logs
2. Verify that all required dependencies are in `requirements.txt`
3. Ensure that the CSV configuration file is properly formatted
4. Check that file paths in workflows match actual repository structure

### Permission Issues
1. Verify that GitHub Actions has the necessary permissions
2. Check that repository settings allow Actions to write to the repository
3. Ensure that GitHub Pages is configured correctly if documentation deployment fails

### Asset Generation Issues
1. Verify that master SVG files exist in `assets/masters/`
2. Check that the CSV configuration file has the correct format
3. Ensure that Python dependencies are correctly specified