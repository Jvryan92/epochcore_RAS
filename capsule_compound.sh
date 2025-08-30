#!/usr/bin/env bash
# EpochCore — Capsule Compounding Tricks Forge
# Mints 40 Compounding Trick capsules
# - Tamper-evident: each capsule has self_sha256 and ledger prev_hash chaining.
# - Safe: no network, no secrets. Requires: bash, jq, sha256sum (or shasum -a 256).
#
# Usage:
#   ./capsule_compound.sh

set -euo pipefail

LEDGER="${LEDGER:-ledger_main.jsonl}"
ROOT="${ROOT:-out/capsules}"
mkdir -p "$ROOT"

# ---- tools ----
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then SHACMD=(shasum -a 256)
else
  echo "Need sha256sum or shasum -a 256" >&2; exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "Need jq (apt/brew install jq)" >&2; exit 1
fi

now(){ date -u +%Y-%m-%dT%H:%M:%SZ; }
sha(){ "${SHACMD[@]}" | awk '{print $1}'; }

# ---- ledger tip ----
prev="genesis"
if [[ -s "$LEDGER" ]]; then
  # last non-empty line's entry_hash
  last_hash=$(tail -n 200 "$LEDGER" | tac | awk 'NF {print; exit}')
  if [[ -n "$last_hash" ]] && echo "$last_hash" | jq -e . >/dev/null 2>&1; then
    prev=$(echo "$last_hash" | jq -r '.entry_hash // "genesis"')
  fi
fi

# Define the compounding tricks directly
declare -a TRICKS=(
  "Recursive Yield Amplification"
  "Temporal Mesh Rebalancing"
  "Quantum Liquidity Loop"
  "Autonomous Capsule Fusion"
  "MeshCredit Cascade"
  "Ledger Provenance Chaining"
  "Adaptive Interest Compounding"
  "Multi-Domain Mesh Synthesis"
  "Capsule Swarm Optimization"
  "Self-Referential Growth"
  "Dynamic Capsule Forking"
  "Resilience Mesh Overlay"
  "StrategyDeck Interlink"
  "Ethical Reflection Loop"
  "Evolutionary Capsule Mutation"
  "Temporal Ledger Stacking"
  "Collaborative Mesh Expansion"
  "Intelligence Capsule Chaining"
  "Autonomous Strategy Rotation"
  "Capsule Provenance Recursion"
  "MeshCredit Recursive Mint"
  "Capsule Ledger Interlock"
  "Self-Improvement Cascade"
  "Quantum Mesh Fork"
  "Adaptive Mesh Reallocation"
  "StrategyDeck Provenance"
  "Temporal Compounding Chain"
  "Capsule Swarm Compounding"
  "Autonomous Mesh Rebalancer"
  "Recursive Ledger Growth"
  "Capsule Evolution Overlay"
  "Ethical Compounding Loop"
  "Collaborative Capsule Fusion"
  "Intelligence Mesh Cascade"
  "StrategyDeck Capsule Chain"
  "Self-Referential Ledger"
  "Quantum Capsule Amplification"
  "Adaptive Mesh Forking"
  "Temporal Mesh Overlay"
  "Capsule Provenance Amplifier"
  "Recursive Mesh Expansion"
)

echo "=== Forging Capsules (40 Compounding Tricks) ==="

# Forge capsules for each trick
for ((i = 0; i < ${#TRICKS[@]} && i < 40; i++)); do
  trick="${TRICKS[$i]}"
  id="CAPSULE-$((i+1))"
  ts="$(now)"
  domain="compounding"
  
  # Define default properties for each trick
  local multiplier=2.0
  local ethical_impact=0.85
  local category="yield"
  
  # Set specific properties based on trick name
  case "$trick" in
    "Recursive Yield Amplification")
      multiplier=2.5
      ethical_impact=0.8
      category="yield"
      ;;
    "Temporal Mesh Rebalancing")
      multiplier=1.7
      ethical_impact=0.9
      category="mesh"
      ;;
    "Quantum Liquidity Loop")
      multiplier=3.0
      ethical_impact=0.7
      category="quantum"
      ;;
    "Autonomous Capsule Fusion")
      multiplier=2.2
      ethical_impact=0.85
      category="fusion"
      ;;
    "MeshCredit Cascade")
      multiplier=1.9
      ethical_impact=0.9
      category="credit"
      ;;
    "Ledger Provenance Chaining")
      multiplier=1.6
      ethical_impact=0.95
      category="ledger"
      ;;
    "Ethical Reflection Loop")
      multiplier=1.5
      ethical_impact=0.98
      category="ethical"
      ;;
    *)
      # Use defaults for other tricks
      ;;
  esac
  
  # body without self_sha256
  body=$(jq -nc --arg id "$id" --arg ts "$ts" --arg d "$domain" \
      --arg name "$trick" --arg desc "Compounding technique: ${category} (x${multiplier})" \
      --arg prev "$prev" --arg multiplier "$multiplier" --arg ethical "$ethical_impact" --arg category "$category" \
      '{
        capsule_id: $id, 
        timestamp: $ts, 
        domain: $d, 
        name: $name, 
        description: $desc, 
        properties: {
          multiplier: $multiplier | tonumber,
          ethical_impact: $ethical | tonumber,
          category: $category
        },
        provenance: {
          prev_hash: $prev,
          compounding: true
        }
      }')

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
  printf "Forged: %s (%s) [sha:%s...]\n" "$id" "$trick" "${h:0:8}"
done

echo "=== Done. Forged 40 capsules into $ROOT and appended to $LEDGER ==="
