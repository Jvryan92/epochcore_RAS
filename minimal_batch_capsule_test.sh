#!/usr/bin/env bash
set -euo pipefail

TRIGGERS=(
  "TREASURYFLOW💵"
  "MARKETCAP📈"
  "PRICINGFORGE💳"
  "BONUSDROP🎁"
  "GOVCOUNCIL⚖️"
  "PULLREQUESTVOTE🔀"
  "ROLLBACKSEAL⏪"
  "MESHSPAWN🌱"
  "CIVILIZATIONBLOCK🌍"
  "AUTOCOMPOUND⏩"
)

declare -A BATCHES
BATCHES["roi-burst"]="1 2 3 4 10"
BATCHES["gov-harden"]="5 6 7 10"
BATCHES["mesh-expand"]="8 9 10"
BATCHES["full-send"]="1 2 3 4 5 6 7 8 9 10"

PICK=""
if [[ $# -gt 0 ]]; then
  case "$1" in
    --batch)
      shift
      B="$1"
      PICK="${BATCHES[$B]:-}"
      if [[ -z "$PICK" ]]; then
        echo "Unknown batch: $B"
        exit 2
      fi
      shift
      ;;
    --pick)
      shift
      PICK="$1"
      shift
      ;;
    *)
      PICK="${BATCHES[full-send]}"
      ;;
  esac
else
  PICK="${BATCHES[full-send]}"
fi

echo "Selected: $PICK"

LED="${PWD}/ledger_main.jsonl"

forge_one() {
  local TRIG="$1"
  local IDX=$((TRIG-1))
  local NAME="${TRIGGERS[$IDX]}"
  local PROV_NOTE="Ledger first. ROI always. Mesh forever."
  echo "{" > test_capsule_${TRIG}.json
  echo "  \"trigger\": \"$NAME\"," >> test_capsule_${TRIG}.json
  echo "  \"provenance\": {\"founder_note\": \"$PROV_NOTE\", \"true_north\": \"locked\"}," >> test_capsule_${TRIG}.json
  echo "  \"mesh\": {" >> test_capsule_${TRIG}.json
  echo "    \"monetary\": [\"Stripe\", \"MeshCredit\", \"ROI Glyphs\"]," >> test_capsule_${TRIG}.json
  echo "    \"governance\": [\"Multisig\", \"PR-vote\", \"Rollback-seal\"]," >> test_capsule_${TRIG}.json
  echo "    \"expansion\": [\"MeshSpawn\", \"CivilizationBlock\", \"Compound\"]" >> test_capsule_${TRIG}.json
  echo "  }," >> test_capsule_${TRIG}.json
  echo "  \"actions\": [\"Timestamp\", \"Log\", \"Seal\", \"Archive\", \"Reinject\"]," >> test_capsule_${TRIG}.json
  echo "  \"intent\": \"Forge ultra capsule for ROI + Mesh + Governance\"" >> test_capsule_${TRIG}.json
  echo "}" >> test_capsule_${TRIG}.json
  # Ledger logging
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $NAME | test_capsule_${TRIG}.json" >> "$LED"
  echo "Forged: test_capsule_${TRIG}.json ($NAME)"
}

for n in $PICK; do
  forge_one "$n"
done
