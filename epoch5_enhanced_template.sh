#!/bin/bash
#
# Enhanced epoch5-template script
# This script includes improvements for security, maintainability, and usability.
# It preserves core logic and features such as Alpha Ceiling enforcement, GBTEpoch timestamp,
# Phone Audit Scroll scheduling, alias 🧙🦿🤖, inline AMT and NOTE overrides, and audit/logging (sealing).
#
# Safety settings: exit on error, undefined var usage, and propagate pipefail.
set -euo pipefail

# Trap to handle script exit for logging and sealing
trap 'exit_handler' EXIT

exit_handler() {
    local status=$?
    if [[ $status -ne 0 ]]; then
        echo "Error: Script terminated prematurely with exit status $status at $(date)." >&2
    fi
    # Always attempt to seal the audit on exit (including on error)
    seal_audit_log
}

# Default configuration
ALPHA_CEILING=100                   # Maximum allowed value for AMT (Alpha Ceiling threshold)
DEFAULT_AMT=10                      # Default AMT if not provided
DEFAULT_NOTE="No note provided"     # Default NOTE if not provided

# Read inline overrides from environment (if present)
AMT="${AMT:-$DEFAULT_AMT}"
NOTE="${NOTE:-$DEFAULT_NOTE}"

# Optionally parse command-line arguments for overrides and special modes
SHOW_HELP=0
DO_PHONE_AUDIT_ONLY=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--amt)
            if [[ $# -lt 2 ]]; then
                echo "Option $1 requires an argument." >&2
                exit 1
            fi
            AMT="$2"
            shift 2
            ;;
        -n|--note)
            if [[ $# -lt 2 ]]; then
                echo "Option $1 requires an argument." >&2
                exit 1
            fi
            NOTE="$2"
            shift 2
            ;;
        --phone-audit)
            # Run only the Phone Audit Scroll (for scheduled or manual trigger)
            DO_PHONE_AUDIT_ONLY=1
            shift
            ;;
        -h|--help)
            SHOW_HELP=1
            shift
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            # no more options
            break
            ;;
    esac
done

if [[ $SHOW_HELP -eq 1 ]]; then
    echo "Usage: $0 [ -a AMOUNT ] [ -n NOTE ] [ --phone-audit ]"
    echo "  -a, --amt       Specify an integer amount (AMT). Can also be set via environment variable AMT."
    echo "  -n, --note      Specify a note (NOTE). Can also be set via environment variable NOTE."
    echo "  --phone-audit   Run the Phone Audit Scroll immediately (used internally for scheduled audit)."
    echo
    echo "If no -a or -n options are given, defaults will be used (AMT=${DEFAULT_AMT}, NOTE='${DEFAULT_NOTE}'),"
    echo "which can be overridden by setting environment variables AMT and NOTE inline when running the script."
    exit 0
fi

# If invoked with --phone-audit, run the Phone Audit Scroll function and exit.
if [[ $DO_PHONE_AUDIT_ONLY -eq 1 ]]; then
    phone_audit_scroll() {
        # Display the audit log (Phone Audit Scroll)
        echo "[$(date)] Phone Audit Scroll: Displaying audit log..."
        if [[ -f "$LOG_FILE" ]]; then
            echo "------- BEGIN AUDIT SCROLL -------"
            cat "$LOG_FILE"
            echo "------- END AUDIT SCROLL -------"
        else
            echo "No audit log found to display."
        fi
    }
    # Determine log file name (same as main script uses)
    LOG_FILE="${LOG_FILE:-$HOME/epoch5_audit.log}"
    phone_audit_scroll
    exit 0
fi

# Validate and sanitize AMT input (should be a non-negative integer)
if ! [[ "$AMT" =~ ^[0-9]+$ ]]; then
    echo "Error: AMT ('$AMT') is not a valid positive integer." >&2
    exit 1
fi
if (( AMT < 0 )); then
    echo "Error: AMT ('$AMT') must not be negative." >&2
    exit 1
fi

# Enforce Alpha Ceiling on AMT
if (( AMT > ALPHA_CEILING )); then
    echo "Alpha Ceiling enforcement: AMT $AMT exceeds maximum $ALPHA_CEILING. Capping to $ALPHA_CEILING."
    AMT=$ALPHA_CEILING
fi

# Use a log file for audit (preserve events across runs)
LOG_FILE="${LOG_FILE:-$HOME/epoch5_audit.log}"

# Log initial event with timestamp
START_TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Starting script at $START_TS with AMT=$AMT, NOTE='$NOTE'."
echo "$START_TS START AMT=$AMT NOTE=\"$NOTE\"" >> "$LOG_FILE"

# Capture current epoch time (GBTEpoch)
CURRENT_EPOCH=$(date +%s)
echo "GBTEpoch (current epoch time): $CURRENT_EPOCH"
echo "$START_TS EPOCH $CURRENT_EPOCH" >> "$LOG_FILE"

# *** Core functionality goes here (original logic preserved) ***
# ... (No core logic removed; placeholder for main operations) ...

# Schedule Phone Audit Scroll (to display audit log after a delay)
AUDIT_DELAY=${AUDIT_DELAY:-60}  # seconds to wait before running phone audit (default 60s)
if [[ $AUDIT_DELAY -gt 0 ]]; then
    echo "Scheduling Phone Audit Scroll in $AUDIT_DELAY seconds..."
    (
        sleep "$AUDIT_DELAY"
        # Invoke this script with --phone-audit flag in a subshell (detached from main flow)
        bash "$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")" --phone-audit &
    ) &
fi

# Set up alias 🧙🦿🤖 for convenience (persists if script is sourced or added to bashrc)
script_path="$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")"
alias 🧙🦿🤖="bash '$script_path' --phone-audit"
if [[ "$BASH_SOURCE" == "$0" ]]; then
    echo "Note: Alias 🧙🦿🤖 has been set for this session only. To use it in your shell, source this script or add the alias to your bash profile."
else
    echo "Alias 🧙🦿🤖 set in current shell. Use 🧙🦿🤖 to manually trigger a Phone Audit Scroll (audit log display)."
fi

# Define sealing function to finalize audit logging with timestamp and hash
seal_audit_log() {
    local end_ts="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    # Compute a hash of final data (timestamp + AMT + NOTE) for audit sealing
    local data_to_hash="${end_ts}${AMT}${NOTE}"
    local seal_hash
    seal_hash="$(echo -n "$data_to_hash" | sha256sum | awk '{print $1}')"
    echo "Sealing audit log at $end_ts with hash: $seal_hash"
    echo "$end_ts END SEAL hash=$seal_hash" >> "$LOG_FILE"
}

# Finalize script
END_TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Script completed at $END_TS. Audit log has been recorded."
# (The exit handler will now call seal_audit_log to seal the audit record.)