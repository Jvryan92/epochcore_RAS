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
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "479c0b1655d602675b0ff1b21c155366a1167095796ba01010bba71168a83307",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtaUSgf9FYyijcA9F4pV4fqmo9gcBjwB
dkilQlOFx1kqlsLHUF4NxqXshsxq9VVo1hH6nBJDC/uBOl6Vt7rIVYoanNF8/cca
o74QsVZ3Le1LWcp1mOnHwl5hWfyQkU/3clT0nS+oCEUbGOuLIB72bELCHOZjE1Hr
NuMVPUsBrh8CzPzQ18CYT7nDv5svyGIHUNSh9s1gf3HXTswAal2ybzD45KuYvVIN
Eq4zwq6ePX/riHZa8w9pCoR00pT4DdibToxXmhkIZj5/Y8c0KLdMKYdtni/2uFlD
Z7UFG5mExzah4aZdzV81ugw6TFK6imahlMgwLU4HwFILolDQXPt3w7uGmbeOug==
=9AMT
-----END PGP SIGNATURE-----

