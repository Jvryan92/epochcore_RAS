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
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "1f976886eeae7f7b4e6689be57308884aa19b7087d12495f43fd82db55a730f8",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtby4Af8DfMSVRBldO8YO1LSOtbfqK2u
e7uHCgthR1NaWETBv76RzxVIZBpxUjkqJw6Z627WpzGTCXootAlHop3FxrDsd1h9
ZcD5LLg0odC/EdNja9paBKj3CqiXv43SLqeQvJrpS+98GmEj3/F8KOtDpySBs9nZ
tG7DfvH4tJ6mLdcj8rWN8Rkmud7rLQmp11WSIEv4DR1G7uMbcBiEzbmygvbgHzSH
MYtgA6N0Z+rasx6tArbCyUMYnhTbI6VS4VbTIKkAQZVG87gzVzJHrzNQRlzYrfxv
NnzKsyARTNNZBpDyTbdPaYcHfJXmpBJQCwQe3AT+xdrTveJK6nDRdmLInN6NLg==
=YJvs
-----END PGP SIGNATURE-----

