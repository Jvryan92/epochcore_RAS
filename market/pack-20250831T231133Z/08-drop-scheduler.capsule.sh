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
  "capsule_id": "08-drop-scheduler",
  "title": "Drop-Window Scheduler",
  "purpose": "Emit ICS + JSON schedule blocks (UTC)",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "5c403477ced96d193b5cfb0288096f32024123824fe92090e1ce2519d42dc056",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "93565929d2541143ed2b3e46e0f3ce61e5fd21bb665158d0eb8a671a1f994a87",
    "size_b64": 812
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2Ryb3Bfc2NoZWR9IjsgbWtkaXIgLXAgIiRPVVQiCklDUz0iJE9VVC9kcm9wcy5pY3MiOyBKU09OPSIkT1VUL2Ryb3BzLmpzb24iCm5vdz0iJChkYXRlIC11ICslWSVtJWRUJUglTSVTWikiCmNhdCA+ICIkSUNTIiA8PElDUwpCRUdJTjpWQ0FMRU5EQVIKVkVSU0lPTjoyLjAKUFJPRElEOi0vL0VQT0NILy9Ecm9wcy8vRU4KQkVHSU46VkVWRU5UClVJRDpkcm9wLSRub3dAZXBvY2gKRFRTVEFNUDokbm93CkRUU1RBUlQ6JG5vdwpEVEVORDokKGRhdGUgLXUgLWQgIiszMCBtaW51dGVzIiArJVklbSVkVCVIJU0lU1ogMj4vZGV2L251bGwgfHwgZGF0ZSAtdSAtdiArMzBNICslWSVtJWRUJUglTSVTWikKU1VNTUFSWTpFUE9DSCBEcm9wIFdpbmRvdwpFTkQ6VkVWRU5UCkVORDpWQ0FMRU5EQVIKSUNTCnByaW50ZiAneyJ0cyI6IiVzIiwid2luZG93cyI6W3sic3RhcnQiOiIlcyIsIm1pbnMiOjMwfV19XG4nICIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiICIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiID4gIiRKU09OIgplY2hvICJXcm90ZTogJElDUyAgJEpTT04iCg==
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtZQPAf/cueFurHIpTKf8aJuH1oyFdyF
m8faOz9rRZQVOX+o+GPe04NgD3Y4nUHFevC4Vg/PTRZNDlsxAGqPbvt1dZAI+GqM
0SEO3RlHaaSctYjtwb2zd7MPVI2gC8Zs/zMqC+S7HCFq3c3yzF5M5I5I9cP/iEGI
BM9TY/TOfX8BPfr/FbcuLeK0NhFHbB0Bc4f9e7+tPR262uq3Ptp85lWmec+zT8Gu
oeXxP9vTJXtlGrG2KwpEIlx90k0tHncbMPsmMt/T/lvJQROTqJPfoddF8rj36yPm
D8+foX09rFCoGJhs0SeefyitZVjf54RLmZ/0XMM0khRcnm+/4rfVcDtwESIsIg==
=LcTe
-----END PGP SIGNATURE-----

