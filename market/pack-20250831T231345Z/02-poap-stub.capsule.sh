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
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "f04b96f19474bf48ccf4b8ff8ff6dd1707a7ff1df1ad5be1dc341559e15b5a2d",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtZEIgf8C/CLNj9OiWXk5IqwksuhCUD2
c8jeKPtIkS59KhKfwIfgsH/Ke3rOHQaxN9VCSl8yPy8HEO2JlA62s3u9bGigvTZX
pZ1u25R/BU6o5iZX4F8O3prToR+M9H3sBQP28qp9KWIT8s1B6b9VtyQFJb3O5+25
COwyg8Fn+kMe8Ser8g1aR4oH1oE8MWci+8c4kUBkz4W7rSNw+fwYnJXdHCjjwckq
4demHQJ2vO6RxvmR2Fz5FeObxJrb/dg3NXgyPCJnMbEQ8T33OlgR9i5sXaFQAhOz
oRoteUnQwJEMO/YXiBT7zHgpgfVIQXBQHDrzMoAWyrKIU841A9fF2gH3+xkIHA==
=/f9h
-----END PGP SIGNATURE-----

