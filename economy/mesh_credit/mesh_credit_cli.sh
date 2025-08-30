#!/usr/bin/env bash
# EpochCore — Mesh Credit CLI
# Non-custodial local wallet for Mesh Credits - universal game economy currency.
set -euo pipefail

DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ROOT="${PWD}"
LEDGER="${ROOT}/ledger_main.jsonl"
WALLET_DIR="${ROOT}/economy/wallets"
ECONOMY_DIR="${ROOT}/economy/mesh_credit"
DLC_DIR="${ROOT}/epoch_game_pack/game/meshgear"
CHAR_DIR="${ROOT}/epoch_game_pack/game/characters"

# Create directories if they don't exist
mkdir -p "${WALLET_DIR}" "${ECONOMY_DIR}"

# sha256 tool shim
if command -v sha256sum >/dev/null 2>&1; then
  SHACMD=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  SHACMD=(shasum -a 256)
else
  echo "Need sha256sum or shasum -a 256"; exit 1
fi

# ---------- helpers ----------
hex() { printf "%s" "$1" | "${SHACMD[@]}" | awk '{print $1}'; }
file_hex() { "${SHACMD[@]}" "$1" | awk '{print $1}'; }
hpart() { local H="$1" OFF="${2:-1}" LEN="${3:-8}"; echo "${H:$((OFF-1)):$LEN}"; }
h2d() { printf "%d" "0x$1"; }

# Generate a deterministic wallet key based on username and passphrase
gen_wallet_key() {
  local USER="$1" PASS="$2" SALT="MESHCREDIT|EPOCH|NONCUSTODIAL"
  hex "${USER}|${PASS}|${SALT}"
}

# Create a new wallet file
init_wallet() {
  local USER="$1" PASS="$2"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} already exists. Use 'show' to view it."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  
  cat > "${WALLET_FILE}" <<JSON
{
  "meta": {
    "created_at": "${DATE_UTC}",
    "last_accessed": "${DATE_UTC}",
    "name": "${USER}",
    "public_key": "${PUB_KEY}"
  },
  "balances": {
    "available": 1000,
    "staked": 0,
    "governance_locked": 0,
    "pending_rewards": 0
  },
  "history": [
    {
      "ts": "${DATE_UTC}",
      "type": "genesis",
      "amount": 1000,
      "description": "Welcome bonus"
    }
  ],
  "staking": {
    "positions": [],
    "rewards_claimed": 0,
    "validator_status": false
  },
  "governance": {
    "voting_power": 0,
    "proposals_created": 0,
    "votes_cast": [],
    "delegation": null
  },
  "nfts": [],
  "achievements": []
}
JSON

  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"wallet_created\",\"user\":\"${USER}\",\"public_key\":\"${PUB_KEY}\",\"initial_balance\":1000}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Wallet created for ${USER} with 1000 MESH welcome bonus"
  echo "🔑 Public Key: ${PUB_KEY}"
  echo "🧾 Recorded to ledger"
}

# Show wallet details
show_wallet() {
  local USER="$1" PASS="$2"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Update last accessed
  sed -i.bak "s/\"last_accessed\":\"[^\"]*\"/\"last_accessed\":\"${DATE_UTC}\"/" "${WALLET_FILE}" && rm "${WALLET_FILE}.bak"
  
  echo "🏦 Mesh Credit Wallet: ${USER}"
  echo "🔑 Public Key: ${PUB_KEY}"
  echo "📊 Balances:"
  
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local STAKED=$(grep -o '"staked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local GOVERNANCE=$(grep -o '"governance_locked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local PENDING=$(grep -o '"pending_rewards":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local TOTAL=$(awk "BEGIN {print ${AVAILABLE}+${STAKED}+${GOVERNANCE}+${PENDING}}")
  
  echo "   Available: ${AVAILABLE} MESH"
  echo "   Staked: ${STAKED} MESH"
  echo "   Governance: ${GOVERNANCE} MESH"
  echo "   Pending Rewards: ${PENDING} MESH"
  echo "   Total: ${TOTAL} MESH"
  echo ""
  echo "📜 Last 3 transactions:"
  grep -A 2 '"type":' "${WALLET_FILE}" | head -n 9 | sed 's/^[ \t]*/   /'
}

# Deposit USD to get MESH credits
deposit_usd() {
  local USER="$1" PASS="$2" AMOUNT="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Get exchange rate from pricing.json
  local EXCHANGE_RATE=100
  if [[ -f "${ECONOMY_DIR}/pricing.json" ]]; then
    EXCHANGE_RATE=$(grep -o '"usd_to_mesh":[^,}]*' "${ECONOMY_DIR}/pricing.json" | cut -d':' -f2)
  fi
  
  local MESH_AMOUNT=$(awk "BEGIN {print ${AMOUNT}*${EXCHANGE_RATE}}")
  
  # Update wallet balance
  local CURRENT=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local NEW_BALANCE=$(awk "BEGIN {print ${CURRENT}+${MESH_AMOUNT}}")
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${CURRENT}/\"available\":${NEW_BALANCE}/" "${WALLET_FILE}" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"deposit\",\"amount\":${MESH_AMOUNT},\"description\":\"USD to MESH conversion\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"usd_deposit\",\"user\":\"${USER}\",\"amount_usd\":${AMOUNT},\"amount_mesh\":${MESH_AMOUNT},\"exchange_rate\":${EXCHANGE_RATE}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Deposited ${AMOUNT} USD for ${MESH_AMOUNT} MESH"
  echo "💰 New balance: ${NEW_BALANCE} MESH"
  echo "🧾 Recorded to ledger"
}

# Transfer MESH to another wallet
transfer_mesh() {
  local USER="$1" PASS="$2" RECIPIENT="$3" AMOUNT="$4"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  local RECIPIENT_FILE="${WALLET_DIR}/${RECIPIENT}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  if [[ ! -f "${RECIPIENT_FILE}" ]]; then
    echo "Recipient wallet for ${RECIPIENT} not found."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Get fee from wallet_spec.json or use default
  local FEE_PERCENT=0.001
  local MIN_FEE=1
  local MAX_FEE=100
  
  if [[ -f "${ECONOMY_DIR}/wallet_spec.json" ]]; then
    FEE_PERCENT=$(grep -o '"fee_percent":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
    MIN_FEE=$(grep -o '"min_fee":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
    MAX_FEE=$(grep -o '"max_fee":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
  fi
  
  local FEE=$(awk "BEGIN {fee=${AMOUNT}*${FEE_PERCENT}; if(fee<${MIN_FEE}) fee=${MIN_FEE}; if(fee>${MAX_FEE}) fee=${MAX_FEE}; print fee}")
  local TOTAL=$(awk "BEGIN {print ${AMOUNT}+${FEE}}")
  
  # Check sender has enough balance
  local SENDER_BALANCE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${SENDER_BALANCE} < ${TOTAL}) ? 1 : 0}") )); then
    echo "⛔ Insufficient balance. You have ${SENDER_BALANCE} MESH, need ${TOTAL} MESH (including ${FEE} MESH fee)."
    return 1
  fi
  
  # Update sender wallet
  local SENDER_NEW_BALANCE=$(awk "BEGIN {print ${SENDER_BALANCE}-${TOTAL}}")
  local SENDER_TEMP="${WALLET_FILE}.tmp"
  sed "s/\"available\":${SENDER_BALANCE}/\"available\":${SENDER_NEW_BALANCE}/" "${WALLET_FILE}" > "${SENDER_TEMP}"
  
  # Add to sender history
  local SENDER_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"transfer_out\",\"amount\":-${AMOUNT},\"fee\":-${FEE},\"recipient\":\"${RECIPIENT}\",\"description\":\"Transfer to ${RECIPIENT}\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${SENDER_ENTRY}," "${SENDER_TEMP}" && rm "${SENDER_TEMP}.bak"
  mv "${SENDER_TEMP}" "${WALLET_FILE}"
  
  # Update recipient wallet
  local RECIPIENT_BALANCE=$(grep -o '"available":[^,}]*' "${RECIPIENT_FILE}" | cut -d':' -f2)
  local RECIPIENT_NEW_BALANCE=$(awk "BEGIN {print ${RECIPIENT_BALANCE}+${AMOUNT}}")
  local RECIPIENT_TEMP="${RECIPIENT_FILE}.tmp"
  sed "s/\"available\":${RECIPIENT_BALANCE}/\"available\":${RECIPIENT_NEW_BALANCE}/" "${RECIPIENT_FILE}" > "${RECIPIENT_TEMP}"
  
  # Add to recipient history
  local RECIPIENT_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"transfer_in\",\"amount\":${AMOUNT},\"sender\":\"${USER}\",\"description\":\"Transfer from ${USER}\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${RECIPIENT_ENTRY}," "${RECIPIENT_TEMP}" && rm "${RECIPIENT_TEMP}.bak"
  mv "${RECIPIENT_TEMP}" "${RECIPIENT_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"mesh_transfer\",\"sender\":\"${USER}\",\"recipient\":\"${RECIPIENT}\",\"amount\":${AMOUNT},\"fee\":${FEE}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Transferred ${AMOUNT} MESH to ${RECIPIENT}"
  echo "💸 Fee: ${FEE} MESH"
  echo "💰 New balance: ${SENDER_NEW_BALANCE} MESH"
  echo "🧾 Recorded to ledger"
}

# Stake MESH for yield
stake_mesh() {
  local USER="$1" PASS="$2" AMOUNT="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Get min stake amount from wallet_spec.json or use default
  local MIN_STAKE=100
  if [[ -f "${ECONOMY_DIR}/wallet_spec.json" ]]; then
    MIN_STAKE=$(grep -o '"min_amount":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
  fi
  
  if (( $(awk "BEGIN {print (${AMOUNT} < ${MIN_STAKE}) ? 1 : 0}") )); then
    echo "⛔ Minimum stake amount is ${MIN_STAKE} MESH."
    return 1
  fi
  
  # Check user has enough balance
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${AVAILABLE} < ${AMOUNT}) ? 1 : 0}") )); then
    echo "⛔ Insufficient balance. You have ${AVAILABLE} MESH available."
    return 1
  fi
  
  # Get current staked amount
  local STAKED=$(grep -o '"staked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  # Calculate new balances
  local NEW_AVAILABLE=$(awk "BEGIN {print ${AVAILABLE}-${AMOUNT}}")
  local NEW_STAKED=$(awk "BEGIN {print ${STAKED}+${AMOUNT}}")
  
  # Get current yield rate from yield_curve.json or use default
  local YIELD_RATE=0.04
  if [[ -f "${ECONOMY_DIR}/yield_curve.json" ]]; then
    YIELD_RATE=$(grep -o '"base_rate":[^,}]*' "${ECONOMY_DIR}/yield_curve.json" | head -1 | cut -d':' -f2)
  fi
  
  # Calculate maturity date (7 days from now)
  local MATURITY_DATE=$(date -u -d "+7 days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+7d +%Y-%m-%dT%H:%M:%SZ)
  
  # Create stake position
  local POSITION="{\"id\":\"$(hex "${USER}|${DATE_UTC}|${AMOUNT}")\",\"amount\":${AMOUNT},\"start_date\":\"${DATE_UTC}\",\"maturity_date\":\"${MATURITY_DATE}\",\"yield_rate\":${YIELD_RATE},\"status\":\"active\"}"
  
  # Update wallet file
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_AVAILABLE}/" "${WALLET_FILE}" | \
    sed "s/\"staked\":${STAKED}/\"staked\":${NEW_STAKED}/" > "${TEMP_FILE}"
  
  # Add position to staking array
  sed -i.bak "/\"positions\":\s*\[/a \\    ${POSITION}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"stake\",\"amount\":${AMOUNT},\"yield_rate\":${YIELD_RATE},\"maturity_date\":\"${MATURITY_DATE}\",\"description\":\"MESH staking position\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"mesh_stake\",\"user\":\"${USER}\",\"amount\":${AMOUNT},\"yield_rate\":${YIELD_RATE},\"maturity_date\":\"${MATURITY_DATE}\"}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Staked ${AMOUNT} MESH at ${YIELD_RATE} yield rate"
  echo "📆 Maturity date: ${MATURITY_DATE}"
  echo "💰 New staked balance: ${NEW_STAKED} MESH"
  echo "🧾 Recorded to ledger"
}

# Unstake MESH (withdraw from staking)
unstake_mesh() {
  local USER="$1" PASS="$2" POSITION_ID="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Check if position exists
  if ! grep -q "\"id\":\"${POSITION_ID}\"" "${WALLET_FILE}"; then
    echo "⛔ Staking position with ID ${POSITION_ID} not found."
    return 1
  fi
  
  # Extract position details
  local POSITION=$(grep -A 10 "\"id\":\"${POSITION_ID}\"" "${WALLET_FILE}" | sed -n '/{/,/}/p')
  local AMOUNT=$(echo "${POSITION}" | grep -o '"amount":[^,}]*' | cut -d':' -f2)
  local START_DATE=$(echo "${POSITION}" | grep -o '"start_date":"[^"]*"' | cut -d'"' -f4)
  local MATURITY_DATE=$(echo "${POSITION}" | grep -o '"maturity_date":"[^"]*"' | cut -d'"' -f4)
  local YIELD_RATE=$(echo "${POSITION}" | grep -o '"yield_rate":[^,}]*' | cut -d':' -f2)
  
  # Check if early unstake
  local EARLY_UNSTAKE=0
  local MATURITY_SECONDS=$(date -d "${MATURITY_DATE}" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "${MATURITY_DATE}" +%s)
  local NOW_SECONDS=$(date -u +%s)
  
  if [[ $NOW_SECONDS -lt $MATURITY_SECONDS ]]; then
    EARLY_UNSTAKE=1
  fi
  
  # Get early unstake penalty
  local PENALTY=0.05
  if [[ -f "${ECONOMY_DIR}/wallet_spec.json" ]]; then
    PENALTY=$(grep -o '"early_unstake_penalty":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
  fi
  
  # Calculate rewards
  local START_SECONDS=$(date -d "${START_DATE}" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "${START_DATE}" +%s)
  local DAYS_STAKED=$(( (NOW_SECONDS - START_SECONDS) / 86400 ))
  local REWARD=$(awk "BEGIN {print ${AMOUNT}*${YIELD_RATE}*${DAYS_STAKED}/365}")
  
  # Apply penalty if early unstake
  if [[ $EARLY_UNSTAKE -eq 1 ]]; then
    local PENALTY_AMOUNT=$(awk "BEGIN {print ${AMOUNT}*${PENALTY}}")
    AMOUNT=$(awk "BEGIN {print ${AMOUNT}-${PENALTY_AMOUNT}}")
    echo "⚠️ Early unstake! Penalty of ${PENALTY_AMOUNT} MESH applied."
  fi
  
  # Add reward
  local TOTAL_RETURN=$(awk "BEGIN {print ${AMOUNT}+${REWARD}}")
  
  # Update balances
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local STAKED=$(grep -o '"staked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local NEW_AVAILABLE=$(awk "BEGIN {print ${AVAILABLE}+${TOTAL_RETURN}}")
  local NEW_STAKED=$(awk "BEGIN {print ${STAKED}-${AMOUNT}}")
  
  # Create temporary file for updates
  local TEMP_FILE="${WALLET_FILE}.tmp"
  
  # Update balances
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_AVAILABLE}/" "${WALLET_FILE}" | \
    sed "s/\"staked\":${STAKED}/\"staked\":${NEW_STAKED}/" > "${TEMP_FILE}"
  
  # Update position status to "closed"
  sed -i.bak "s/\"status\":\"active\"/\"status\":\"closed\"/" "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"unstake\",\"amount\":${AMOUNT},\"reward\":${REWARD},\"early_unstake\":${EARLY_UNSTAKE},\"description\":\"Unstaked position ${POSITION_ID}\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"mesh_unstake\",\"user\":\"${USER}\",\"amount\":${AMOUNT},\"reward\":${REWARD},\"early_unstake\":${EARLY_UNSTAKE},\"days_staked\":${DAYS_STAKED}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Unstaked ${AMOUNT} MESH with ${REWARD} MESH reward"
  echo "💰 Total returned: ${TOTAL_RETURN} MESH"
  echo "💰 New available balance: ${NEW_AVAILABLE} MESH"
  echo "🧾 Recorded to ledger"
}

# Buy gear from the DLC
buy_gear() {
  local USER="$1" PASS="$2" ITEM_ID="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Check if DLC directory exists
  if [[ ! -d "${DLC_DIR}" ]]; then
    echo "⛔ DLC directory not found. Please install the Meshgear DLC first."
    return 1
  fi
  
  # Check if item exists
  local ITEM_FILE="${DLC_DIR}/${ITEM_ID}.json"
  if [[ ! -f "${ITEM_FILE}" ]]; then
    echo "⛔ Item with ID ${ITEM_ID} not found in the DLC."
    return 1
  fi
  
  # Get item details
  local ITEM_NAME=$(grep -o '"name":"[^"]*"' "${ITEM_FILE}" | cut -d'"' -f4)
  local ITEM_RARITY=$(grep -o '"rarity":"[^"]*"' "${ITEM_FILE}" | cut -d'"' -f4)
  
  # Get price based on rarity
  local PRICE=1000
  if [[ -f "${ECONOMY_DIR}/pricing.json" ]]; then
    if [[ "${ITEM_RARITY}" == "Legendary" ]]; then
      PRICE=$(grep -o '"Legendary":[^,}]*' "${ECONOMY_DIR}/pricing.json" | head -1 | cut -d':' -f2)
    elif [[ "${ITEM_RARITY}" == "Epic" ]]; then
      PRICE=$(grep -o '"Epic":[^,}]*' "${ECONOMY_DIR}/pricing.json" | head -1 | cut -d':' -f2)
    elif [[ "${ITEM_RARITY}" == "Rare" ]]; then
      PRICE=$(grep -o '"Rare":[^,}]*' "${ECONOMY_DIR}/pricing.json" | head -1 | cut -d':' -f2)
    fi
  fi
  
  # Check if user has enough balance
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${AVAILABLE} < ${PRICE}) ? 1 : 0}") )); then
    echo "⛔ Insufficient balance. You have ${AVAILABLE} MESH, item costs ${PRICE} MESH."
    return 1
  fi
  
  # Update wallet balance
  local NEW_BALANCE=$(awk "BEGIN {print ${AVAILABLE}-${PRICE}}")
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_BALANCE}/" "${WALLET_FILE}" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"purchase\",\"amount\":-${PRICE},\"item_id\":\"${ITEM_ID}\",\"description\":\"Purchased ${ITEM_NAME}\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Add to NFTs
  local NFT_ENTRY="{\"id\":\"${ITEM_ID}\",\"name\":\"${ITEM_NAME}\",\"rarity\":\"${ITEM_RARITY}\",\"acquired\":\"${DATE_UTC}\",\"price\":${PRICE}}"
  sed -i.bak "/\"nfts\":\s*\[/a \\    ${NFT_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"gear_purchase\",\"user\":\"${USER}\",\"item_id\":\"${ITEM_ID}\",\"item_name\":\"${ITEM_NAME}\",\"price\":${PRICE}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Purchased ${ITEM_NAME} (${ITEM_RARITY}) for ${PRICE} MESH"
  echo "💰 New balance: ${NEW_BALANCE} MESH"
  echo "🧾 Recorded to ledger"
}

# Buy a character
buy_character() {
  local USER="$1" PASS="$2" CHAR_ID="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Check if character directory exists
  if [[ ! -d "${CHAR_DIR}" ]]; then
    echo "⛔ Character directory not found. Please install the Characters Pack first."
    return 1
  fi
  
  # Check if character exists
  local CHAR_FILE="${CHAR_DIR}/${CHAR_ID}.json"
  if [[ ! -f "${CHAR_FILE}" ]]; then
    echo "⛔ Character with ID ${CHAR_ID} not found."
    return 1
  fi
  
  # Get character details
  local CHAR_NAME=$(grep -o '"name":"[^"]*"' "${CHAR_FILE}" | cut -d'"' -f4)
  
  # Get price from pricing.json or use default
  local PRICE=5000
  if [[ -f "${ECONOMY_DIR}/pricing.json" ]]; then
    PRICE=$(grep -o '"base_price":[^,}]*' "${ECONOMY_DIR}/pricing.json" | head -1 | cut -d':' -f2)
  fi
  
  # Check if user has enough balance
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${AVAILABLE} < ${PRICE}) ? 1 : 0}") )); then
    echo "⛔ Insufficient balance. You have ${AVAILABLE} MESH, character costs ${PRICE} MESH."
    return 1
  fi
  
  # Update wallet balance
  local NEW_BALANCE=$(awk "BEGIN {print ${AVAILABLE}-${PRICE}}")
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_BALANCE}/" "${WALLET_FILE}" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"purchase\",\"amount\":-${PRICE},\"char_id\":\"${CHAR_ID}\",\"description\":\"Purchased character ${CHAR_NAME}\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Add to NFTs
  local NFT_ENTRY="{\"id\":\"${CHAR_ID}\",\"name\":\"${CHAR_NAME}\",\"type\":\"character\",\"acquired\":\"${DATE_UTC}\",\"price\":${PRICE}}"
  sed -i.bak "/\"nfts\":\s*\[/a \\    ${NFT_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"character_purchase\",\"user\":\"${USER}\",\"char_id\":\"${CHAR_ID}\",\"char_name\":\"${CHAR_NAME}\",\"price\":${PRICE}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Purchased character ${CHAR_NAME} for ${PRICE} MESH"
  echo "💰 New balance: ${NEW_BALANCE} MESH"
  echo "🧾 Recorded to ledger"
}

# Lock MESH for governance voting
governance_stake() {
  local USER="$1" PASS="$2" AMOUNT="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Get min voting power from wallet_spec.json or use default
  local MIN_VOTING_POWER=1000
  if [[ -f "${ECONOMY_DIR}/wallet_spec.json" ]]; then
    MIN_VOTING_POWER=$(grep -o '"min_voting_power":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | cut -d':' -f2)
  fi
  
  if (( $(awk "BEGIN {print (${AMOUNT} < ${MIN_VOTING_POWER}) ? 1 : 0}") )); then
    echo "⛔ Minimum governance stake is ${MIN_VOTING_POWER} MESH."
    return 1
  fi
  
  # Check if user has enough balance
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${AVAILABLE} < ${AMOUNT}) ? 1 : 0}") )); then
    echo "⛔ Insufficient balance. You have ${AVAILABLE} MESH available."
    return 1
  fi
  
  # Get current governance locked amount
  local GOVERNANCE=$(grep -o '"governance_locked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local VOTING_POWER=$(grep -o '"voting_power":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  # Calculate new balances
  local NEW_AVAILABLE=$(awk "BEGIN {print ${AVAILABLE}-${AMOUNT}}")
  local NEW_GOVERNANCE=$(awk "BEGIN {print ${GOVERNANCE}+${AMOUNT}}")
  local NEW_VOTING_POWER=$(awk "BEGIN {print ${VOTING_POWER}+${AMOUNT}}")
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_AVAILABLE}/" "${WALLET_FILE}" | \
    sed "s/\"governance_locked\":${GOVERNANCE}/\"governance_locked\":${NEW_GOVERNANCE}/" | \
    sed "s/\"voting_power\":${VOTING_POWER}/\"voting_power\":${NEW_VOTING_POWER}/" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"governance_stake\",\"amount\":${AMOUNT},\"description\":\"Locked MESH for governance voting\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"governance_stake\",\"user\":\"${USER}\",\"amount\":${AMOUNT},\"new_voting_power\":${NEW_VOTING_POWER}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Locked ${AMOUNT} MESH for governance"
  echo "🗳️ New voting power: ${NEW_VOTING_POWER}"
  echo "💰 New available balance: ${NEW_AVAILABLE} MESH"
  echo "🧾 Recorded to ledger"
}

# Become a validator
become_validator() {
  local USER="$1" PASS="$2"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Check if already a validator
  if grep -q '"validator_status":true' "${WALLET_FILE}"; then
    echo "⛔ You are already a validator."
    return 1
  fi
  
  # Get min validator stake from wallet_spec.json or use default
  local MIN_VALIDATOR_STAKE=100000
  if [[ -f "${ECONOMY_DIR}/wallet_spec.json" ]]; then
    MIN_VALIDATOR_STAKE=$(grep -o '"min_stake":[^,}]*' "${ECONOMY_DIR}/wallet_spec.json" | head -n 2 | tail -n 1 | cut -d':' -f2)
  fi
  
  # Check if user has enough staked
  local STAKED=$(grep -o '"staked":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  
  if (( $(awk "BEGIN {print (${STAKED} < ${MIN_VALIDATOR_STAKE}) ? 1 : 0}") )); then
    echo "⛔ Insufficient stake. You need at least ${MIN_VALIDATOR_STAKE} MESH staked to become a validator."
    return 1
  fi
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"validator_status\":false/\"validator_status\":true/" "${WALLET_FILE}" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"validator_status\",\"description\":\"Became a validator\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"validator_registration\",\"user\":\"${USER}\",\"stake\":${STAKED}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ You are now a validator!"
  echo "🔍 You can validate DLC and character files with the 'validate' command"
  echo "💰 You will earn additional staking rewards as a validator"
  echo "🧾 Recorded to ledger"
}

# Validate files (for validators)
validate_files() {
  local USER="$1" PASS="$2" TARGET="$3"
  local WALLET_FILE="${WALLET_DIR}/${USER}.json"
  
  if [[ ! -f "${WALLET_FILE}" ]]; then
    echo "Wallet for ${USER} not found. Use 'init' to create one."
    return 1
  fi
  
  local KEY=$(gen_wallet_key "${USER}" "${PASS}")
  local PUB_KEY=$(hpart "${KEY}" 1 16)
  local STORED_PUB_KEY=$(grep -o '"public_key":"[^"]*"' "${WALLET_FILE}" | cut -d'"' -f4)
  
  if [[ "${PUB_KEY}" != "${STORED_PUB_KEY}" ]]; then
    echo "⛔ Authentication failed. Incorrect passphrase."
    return 1
  fi
  
  # Check if validator
  if ! grep -q '"validator_status":true' "${WALLET_FILE}"; then
    echo "⛔ Only validators can validate files. Use 'become-validator' first."
    return 1
  fi
  
  local TARGET_DIR=""
  local FILES_TYPE=""
  
  if [[ "${TARGET}" == "dlc" ]]; then
    TARGET_DIR="${DLC_DIR}"
    FILES_TYPE="DLC Meshgear"
  elif [[ "${TARGET}" == "characters" ]]; then
    TARGET_DIR="${CHAR_DIR}"
    FILES_TYPE="Characters"
  else
    echo "⛔ Invalid target. Use 'dlc' or 'characters'."
    return 1
  fi
  
  if [[ ! -d "${TARGET_DIR}" ]]; then
    echo "⛔ Target directory not found."
    return 1
  fi
  
  echo "🔍 Validating ${FILES_TYPE} files..."
  
  local VALID=0
  local INVALID=0
  local INVALID_FILES=""
  
  for f in "${TARGET_DIR}"/*.json; do
    [[ "${f}" == *".seal.json" ]] && continue
    
    local FILE_NAME=$(basename "${f}")
    local SEAL_FILE="${f%.json}.seal.json"
    
    if [[ ! -f "${SEAL_FILE}" ]]; then
      echo "⚠️ Missing seal for ${FILE_NAME}"
      INVALID=$((INVALID+1))
      INVALID_FILES="${INVALID_FILES} ${FILE_NAME}"
      continue
    fi
    
    local ACTUAL_HASH=$(file_hex "${f}")
    local EXPECTED_HASH=$(grep -o '"sha256":"[^"]*"' "${SEAL_FILE}" | cut -d'"' -f4)
    
    if [[ "${ACTUAL_HASH}" != "${EXPECTED_HASH}" ]]; then
      echo "❌ Invalid hash for ${FILE_NAME}"
      INVALID=$((INVALID+1))
      INVALID_FILES="${INVALID_FILES} ${FILE_NAME}"
    else
      VALID=$((VALID+1))
    fi
  done
  
  # Calculate EPOCH ROOT (Merkle root of all valid files)
  local ALL_HASHES=""
  for f in "${TARGET_DIR}"/*.json; do
    [[ "${f}" == *".seal.json" ]] && continue
    ALL_HASHES="${ALL_HASHES}$(file_hex "${f}")"
  done
  
  local EPOCH_ROOT=$(hex "${ALL_HASHES}")
  
  # Reward for validation
  local REWARD=50
  local AVAILABLE=$(grep -o '"available":[^,}]*' "${WALLET_FILE}" | cut -d':' -f2)
  local NEW_AVAILABLE=$(awk "BEGIN {print ${AVAILABLE}+${REWARD}}")
  
  # Create temp file for the update
  local TEMP_FILE="${WALLET_FILE}.tmp"
  sed "s/\"available\":${AVAILABLE}/\"available\":${NEW_AVAILABLE}/" "${WALLET_FILE}" > "${TEMP_FILE}"
  
  # Add to history
  local HISTORY_ENTRY="{\"ts\":\"${DATE_UTC}\",\"type\":\"validation_reward\",\"amount\":${REWARD},\"description\":\"Reward for validating ${FILES_TYPE} files\"}"
  sed -i.bak "/\"history\":\s*\[/a \\    ${HISTORY_ENTRY}," "${TEMP_FILE}" && rm "${TEMP_FILE}.bak"
  
  # Replace original with updated file
  mv "${TEMP_FILE}" "${WALLET_FILE}"
  
  # Add to ledger
  local LEDGE_LINE="{\"ts\":\"${DATE_UTC}\",\"event\":\"files_validation\",\"user\":\"${USER}\",\"target\":\"${TARGET}\",\"valid\":${VALID},\"invalid\":${INVALID},\"epoch_root\":\"${EPOCH_ROOT}\",\"reward\":${REWARD}}"
  echo "${LEDGE_LINE}" >> "${LEDGER}"
  
  echo "✅ Validation complete"
  echo "✓ Valid files: ${VALID}"
  if [[ $INVALID -gt 0 ]]; then
    echo "❌ Invalid files: ${INVALID} (${INVALID_FILES})"
  else
    echo "✓ No invalid files found"
  fi
  echo "🌱 EPOCH ROOT: ${EPOCH_ROOT}"
  echo "💰 Validator reward: ${REWARD} MESH"
  echo "🧾 Recorded to ledger"
}

# ---------- main ----------
usage() {
  cat <<'USAGE'
Mesh Credit CLI - Non-custodial wallet for EpochCore game economy

USAGE:
  mesh_credit_cli.sh init <username> <passphrase>     # Create a new wallet
  mesh_credit_cli.sh show <username> <passphrase>     # Show wallet details
  mesh_credit_cli.sh deposit <username> <passphrase> <usd_amount>  # Convert USD to MESH
  mesh_credit_cli.sh transfer <username> <passphrase> <recipient> <amount>  # Send MESH
  mesh_credit_cli.sh stake <username> <passphrase> <amount>  # Stake for yield
  mesh_credit_cli.sh unstake <username> <passphrase> <position_id>  # Unstake
  mesh_credit_cli.sh buy-gear <username> <passphrase> <item_id>  # Buy DLC gear
  mesh_credit_cli.sh buy-character <username> <passphrase> <char_id>  # Buy character
  mesh_credit_cli.sh governance <username> <passphrase> <amount>  # Lock for voting
  mesh_credit_cli.sh become-validator <username> <passphrase>  # Become a validator
  mesh_credit_cli.sh validate <username> <passphrase> <dlc|characters>  # Validate files
USAGE
}

main() {
  case "${1:-}" in
    init) [[ $# -ge 3 ]] && init_wallet "$2" "$3" || usage ;;
    show) [[ $# -ge 3 ]] && show_wallet "$2" "$3" || usage ;;
    deposit) [[ $# -ge 4 ]] && deposit_usd "$2" "$3" "$4" || usage ;;
    transfer) [[ $# -ge 5 ]] && transfer_mesh "$2" "$3" "$4" "$5" || usage ;;
    stake) [[ $# -ge 4 ]] && stake_mesh "$2" "$3" "$4" || usage ;;
    unstake) [[ $# -ge 4 ]] && unstake_mesh "$2" "$3" "$4" || usage ;;
    buy-gear) [[ $# -ge 4 ]] && buy_gear "$2" "$3" "$4" || usage ;;
    buy-character) [[ $# -ge 4 ]] && buy_character "$2" "$3" "$4" || usage ;;
    governance) [[ $# -ge 4 ]] && governance_stake "$2" "$3" "$4" || usage ;;
    become-validator) [[ $# -ge 3 ]] && become_validator "$2" "$3" || usage ;;
    validate) [[ $# -ge 4 ]] && validate_files "$2" "$3" "$4" || usage ;;
    *) usage ;;
  esac
}

main "$@"
