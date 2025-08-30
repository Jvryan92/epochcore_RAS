#!/usr/bin/env bash
# MESH CREDIT CLI - Non-custodial wallet for the EpochCore economy
# Supports: wallet init/show/deposit/transfer, staking, governance, shop, validator
set -euo pipefail

DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${PWD}/epoch_game_pack"
PYTHON_EXEC="python3"  # Change this if needed for your environment
ECONOMY_SCRIPT="${SCRIPT_DIR}/../scripts/mesh_credit_economy.py"

# Ensure economy directory exists
mkdir -p "${ROOT}/economy/mesh_credit/wallets"

# ---------- Helpers ----------
check_economy_script() {
  if [[ ! -f "$ECONOMY_SCRIPT" ]]; then
    echo "Error: Mesh Credit economy script not found at $ECONOMY_SCRIPT"
    exit 1
  fi
}

# ---------- CLI Commands ----------

# Initialize the economy if needed
init_economy() {
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" init
}

# Wallet management
wallet_create() {
  local wallet_id="$1"
  local balance="${2:-0}"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet create "$wallet_id" --balance "$balance"
}

wallet_show() {
  local wallet_id="$1"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet get "$wallet_id"
}

wallet_list() {
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet list
}

wallet_deposit() {
  local wallet_id="$1"
  local usd_amount="$2"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet deposit "$wallet_id" "$usd_amount"
}

wallet_transfer() {
  local from_wallet="$1"
  local to_wallet="$2"
  local amount="$3"
  local memo="${4:-}"
  
  check_economy_script
  if [[ -n "$memo" ]]; then
    $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet transfer "$from_wallet" "$to_wallet" "$amount" --memo "$memo"
  else
    $PYTHON_EXEC "$ECONOMY_SCRIPT" wallet transfer "$from_wallet" "$to_wallet" "$amount"
  fi
}

# Staking management
stake_add() {
  local wallet_id="$1"
  local amount="$2"
  local lockup="${3:-0}"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" stake add "$wallet_id" "$amount" --lockup "$lockup"
}

stake_remove() {
  local wallet_id="$1"
  local amount="$2"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" stake remove "$wallet_id" "$amount"
}

stake_yield() {
  local wallet_id="$1"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" stake yield "$wallet_id"
}

stake_epoch() {
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" stake epoch
}

# Governance management
governance_stake() {
  local wallet_id="$1"
  local amount="$2"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" governance stake "$wallet_id" "$amount"
}

governance_unstake() {
  local wallet_id="$1"
  local amount="$2"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" governance unstake "$wallet_id" "$amount"
}

# Shop functionality
shop_buy() {
  local wallet_id="$1"
  local item_id="$2"
  local item_type="$3"
  local rarity="$4"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" shop buy "$wallet_id" "$item_id" "$item_type" "$rarity"
}

# Verification tools
verify_file() {
  local file_path="$1"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" verify file "$file_path"
}

reseal_file() {
  local file_path="$1"
  
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" verify reseal "$file_path"
}

# Economy management
update_economy() {
  check_economy_script
  $PYTHON_EXEC "$ECONOMY_SCRIPT" economy update
}

# ---------- Main CLI ----------
usage() {
  cat <<EOF
MESH CREDIT CLI - Non-custodial wallet for the EpochCore economy

USAGE:
  $(basename "$0") init                            Initialize Mesh Credit economy
  
  # Wallet Commands
  $(basename "$0") wallet create <id> [balance]    Create a new wallet
  $(basename "$0") wallet show <id>                Show wallet details
  $(basename "$0") wallet list                     List all wallets
  $(basename "$0") wallet deposit <id> <usd>       Deposit USD to wallet
  $(basename "$0") wallet transfer <from> <to> <amount> [memo]  Transfer MESH
  
  # Staking Commands
  $(basename "$0") stake add <id> <amount> [lockup_days]  Stake MESH
  $(basename "$0") stake remove <id> <amount>      Unstake MESH
  $(basename "$0") stake yield <id>                Calculate yield
  $(basename "$0") stake epoch                     Process epoch yield
  
  # Governance Commands
  $(basename "$0") gov stake <id> <amount>         Stake for governance
  $(basename "$0") gov unstake <id> <amount>       Unstake from governance
  
  # Shop Commands
  $(basename "$0") shop buy <id> <item_id> <type> <rarity>  Buy an item
  
  # Verification Commands
  $(basename "$0") verify file <path>              Verify file integrity
  $(basename "$0") verify reseal <path>            Reseal a file
  
  # Economy Commands
  $(basename "$0") economy update                  Update economy state

EXAMPLES:
  $(basename "$0") wallet create player_one 100
  $(basename "$0") wallet deposit player_one 20
  $(basename "$0") stake add player_one 500 30
  $(basename "$0") shop buy player_one "tn_compass_crown" "gear_cosmetic" "Legendary"

EOF
}

# Parse command line
if [[ $# -lt 1 ]]; then
  usage
  exit 0
fi

CMD="$1"
shift

case "$CMD" in
  init)
    init_economy
    ;;
    
  wallet)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      create)
        [[ $# -lt 1 ]] && { echo "Error: Missing wallet ID"; exit 1; }
        wallet_create "$@"
        ;;
      show)
        [[ $# -lt 1 ]] && { echo "Error: Missing wallet ID"; exit 1; }
        wallet_show "$1"
        ;;
      list)
        wallet_list
        ;;
      deposit)
        [[ $# -lt 2 ]] && { echo "Error: Usage: wallet deposit <id> <usd_amount>"; exit 1; }
        wallet_deposit "$1" "$2"
        ;;
      transfer)
        [[ $# -lt 3 ]] && { echo "Error: Usage: wallet transfer <from> <to> <amount> [memo]"; exit 1; }
        if [[ $# -ge 4 ]]; then
          wallet_transfer "$1" "$2" "$3" "$4"
        else
          wallet_transfer "$1" "$2" "$3"
        fi
        ;;
      *)
        echo "Unknown wallet command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  stake)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      add)
        [[ $# -lt 2 ]] && { echo "Error: Usage: stake add <id> <amount> [lockup_days]"; exit 1; }
        if [[ $# -ge 3 ]]; then
          stake_add "$1" "$2" "$3"
        else
          stake_add "$1" "$2"
        fi
        ;;
      remove)
        [[ $# -lt 2 ]] && { echo "Error: Usage: stake remove <id> <amount>"; exit 1; }
        stake_remove "$1" "$2"
        ;;
      yield)
        [[ $# -lt 1 ]] && { echo "Error: Missing wallet ID"; exit 1; }
        stake_yield "$1"
        ;;
      epoch)
        stake_epoch
        ;;
      *)
        echo "Unknown stake command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  gov|governance)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      stake)
        [[ $# -lt 2 ]] && { echo "Error: Usage: gov stake <id> <amount>"; exit 1; }
        governance_stake "$1" "$2"
        ;;
      unstake)
        [[ $# -lt 2 ]] && { echo "Error: Usage: gov unstake <id> <amount>"; exit 1; }
        governance_unstake "$1" "$2"
        ;;
      *)
        echo "Unknown governance command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  shop)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      buy)
        [[ $# -lt 4 ]] && { echo "Error: Usage: shop buy <id> <item_id> <type> <rarity>"; exit 1; }
        shop_buy "$1" "$2" "$3" "$4"
        ;;
      *)
        echo "Unknown shop command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  verify)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      file)
        [[ $# -lt 1 ]] && { echo "Error: Missing file path"; exit 1; }
        verify_file "$1"
        ;;
      reseal)
        [[ $# -lt 1 ]] && { echo "Error: Missing file path"; exit 1; }
        reseal_file "$1"
        ;;
      *)
        echo "Unknown verify command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  economy)
    SUBCMD="$1"
    shift
    case "$SUBCMD" in
      update)
        update_economy
        ;;
      *)
        echo "Unknown economy command: $SUBCMD"
        usage
        exit 1
        ;;
    esac
    ;;
    
  help|-h|--help)
    usage
    ;;
    
  *)
    echo "Unknown command: $CMD"
    usage
    exit 1
    ;;
esac

exit 0
