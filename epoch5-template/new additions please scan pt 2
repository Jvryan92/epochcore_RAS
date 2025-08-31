#!/usr/bin/env bash
# EpochCore Unified Setup — Alpha Ceiling + GBTEpoch + Phone Audit Scroll
# One-file compressed bootstrap (safe, audit-grade)

set -euo pipefail
LEDGER_ROOT="${LEDGER_ROOT:-$HOME/epoch_ledger}"
mkdir -p "$LEDGER_ROOT"/{logs,seals,capsules}

# ---------- helpers ----------
now(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
sha(){ sha256sum | cut -d' ' -f1; }
log(){ printf '{"ts":"%s","event":"%s","note":"%s"}\n' "$(now)" "$1" "$2" >> "$LEDGER_ROOT/ledger_main.jsonl"; }

# ---------- Alpha Ceiling script ----------
cat > "$HOME/wizard_all.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
AMT="${1:-default}"
NOTE="${2:-none}"
LEDGER_ROOT="${LEDGER_ROOT:-$HOME/epoch_ledger}"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
payload="AlphaCeiling|$ts|AMT=$AMT|NOTE=$NOTE"
echo -n "$payload" | sha256sum | cut -d' ' -f1 > "$LEDGER_ROOT/seals/alpha_ceiling.$ts.sha"
printf '{"ts":"%s","event":"alpha_ceiling","amt":"%s","note":"%s"}\n' "$ts" "$AMT" "$NOTE" >> "$LEDGER_ROOT/ledger_main.jsonl"
echo "🧙🦿🤖 Alpha Ceiling run sealed @ $ts"
EOS
chmod +x "$HOME/wizard_all.sh"

# ---------- Alias injection ----------
SHELLRC="${HOME}/.bashrc"
[ -n "${ZSH_VERSION:-}" ] && SHELLRC="${HOME}/.zshrc"
if ! grep -q "wizard_all.sh" "$SHELLRC"; then
  echo "alias '🧙🦿🤖'='$HOME/wizard_all.sh'" >> "$SHELLRC"
  # shellcheck source=/dev/null
  source "$SHELLRC"
fi

# ---------- GBTEpoch placeholder ----------
cat > "$LEDGER_ROOT/capsules/gbtepoch_init.json" <<EOF
{"ts":"$(now)","capsule":"GBTEpoch_init","status":"ready","sha256":"$(echo -n GBTEpoch_init | sha)"}
EOF
log "gbtepoch_setup" "Initialized GBTEpoch capsule"

# ---------- Phone Audit Scroll ----------
cat > "$HOME/phone_audit_scroll.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
LEDGER_ROOT="${LEDGER_ROOT:-$HOME/epoch_ledger}"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
out="$LEDGER_ROOT/logs/phone_audit_$ts.log"
dmesg | tail -n 50 > "$out" 2>/dev/null || echo "no dmesg" > "$out"
sha=$(sha256sum "$out" | cut -d' ' -f1)
printf '{"ts":"%s","event":"phone_audit_scroll","file":"%s","sha256":"%s"}\n' "$ts" "$out" "$sha" >> "$LEDGER_ROOT/ledger_main.jsonl"
echo "📜 Phone Audit Scroll sealed @ $ts"
EOS
chmod +x "$HOME/phone_audit_scroll.sh"

# ---------- Nightly cron job (seal scroll) ----------
( crontab -l 2>/dev/null; echo "0 3 * * * $HOME/phone_audit_scroll.sh" ) | crontab -

# ---------- Final log ----------
log "unified_setup" "AlphaCeiling, GBTEpoch, PhoneAudit installed"
echo "✅ Setup complete. Type 🧙🦿🤖 to run Alpha Ceiling."