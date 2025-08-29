#!/usr/bin/env bash
set -euo pipefail

# Add associative array for batches
declare -A BATCHES
BATCHES["roi-burst"]="1 2 3"
BATCHES["mesh-expand"]="4 5 6"
BATCHES["full-send"]="1 2 3 4 5 6"

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
  echo "{" > test_capsule_${TRIG}.json
  echo "  \"trigger\": \"$TRIG\"" >> test_capsule_${TRIG}.json
  echo "}" >> test_capsule_${TRIG}.json
  echo "Forged: test_capsule_${TRIG}.json"
}

for n in $PICK; do
  forge_one "$n"
done
