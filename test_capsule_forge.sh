#!/usr/bin/env bash
# Simplified test script to generate capsules for one domain

set -euo pipefail

LEDGER="ledger_test.jsonl"
ROOT="out/test_capsules"
mkdir -p "$ROOT"
> "$LEDGER"  # Create empty ledger

if command -v sha256sum >/dev/null 2>&1; then 
  SHACMD=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then 
  SHACMD=(shasum -a 256)
else
  echo "Need sha256sum or shasum -a 256" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Need jq" >&2
  exit 1
fi

now(){ date -u +%Y-%m-%dT%H:%M:%SZ; }
sha(){ "${SHACMD[@]}" | awk '{print $1}'; }

# Start with genesis
prev="genesis"

# Simple test domain with 3 items
DOMAIN="test"
ITEMS=(
  "Test Capsule 1|Test description 1"
  "Test Capsule 2|Test description 2" 
  "Test Capsule 3|Test description 3"
)

echo "=== Test Capsule Forge ==="

for ((i=0; i<${#ITEMS[@]}; i++)); do
  IFS='|' read -r name desc <<< "${ITEMS[$i]}"
  id="TEST-$(printf '%02d' $((i+1)))"
  ts="$(now)"

  # body without self_sha256
  body=$(jq -nc --arg id "$id" --arg ts "$ts" --arg d "$DOMAIN" --arg name "$name" --arg desc "$desc" --arg prev "$prev" \
    '{capsule_id:$id,timestamp:$ts,domain:$d,name:$name,description:$desc,provenance:{prev_hash:$prev,test:true}}')

  # hash over body
  h=$(echo -n "$body" | sha)

  # full capsule
  capsule=$(echo -n "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

  # write capsule
  echo "$capsule" > "$ROOT/$id.json"

  # append ledger entry (hash-chained)
  jq -nc --arg ts "$ts" --arg id "$id" --arg h "$h" --arg prev "$prev" \
    '{ts:$ts,capsule_id:$id,entry_hash:$h,prev_hash:$prev}' >> "$LEDGER"

  prev="$h"
  echo "✅ $id - $name"
done

echo "🔒 Done. Ledger tip: $prev"
ls -la "$ROOT"
