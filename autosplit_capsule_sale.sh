#!/usr/bin/env bash
# File: autosplit_capsule_sale.sh
# Purpose: auto-split every capsule sale into 3 sealed pools + append to ledger
set -euo pipefail

LEDGER="founder_pack/ledger_main.jsonl"
mkdir -p "$(dirname "$LEDGER")"

DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
AMT="${1:-100}" # default capsule price = $100

# Split percentages 
FOUNDER_PCT=0.45
MESH_PCT=0.30
GOV_PCT=0.15
TOPSELLER_PCT=0.10

founder_amt=$(awk -v a="$AMT" -v p="$FOUNDER_PCT" 'BEGIN{printf "%.2f",a*p}')
mesh_amt=$(awk -v a="$AMT" -v p="$MESH_PCT" 'BEGIN{printf "%.2f",a*p}')
gov_amt=$(awk -v a="$AMT" -v p="$GOV_PCT" 'BEGIN{printf "%.2f",a*p}')

sha=$(printf "%s|%s|%s|%s|%s" "$DATE_UTC" "$AMT" "$founder_amt" "$mesh_amt" "$gov_amt" | sha256sum | awk '{print $1}')

entry=$(cat <<JSON
{"ts":"$DATE_UTC","event":"capsule_sale","price_usd":$AMT,
"splits":{"founder":$founder_amt,"meshcredit":$mesh_amt,"governance":$gov_amt},
"sha256":"$sha"}
JSON
)

echo "$entry" >> "$LEDGER"
echo "✅ Capsule sale recorded → Founder: \$$founder_amt, MeshCredit: \$$mesh_amt, Governance: \$$gov_amt"
