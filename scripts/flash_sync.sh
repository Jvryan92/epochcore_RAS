#!/bin/bash
# FLASH SYNC: Cross-Repo Manifest & Audit Sync for EpochCore Autonomous Agents

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="/tmp/epochcore_flash_sync_$$"
SYNC_TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")

# List of repo URLs (use SSH or HTTPS as appropriate)
REPOS=(
    "git@github.com:Jvryan92/epochcore_RAS.git"
    "git@github.com:EpochCore5/epochcore_RAS.git"
    "git@github.com:Jvryan92/EpochCore_OS.git"
    "git@github.com:Jvryan92/StategyDECK.git"
    "git@github.com:Jvryan92/saas-hub.git"
    "git@github.com:EpochCore5/epoch5-template.git"
    "git@github.com:Jvryan92/epoch-mesh.git"
)

# Files and directories to sync
SYNC_ITEMS=(
    "agents/"
    "manifests/"
    ".github/workflows/recursive_matrix_autonomy.yml"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 FLASH SYNC: Cross-Repo EpochCore Autonomous Agent Propagation${NC}"
echo "================================================================"
echo "Sync timestamp: $SYNC_TIMESTAMP"
echo "Source directory: $SCRIPT_DIR"
echo "Temp directory: $TEMP_DIR"
echo ""

# Create temp directory
mkdir -p "$TEMP_DIR"
trap "rm -rf $TEMP_DIR" EXIT

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

# Validate source files exist
log "Validating source files..."
for item in "${SYNC_ITEMS[@]}"; do
    if [ ! -e "$item" ]; then
        error "Source item not found: $item"
        exit 1
    fi
    log "✓ Found: $item"
done

# Create sync manifest
log "Creating sync manifest..."
cat > "$TEMP_DIR/flash_sync_manifest.json" << EOF
{
  "flash_sync": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "v1.0",
    "source_repo": "$(git remote get-url origin 2>/dev/null || echo 'unknown')",
    "sync_id": "flash_sync_$SYNC_TIMESTAMP",
    "items_synced": [
$(IFS=','; printf '      "%s"\n' "${SYNC_ITEMS[@]}" | sed '$s/,$//')
    ],
    "target_repositories": [
$(IFS=','; printf '      "%s"\n' "${REPOS[@]}" | sed 's|git@github.com:\(.*\)\.git|https://github.com/\1|' | sed '$s/,$//')
    ],
    "sync_strategy": "flash_propagation",
    "execution_mode": "autonomous",
    "recursive_depth": 3
  },
  "agent_status": {
    "kpi_prediction_agent": "v4",
    "failure_remediation_agent": "v4", 
    "portfolio_optimizer": "v4",
    "meta_experiment_cascade": "v4",
    "resource_allocation_agent": "v3",
    "compliance_auditor": "v4",
    "innovation_diffuser": "v4",
    "user_feedback_engine": "v4",
    "explainability_agent": "v4",
    "agent_registry": "v4",
    "audit_evolution_manager": "v3"
  }
}
EOF

log "Sync manifest created"

# Function to sync to a single repository
sync_repo() {
    local repo_url=$1
    local repo_name=$(basename "$repo_url" .git)
    local repo_dir="$TEMP_DIR/$repo_name"
    
    log "Syncing to repository: $repo_name"
    
    # Clone repository
    if ! git clone "$repo_url" "$repo_dir" &>/dev/null; then
        warn "Failed to clone $repo_url - skipping"
        return 1
    fi
    
    cd "$repo_dir"
    
    # Create sync branch
    local branch_name="flash-sync-$SYNC_TIMESTAMP"
    git checkout -b "$branch_name" &>/dev/null
    
    # Copy sync items
    for item in "${SYNC_ITEMS[@]}"; do
        local source_path="$SCRIPT_DIR/$item"
        local target_path="$repo_dir/$item"
        
        if [ -d "$source_path" ]; then
            # Directory sync
            mkdir -p "$(dirname "$target_path")"
            cp -r "$source_path" "$(dirname "$target_path")/" 2>/dev/null || {
                warn "Failed to copy directory $item to $repo_name"
                continue
            }
            log "  ✓ Synced directory: $item"
        elif [ -f "$source_path" ]; then
            # File sync
            mkdir -p "$(dirname "$target_path")"
            cp "$source_path" "$target_path" 2>/dev/null || {
                warn "Failed to copy file $item to $repo_name"
                continue
            }
            log "  ✓ Synced file: $item"
        fi
    done
    
    # Copy sync manifest
    cp "$TEMP_DIR/flash_sync_manifest.json" "$repo_dir/manifests/"
    
    # Check if there are changes
    if git diff --quiet && git diff --cached --quiet; then
        log "  ↳ No changes detected in $repo_name"
        return 0
    fi
    
    # Stage and commit changes
    git add . 2>/dev/null
    git commit -m "🚀 Flash Sync: EpochCore Autonomous Agents Update

- Synced autonomous agent stubs (v3-v4)
- Updated recursive matrix workflow 
- Propagated manifests and audit logs
- Flash sync timestamp: $SYNC_TIMESTAMP

Auto-synced from EpochCore RAS autonomous pipeline
Ready for recursive autonomous operation across portfolio" &>/dev/null
    
    # Push changes
    if git push origin "$branch_name" &>/dev/null; then
        log "  ✅ Successfully pushed to $repo_name:$branch_name"
        echo "     📋 Create PR: git checkout $branch_name && git push origin $branch_name"
    else
        warn "Failed to push to $repo_name"
        return 1
    fi
    
    cd "$TEMP_DIR"
}

# Main sync loop
log "Starting flash sync to ${#REPOS[@]} repositories..."
echo ""

successful_syncs=0
failed_syncs=0

for repo in "${REPOS[@]}"; do
    echo -e "${BLUE}Processing $(basename "$repo" .git)...${NC}"
    if sync_repo "$repo"; then
        ((successful_syncs++))
    else
        ((failed_syncs++))
    fi
    echo ""
done

# Summary
echo "================================================================"
echo -e "${GREEN}🎯 FLASH SYNC COMPLETE${NC}"
echo ""
echo "📊 Summary:"
echo "  Successful syncs: $successful_syncs"
echo "  Failed syncs: $failed_syncs"
echo "  Total repositories: ${#REPOS[@]}"
echo ""
echo "📁 Synced items:"
for item in "${SYNC_ITEMS[@]}"; do
    echo "  • $item"
done
echo ""
echo "🔄 Next steps:"
echo "  1. Review and merge PRs in target repositories"
echo "  2. Verify agent execution in each repo"
echo "  3. Monitor cross-portfolio recursive improvements"
echo ""
echo "⚡ Flash sync ritual complete - Portfolio ready for autonomous operation!"

exit $failed_syncs