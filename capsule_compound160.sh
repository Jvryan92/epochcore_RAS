#!/usr/bin/env bash
# EpochCore — MeshCredit Capsule Compounder (160 in one)
# Mints 160 MeshCredit-native capsules across 16 domains (10 each).
# - Tamper-evident: each capsule has self_sha256 and ledger prev_hash chaining.
# - Safe: no network, no secrets. Requires: bash, jq, sha256sum (or shasum -a 256).
#
# Usage:
#   ./capsule_compound160.sh            # mint all 160
#   ./capsule_compound160.sh all160     # same as default
#   ./capsule_compound160.sh <domain>   # one of: liquidity trading lending insurance gaming-mc saas-mc iaas-mc paas-mc ras-mc gov-mc culture-mc edu health ai energy global
# Env:
#   LEDGER=ledger_main.jsonl ROOT=out/meshcredit_capsules ./capsule_compound160.sh

set -euo pipefail

# Add debug output
set -x

SET="${1:-all160}"
LEDGER="${LEDGER:-ledger_main.jsonl}"
ROOT="${ROOT:-out/meshcredit_capsules}"
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
  if [[ -n "$last_hash" ]]; then
    if echo "$last_hash" | jq -e . >/dev/null 2>&1; then
      prev=$(echo "$last_hash" | jq -r '.entry_hash // "genesis"')
    else
      echo "Warning: Last line in ledger is not valid JSON, using genesis instead"
    fi
  fi
fi

# ---- domains → items (Name|Description) ----
declare -A CAPS

CAPS["liquidity"]=$'Yield Capsule|Staked ROI\nLiquidity Loop|Recycled credit\nCompounding Bond|Auto-scale ROI\nCross-Pool Capsule|Bridged pools\nYield ETF|Bundle yields\nStable Yield|Stable ROI\nYield Futures|Forward ROI\nROI Swap|Swap rights\nInfinite Loop|Perpetual compounding\nROI Crown|Annual top yield'
CAPS["trading"]=$'DEX Share|Exchange equity\nFee Split|DEX fees\nSpread Bonds|Spread ROI\nArbitrage|Arb capsule\nLeverage|Leverage credit\nShort Capsule|Shorts\nPerp Capsule|Perpetuals\nMarket-Maker|LP capsule\nFlash Credit|Flash loan\nDEX Crown|Trader king'
CAPS["lending"]=$'Credit Line|Revolving loan\nMortgage|Asset-backed loan\nPayday|Instant loan\nCredit Score|Rating capsule\nRisk Bond|Insure borrowers\nMargin Capsule|Leverage credit\nCollateral Vault|Collateral store\nLoan Crowns|Lending guilds\nMicroLoan|Tiny loans\nLending Thrones|Lender kings'
CAPS["insurance"]=$'Coverage Capsule|Insurance\nMesh Pool|Shared coverage\nDrift Insurance|Agent drift\nCrash Bond|Market crash\nWeather Credit|Climate risk\nHealth Mesh|Health insurance\nSafety Fund|Safety pool\nFraud Vault|Fraud logs\nBlack Swan|Rare-event payout\nRisk Thrones|Risk rulers'
CAPS["gaming-mc"]=$'Loot Bonds|Loot ROI\nPvP Stakes|Battle ROI\nSpeedrun ROI|WR prize\nClan Treasury|Guild fund\neSports Mesh|Tournament ROI\nSeasonal Vault|Prize pools\nRNG Drop|Fair drops\nVictory Crowns|Champion prize\nQuest Tokens|Quest rewards\nGame Thrones|Esports rulers'
CAPS["saas-mc"]=$'Sub ROI|SaaS revenue\nSeat Credit|Seat monetized\nUpgrade Bond|Upgrade rights\nReferral Credit|Growth credits\nUsage Token|Metered SaaS\nFeature Rights|Toggle capsule\nApp Loyalty|Loyalty ROI\nChurn Insurance|Churn hedge\nUpsell Vault|Upsell fund\nSaaS Thrones|App ruler'
CAPS["iaas-mc"]=$'VM Credits|Compute credits\nBandwidth Bonds|Bandwidth ROI\nPower Mesh|Power ROI\nEdge Compute|Edge ROI\nQuantum Lease|Quantum slots\nSLA Bond|Uptime ROI\nDisaster Pool|Disaster fund\nEnergy Crown|Energy ROI\nCarbon Credits|Offset capsules\nInfra Thrones|Infra rulers'
CAPS["paas-mc"]=$'API Keys|Quota capsules\nPlugin Rights|Plugin slots\nDebug Vault|Debug ROI\nDev Guild|Dev guild ROI\nCI Badge Bonds|CI coverage\nHackathon Pool|Hackathon fund\nDoc Proof|Docs sealed\nBuilder Rewards|Builder ROI\nSDK Crown|SDK award\nDev Thrones|Dev ruler'
CAPS["ras-mc"]=$'Clone Credit|Clone ROI\nMesh Link|Agent links\nSkill Bond|Skill ROI\nDrift Pool|Drift hedge\nJury Credits|Jury ROI\nMemory Seals|Memory ROI\nSwarm ROI|Swarm pool\nEvolution Pool|Recursive ROI\nAgent Thrones|Agent rulers\nAI Crown|AI leader'
CAPS["gov-mc"]=$'Vote Bonds|Vote ROI\nQuorum Credits|Quorum ROI\nVeto Rights|Monetized veto\nProposal Bonds|Proposal cost\nTerm Vaults|Term fund\nTreasury Mesh|Treasury ROI\nAudit Credit|Audit ROI\nCouncil Crowns|Council ROI\nCivic Credit|Citizen ROI\nGov Thrones|Gov rulers'
CAPS["culture-mc"]=$'Music Royalties|Music ROI\nFilm Credits|Film ROI\nArt Bonds|Art ROI\nFestival Tokens|Festival ROI\nMyth Rights|Myth ROI\nLore Chains|Lore ROI\nStory Credit|Writer ROI\nLegend Crowns|Legend ROI\nHeritage Mesh|Heritage ROI\nFounder Thrones|Founder ROI'
CAPS["edu"]=$'Learning Credits|Edu ROI\nPuzzle Tokens|Puzzle ROI\nSchool Vault|School ROI\nTeacher Bonds|Teacher ROI\nKid Quests|Kid ROI\nKnowledge Rights|Knowledge ROI\nStudy Mesh|Study ROI\nEducation Crowns|Edu awards\nKid Thrones|Kids leaders\nFamily Mesh|Family ROI'
CAPS["health"]=$'Fitness Credits|Workout ROI\nDiet Bonds|Diet ROI\nSleep Tokens|Sleep ROI\nHealth Pools|Group ROI\nTherapy Rights|Therapy ROI\nWellness Crown|Wellness ROI\nMeditation Mesh|Meditation ROI\nBio Data Rights|Data ROI\nHealth Thrones|Health rulers\nDNA Mesh|DNA ROI'
CAPS["ai"]=$'Model Rights|Model ROI\nTraining Credits|Training ROI\nDataset Bonds|Dataset ROI\nAPI Calls|API ROI\nFine-Tune ROI|Fine-tune ROI\nModel Crowns|Model awards\nAI Futures|Model futures\nPatent Capsules|IP ROI\nAI Thrones|AI rulers\nResearch Mesh|Research ROI'
CAPS["energy"]=$'Solar Credits|Solar ROI\nWind Bonds|Wind ROI\nHydro Mesh|Hydro ROI\nNuclear Credits|Nuclear ROI\nEnergy Pools|Energy fund\nGrid Crowns|Grid award\nCarbon Mesh|Carbon ROI\nBattery Bonds|Battery ROI\nGreen Thrones|Green ROI\nEnergy Royals|Energy crowns'
CAPS["global"]=$'Border Rights|Border ROI\nCurrency Mesh|Currency ROI\nTrade Bonds|Trade ROI\nTariff Proofs|Tariff ROI\nPort Crowns|Port ROI\nGlobal Thrones|World rulers\nDiplomacy Mesh|Diplomacy ROI\nPeace Bonds|Peace ROI\nWar Insurance|Conflict hedge\nWorld Crown|World ruler'

ORDER=(liquidity trading lending insurance gaming-mc saas-mc iaas-mc paas-mc ras-mc gov-mc culture-mc edu health ai energy global)

mint_domain () {
  local domain="$1"
  local items="${CAPS[$domain]:-}"
  [[ -n "$items" ]] || { echo "Unknown domain: $domain" >&2; exit 2; }

  local idx=0
  while IFS=$'\n' read -r line; do
    [[ -n "$line" ]] || continue
    IFS='|' read -r name desc <<<"$line"
    ((idx++))
    local id="MC-${domain^^}-$(printf '%02d' "$idx")"
    local ts; ts="$(now)"

    # body without self_sha256
    local body; body=$(jq -nc --arg id "$id" --arg ts "$ts" --arg d "$domain" --arg name "$name" --arg desc "$desc" --arg prev "$prev" \
      '{capsule_id:$id,timestamp:$ts,domain:$d,name:$name,description:$desc,provenance:{prev_hash:$prev,meshcredit:true}}')

    # hash over body
    local h; h=$(echo -n "$body" | sha)

    # full capsule
    local capsule; capsule=$(echo -n "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

    # write capsule
    echo "$capsule" > "$ROOT/$id.json"

    # append ledger entry (hash-chained)
    jq -nc --arg ts "$ts" --arg id "$id" --arg h "$h" --arg prev "$prev" \
      '{ts:$ts,capsule_id:$id,entry_hash:$h,prev_hash:$prev}' >> "$LEDGER"

    prev="$h"
    printf "✅ %s — %s: %s\n" "$id" "$domain" "$name"
  done <<< "$items"
}

echo "=== MeshCredit Forge (160) → ROOT=$ROOT LEDGER=$LEDGER ==="

if [[ "$SET" == "all160" ]]; then
  for d in "${ORDER[@]}"; do mint_domain "$d"; done
else
  # allow single domain run
  mint_domain "$SET"
fi

echo "🔒 Done. Ledger tip: $prev"
