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
  "capsule_id": "06-gov-commit",
  "title": "Governance Commit Capsule",
  "purpose": "Commit–reveal seed (demo VRF stub) for votes",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "efa48a28fccad16e49af1bb03b99169ffe7d1a1c2ca49708bfc2ee0b3f9a5506",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "1428f212589ee3ce7c3cc0cc07fb2f167164c6b79e910cc877d84ff9b48839b8",
    "size_b64": 500
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2dvdl9jb21taXR9IjsgbWtkaXIgLXAgIiRPVVQiCnNlZWQ9IiQoZGF0ZSAtdSArJXMpJFJBTkRPTSIKY29tbWl0PSQocHJpbnRmICIlcyIgIiRzZWVkIiB8IHNoYTI1NnN1bSAyPi9kZXYvbnVsbCB8IGF3ayAne3ByaW50ICQxfScpClsgLXogIiRjb21taXQiIF0gJiYgY29tbWl0PSQocHJpbnRmICIlcyIgIiRzZWVkIiB8IHNoYXN1bSAtYSAyNTYgfCBhd2sgJ3twcmludCAkMX0nKQpwcmludGYgJ3siY29tbWl0IjoiJXMiLCJ0cyI6IiVzIn1cbicgIiRjb21taXQiICIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiIHwgdGVlICIkT1VUL2NvbW1pdC5qc29uIgo=
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtYs8wf9HRut7KB9JzlnHDcg98pCI8sF
ZUaWUR8Nf6pfNuiNnU2t+ZTz5+pLqpXA5cD651QrJJeCQ2r7TxbfRg5iEa+AtNf5
ERC6sE0rNr+txKcVJzpluydXvQHM9y5/oc2RJKqxyMy7KBYDCcU1CDivYsKn58sR
kFwgFb9RQtqjNU7y1uRTkheq/rVh5IuJGGTyrQH0i458KUwCdkzHWZOn0tOwpZC4
QCV75DdYh6HuMnSK+bL5oy1lViCq6dCER4OpjiLA/RF8dMx8sJHfHQEUTJ8yNSqa
0tFU9oRAjHQsFuKIOUBK99Z2Q3HhGCsafl1Yvzl6V5hDROlv8EsbLuaW586OQg==
=cdvh
-----END PGP SIGNATURE-----

