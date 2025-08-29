#!/usr/bin/env bash
set -euo pipefail

# Full trigger list
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

forge_one() {
  local TRIG="$1"
  local IDX=$((TRIG-1))
  local NAME="${TRIGGERS[$IDX]}"
  echo "{" > test_capsule_${TRIG}.json
  echo "  \"trigger\": \"$NAME\"" >> test_capsule_${TRIG}.json
  echo "}" >> test_capsule_${TRIG}.json
  echo "Forged: test_capsule_${TRIG}.json ($NAME)"
}

for n in $PICK; do
  forge_one "$n"
done
