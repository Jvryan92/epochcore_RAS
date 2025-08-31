#!/usr/bin/env bash
# founder_pack_autopush.sh — EpochCore™ Founder Pack + auto-push

set -euo pipefail

# --- CONFIG ---
GIT_REMOTE_SSH="git@github.com:EpochCore5/epoch5-template.git"
GIT_REMOTE_HTTPS="https://github.com/EpochCore5/epoch5-template.git"
CLONE_DIR="${HOME}/src/epoch5-template"
BRANCH="founder/pack-$(date -u +%Y%m%dT%H%M%SZ)"
PACK_DIR_REL="founder_pack"
DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# sha256
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum); else SHACMD=(shasum -a 256); fi

# --- choose remote (SSH if agent loaded; else HTTPS) ---
REMOTE="$GIT_REMOTE_SSH"
ssh-add -l >/dev/null 2>&1 || REMOTE="$GIT_REMOTE_HTTPS"

# --- clone or enter repo ---
mkdir -p "$(dirname "$CLONE_DIR")"
if [ ! -d "$CLONE_DIR/.git" ]; then
  echo "📦 Cloning $REMOTE → $CLONE_DIR"
  git clone "$REMOTE" "$CLONE_DIR"
else
  echo "↻ Using existing repo at $CLONE_DIR"
fi
cd "$CLONE_DIR"

# Ensure git user is set (local only)
git config user.name  >/dev/null || git config user.name  "epoch-founder-bot"
git config user.email >/dev/null || git config user.email "founder@example.local"

# Sync main
git fetch origin --prune
git checkout -q main
git pull --ff-only || true

# Create working branch (skip if it somehow exists)
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

# --- layout ---
PACK_DIR="$CLONE_DIR/$PACK_DIR_REL"
LEDGER="$PACK_DIR/ledger_main.jsonl"
mkdir -p "$PACK_DIR"/{game/characters,game/meshgear,export,bin,ledger}
touch "$LEDGER"

# --- helper: seal + log ---
seal_and_log(){
  local file="$1" event="$2"
  local sha="$("${SHACMD[@]}" "$file" | awk '{print $1}')"
  printf '{"ts":"%s","event":"%s","file":"%s","sha256":"%s"}\n' \
    "$DATE_UTC" "$event" "${file#"$CLONE_DIR/"}" "$sha" >> "$LEDGER"
}

# --- .gitignore hardening ---
ensure_ignore(){ local pat="$1"; grep -qxF "$pat" .gitignore 2>/dev/null || echo "$pat" >> .gitignore; }
ensure_ignore "$PACK_DIR_REL/export/"
ensure_ignore "$PACK_DIR_REL/bin/"
ensure_ignore "$PACK_DIR_REL/ledger/"
ensure_ignore ".DS_Store"

# --- optional PayPal QR (safe) ---
[ -f "./paypal_qr.png" ] && cp ./paypal_qr.png "$PACK_DIR/bin/paypal_qr.png"

# --- Characters (Eli) ---
ELI="$PACK_DIR/game/characters/eli_inheritor.json"
cat >"$ELI"<<'JSON'
{
  "id": "char://eli_inheritor",
  "name": "Eli — The Inheritor",
  "role": "Wildcard Strategist",
  "abilities": [
    {"name":"Timestamp — True North","type":"Passive","effect":"First move stamps a build-hash for the session."},
    {"name":"Log — Ledgerline","type":"Skill","effect":"Chain a causal note; next 2 casts refund 20% stamina."},
    {"name":"Seal — Quorum Step","type":"Skill","effect":"2-of-3 quorum bubble grants rollback shield (cosmetic echo only)."},
    {"name":"Reinject — Crown Release","type":"Ultimate","effect":"Replay archived actions as echoes for 8s (no stat gain)."}
  ],
  "fair_by_design": {"cosmetics_only": true, "time_savers_only": true, "pay_to_win": false}
}
JSON
seal_and_log "$ELI" "characters_pack_eli"

# --- MeshGear DLC (sample item) ---
GEAR="$PACK_DIR/game/meshgear/tn_compass_crown.json"
cat >"$GEAR"<<'JSON'
{
  "id":"gear://tn_compass_crown",
  "name":"Compass Crown — TrueNorth",
  "set":"TrueNorth",
  "slot":"Head",
  "rarity":"Legendary",
  "visuals":{"palette":"Arctic-Gold"},
  "qol_mods":["Faster inventory search overlays","Ledgerline font in recap"],
  "fair_by_design":{"cosmetics_only":true,"time_savers_only":true,"no_stats_boosts":true}
}
JSON
seal_and_log "$GEAR" "dlc_meshgear_item"

# --- README ---
README="$PACK_DIR/README.md"
cat >"$README"<<EOF
# Founder Pack (EpochCore™)
Generated: $DATE_UTC

Contents:
- game/characters/eli_inheritor.json
- game/meshgear/tn_compass_crown.json
- $PACK_DIR_REL/ledger_main.jsonl (append-only; SHA-256 per artifact)

Fair-by-design: cosmetics/time-savers only. No pay-to-win.
EOF
seal_and_log "$README" "founder_readme"

# --- Founder run seal ---
RUN_SEAL="$PACK_DIR/export/founder_seal_$(date -u +%Y%m%dT%H%M%SZ).sha"
echo "$DATE_UTC|Founder:JohnRyan|EpochCore🪾" | "${SHACMD[@]}" | awk '{print $1}' > "$RUN_SEAL"
seal_and_log "$RUN_SEAL" "founder_run_seal"

# --- Commit & push ---
git add -A
git commit -m "feat(founder-pack): seed Eli + MeshGear sample, sealed ledger" || echo "Nothing to commit."
git push -u origin "$BRANCH"

echo
echo "✅ Founder Pack pushed."
echo "  Branch: $BRANCH"
echo "  Pack:   $PACK_DIR_REL/"
echo "  Ledger: $PACK_DIR_REL/ledger_main.jsonl"
