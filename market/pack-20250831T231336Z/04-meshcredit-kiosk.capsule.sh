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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "27b9556de4cd94afe27b31c091156e358020ffd0a095bef135c139f7bdce6e12",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtbE5wf/UKAFaoB/kXYuKCyHByG+DrmHh5GcvkncKGGngIlhfFhuEYorTCNI2aLq
CYswTUzyaPe4/abAm42nC2jBNpEe6FuISBfsKRozn2oTm/ZL5+5kLvlXgnfY7Ypn
NU4t0J1vikTJ0fO2PCG5UTD8K7hZ1lmvogSludh02TJQ/LIu4zPGsEJ4vHNrGvr9
s7PYm4tQk38/ug24kWm5Ai9NYnQW7RccE2SgBwN6y1dUXgO+ru/HEgiAbAhROX8M
6iiCOUaLUp5F6Kruae30aMNQTani9jX9WIzJAzY2DW7nuX3pui7XOoHFSSf8Bmwo
+ekV9GyXbl34NhmI/c+TBs+fu7TbtA==
=6xmh
-----END PGP SIGNATURE-----

