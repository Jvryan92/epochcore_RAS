#!/usr/bin/env bash
# EpochCore — Ultra Trigger Pack v10.0 (Batch Forge)
# Mint multiple capsules per run: ROI, Governance, Mesh Expansion, or custom multi-select.
# Safe: no network, append-only ledger, SHA-256 seals, zip archives.

set -euo pipefail

ROOT="${PWD}/out"
LED="${PWD}/ledger_main.jsonl"
mkdir -p "$ROOT/capsules" "$ROOT/archive"

# sha tool
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum)
elif command -v shasum   >/dev/null 2>&1; then SHACMD=(shasum -a 256)
else echo "Need sha256sum or shasum -a 256"; exit 1; fi

# jq optional; fall back to raw JSON echo
have_jq(){ command -v jq >/dev/null 2>&1; }

# ---------- trigger catalog ----------
TRIGGERS=(
  "TREASURYFLOW💵"     # 1  revenue inflow/outflow logs + ROI metrics
  "MARKETCAP📈"        # 2  ARR/MRR/LTV/CAC calc + ROI glyphs
  "PRICINGFORGE💳"     # 3  SKU & tier capsules + price governance
  "BONUSDROP🎁"        # 4  VRF daily prizes / cashback capsules
  "GOVCOUNCIL⚖️"       # 5  5-of-9 multisig council, time-locked powers
  "PULLREQUESTVOTE🔀"  # 6  PR quorum capsules; merge only with votes
  "ROLLBACKSEAL⏪"     # 7  revert-to-sealed lineage (safety)
  "MESHSPAWN🌱"        # 8  spawn 10 SaaS nodes (repos) auto-CI/CD
  "CIVILIZATIONBLOCK🌍" # 9  meta bundle: infra+SaaS+governance
  "AUTOCOMPOUND⏩"     # 10 leverage ×10 on last N capsules
)

# ---------- preset batches ----------
# (Space-separated indices into TRIGGERS array, 1-based)
declare -A BATCHES=(
  ["roi-burst"]="1 2 3 4 10"
  ["gov-harden"]="5 6 7 10"
  ["mesh-expand"]="8 9 10"
  ["full-send"]="1 2 3 4 5 6 7 8 9 10"
)

usage(){
cat <<USG
EpochCore Ultra Trigger Pack — Batch Forge
Usage:
  $0                       # interactive menu (multi-select)
  $0 --batch roi-burst     # preset: ROI capsules
  $0 --batch gov-harden    # preset: governance hardening
  $0 --batch mesh-expand   # preset: mesh expansion
  $0 --batch full-send     # preset: everything
  $0 --pick "1 3 8 10"     # run selected triggers by number (space-separated)
  $0 --dry-run ...         # show what would be forged without writing files

Presets:
  roi-burst, gov-harden, mesh-expand, full-send
USG
}

DRY=0; PICK=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --batch) shift; B="$1"; PICK="${BATCHES[$B]:-}"; [[ -n "$PICK" ]] || { echo "Unknown batch: $B"; exit 2; }; shift;;
    --pick)  shift; PICK="$1"; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

if [[ -z "${PICK}" ]]; then
  echo "=== EpochCore Ultra Trigger Pack v10.0 — Batch Forge ==="
  i=1; for m in "${TRIGGERS[@]}"; do printf " %2d) %s\n" "$i" "$m"; ((i++)); done
  read -rp "Select one or more (e.g., '1 2 8 10' or press Enter for full-send): " PICK
  [[ -n "$PICK" ]] || PICK="${BATCHES[full-send]}"
fi

# normalize selection (unique, numeric, in-range)
norm_pick(){
  awk '
    BEGIN{split("",seen)}
    {for(i=1;i<=NF;i++){ if($i ~ /^[0-9]+$/){ if(!seen[$i]++){ printf "%s ", $i }}}}
  ' <<<"$1"
}
PICK="$(norm_pick "$PICK")"

forge_one(){
  local TRIG="$1"
  local UUID; UUID="$( (command -v uuidgen >/dev/null 2>&1 && uuidgen) || cat /proc/sys/kernel/random/uuid )"
  local TS;   TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local BASE="capsule_$(date -u +%Y%m%d_%H%M%S)_${UUID}"
  local CAP="$ROOT/capsules/${BASE}.json"
  local PROV_NOTE="Ledger first. ROI always. Mesh forever."

  # write capsule
  cat >"$CAP"<<JSON
{"version":"1.0","capsule_id":"$BASE","trigger":"$TRIG","timestamp":"$TS",
 "provenance":{"founder_note":"$PROV_NOTE","true_north":"locked"},
 "mesh":{"monetary":["Stripe","MeshCredit","ROI Glyphs"],
         "governance":["Multisig","PR-vote","Rollback-seal"],
         "expansion":["MeshSpawn","CivilizationBlock","Compound"]},
 "actions":["Timestamp","Log","Seal","Archive","Reinject"],
 "intent":"Forge ultra capsule for ROI + Mesh + Governance"}
JSON

  # seal + archive
  local HASH; HASH="$("${SHACMD[@]}" "$CAP" | awk '{print $1}')"
  local ARC="$ROOT/archive/${BASE}.zip"
  (cd "$ROOT/capsules" && zip -q -9 "$(basename "$ARC")" "$(basename "$CAP")")

  # ledger line
  if have_jq; then
    local LINE; LINE=$(jq -nc \
      --arg ts "$TS" --arg trig "$TRIG" --arg cap "$CAP" --arg sha "$HASH" --arg arc "$ARC" \
      '{"ts":$ts,"event":"ultra_capsule","trigger":$trig,"capsule":$cap,"sha256":$sha,"archive":$arc}')
    echo "$LINE" >> "$LED"
  else
    printf '{"ts":"%s","event":"%s","trigger":"%s","capsule":"%s","sha256":"%s","archive":"%s"}\n' \
      "$TS" "ultra_capsule" "$TRIG" "$CAP" "$HASH" "$ARC" >> "$LED"
  fi

  echo "✅ Forged: $(basename "$CAP")  🔒 $HASH"
}

echo "Selected: $PICK"
if [[ "$DRY" -eq 1 ]]; then
  echo "(dry-run) Would mint triggers:"
  for n in $PICK; do
    idx=$((n-1))
    [[ $idx -ge 0 && $idx -lt ${#TRIGGERS[@]} ]] || { echo "  ! skip invalid #$n"; continue; }
    echo "  - ${TRIGGERS[$idx]}"
  done
  exit 0
fi

# mint loop
for n in $PICK; do
  idx=$((n-1))
  if [[ $idx -lt 0 || $idx -ge ${#TRIGGERS[@]} ]]; then
    echo "⚠️  Skipping invalid selection #$n"; continue
  fi
  forge_one "${TRIGGERS[$idx]}"
  # micro-splay to keep timestamps unique and readable in ledger
  sleep 0.2
done

echo "🧾 Ledger: $LED"
echo "📂 Capsules: $ROOT/capsules"
echo "📦 Archives: $ROOT/archive"
echo "🌱 Done."
