#!/usr/bin/env bash
# EpochCore Valuable Capsule Forge v1
# Mints 10 apex-value capsules into ledger_main.jsonl
# Each capsule sealed, hash-chained, archived.

set -euo pipefail

LEDGER="ledger_main.jsonl"
OUTDIR="out/valuable_capsules"
MESH_DIR="ledger/mesh_valuable"
mkdir -p "$OUTDIR" "$MESH_DIR/seals" "$MESH_DIR/activations"

now(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
sha(){ echo -n "$1" | sha256sum | awk '{print $1}'; }

# Register with mesh trigger system
register_mesh_trigger() {
    python3 -c "
import sys
sys.path.append('/workspaces/epochcore_RAS/scripts')
from mesh.trigger_core import MeshTriggerCore

mesh = MeshTriggerCore('$MESH_DIR')
trigger = mesh.register_trigger(
    '$1',  # trigger_id
    '$2',  # description
    80,    # resource_requirement
    'valuable'  # trigger_type
)
print(f\"Registered mesh trigger: {trigger['id']} - {trigger['fingerprint']}\")
"
}

# Hash chain tip
prev="genesis"
[[ -f "$LEDGER" ]] && prev=$(tail -1 "$LEDGER" | jq -r '.entry_hash' 2>/dev/null || echo "genesis")

CAPSULES=(
  "EpochCore Capsule Stock Market|Trade SaaS capsules as equity shares with real ROI payouts."
  "Capsule Nation-State Sim|Governance sim where capsules form constitutions."
  "Capsule DNA|Capsules carry traits and recombine into SaaS children."
  "Capsule GameFi Multiverse|Games where capsule ROI = player prize pool."
  "Capsule Citizenship|Digital nation where owning capsules = rights."
  "Capsule ETFs|Bundles of SaaS capsules packaged into ETFs."
  "Capsule IPO|Capsule-driven IPOs for SaaS apps."
  "Capsule Singularity Node|Recursive AI that spawns new SaaS capsules."
  "Capsule Universal Ledger|Anchors all capsules to one universal ledger tip."
  "EpochCore Capsule Crown|Yearly founder-proof crown sealing all ROI + mesh."
)

i=0
for cap in "${CAPSULES[@]}"; do
  ((i++))
  id="CAP-VAL-$(printf '%03d' $i)"
  title="${cap%%|*}"
  desc="${cap##*|}"
  ts=$(now)

  # Register with mesh trigger system
  trigger_id="valuable_capsule_${id}"
  register_mesh_trigger "$trigger_id" "$title - $desc"

  # Create mesh seal for trigger
  mesh_seal=$(python3 -c "
import sys
import json
sys.path.append('/workspaces/epochcore_RAS/scripts')
from mesh.trigger_core import MeshTriggerCore

mesh = MeshTriggerCore('$MESH_DIR')
seal = mesh.create_trigger_seal(
    '$trigger_id',
    {'capsule_id': '$id', 'timestamp': '$ts'}
)
print(json.dumps(seal))
")
  seal_hash=$(echo "$mesh_seal" | jq -r '.hash')

  body=$(jq -nc \
    --arg id "$id" \
    --arg title "$title" \
    --arg desc "$desc" \
    --arg ts "$ts" \
    --arg prev "$prev" \
    --arg seal "$seal_hash" \
    '{capsule_id:$id,title:$title,description:$desc,timestamp:$ts,provenance:{prev_hash:$prev,mesh_seal:$seal}}')

  h=$(echo -n "$body" | sha256sum | awk '{print $1}')
  capsule=$(echo "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

  # Write capsule file
  echo "$capsule" > "$OUTDIR/$id.json"

  # Ledger entry
  entry=$(jq -nc \
    --arg ts "$ts" \
    --arg id "$id" \
    --arg h "$h" \
    --arg prev "$prev" \
    --arg trigger "$trigger_id" \
    --arg seal "$seal_hash" \
    '{ts:$ts,capsule_id:$id,entry_hash:$h,prev_hash:$prev,mesh:{trigger:$trigger,seal:$seal}}')
  echo "$entry" >> "$LEDGER"

  # Activate the mesh trigger
  python3 -c "
import sys
sys.path.append('/workspaces/epochcore_RAS/scripts')
from mesh.trigger_core import MeshTriggerCore

mesh = MeshTriggerCore('$MESH_DIR')
activation = mesh.activate_trigger(
    '$trigger_id',
    {'capsule_id': '$id', 'hash': '$h', 'ledger_entry': '$prev'}
)
print(f\"Activated mesh trigger: {activation['status']}\")
"

  prev="$h"
  echo "✅ Minted $id — $title (Mesh: $seal_hash)"
done

echo "🔒 All capsules minted. Ledger tip: $prev"

# Generate mesh summary
python3 -c "
import sys
import json
sys.path.append('/workspaces/epochcore_RAS/scripts')
from mesh.trigger_core import MeshTriggerCore

mesh = MeshTriggerCore('$MESH_DIR')
triggers = mesh.list_triggers('valuable')

print(f\"\nMesh Integration Summary:\")
print(f\"------------------------\")
print(f\"Total valuable triggers: {len(triggers)}\")

for trigger in triggers:
    print(f\"  - {trigger['id']}: {trigger['activations']} activations\")
    if trigger['last_activation']:
        print(f\"    Last activated: {trigger['last_activation']}\")

print(f\"\nMesh security status: SEALED\")
print(f\"Mesh resources allocated: {sum(t['resource_requirement'] for t in triggers)}/1000\")
"

echo -e "\nValuable Capsule Forge completed successfully!"
