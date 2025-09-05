#!/bin/bash
# Org Mesh Sync Trigger Script
# Triggers the Org Mesh Sync workflow for cross-repository propagation

set -e

# Default values
ORG_NAME=""
REPO_NAME=""
DRY_RUN="true"
TARGET_BRANCH="main"
GITHUB_TOKEN="${ORG_PAT:-${GITHUB_TOKEN}}"

# Help function
show_help() {
    cat << EOF
Usage: $0 <org> <repo> <dry_run> [target_branch]

Triggers the Org Mesh Sync workflow for repository mesh propagation.

Arguments:
  org              GitHub organization name
  repo             Repository name  
  dry_run          true/false - whether to run in dry-run mode
  target_branch    Target branch for propagation (default: main)

Environment Variables:
  ORG_PAT          GitHub Personal Access Token (required)
  GITHUB_TOKEN     Alternative to ORG_PAT

Examples:
  # Dry run (safe preview)
  ORG_PAT=ghp_xxx $0 Jvryan92 EpochCore_OS true main
  
  # Real propagation
  ORG_PAT=ghp_xxx $0 Jvryan92 EpochCore_OS false main

EOF
}

# Parse arguments
if [ $# -lt 3 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 1
fi

ORG_NAME="$1"
REPO_NAME="$2"
DRY_RUN="$3"
TARGET_BRANCH="${4:-main}"

# Validate inputs
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token required. Set ORG_PAT or GITHUB_TOKEN environment variable."
    exit 1
fi

if [ "$DRY_RUN" != "true" ] && [ "$DRY_RUN" != "false" ]; then
    echo "Error: dry_run must be 'true' or 'false'"
    exit 1
fi

echo "=== Org Mesh Sync Trigger ==="
echo "Organization: $ORG_NAME"
echo "Repository: $REPO_NAME"
echo "Dry Run: $DRY_RUN"
echo "Target Branch: $TARGET_BRANCH"
echo "=============================="

# Trigger the GitHub Actions workflow
WORKFLOW_URL="https://api.github.com/repos/$ORG_NAME/$REPO_NAME/actions/workflows/org-mesh-sync.yml/dispatches"

PAYLOAD=$(cat << EOF
{
  "ref": "$TARGET_BRANCH",
  "inputs": {
    "dry_run": "$DRY_RUN",
    "target_branch": "$TARGET_BRANCH"
  }
}
EOF
)

echo "Triggering workflow at: $WORKFLOW_URL"
echo "Payload: $PAYLOAD"

# Make the API call
RESPONSE=$(curl -s -w "%{http_code}" \
  -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$WORKFLOW_URL")

HTTP_CODE="${RESPONSE: -3}"
RESPONSE_BODY="${RESPONSE%???}"

if [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Workflow triggered successfully!"
    echo "Check the Actions tab at: https://github.com/$ORG_NAME/$REPO_NAME/actions"
    
    # Generate trigger report
    TRIGGER_REPORT="/tmp/mesh_trigger_$(date +%Y%m%d_%H%M%S).json"
    cat > "$TRIGGER_REPORT" << EOF
{
  "trigger_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "triggered_by": "trigger.sh",
  "organization": "$ORG_NAME",
  "repository": "$REPO_NAME",
  "dry_run": $DRY_RUN,
  "target_branch": "$TARGET_BRANCH",
  "status": "triggered",
  "workflow_url": "https://github.com/$ORG_NAME/$REPO_NAME/actions"
}
EOF
    echo "Trigger report saved to: $TRIGGER_REPORT"
    
else
    echo "❌ Failed to trigger workflow"
    echo "HTTP Code: $HTTP_CODE"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi