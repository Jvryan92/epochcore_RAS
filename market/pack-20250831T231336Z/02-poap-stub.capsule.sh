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
  "capsule_id": "02-poap-stub",
  "title": "POAP Claim Stub",
  "purpose": "Time-window attendance claims (JSON), no chain",
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "7a0b927c48a438eb943ab22294b28f16c1e16d243a4192df0c660097b18d6878",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "ad0ea01324213602bc5a030688940f7baba9554647c68614c1e97d158b9bfc49",
    "size_b64": 552
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L3BvYXBfc3R1Yn0iOyBXSU5ET1dfTUlOPSIke1dJTkRPV19NSU46LTYwfSIKbWtkaXIgLXAgIiRPVVQiClM9IiRPVVQvcG9hcF93aW5kb3cuanNvbiIKU1RBUlQ9IiQoZGF0ZSAtdSArJVktJW0tJWRUJUg6JU06JVNaKSIKRU5EPSIkKGRhdGUgLXUgLWQgIiRXSU5ET1dfTUlOIG1pbiIgKyVZLSVtLSVkVCVIOiVNOiVTWiAyPi9kZXYvbnVsbCB8fCBkYXRlIC11IC12ICsiJFdJTkRPV19NSU4iTSArJVktJW0tJWRUJUg6JU06JVNaKSIKcHJpbnRmICd7InN0YXJ0IjoiJXMiLCJlbmQiOiIlcyIsInJ1bGVzIjp7ImdlbyI6ZmFsc2UsInJhdGVfbGltaXQiOnRydWV9fVxuJyAiJFNUQVJUIiAiJEVORCIgPiAiJFMiCmVjaG8gIldyb3RlOiAkUyIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtYhBwf9HJPk6VLK7lW/DwEqGsQobkc8pGpGnwyT2CdvdqIfvtzUsumSesCevwLL
A/2DQwCf9G+and5ifI8mfIKLlJm6K3je2uxfmMqLyAPISXquFxXfnZ84VcNpS2vG
bhohzHMvm+7R3l2Lts8rkrOMuHfXjn5/NL7ug2ohtzIjBfXRkYlaJ6kTHAKyP5oS
OS5PpYjDWWrF6Dy29Ty8Tp4F2kD2bcQ1vD3RWrB5iFmuNhdP56UmY554fPSOBVM0
vCtRBDpW6mBBYJXr5p+wnfFfqKDmD4QHUXaGxRt/q4D7f0sVq/b3wtQ0oxlzxDG2
J6rdF3rC+jlNN6v2LpKzS580ln4SOA==
=Q78T
-----END PGP SIGNATURE-----

