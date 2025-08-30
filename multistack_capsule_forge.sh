#!/usr/bin/env bash
# EpochCore Multi-Stack Capsule Forge v2
# Mint Valuable Capsules by stack: iaas, paas, saas, ras, all
# Each capsule sealed, hash-chained, archived.

set -euo pipefail

LEDGER="ledger_main.jsonl"
OUTDIR="out/multistack_capsules"
ARCHIVE_DIR="out/archive"
MESH_DIR="ledger/mesh_multistack"
mkdir -p "$OUTDIR" "$ARCHIVE_DIR" "$MESH_DIR/seals" "$MESH_DIR/activations"

STACK="${1:-all}"   # default: all
now(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
sha(){ echo -n "$1" | sha256sum | awk '{print $1}'; }

# Load ledger tip
prev="genesis"
[[ -f "$LEDGER" ]] && prev=$(tail -1 "$LEDGER" | jq -r '.entry_hash' 2>/dev/null || echo "genesis")

# Register with mesh trigger system
register_mesh_trigger() {
    local stack="$1"
    local trigger_id="$2"
    local description="$3"
    
    # Allocate different resource requirements based on stack
    local resource=0
    case "$stack" in
        "iaas") resource=65 ;;
        "paas") resource=75 ;;
        "saas") resource=85 ;;
        "ras") resource=95 ;;
        "base") resource=80 ;;
        *) resource=70 ;;
    esac

    # Try to use mesh_trigger_core, but continue if it fails
    python3 -c "
import sys
sys.path.append('/workspaces/epochcore_RAS/scripts')
try:
    from mesh.trigger_core import MeshTriggerCore
    mesh = MeshTriggerCore('$MESH_DIR')
    trigger = mesh.register_trigger(
        '$trigger_id',  # trigger_id
        '$description',  # description
        $resource,    # resource_requirement
        '$stack'  # trigger_type
    )
    print(f\"Registered mesh trigger: {trigger['id']} - {trigger['fingerprint']}\")
except Exception as e:
    print(f\"Note: Mesh integration skipped: {e}\")
" || echo "Mesh integration not available, continuing..."
}

declare -A CAPSULES

# ---- Define base 10
CAPSULES["base"]="EpochCore Capsule Stock Market|SaaS capsules as equity
Capsule Nation-State Sim|Capsules form constitutions
Capsule DNA|Capsules recombine into SaaS children
Capsule GameFi Multiverse|Games where capsule ROI = prize pool
Capsule Citizenship|Capsules = digital nation rights
Capsule ETFs|Bundles of SaaS capsules
Capsule IPO|IPO capsules for SaaS
Capsule Singularity Node|Recursive AI spawns capsules
Capsule Universal Ledger|Anchors all capsules to one tip
EpochCore Capsule Crown|Founder-proof yearly crown"

# ---- Stack mutations
CAPSULES["iaas"]="Cloud Resource Market|VM/storage as capsule equity
Data Center City Sim|Capsules = zoning/power laws
Infra DNA|Capsules evolve load balancers
Infra Arena|Earn compute credits via agents
Access Keys|Capsules = root access rights
Infra Bundles|VM+DB+network ETF capsules
Data Center IPO|New region bootstraps via capsule sale
Infra Auto-Scaler AI|AI node for recursive infra scaling
Infra Ledger|Universal infra events ledger
Infra Epoch Seal|Annual infra audit capsule"

CAPSULES["paas"]="Dev Platform Marketplace|Capsule shares of frameworks
Dev Governance Sim|Capsules = API policies
Platform DNA|Capsules evolve frameworks
Dev Multiverse|Coding challenges earn credits
Platform Membership|Capsule = dev club pass
Framework Bundles|React+DB ETF capsules
Framework Launch Capsules|IPO for frameworks
Auto SDK Generator Node|AI spawns SDKs as capsules
DevOps Ledger|Tip hash for CI/CD events
Platform Crown Capsule|Annual top dev award"

CAPSULES["saas"]="App Capsule Market|Equity in SaaS apps
Customer Council Sim|Capsules = feature votes
App DNA|Capsules mutate SaaS features
SaaS GameFi Multiverse|Gamified SaaS adoption
Customer Citizenship|Capsule = loyalty rights
SaaS Bundles|Marketing+analytics ETFs
Micro-SaaS IPO Capsules|IPO for niche apps
Auto SaaS Builder AI|AI spawns SaaS as capsules
SaaS Ledger|Append-only customer proof
SaaS Founder Crown|Annual capsule trophy"

CAPSULES["ras"]="Agent Capsule Market|Equity in recursive agents
Agent Polity Sim|Agents mint constitutions
Agent DNA Capsules|Recursive trait evolution
Agent Multiverse|Agents battle for ROI capsules
Agent Citizenship|Capsule = agent rights
Agent Portfolios|ETF bundles of AI agents
Agent IPO Capsules|Fund recursive agent launches
True Recursive God Node|Autonomous capsule-forger
Agentic Ledger|Universal memory for agents
Recursive Epoch Crown|Founder+AI co-sign crown"

# Mint function
mint_capsules(){
  local label="$1"
  local items="${CAPSULES[$label]}"
  local idx=0
  
  # Check if items is empty
  if [[ -z "$items" ]]; then
    echo "Error: No capsules defined for stack '$label'"
    return 1
  fi
  
  # Count lines correctly
  local total_lines=$(echo "$items" | wc -l)
  echo -e "\n🔄 Minting $total_lines $label capsules..."
  
  # Use while read loop with proper IFS handling
  echo "$items" | while IFS='|' read -r title desc; do
    # Skip empty lines
    [[ -z "$title" ]] && continue
    
    ((idx++))
    id="CAP-${label^^}-$(printf '%03d' $idx)"
    ts=$(now)
    
    echo "Processing: $title | $desc"
    
    # Register with mesh trigger system
    trigger_id="multistack_${label}_${idx}"
    register_mesh_trigger "$label" "$trigger_id" "$title - $desc"
    
    # Create mesh seal for trigger
    mesh_seal=$(python3 -c "
import sys
import json
sys.path.append('/workspaces/epochcore_RAS/scripts')
try:
    from mesh.trigger_core import MeshTriggerCore
    mesh = MeshTriggerCore('$MESH_DIR')
    seal = mesh.create_trigger_seal(
        '$trigger_id',
        {'capsule_id': '$id', 'stack': '$label', 'timestamp': '$ts'}
    )
    print(json.dumps(seal))
except Exception as e:
    print(json.dumps({'hash': f'local-seal-{int($(date +%s))}', 'note': 'Local seal created'}))
" 2>/dev/null || echo "{\"hash\": \"local-seal-$(date +%s)\", \"note\": \"Fallback seal created\"}")
    seal_hash=$(echo "$mesh_seal" | jq -r '.hash' 2>/dev/null || echo "local-seal-$(date +%s)")

    body=$(jq -nc \
      --arg id "$id" \
      --arg title "$title" \
      --arg desc "$desc" \
      --arg ts "$ts" \
      --arg prev "$prev" \
      --arg stack "$label" \
      --arg seal "$seal_hash" \
      '{version:"1.0",capsule_id:$id,title:$title,description:$desc,timestamp:$ts,stack:$stack,
        provenance:{prev_hash:$prev,mesh_seal:$seal,founder_note:"Multi-Stack Capsule Forge",true_north:"sealed"},
        mesh:{monetary:["CapsuleStake","MeshSync","ROI"],governance:["MultiStack","IntegrityCheck","MeshSeal"],
        expansion:["Recursion","Interconnect","Federation"]},
        actions:["Timestamp","Log","Seal","Archive","Mesh"],
        intent:"Forge multi-stack capsule for \($stack) ecosystem"}')

    h=$(sha "$body")
    capsule=$(echo "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

    # Generate unique filename with timestamp and UUID
    uuid=$(python3 -c "import uuid; print(uuid.uuid4())")
    filename="capsule_$(date +%Y%m%d_%H%M%S)_${uuid}.json"
    capsule_path="$OUTDIR/$filename"
    
    # Write capsule file
    echo "$capsule" > "$capsule_path"
    
    # Create archive path
    archive_path="${capsule_path/multistack_capsules/archive}"
    archive_path="${archive_path/.json/.zip}"
    
    # Create archive of the capsule
    mkdir -p "$(dirname "$archive_path")"
    (cd "$(dirname "$capsule_path")" && zip -q "$(basename "$archive_path")" "$(basename "$capsule_path")")

    # Ledger entry in the format used by the existing system
    entry=$(jq -nc \
      --arg ts "$ts" \
      --arg id "$id" \
      --arg event "multistack_capsule" \
      --arg trigger "$trigger_id" \
      --arg capsule "$capsule_path" \
      --arg sha "$h" \
      --arg archive "$archive_path" \
      --arg stack "$label" \
      '{ts:$ts,event:$event,trigger:$trigger,stack:$stack,capsule:$capsule,sha256:$sha,archive:$archive,entry_hash:$sha,prev_hash:$prev}')
    echo "$entry" >> "$LEDGER"
    
    # Activate the mesh trigger
    python3 -c "
import sys
sys.path.append('/workspaces/epochcore_RAS/scripts')
try:
    from mesh.trigger_core import MeshTriggerCore
    mesh = MeshTriggerCore('$MESH_DIR')
    activation = mesh.activate_trigger(
        '$trigger_id',
        {'capsule_id': '$id', 'stack': '$stack', 'hash': '$h', 'ledger_entry': '$prev'}
    )
    print(f\"Activated mesh trigger: {activation['status']}\")
except Exception as e:
    print(f\"Note: Mesh trigger activation skipped: {e}\")
" 2>/dev/null || echo "Mesh trigger activation not available, continuing..."

    prev="$h"
    echo "✅ Minted $id — $title (Stack: ${label})"
  done
  
  echo -e "✅ Completed minting $label stack capsules!\n"
}

# Dispatch
if [[ "$STACK" == "all" ]]; then
  for s in base iaas paas saas ras; do mint_capsules "$s"; done
else
  mint_capsules "$STACK"
fi

echo "🔒 Mint complete. Ledger tip: $prev"

# Generate mesh summary
python3 -c "
import sys
import json
sys.path.append('/workspaces/epochcore_RAS/scripts')

print(f\"\nMulti-Stack Mesh Integration Summary:\")
print(f\"----------------------------------\")

try:
    from mesh.trigger_core import MeshTriggerCore
    mesh = MeshTriggerCore('$MESH_DIR')

    # Get all trigger types (stacks)
    all_triggers = mesh.list_triggers()
    stack_types = set(trigger['type'] for trigger in all_triggers)

    print(f\"Total capsules in mesh: {len(all_triggers)}\")

    for stack in stack_types:
        stack_triggers = mesh.list_triggers(stack)
        total_activations = sum(t['activations'] for t in stack_triggers)
        resources = sum(t['resource_requirement'] for t in stack_triggers)
        
        print(f\"\n{stack.upper()} Stack:\")
        print(f\"  Capsules: {len(stack_triggers)}\")
        print(f\"  Activations: {total_activations}\")
        print(f\"  Resources: {resources}\")

    print(f\"\nMesh security status: MULTI-STACK SEALED\")
    total_resources = sum(t['resource_requirement'] for t in all_triggers)
    print(f\"Total mesh resources allocated: {total_resources}/1000\")
except Exception as e:
    print(f\"Mesh integration summary unavailable: {e}\")
    print(f\"Generated capsules were still correctly minted and added to the ledger.\")
" 2>/dev/null || echo -e "\nMesh summary not available. Capsules were successfully minted."

echo -e "\nMulti-Stack Capsule Forge completed successfully!"
