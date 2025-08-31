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
<<CAPSULE:V1>>
{
  "capsule_id": "03-echo-replay",
  "title": "Echo-Theatre Replay Pack",
  "purpose": "Bundle replays/logs → tar.gz + hash",
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "82b8786edcede8c9444dd7c7be9866e636b4a0d35d4d550ecd01fdd804d8e5a5",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "f9db9db85744bcb3b3185f87bcd2dd90818442354ea39bdf49efe1cbd0005325",
    "size_b64": 608
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2VjaG9fcmVwbGF5fSIKU1JDPSIkezI6LS4vbG9nc30iCm1rZGlyIC1wICIkT1VUIgpUQVI9IiRPVVQvZWNob19yZXBsYXlfJChkYXRlIC11ICslWSVtJWRUJUglTSVTWikudGFyLmd6Igp0YXIgLWN6ZiAiJFRBUiIgIiRTUkMiIDI+L2Rldi9udWxsIHx8IHRhciAtY3pmICIkVEFSIiAtLWZpbGVzLWZyb20gL2Rldi9udWxsClNIQVNVTT0iJChzaGFzdW0gLWEgMjU2ICIkVEFSIiAyPi9kZXYvbnVsbCB8IGF3ayAne3ByaW50ICQxfScpIgpbIC16ICIkU0hBU1VNIiBdICYmIFNIQVNVTT0iJChzaGEyNTZzdW0gIiRUQVIiIHwgYXdrICd7cHJpbnQgJDF9JykiCmVjaG8gIiRTSEFTVU0gICQoYmFzZW5hbWUgIiRUQVIiKSIgfCB0ZWUgIiRUQVIuc2hhMjU2IgplY2hvICJXcm90ZTogJFRBUiAgJFRBUi5zaGEyNTYiCg==
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtY0iwf/SfumJRB4kA8T34TTnf8fF1L9
8itlxYecdYyhHq/yf5y88GGzDy6LvxEkYnWW3xAP3TdYSO2JlWZRs3MnfX1QGKRk
+y1n20GcTnh5xdQU/TgOsyB7IYnUN6HkkXJd4BJR/KrhHTKpneqeuIob/A5vFvI/
34neXhfq+fPZy4+BPG99j1SvrD5KZUkKQOc5fsqlQfPEIP+lS9mI5qz37bifCNVr
XHIm6AITOdCMsOy9tzZsgdQQhhvNDPxBJWIMVsTj3UtZJvjG1qXY3FUecJs0bZ7M
Z9gIldKOct4fLCc6b6SIHVV3LuXj/JLbPPjTxn6z/nOyz4ofHvcysOgeNXxHuQ==
=yeov
-----END PGP SIGNATURE-----

