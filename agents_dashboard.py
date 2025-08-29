import json
import os
from glob import glob

import pandas as pd
import streamlit as st

st.set_page_config(page_title="EpochCore Agents Dashboard", layout="wide")
st.title("EpochCore Agents Dashboard")

capsule_dir = "out/capsules"
ledger_file = "ledger_main.jsonl"

# #!/usr/bin/env bash
# EpochCore — MeshCapsules Forge (200 Compounding Capsules)
# Mints 200 new capsules (20 domains × 10 each), hash-chained into ledger_main.jsonl.
# Safe: no network, no secrets. Requires: bash, jq, sha256sum (or shasum -a 256).
#
# #!/usr/bin/env bash
# EpochCore — MeshCapsules Forge (200 Compounding Capsules)
# Mints 200 new capsules (20 domains × 10 each), hash-chained into ledger_main.jsonl.
# Safe: no network, no secrets. Requires: bash, jq, sha256sum (or shasum -a 256).
#
# Usage:
#   ./capsule_compound200.sh            # mint all 200
#   ./capsule_compound200.sh all200     # same
#   ./capsule_compound200.sh <domain>   # one domain only (see ORDER list)

set -euo pipefail

SET="${1:-all200}"
LEDGER="${LEDGER:-ledger_main.jsonl}"
ROOT="${ROOT:-out/meshcapsules_200}"
mkdir -p "$ROOT"

# --- sha tool shim ---
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

# --- load ledger tip (prev hash) ---
prev="genesis"
if [[ -s "$LEDGER" ]]; then
  last_line="$(tail -n 500 "$LEDGER" | awk 'NF{last=$0} END{print last}')"
  if [[ -n "$last_line" ]] && echo "$last_line" | jq -e . >/dev/null 2>&1; then
    prev="$(echo "$last_line" | jq -r '.entry_hash // "genesis"')"
  fi
fi

# --- Domains (20) → 10 capsules each (Name|Description) ---
declare -A CAPS

CAPS["revops"]=$'Pipeline Compounding|Auto-routes revenue to highest-ROI repos\nARR Escalator|Seasonal yield ladder bound to governance caps\nQuota Mesh|Contributor quotas tokenize into dividend rights\nRevenue Split Orchestrator|Programmable splits to teams via ledger\nUpsell Trigger Bonds|Feature usage mints upsell payouts\nRetention Crown|Loyalty-weighted revenue crown each season\nChurn Hedge Capsule|Anti-churn insurance backing cashflows\nPrice Experiment Ledger|PR-based pricing trials, sealed & shared\nRev Forecast Oracle|Model-driven ARR predictions feed treasury\nCash Flow ETF|Bundle of product flows packaged as capsule'
CAPS["growth"]=$'K-Factor Booster|Referral ROI compounding across repos\nOnramp A/B Capsule|Growth tests with revenue share\nInvite Credit Loop|Invites mint credits that vest on usage\nVirality Split|Creator/guild rev-splits ledgered by hash\nFunnel Heatmap Seal|Growth telemetry → governance signals\nActivation Ladder|Time-locked perks for D1/D7 milestones\nReactivation Bonds|Dormant users funded by bounty bonds\nWaitlist Futures|Pre-launch demand tokenized\nGrowth Guild Capsule|Community-led growth with treasury\nCampaign ROI Oracle|Attribution oracle drives spend'
CAPS["partner"]=$'Partner RevShare Keys|Per-partner signed revenue keys\nCo-Sell Capsule|Joint pipeline ledger + payout\nIntegration ETF|Bundle of partner integrations\nMarketplace Royalty|Storefront fees flow to capsule\nPartner SLA Bond|SLA-backed payouts for shared deals\nCo-Marketing Vault|Campaign funds with proof-of-spend\nAlliance Governance|Multi-sig council for partner merges\nChannel Booster|Tiered incentives via MeshCredit\nJoint Roadmap Vote|Shared feature votes on-chain\nPartner Crown|Seasonal top partner capsule'
CAPS["ads"]=$'Attention Futures|Impression futures w/ fraud guards\nCPC Floor Bond|Price floors stabilized by treasury\nCleanRoom Capsule|Privacy-safe attribution proofs\nCreator Ad Rails|Rev-share ad capsule for creators\nCPA Reward Pools|Pay-on-outcome vaults\nBrand Safety Oracle|Risk score gates spend\nAd Slot NFT|Schedule/time-slot token with receipts\nBudget Rebalance Bot|Auto-shifts to best ROAS repos\nFrequency Cap Seal|Fairness guardrail in ledger\nAd Market Crown|Top ROAS crown capsule'
CAPS["ugc"]=$'UGC Royalty Chains|Creator royalties enforced at merge\nBlueprint Remix Rights|Remixable license capsule\nUGC Fraud Sentinel|Sybil detector slashes bad actors\nTemplate ETF|Top templates bundled w/ yield\nCosmetic Forge|UGC cosmetics monetized w/o P2W\nUGC SLA Support|Priority queues for creators\nSeasonal UGC Pass|Time-limited creator perks\nCanon Lore Registry|Official canon gated by vote\nCreator Guild Vault|Shared treasury for UGC\nUGC Crown|Season MVP creator capsule'
CAPS["securityx"]=$'Supply-Chain Lock|Sig-verification for deps at merge\nKey Rotation Capsule|Governance-timed key rotations\nSecretless Runner|Ephemeral tokens w/ attest proofs\nAttack Surface Bond|Bounty pool for CVE closure\nZero-Trust Mesh|Policy capsule gating actions\nAnomaly Beacon|OTel-based anomaly triggers\nIncident Replay Seal|Postmortem + fix proofs\nBreakglass Multisig|Timed emergency powers\nPackage Quarantine|Auto-sandbox for new deps\nSecurity Crown|Season security king'
CAPS["compliancex"]=$'Policy TimeLock|Change windows on regulated paths\nRegion Gate Capsule|Geo-policy runtime proofs\nAudit Evidence Vault|Immutable trail for audits\nData Retention Seal|TTL-driven lifecycle rules\nPII Redaction Capsule|Deterministic masking proofs\nConsent Ledger|Granular consent receipts\nLicense Guard|OSS license compliance checks\nExport Control Gate|Runtime export checks\nReg Report Capsule|Periodic filings sealed\nCompliance Crown|Top compliance score'
CAPS["onchain"]=$'Gasless Entry Mesh|4337 paymaster for UX\nVault Timelock|Upgradeable contracts with delays\nSplit Router|Revenue splitter contract\nVRF Drop Capsule|Provably fair reveals\nMerkle Allowlist|Fair mints without wars\nFee Switch Bond|Governed fee toggles\nBridge Receipt Seal|Cross-domain proof capsule\nStaking Lock Ladder|Tiered time-lock perks\nOracle Guardrail|Multi-source sanity checks\nOnchain Crown|Best reliability chain'
CAPS["chainops"]=$'Chain Health Oracle|Liveness/latency signals\nMEV Shield Capsule|Batching + privacy lanes\nGas Budget Sentinel|Per-action spend caps\nFork Monitor Seal|Fork detection + policy\nNode Diversity ETF|Client/region distribution\nIndexer SLA Bond|Query uptime staking\nSnapshot Attestor|State snapshot proofs\nUpgrade Ceremony|Signed release rituals\nRollup Cost Optimizer|Batching ROI agent\nOps Crown|Best chain-ops capsule'
CAPS["observability"]=$'Trace Mesh Capsule|Cross-repo trace IDs\nCausal Chain Seal|because-chain linking outputs\nGolden Signal Bonds|SLO-backed alerts\nDrift Heat Index|Model/data drift index\nDark Launch Receipt|Canary proofs in ledger\nError Budget Bank|Spend SLO like currency\nPerf Ladder|p95/p99 tiers → perks\nBlackbox Probe Guild|Synthetic checks network\nSnapshot TimeCapsule|Perf snapshots sealed\nObs Crown|Top SLO adherence'
CAPS["quality"]=$'Flake Slayer Bond|Flaky test bounties\nCoverage Ladder|Tiered rewards for % coverage\nSpec Truth Capsule|Spec-as-law with proofs\nBug Bounty Mesh|Priority bug funding pool\nHermetic Build Seal|Repro builds proof\nQA Guild Capsule|Reviewer pool incentives\nRegression Oracle|Trend detector triggers\nRelease Gate Capsule|Ship only if gates pass\nFixture Forge|Shared fixtures w/ royalties\nQuality Crown|Season QA champion'
CAPS["mlopsx"]=$'Dataset Royalty|Data creators paid per use\nLabel Bond|Quality-weighted label payouts\nEval Mesh|Eval suites as capsules\nSafety RedTeam|Adversarial test corpus\nHallucination Hedge|Penalty pool for errors\nBias Audit Seal|Fairness reports ledgered\nFeature Store ETF|Reusable features bundle\nModel Card Attest|Signed model docs\nRollback Switch|Versioned rollback policy\nMLOps Crown|Top model reliability'
CAPS["swarmx"]=$'Swarm Credit Pool|Agents share credit budget\nTask Market Capsule|Bids = utility/cost\nSkill Exchange|Agent skill rentals\nReputation Ladder|Reliability → more work\nGossip Pulse Seal|Heartbeat & gossip cache\nQuorum Commit|2-of-3 safety votes\nCounterfactual Scout|Risk scan pre-commit\nBatch Synth Agent|Adaptive batching node\nCircuit Breaker Mesh|Trip + heal patterns\nSwarm Crown|Top swarm ROI'
CAPS["memoryx"]=$'Vector Ledger|Shared memory with CRDT\nBlackboard Notes|Merge-safe artifacts\nOutcome Replay|Traces → outcomes map\nDelta Journal|Diff+reason updates\nWorld Model Tome|Documented proposals\nRecall Budget|Token budget vault\nMemory Pin Capsule|Hot cache pins\nForgetting Policy|TTL + decay controls\nProvenance Graph|Who influenced what\nMemory Crown|Best recall impact'
CAPS["oraclex"]=$'Market Data Pipe|Price/feed capsule\nTraffic Oracle|Web analytics feed\nChurn Oracle|Retention metrics feed\nRisk Score Pipe|Fraud/abuse scores\nWeather Oracle|Climate inputs\nCompliance Oracle|Reg updates feed\nNews Sentiment|Media sentiment feed\nCost Index|Infra/ads cost feed\nQuality Index|Defect trend feed\nOracle Crown|Most accurate oracle'
CAPS["arbitragex"]=$'Spread Hunter|Cross-vault spread capture\nLatency Arb|Region latency arbitrage\nDemand Rebalance|Hot vault → cold vault\nFee Tier Switch|Optimal fee band chooser\nInventory Flip|Capsule secondary desk\nYield Hop|Pool-to-pool compounding\nBasis Trade|Deriv vs spot capsule\nVolatility Hedge|Straddle/strangle pack\nReorg Hedge|Chain risk hedge\nArb Crown|Season top arb'
CAPS["creatorx"]=$'Season Pass Royalty|Creator pass payouts\nDrops Scheduler|Timed drops with VRF\nCollab Split Capsule|Multi-creator splits\nFan Club Vault|Membership → perks\nTip Credit Loop|Tipping mints credits\nUGC Moderation Bond|Deposit for fairness\nRemix Registry|Lineage + share back\nCreator Ad Slots|Self-serve paid slots\nMerch Bridge|IRL linkage proofs\nCreator Crown|Top earner creator'
CAPS["brandx"]=$'Trademark Registry|Brand use allowlist\nLore Bible Seal|Brand canon guard\nCo-Brand Capsule|Joint brand agreements\nSponsorship Bond|Deliverables escrowed\nBrand Safety Map|Risk zones + gates\nIP License Keys|Programmable license\nAsset Vault|Brand assets with rights\nCrisis Playbook|Pre-approved responses\nSentiment Oracle|Brand health feed\nBrand Crown|Season brand leader'
CAPS["loyaltyx"]=$'Tier Ladder Capsule|Bronze→Diamond perks\nStreak Bond|Daily streak → yield\nQuest Club|Missions mint credits\nCashback Mesh|Spend → credit loop\nStatus Match Bridge|Import external tiers\nRedemption Vault|Inventory-backed rewards\nReferral Guild|Team-based referrals\nAnniversary Drop|Milestone gifts\nVIP Handshake|Invite-only perks\nLoyalty Crown|Top loyalty score'
CAPS["marketintel"]=$'Repo Score Index|Composite performance score\nFeature Heat Index|Usage heat → roadmap\nPrice Elasticity Probe|Demand curve tests\nChurn Root Cause|Attribution capsule\nCompetitor Radar|Signals watch capsule\nSegment Profit Map|Unit economics per segment\nForecast Ensemble|Model-blended outlook\nROI Leaderboard|Public ROI ranks\nSignal Bounty|Pay for missing signals\nIntel Crown|Top actionable intel'

# Mint order
ORDER=(revops growth partner ads ugc securityx compliancex onchain chainops observability quality mlopsx swarmx memoryx oraclex arbitragex creatorx brandx loyaltyx marketintel)

# --- minting ---
mint_domain () {
  local domain="$1"
  local items="${CAPS[$domain]:-}"
  [[ -n "$items" ]] || { echo "Unknown domain: $domain" >&2; exit 2; }

  local idx=0
  while IFS=$'\n' read -r line; do
    [[ -n "$line" ]] || continue
    IFS='|' read -r name desc <<<"$line"
    ((idx++))
    local id="MX-${domain^^}-$(printf '%02d' "$idx")"
    local ts; ts="$(now)"

    # Body (no self_sha256)
    local body; body=$(jq -nc \
      --arg id "$id" --arg ts "$ts" --arg d "$domain" \
      --arg name "$name" --arg desc "$desc" --arg prev "$prev" \
      --argjson monet '{"roi":"compounding","meshcredit":true,"payouts":["dividends","royalties","splits"]}' \
      --argjson gov   '{"quorum":true,"timelock":true,"multisig":true,"replay_guard":true}' \
      --argjson scale '{"cross_repo":true,"ha":true,"sync":true}' \
      '{capsule_id:$id,timestamp:$ts,domain:$d,name:$name,description:$desc,
        monetization:$monet,governance:$gov,scalability:$scale,
        provenance:{prev_hash:$prev,author:"Founder+Agent",schema:"v1"}}')

    local h; h=$(echo -n "$body" | sha)
    local capsule; capsule=$(echo -n "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

    echo "$capsule" > "$ROOT/$id.json"
    jq -nc --arg ts "$ts" --arg id "$id" --arg h "$h" --arg prev "$prev" \
      '{ts:$ts,capsule_id:$id,entry_hash:$h,prev_hash:$prev}' >> "$LEDGER"

    prev="$h"
    printf "✅ %s — %s: %s\n" "$id" "$domain" "$name"
  done <<< "$items"
}

echo "=== MeshCapsules Forge (200) → ROOT=$ROOT LEDGER=$LEDGER ==="

if [[ "$SET" == "all200" ]]; then
  for d in "${ORDER[@]}"; do mint_domain "$d"; done
else
  mint_domain "$SET"
fi

echo "🔒 Done. Ledger tip: $prev"chmod +x capsule_compound200.sh
./capsule_compound200.sh          # mint all 200
# or a single domain:
./capsule_compound200.sh mlopsx

set -euo pipefail

SET="${1:-all200}"
LEDGER="${LEDGER:-ledger_main.jsonl}"
ROOT="${ROOT:-out/meshcapsules_200}"
mkdir -p "$ROOT"

# --- sha tool shim ---
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

# --- load ledger tip (prev hash) ---
prev="genesis"
if [[ -s "$LEDGER" ]]; then
  last_line="$(tail -n 500 "$LEDGER" | awk 'NF{last=$0} END{print last}')"
  if [[ -n "$last_line" ]] && echo "$last_line" | jq -e . >/dev/null 2>&1; then
    prev="$(echo "$last_line" | jq -r '.entry_hash // "genesis"')"
  fi
fi

# --- Domains (20) → 10 capsules each (Name|Description) ---
declare -A CAPS

CAPS["revops"]=$'Pipeline Compounding|Auto-routes revenue to highest-ROI repos\nARR Escalator|Seasonal yield ladder bound to governance caps\nQuota Mesh|Contributor quotas tokenize into dividend rights\nRevenue Split Orchestrator|Programmable splits to teams via ledger\nUpsell Trigger Bonds|Feature usage mints upsell payouts\nRetention Crown|Loyalty-weighted revenue crown each season\nChurn Hedge Capsule|Anti-churn insurance backing cashflows\nPrice Experiment Ledger|PR-based pricing trials, sealed & shared\nRev Forecast Oracle|Model-driven ARR predictions feed treasury\nCash Flow ETF|Bundle of product flows packaged as capsule'
CAPS["growth"]=$'K-Factor Booster|Referral ROI compounding across repos\nOnramp A/B Capsule|Growth tests with revenue share\nInvite Credit Loop|Invites mint credits that vest on usage\nVirality Split|Creator/guild rev-splits ledgered by hash\nFunnel Heatmap Seal|Growth telemetry → governance signals\nActivation Ladder|Time-locked perks for D1/D7 milestones\nReactivation Bonds|Dormant users funded by bounty bonds\nWaitlist Futures|Pre-launch demand tokenized\nGrowth Guild Capsule|Community-led growth with treasury\nCampaign ROI Oracle|Attribution oracle drives spend'
CAPS["partner"]=$'Partner RevShare Keys|Per-partner signed revenue keys\nCo-Sell Capsule|Joint pipeline ledger + payout\nIntegration ETF|Bundle of partner integrations\nMarketplace Royalty|Storefront fees flow to capsule\nPartner SLA Bond|SLA-backed payouts for shared deals\nCo-Marketing Vault|Campaign funds with proof-of-spend\nAlliance Governance|Multi-sig council for partner merges\nChannel Booster|Tiered incentives via MeshCredit\nJoint Roadmap Vote|Shared feature votes on-chain\nPartner Crown|Seasonal top partner capsule'
CAPS["ads"]=$'Attention Futures|Impression futures w/ fraud guards\nCPC Floor Bond|Price floors stabilized by treasury\nCleanRoom Capsule|Privacy-safe attribution proofs\nCreator Ad Rails|Rev-share ad capsule for creators\nCPA Reward Pools|Pay-on-outcome vaults\nBrand Safety Oracle|Risk score gates spend\nAd Slot NFT|Schedule/time-slot token with receipts\nBudget Rebalance Bot|Auto-shifts to best ROAS repos\nFrequency Cap Seal|Fairness guardrail in ledger\nAd Market Crown|Top ROAS crown capsule'
CAPS["ugc"]=$'UGC Royalty Chains|Creator royalties enforced at merge\nBlueprint Remix Rights|Remixable license capsule\nUGC Fraud Sentinel|Sybil detector slashes bad actors\nTemplate ETF|Top templates bundled w/ yield\nCosmetic Forge|UGC cosmetics monetized w/o P2W\nUGC SLA Support|Priority queues for creators\nSeasonal UGC Pass|Time-limited creator perks\nCanon Lore Registry|Official canon gated by vote\nCreator Guild Vault|Shared treasury for UGC\nUGC Crown|Season MVP creator capsule'
CAPS["securityx"]=$'Supply-Chain Lock|Sig-verification for deps at merge\nKey Rotation Capsule|Governance-timed key rotations\nSecretless Runner|Ephemeral tokens w/ attest proofs\nAttack Surface Bond|Bounty pool for CVE closure\nZero-Trust Mesh|Policy capsule gating actions\nAnomaly Beacon|OTel-based anomaly triggers\nIncident Replay Seal|Postmortem + fix proofs\nBreakglass Multisig|Timed emergency powers\nPackage Quarantine|Auto-sandbox for new deps\nSecurity Crown|Season security king'
CAPS["compliancex"]=$'Policy TimeLock|Change windows on regulated paths\nRegion Gate Capsule|Geo-policy runtime proofs\nAudit Evidence Vault|Immutable trail for audits\nData Retention Seal|TTL-driven lifecycle rules\nPII Redaction Capsule|Deterministic masking proofs\nConsent Ledger|Granular consent receipts\nLicense Guard|OSS license compliance checks\nExport Control Gate|Runtime export checks\nReg Report Capsule|Periodic filings sealed\nCompliance Crown|Top compliance score'
CAPS["onchain"]=$'Gasless Entry Mesh|4337 paymaster for UX\nVault Timelock|Upgradeable contracts with delays\nSplit Router|Revenue splitter contract\nVRF Drop Capsule|Provably fair reveals\nMerkle Allowlist|Fair mints without wars\nFee Switch Bond|Governed fee toggles\nBridge Receipt Seal|Cross-domain proof capsule\nStaking Lock Ladder|Tiered time-lock perks\nOracle Guardrail|Multi-source sanity checks\nOnchain Crown|Best reliability chain'
CAPS["chainops"]=$'Chain Health Oracle|Liveness/latency signals\nMEV Shield Capsule|Batching + privacy lanes\nGas Budget Sentinel|Per-action spend caps\nFork Monitor Seal|Fork detection + policy\nNode Diversity ETF|Client/region distribution\nIndexer SLA Bond|Query uptime staking\nSnapshot Attestor|State snapshot proofs\nUpgrade Ceremony|Signed release rituals\nRollup Cost Optimizer|Batching ROI agent\nOps Crown|Best chain-ops capsule'
CAPS["observability"]=$'Trace Mesh Capsule|Cross-repo trace IDs\nCausal Chain Seal|because-chain linking outputs\nGolden Signal Bonds|SLO-backed alerts\nDrift Heat Index|Model/data drift index\nDark Launch Receipt|Canary proofs in ledger\nError Budget Bank|Spend SLO like currency\nPerf Ladder|p95/p99 tiers → perks\nBlackbox Probe Guild|Synthetic checks network\nSnapshot TimeCapsule|Perf snapshots sealed\nObs Crown|Top SLO adherence'
CAPS["quality"]=$'Flake Slayer Bond|Flaky test bounties\nCoverage Ladder|Tiered rewards for % coverage\nSpec Truth Capsule|Spec-as-law with proofs\nBug Bounty Mesh|Priority bug funding pool\nHermetic Build Seal|Repro builds proof\nQA Guild Capsule|Reviewer pool incentives\nRegression Oracle|Trend detector triggers\nRelease Gate Capsule|Ship only if gates pass\nFixture Forge|Shared fixtures w/ royalties\nQuality Crown|Season QA champion'
CAPS["mlopsx"]=$'Dataset Royalty|Data creators paid per use\nLabel Bond|Quality-weighted label payouts\nEval Mesh|Eval suites as capsules\nSafety RedTeam|Adversarial test corpus\nHallucination Hedge|Penalty pool for errors\nBias Audit Seal|Fairness reports ledgered\nFeature Store ETF|Reusable features bundle\nModel Card Attest|Signed model docs\nRollback Switch|Versioned rollback policy\nMLOps Crown|Top model reliability'
CAPS["swarmx"]=$'Swarm Credit Pool|Agents share credit budget\nTask Market Capsule|Bids = utility/cost\nSkill Exchange|Agent skill rentals\nReputation Ladder|Reliability → more work\nGossip Pulse Seal|Heartbeat & gossip cache\nQuorum Commit|2-of-3 safety votes\nCounterfactual Scout|Risk scan pre-commit\nBatch Synth Agent|Adaptive batching node\nCircuit Breaker Mesh|Trip + heal patterns\nSwarm Crown|Top swarm ROI'
CAPS["memoryx"]=$'Vector Ledger|Shared memory with CRDT\nBlackboard Notes|Merge-safe artifacts\nOutcome Replay|Traces → outcomes map\nDelta Journal|Diff+reason updates\nWorld Model Tome|Documented proposals\nRecall Budget|Token budget vault\nMemory Pin Capsule|Hot cache pins\nForgetting Policy|TTL + decay controls\nProvenance Graph|Who influenced what\nMemory Crown|Best recall impact'
CAPS["oraclex"]=$'Market Data Pipe|Price/feed capsule\nTraffic Oracle|Web analytics feed\nChurn Oracle|Retention metrics feed\nRisk Score Pipe|Fraud/abuse scores\nWeather Oracle|Climate inputs\nCompliance Oracle|Reg updates feed\nNews Sentiment|Media sentiment feed\nCost Index|Infra/ads cost feed\nQuality Index|Defect trend feed\nOracle Crown|Most accurate oracle'
CAPS["arbitragex"]=$'Spread Hunter|Cross-vault spread capture\nLatency Arb|Region latency arbitrage\nDemand Rebalance|Hot vault → cold vault\nFee Tier Switch|Optimal fee band chooser\nInventory Flip|Capsule secondary desk\nYield Hop|Pool-to-pool compounding\nBasis Trade|Deriv vs spot capsule\nVolatility Hedge|Straddle/strangle pack\nReorg Hedge|Chain risk hedge\nArb Crown|Season top arb'
CAPS["creatorx"]=$'Season Pass Royalty|Creator pass payouts\nDrops Scheduler|Timed drops with VRF\nCollab Split Capsule|Multi-creator splits\nFan Club Vault|Membership → perks\nTip Credit Loop|Tipping mints credits\nUGC Moderation Bond|Deposit for fairness\nRemix Registry|Lineage + share back\nCreator Ad Slots|Self-serve paid slots\nMerch Bridge|IRL linkage proofs\nCreator Crown|Top earner creator'
CAPS["brandx"]=$'Trademark Registry|Brand use allowlist\nLore Bible Seal|Brand canon guard\nCo-Brand Capsule|Joint brand agreements\nSponsorship Bond|Deliverables escrowed\nBrand Safety Map|Risk zones + gates\nIP License Keys|Programmable license\nAsset Vault|Brand assets with rights\nCrisis Playbook|Pre-approved responses\nSentiment Oracle|Brand health feed\nBrand Crown|Season brand leader'
CAPS["loyaltyx"]=$'Tier Ladder Capsule|Bronze→Diamond perks\nStreak Bond|Daily streak → yield\nQuest Club|Missions mint credits\nCashback Mesh|Spend → credit loop\nStatus Match Bridge|Import external tiers\nRedemption Vault|Inventory-backed rewards\nReferral Guild|Team-based referrals\nAnniversary Drop|Milestone gifts\nVIP Handshake|Invite-only perks\nLoyalty Crown|Top loyalty score'
CAPS["marketintel"]=$'Repo Score Index|Composite performance score\nFeature Heat Index|Usage heat → roadmap\nPrice Elasticity Probe|Demand curve tests\nChurn Root Cause|Attribution capsule\nCompetitor Radar|Signals watch capsule\nSegment Profit Map|Unit economics per segment\nForecast Ensemble|Model-blended outlook\nROI Leaderboard|Public ROI ranks\nSignal Bounty|Pay for missing signals\nIntel Crown|Top actionable intel'

# Mint order
ORDER=(revops growth partner ads ugc securityx compliancex onchain chainops observability quality mlopsx swarmx memoryx oraclex arbitragex creatorx brandx loyaltyx marketintel)

# --- minting ---
mint_domain () {
  local domain="$1"
  local items="${CAPS[$domain]:-}"
  [[ -n "$items" ]] || { echo "Unknown domain: $domain" >&2; exit 2; }

  local idx=0
  while IFS=$'\n' read -r line; do
    [[ -n "$line" ]] || continue
    IFS='|' read -r name desc <<<"$line"
    ((idx++))
    local id="MX-${domain^^}-$(printf '%02d' "$idx")"
    local ts; ts="$(now)"

    # Body (no self_sha256)
    local body; body=$(jq -nc \
      --arg id "$id" --arg ts "$ts" --arg d "$domain" \
      --arg name "$name" --arg desc "$desc" --arg prev "$prev" \
      --argjson monet '{"roi":"compounding","meshcredit":true,"payouts":["dividends","royalties","splits"]}' \
      --argjson gov   '{"quorum":true,"timelock":true,"multisig":true,"replay_guard":true}' \
      --argjson scale '{"cross_repo":true,"ha":true,"sync":true}' \
      '{capsule_id:$id,timestamp:$ts,domain:$d,name:$name,description:$desc,
        monetization:$monet,governance:$gov,scalability:$scale,
        provenance:{prev_hash:$prev,author:"Founder+Agent",schema:"v1"}}')

    local h; h=$(echo -n "$body" | sha)
    local capsule; capsule=$(echo -n "$body" | jq --arg h "$h" '. + {self_sha256:$h}')

    echo "$capsule" > "$ROOT/$id.json"
    jq -nc --arg ts "$ts" --arg id "$id" --arg h "$h" --arg prev "$prev" \
      '{ts:$ts,capsule_id:$id,entry_hash:$h,prev_hash:$prev}' >> "$LEDGER"

    prev="$h"
    printf "✅ %s — %s: %s\n" "$id" "$domain" "$name"
  done <<< "$items"
}

echo "=== MeshCapsules Forge (200) → ROOT=$ROOT LEDGER=$LEDGER ==="

if [[ "$SET" == "all200" ]]; then
  for d in "${ORDER[@]}"; do mint_domain "$d"; done
else
  mint_domain "$SET"
fi

echo "🔒 Done. Ledger tip: $prev" capsules


def load_capsules():
    capsules = []
    for f in glob(os.path.join(capsule_dir, "*.json")):
        with open(f) as cf:
            try:
                capsules.append(json.load(cf))
            except Exception:
                continue
    return capsules


# Load ledger events


def load_ledger():
    events = []
    if os.path.exists(ledger_file):
        with open(ledger_file) as lf:
            for line in lf:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
    return events


capsules = load_capsules()
events = load_ledger()

st.sidebar.title("Agent & Capsule Filters")
search = st.sidebar.text_input("Search Capsule/Agent/Trigger")

if search:
    capsules = [c for c in capsules if search.lower() in str(c).lower()]
    events = [e for e in events if search.lower() in str(e).lower()]

st.subheader("Agent Capsule Metrics")
if capsules:
    df_caps = pd.DataFrame(capsules)
    st.dataframe(df_caps)
    st.bar_chart(df_caps["trigger"].value_counts())
    st.write(f"Total Capsules: {len(df_caps)}")
    st.write(f"Triggers: {df_caps['trigger'].unique().tolist()}")
    st.write(
        f"ROI Capsules: {df_caps[df_caps['trigger'].str.contains('ROI|TREASURYFLOW|MARKETCAP|PRICINGFORGE|BONUSDROP|AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )
else:
    st.write("No capsules found.")

st.subheader("Ledger Events & ROI Analytics")
if events:
    df_events = pd.DataFrame(events)
    st.dataframe(df_events)
    st.line_chart(df_events["ts"].value_counts().sort_index())
    st.bar_chart(df_events["event"].value_counts())
    st.write(f"Total Ledger Events: {len(df_events)}")
    st.write(
        f"ROI Events: {df_events[df_events['trigger'].str.contains('ROI|TREASURYFLOW|MARKETCAP|PRICINGFORGE|BONUSDROP|AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )
else:
    st.write("No ledger events found.")

st.subheader("Agent Performance & Governance")
if capsules:
    st.write(
        f"Governance Capsules: {df_caps[df_caps['trigger'].str.contains('GOVCOUNCIL|PULLREQUESTVOTE|ROLLBACKSEAL', case=False, na=False)].shape[0]}"
    )
    st.write(
        f"Mesh Expansion Capsules: {df_caps[df_caps['trigger'].str.contains('MESHSPAWN|CIVILIZATIONBLOCK', case=False, na=False)].shape[0]}"
    )
    st.write(
        f"Compound Capsules: {df_caps[df_caps['trigger'].str.contains('AUTOCOMPOUND', case=False, na=False)].shape[0]}"
    )

st.sidebar.markdown("---")
st.sidebar.write("Export capsules or ledger as JSON")
if st.sidebar.button("Export Capsules"):
    st.sidebar.download_button(
        "Download Capsules", json.dumps(capsules, indent=2), "capsules.json"
    )
if st.sidebar.button("Export Ledger"):
    st.sidebar.download_button(
        "Download Ledger", json.dumps(events, indent=2), "ledger.json"
    )
