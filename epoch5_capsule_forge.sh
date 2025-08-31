#!/usr/bin/env bash
# epoch5_capsule_forge.sh — Forge 10 compounding, single-file, market-ready capsules (audit-grade, portable)
# Zero guesswork: fully specified, reproducible, and sealed with GPG (inline detached signature).
#
# WHAT YOU GET (in ./market/pack-<UTC>/):
#   • 10 self-contained *.capsule.sh files — each verifies its own inline GPG signature, then runs its payload
#   • pack_manifest.json        — canonical manifest of all capsules (ids, hashes, chain)
#   • pack_manifest.sha256      — SHA-256 of the manifest
#   • README_pack.md            — quick usage + verification guide
#
# REQUIREMENTS (Linux/macOS):
#   - bash, coreutils (date, awk, sed, sort, sha256sum or shasum), base64, tar
#   - gpg (with a default signing key)          # set SIGNING_KEY=<fingerprint|email> to pick a key
#   - uuidgen  (or python3 for fallback)
#
# USAGE:
#   ./epoch5_capsule_forge.sh
#   SIGNING_KEY="you@example.com" FOUNDER_NOTE="Founder: You — 'Ship receipts, not vibes.'" ./epoch5_capsule_forge.sh
#
# DESIGN NOTES:
#   • "Compounding": Each capsule metadata includes chain_prev (SHA-256) → a linear chain across 10 capsules.
#   • "Manifest Hash": The pack computes a canonical manifest hash; each capsule embeds this manifest_hash.
#   • "Session UUID": One UUID applied to all capsules in this forging run.
#   • "Provenance": Timestamps, tool versions, and signer key-id embedded.
#   • "One file only": Each capsule is a single executable shell file with an embedded, inline armored PGP signature.
#
set -euo pipefail

# ---------- tools & shims ----------
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 2; }; }
need gpg
need base64
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum); else SHACMD=(shasum -a 256); fi

uuid() {
  if command -v uuidgen >/dev/null 2>&1; then uuidgen
  elif command -v python3 >/dev/null 2>&1; then python3 - <<'PY'
import uuid; print(uuid.uuid4())
PY
  else
    date +%s | "${SHACMD[@]}" | awk '{print substr($1,1,8) "-" substr($1,9,4) "-" substr($1,13,4) "-" substr($1,17,4) "-" substr($1,21,12)}'
  fi
}

# ---------- config ----------
DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SESSION_UUID="${SESSION_UUID:-$(uuid)}"
FOUNDER_NOTE="${FOUNDER_NOTE:-Founder: John Ryan — 'Sovereign stack, fair-by-design.'}"
SIGNING_KEY_ARG=()
[[ -n "${SIGNING_KEY:-}" ]] && SIGNING_KEY_ARG=(--local-user "$SIGNING_KEY")

PACK_DIR="./market/pack-$STAMP"
mkdir -p "$PACK_DIR"

# Capsule catalog (id|title|short purpose)
# Keep ids slug-safe (lowercase, dashes).
read -r -d '' CATALOG <<'CAT' || true
01-locker-drop     | LockerCode Dropper           | Generate redeem codes & CSV/JSON (offline, rate-limit friendly)
02-poap-stub       | POAP Claim Stub              | Time-window attendance claims (JSON), no chain
03-echo-replay     | Echo-Theatre Replay Pack     | Bundle replays/logs → tar.gz + hash
04-meshcredit-kiosk| MeshCredit Kiosk             | Emit $100 receipt capsules → jsonl + seals
05-creator-splits  | Creator Split Planner        | Compute split JSON (royalty/primary/secondary)
06-gov-commit      | Governance Commit Capsule    | Commit–reveal seed (demo VRF stub) for votes
07-fair-balancer   | A/B Balancer Capsule         | Simulate fairness KPIs over params (CSV)
08-drop-scheduler  | Drop-Window Scheduler        | Emit ICS + JSON schedule blocks (UTC)
09-telemetry-harv  | Telemetry Harvester          | Turn local logs → jsonl with line-hashes
10-storefront-snap | Storefront Snapshot          | Static snapshot skeleton with manifest
CAT

# ---------- helpers ----------
file_sha() { "${SHACMD[@]}" "$1" | awk '{print $1}'; }
text_sha() { printf "%s" "$1" | "${SHACMD[@]}" | awk '{print $1}'; }

# payload generator: tiny self-contained scripts specialized per capsule id
gen_payload() {
  local id="$1" title="$2" purpose="$3"
  case "$id" in
    01-locker-drop)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/locker_drop}"; COUNT="${COUNT:-1000}"; PREFIX="${PREFIX:-EPOCH}"
mkdir -p "$OUT"
CSV="$OUT/codes.csv"; JSON="$OUT/codes.jsonl"
: > "$CSV"; : > "$JSON"
echo "code,issued_at" >> "$CSV"
for i in $(seq 1 "$COUNT"); do
  c="$PREFIX-$(date -u +%y%m%d)-$RANDOM$RANDOM"
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "$c,$ts" >> "$CSV"
  printf '{"code":"%s","ts":"%s"}\n' "$c" "$ts" >> "$JSON"
done
echo "Wrote: $CSV  $JSON"
SH
      ;;
    02-poap-stub)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/poap_stub}"; WINDOW_MIN="${WINDOW_MIN:-60}"
mkdir -p "$OUT"
S="$OUT/poap_window.json"
START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
END="$(date -u -d "$WINDOW_MIN min" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v +"$WINDOW_MIN"M +%Y-%m-%dT%H:%M:%SZ)"
printf '{"start":"%s","end":"%s","rules":{"geo":false,"rate_limit":true}}\n' "$START" "$END" > "$S"
echo "Wrote: $S"
SH
      ;;
    03-echo-replay)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/echo_replay}"
SRC="${2:-./logs}"
mkdir -p "$OUT"
TAR="$OUT/echo_replay_$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tar -czf "$TAR" "$SRC" 2>/dev/null || tar -czf "$TAR" --files-from /dev/null
SHASUM="$(shasum -a 256 "$TAR" 2>/dev/null | awk '{print $1}')"
[ -z "$SHASUM" ] && SHASUM="$(sha256sum "$TAR" | awk '{print $1}')"
echo "$SHASUM  $(basename "$TAR")" | tee "$TAR.sha256"
echo "Wrote: $TAR  $TAR.sha256"
SH
      ;;
    04-meshcredit-kiosk)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/meshcredit}"; PRICE="${PRICE:-100}"
mkdir -p "$OUT"
J="$OUT/sales.jsonl"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
id="sale-$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
printf '{"id":"%s","ts":"%s","amount_usd":%s,"note":"capsule sale"}\n' "$id" "$ts" "$PRICE" | tee -a "$J"
SH
      ;;
    05-creator-splits)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/splits}"; mkdir -p "$OUT"
cat > "$OUT/splits.json" <<JSON
{"primary":{"creator":0.6,"studio":0.35,"pool":0.05},"secondary":{"creator":0.5,"studio":0.2,"pool":0.3}}
JSON
echo "Wrote: $OUT/splits.json"
SH
      ;;
    06-gov-commit)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/gov_commit}"; mkdir -p "$OUT"
seed="$(date -u +%s)$RANDOM"
commit=$(printf "%s" "$seed" | sha256sum 2>/dev/null | awk '{print $1}')
[ -z "$commit" ] && commit=$(printf "%s" "$seed" | shasum -a 256 | awk '{print $1}')
printf '{"commit":"%s","ts":"%s"}\n' "$commit" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee "$OUT/commit.json"
SH
      ;;
    07-fair-balancer)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/fair_balancer}"; N="${N:-1000}"; mkdir -p "$OUT"
CSV="$OUT/kpi.csv"; echo "trial,clean_plays,quit_rate,match_delta" > "$CSV"
for i in $(seq 1 "$N"); do
  cp=$((RANDOM%10+1)); qr=$((RANDOM%20)); md=$((RANDOM%5))
  echo "$i,$cp,$qr,$md" >> "$CSV"
done
echo "Wrote: $CSV"
SH
      ;;
    08-drop-scheduler)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/drop_sched}"; mkdir -p "$OUT"
ICS="$OUT/drops.ics"; JSON="$OUT/drops.json"
now="$(date -u +%Y%m%dT%H%M%SZ)"
cat > "$ICS" <<ICS
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//EPOCH//Drops//EN
BEGIN:VEVENT
UID:drop-$now@epoch
DTSTAMP:$now
DTSTART:$now
DTEND:$(date -u -d "+30 minutes" +%Y%m%dT%H%M%SZ 2>/dev/null || date -u -v +30M +%Y%m%dT%H%M%SZ)
SUMMARY:EPOCH Drop Window
END:VEVENT
END:VCALENDAR
ICS
printf '{"ts":"%s","windows":[{"start":"%s","mins":30}]}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$JSON"
echo "Wrote: $ICS  $JSON"
SH
      ;;
    09-telemetry-harv)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/telemetry}"; SRC="${2:-/var/log/system.log}"
mkdir -p "$OUT"; J="$OUT/telemetry.jsonl"
: > "$J"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ -f "$SRC" ]; then tail -n 50 "$SRC" | while IFS= read -r line; do
  h=$(printf "%s" "$line" | sha256sum 2>/dev/null | awk '{print $1}')
  [ -z "$h" ] && h=$(printf "%s" "$line" | shasum -a 256 | awk '{print $1}')
  printf '{"ts":"%s","line_hash":"%s","sample":"%s"}\n' "$ts" "$h" "$(echo "$line" | sed 's/"/\\"/g' | cut -c1-120)" >> "$J"
done
else
  printf '{"ts":"%s","line_hash":"%s","sample":"%s"}\n' "$ts" "no-src" "no source file" >> "$J"
fi
echo "Wrote: $J"
SH
      ;;
    10-storefront-snap)
      cat <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-out/storefront}"; mkdir -p "$OUT"
cat > "$OUT/index.html" <<HTML
<!doctype html><meta charset="utf-8">
<title>EPOCH Storefront Snapshot</title>
<h1>EPOCH — Snapshot</h1>
<p>Static drop; replace with your content. This file is generated by a capsule.</p>
HTML
(sha256sum "$OUT/index.html" 2>/dev/null || shasum -a 256 "$OUT/index.html") | awk '{print $1"  index.html"}' > "$OUT/manifest.sha256"
echo "Wrote: $OUT/index.html  $OUT/manifest.sha256"
SH
      ;;
  esac
}

# Build stage: create raw content blocks (metadata + payload) → prehash list
TMPDIR="$(mktemp -d)"
PRELIST="$TMPDIR/prehash_list.txt"
: > "$PRELIST"

# Will store per-capsule info for after-pass signing
declare -a IDS TITLES PURPOSES PREHASHES PAYLOAD_B64 METAS
CHAIN_PREV="genesis"

# parse catalog
i=0
while IFS='|' read -r id_raw title_raw purpose_raw; do
  id="$(echo "$id_raw" | awk '{$1=$1; print $1}')"               # trim
  title="$(echo "$title_raw" | sed 's/^ *//;s/ *$//')"
  purpose="$(echo "$purpose_raw" | sed 's/^ *//;s/ *$//')"
  [ -z "$id" ] && continue
  i=$((i+1))

  # payload
  PAY_SCRIPT="$TMPDIR/payload_$id.sh"
  gen_payload "$id" "$title" "$purpose" > "$PAY_SCRIPT"
  chmod +x "$PAY_SCRIPT"
  P64="$(base64 < "$PAY_SCRIPT" | tr -d '\n')"

  # minimal metadata (no manifest_hash yet)
  META="$(cat <<JSON
{
  "capsule_id": "$id",
  "title": "$title",
  "purpose": "$purpose",
  "session_uuid": "$SESSION_UUID",
  "founder_note": "$FOUNDER_NOTE",
  "date_utc": "$DATE_UTC",
  "chain_prev": "$CHAIN_PREV",
  "provenance": {
    "forge_stamp": "$STAMP",
    "shell": "${SHELL:-bash}",
    "signer_hint": "${SIGNING_KEY:-default-gpg-key}"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "$(text_sha "$P64")",
    "size_b64": ${#P64}
  }
}
JSON
)"

  CONTENT_TO_SIGN="<<CAPSULE:V1>>"$'\n'"$META"$'\n'"<<PAYLOAD>>"$'\n'"$P64"$'\n'"</CAPSULE>"$'\n'
  PREHASH="$(text_sha "$CONTENT_TO_SIGN")"

  # store arrays
  IDS[$i]="$id"; TITLES[$i]="$title"; PURPOSES[$i]="$purpose"
  PREHASHES[$i]="$PREHASH"; PAYLOAD_B64[$i]="$P64"; METAS[$i]="$META"

  echo "$id|$PREHASH" >> "$PRELIST"
  CHAIN_PREV="$PREHASH" # next capsule compounding link
done <<< "$CATALOG"

# Compute manifest hash (canonical: sort by id, then "id|prehash" joined with \n)
sort "$PRELIST" > "$TMPDIR/prehash_sorted.txt"
MANIFEST_CANON="$(cat "$TMPDIR/prehash_sorted.txt")"
MANIFEST_HASH="$(text_sha "$MANIFEST_CANON")"

# Write pack manifest
PACK_MANIFEST="$PACK_DIR/pack_manifest.json"
{
  echo "{"
  echo '  "session_uuid": "'"$SESSION_UUID"'",'
  echo '  "date_utc": "'"$DATE_UTC"'",'
  echo '  "manifest_hash": "'"$MANIFEST_HASH"'",'
  echo '  "capsules": ['
  for idx in $(seq 1 ${#IDS[@]}); do
    printf '    {"id":"%s","title":"%s","prehash":"%s"}' "${IDS[$idx]}" "${TITLES[$idx]}" "${PREHASHES[$idx]}"
    [[ $idx -lt ${#IDS[@]} ]] && printf ','
    printf '\n'
  done
  echo "  ]"
  echo "}"
} > "$PACK_MANIFEST"
echo "$(file_sha "$PACK_MANIFEST")  $(basename "$PACK_MANIFEST")" > "$PACK_DIR/pack_manifest.sha256"

# Assemble & sign final capsules (embed manifest_hash + inline signature)
for idx in $(seq 1 ${#IDS[@]}); do
  id="${IDS[$idx]}"; title="${TITLES[$idx]}"; purpose="${PURPOSES[$idx]}"
  p64="${PAYLOAD_B64[$idx]}"

  # Update chain_prev (compounding) = previous PREHASH if exists
  if [[ $idx -eq 1 ]]; then chain_prev="genesis"; else chain_prev="${PREHASHES[$((idx-1))]}"; fi

  META_FINAL="$(cat <<JSON
{
  "capsule_id": "$id",
  "title": "$title",
  "purpose": "$purpose",
  "session_uuid": "$SESSION_UUID",
  "founder_note": "$FOUNDER_NOTE",
  "date_utc": "$DATE_UTC",
  "chain_prev": "$chain_prev",
  "manifest_hash": "$MANIFEST_HASH",
  "provenance": {
    "forge_stamp": "$STAMP",
    "shell": "${SHELL:-bash}",
    "signer_hint": "${SIGNING_KEY:-default-gpg-key}"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "$(text_sha "$p64")",
    "size_b64": ${#p64}
  }
}
JSON
)"

  CONTENT_TO_SIGN="<<CAPSULE:V1>>"$'\n'"$META_FINAL"$'\n'"<<PAYLOAD>>"$'\n'"$p64"$'\n'"</CAPSULE>"$'\n'

  # Produce detached armored signature (we'll inline it)
  CFILE="$TMPDIR/$id.content"
  SIGFILE="$TMPDIR/$id.sig.asc"
  printf "%s" "$CONTENT_TO_SIGN" > "$CFILE"
  gpg --armor --yes --batch --detach-sign "${SIGNING_KEY_ARG[@]}" --output "$SIGFILE" "$CFILE"

  # Build single-file, self-verifying executable
  OUT="$PACK_DIR/${id}.capsule.sh"
  cat > "$OUT" <<'HDR'
#!/usr/bin/env bash
# EPOCH5 Capsule — single-file (metadata + payload + inline GPG detached signature)
set -euo pipefail
SELF="$0"
usage(){ cat <<USG
Usage:
  $SELF run [--out DIR]       # verify signature, decode payload, execute payload
  $SELF verify                # verify inline signature
  $SELF meta                  # print embedded metadata JSON
USG
}
extract_block(){
  # $1 = start marker, $2 = end marker
  awk -v s="$1" -v e="$2" 'f{print} $0~s{f=1} $0~e{exit}' "$SELF" | sed "1d"
}
verify_sig(){
  extract_block '^<<CAPSULE:V1>>' '^</CAPSULE>$' > "$TMPDIR/content.txt"
  extract_block '^-----BEGIN PGP SIGNATURE-----' '^-----END PGP SIGNATURE-----$' \
    > "$TMPDIR/sig.asc"
  gpg --verify "$TMPDIR/sig.asc" "$TMPDIR/content.txt" >/dev/null 2>&1 && echo "✓ signature OK" || { echo "✗ signature FAIL"; exit 3; }
}
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
case "${1:-}" in
  run)
    verify_sig
    extract_block '^<<CAPSULE:V1>>' '^<<PAYLOAD>>$' | sed '1d' > "$TMPDIR/meta.json"
    extract_block '^<<PAYLOAD>>$' '^</CAPSULE>$' | sed '1d' | tr -d '\n' > "$TMPDIR/payload.b64"
    base64 -d < "$TMPDIR/payload.b64" > "$TMPDIR/payload.sh"
    chmod +x "$TMPDIR/payload.sh"
    OUTDIR="${2:-out}"
    mkdir -p "$OUTDIR" >/dev/null 2>&1 || true
    echo "→ Capsule meta:"
    cat "$TMPDIR/meta.json"
    echo
    echo "→ Running payload..."
    "$TMPDIR/payload.sh" "$OUTDIR"
    ;;
  verify)
    verify_sig
    ;;
  meta)
    extract_block '^<<CAPSULE:V1>>' '^<<PAYLOAD>>$' | sed '1d'
    ;;
  *) usage ;;
esac
exit 0
# == EMBEDDED CONTENT BELOW ==
HDR

  # Append content + signature inline
  {
    printf '%s\n' '<<CAPSULE:V1>>'
    printf '%s\n' "$META_FINAL"
    printf '%s\n' '<<PAYLOAD>>'
    printf '%s\n' "$CONTENT_TO_SIGN" | awk '/^<<PAYLOAD>>/{f=1;next} /^<\/CAPSULE>/{f=0} f{print}' | tr -d '\n'
    printf '\n%s\n' '</CAPSULE>'
    cat "$SIGFILE"
    echo
  } >> "$OUT"

  chmod +x "$OUT"
done

# Write README
cat > "$PACK_DIR/README_pack.md" <<README
# EPOCH5 Capsule Pack — $STAMP

**Session UUID:** $SESSION_UUID  
**Manifest Hash:** $MANIFEST_HASH  
**Founder Note:** $FOUNDER_NOTE  
**Forged at (UTC):** $DATE_UTC

## Files
- \`pack_manifest.json\` (canonical list)
- \`pack_manifest.sha256\`
- \`*.capsule.sh\` (10 self-contained, signed executables)

## Verify
\`\`\`bash
# verify manifest
sha256sum -c pack_manifest.sha256   # (macOS) shasum -a 256 -c pack_manifest.sha256

# verify one capsule
./01-locker-drop.capsule.sh verify
\`\`\`

## Run a capsule
\`\`\`bash
./01-locker-drop.capsule.sh run out/locker
./04-meshcredit-kiosk.capsule.sh run out/meshcredit
\`\`\`
README

echo "✅ Forged 10 capsules → $PACK_DIR"
echo "   Manifest: $PACK_MANIFEST"
echo "   Hash:     $(cat "$PACK_DIR/pack_manifest.sha256")"
echo
echo "Examples:"
echo "  (cd $PACK_DIR && ./01-locker-drop.capsule.sh verify && ./01-locker-drop.capsule.sh run out/locker)"