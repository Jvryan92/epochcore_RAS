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
  "capsule_id": "04-meshcredit-kiosk",
  "title": "MeshCredit Kiosk",
  "purpose": "Emit $100 receipt capsules → jsonl + seals",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "12a9d33c3b7b2d44bb797454d60f4f98b1898f12bfcb579be979522acf634c78",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "fda31062a2b16b5119cc71433831cc90bf966513dbc7c5ea2e440ddbcdf408ad",
    "size_b64": 416
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L21lc2hjcmVkaXR9IjsgUFJJQ0U9IiR7UFJJQ0U6LTEwMH0iCm1rZGlyIC1wICIkT1VUIgpKPSIkT1VUL3NhbGVzLmpzb25sIgp0cz0iJChkYXRlIC11ICslWS0lbS0lZFQlSDolTTolU1opIgppZD0ic2FsZS0kKGRhdGUgLXUgKyVZJW0lZFQlSCVNJVNaKS0kUkFORE9NIgpwcmludGYgJ3siaWQiOiIlcyIsInRzIjoiJXMiLCJhbW91bnRfdXNkIjolcywibm90ZSI6ImNhcHN1bGUgc2FsZSJ9XG4nICIkaWQiICIkdHMiICIkUFJJQ0UiIHwgdGVlIC1hICIkSiIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtbTaggAqL3GWlu9b7UOnym4kjZF1RzI
et076Zt6PFTj/tiCLOdUwv7tbBqnMzobVVVN4Ij4Bk+6mLeVM25PKy+fuzB6fUEf
Omxvae4h29yms23ahMfvYm7mM78ok6HRAM9KNEs+TdrAbQecxGRXt+DImpl5Nnc2
gPoWW0yVlGUIt7GGSIpFr1SP8sutfT/Ujg3sLCuYhc+kAgn/v2mWmvEGguZVHWNg
vr8mBshsOogpmVs/zw9G2xYJHjT9rmB3NLeWB1Y+ZNnZiGxRSj7DLHEuxPOdn+9N
F1s2dkbplFtb61S851cSpC2dYo8S1Vk7JFL5nNeyu+NPiktMeuRAFStgM9MptQ==
=SCZf
-----END PGP SIGNATURE-----

