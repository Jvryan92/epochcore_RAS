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
  "capsule_id": "07-fair-balancer",
  "title": "A/B Balancer Capsule",
  "purpose": "Simulate fairness KPIs over params (CSV)",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "2924116e787b006ef2aa5f4205c6ea46f07f12c427e2a7c6329928ce62c11635",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "872ffc04ad6a1a80117ac9301d5390509bb203c62b30e18158bc21d9b1e5b99b",
    "size_b64": 428
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2ZhaXJfYmFsYW5jZXJ9IjsgTj0iJHtOOi0xMDAwfSI7IG1rZGlyIC1wICIkT1VUIgpDU1Y9IiRPVVQva3BpLmNzdiI7IGVjaG8gInRyaWFsLGNsZWFuX3BsYXlzLHF1aXRfcmF0ZSxtYXRjaF9kZWx0YSIgPiAiJENTViIKZm9yIGkgaW4gJChzZXEgMSAiJE4iKTsgZG8KICBjcD0kKChSQU5ET00lMTArMSkpOyBxcj0kKChSQU5ET00lMjApKTsgbWQ9JCgoUkFORE9NJTUpKQogIGVjaG8gIiRpLCRjcCwkcXIsJG1kIiA+PiAiJENTViIKZG9uZQplY2hvICJXcm90ZTogJENTViIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtbKMQgAujaXW22CdfJ5NHBdZibDMHsf
lQHrPF/5eUHMTqcdsOUixD2DoUfHr8Jw72jKMOIeWSUK/jAAXLHqmnH5xYSj/XKZ
mHmb3tT/+ZzFu8MCPf5fWzpI0/deMPLsqOBORVxhl9JoY6WV6J+MRs3EaxrpmBfN
6tKZUsoACPQd3v3cAfUnCgbXZJnLY4gKPqVDtIzKOfVi1PaVqRlnz3/mibTMQs0b
XGjCZYM67Ff2O89zq/9mrzvXZ+WLjJptQ08q2ekpVCaVQPVPlVNcNjJWTsTSo66y
wmJUsrewvnd9kWo9Y8ZehYZDHEYangKLLlFg+Pd8li/M5gegbD7kNjeRdr2p/Q==
=xIN8
-----END PGP SIGNATURE-----

