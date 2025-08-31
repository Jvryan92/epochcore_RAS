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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "3b9c38f6f853279a90c833cbe79ce0279fb2a70fcd94be6abcfe72011187e616",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtZ8Bgf/YByT5c4IislYrjlVsUJLM+uezvIG0jcMrdjPxHLSDdgMQ4XTgl5LnqRU
K0gHLNYjcScfEAmnr6F9kg1LgKSb4993tLL6sYdLJ30S5DLYrZL8iKUkr/4HECm5
SiDszP1V0nnwxlhNLHZ1Z4w1+r/nMXGmpf+Y7kWXsxsJMJ8w1kDIdJv1rqEnZnqA
jjiuuZw+BdIzBEae1zoTPtmHz/xULfEGgK1orzE0YDyADgouMIK/1dyW4x8B2ae5
Eu2YZLlCNBM060dxOytU6bhRRlDlZTngDmzpvU6oVaALbqWvUK4Mp6SnoTV1yadz
JfQYs7eh/8wESLqalL6/mBjHjUgjrA==
=MCNV
-----END PGP SIGNATURE-----

