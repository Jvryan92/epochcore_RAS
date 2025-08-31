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
  "capsule_id": "05-creator-splits",
  "title": "Creator Split Planner",
  "purpose": "Compute split JSON (royalty/primary/secondary)",
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "8a8bde76063280bcd358442316b5a616a16da665faebee5665f4e827ba6c5309",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "86b4bc450f1991d760e6d478cfa303640c3c56856efa40b7671131e43d3f9e67",
    "size_b64": 336
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L3NwbGl0c30iOyBta2RpciAtcCAiJE9VVCIKY2F0ID4gIiRPVVQvc3BsaXRzLmpzb24iIDw8SlNPTgp7InByaW1hcnkiOnsiY3JlYXRvciI6MC42LCJzdHVkaW8iOjAuMzUsInBvb2wiOjAuMDV9LCJzZWNvbmRhcnkiOnsiY3JlYXRvciI6MC41LCJzdHVkaW8iOjAuMiwicG9vbCI6MC4zfX0KSlNPTgplY2hvICJXcm90ZTogJE9VVC9zcGxpdHMuanNvbiIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtbeIQf/TqXjsvgMfGyYOhBCKaFJJGJu
YMJLumNuB7AsE/rF/vrYKB/LDmoId70GU1iKQzh8K+ixaIQARb95rKI1PlYnr5Tv
jEnehuGh2XVy+PnKD3PLtTje5vHyRkjn7z48k7M6r2aiMRUnFqivn1DQMAUgQFuQ
IyBeZga/7wryKYEvwft+A0nSaWpKrgErCrqwgrerGiWidEaqWt7rMRx/GFueK4Em
lDtpidhKdm1Pamv2uYs/IuE8n+0L3W3+wiJ/FJdIJREdEFuAsCluHpZmmlI68vF4
zkg+vLskPw8uIHw2+tLvQYaC8Mxn+onwBY8/vVBzkII1LvySoQNBxhVWvH/BMA==
=PFSe
-----END PGP SIGNATURE-----

