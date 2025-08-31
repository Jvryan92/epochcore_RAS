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
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "336c045b08f3a82547ad9a1c04aabeb5c75d6c64f570969b51ed1095727bd112",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtaKLgf/dUNwwbKzJi82qCyyv+1znudO
vMWHprsN1Eb3UNtE45DYbJcS0prRNpiLh8rZ05mFb/KspaetKubRgdf5yxe1eak7
9LmNlzrkX/173eNONHmLfh53pDsEojFD7IUOpo1lz1+uwH8yfeckGFzrdpqxnjVa
xqd2dC6D0mziD2iRqYbZ+6SiToFB8BkX5vToaGRCbduuimM/obCeTQ02SWiU7sAr
NdeerDYRs2RAFGQnO6S8lQpkHnKYr0VUawuSisXhFC0yl1GMl7y7vIbpr5Ji4bTD
KJyrJyyJNeLKSfNdhIzaY9M6crZpMJtwaF7HeQWsp77ZN/f47dgcBH8E41AEZQ==
=x33C
-----END PGP SIGNATURE-----

