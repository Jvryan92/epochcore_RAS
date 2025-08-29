#!/usr/bin/env bash
set -euo pipefail

# Minimal argument parsing and batch selection
BATCHES=("1 2 3" "4 5 6")
PICK=""
if [[ $# -gt 0 ]]; then
  case "$1" in
    --batch)
      shift
      PICK="${BATCHES[0]}"
      ;;
    --pick)
      shift
      PICK="$1"
      ;;
    *)
      PICK="${BATCHES[1]}"
      ;;
  esac
else
  PICK="${BATCHES[0]}"
fi

echo "Selected: $PICK"

# Minimal function
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
