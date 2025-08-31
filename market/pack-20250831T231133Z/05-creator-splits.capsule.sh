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
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "d4d3a01dc11075cd219e036f5e2c2c3e4a1c5aad6f96fd138e93d2638889d883",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtZDLwf9GYDwVsHH/MyFQVZC94yTo251
TurSfqBcuj1YaF27J5ZI/G+ZlyoZfNNQg919afWj8Oq9ne4EAjT1xBk/NYQVrzdf
gxN4vwM5BYbEoBFGOC6xQ6jfbbUV4XTwgmcF9A4C+rWXxOnlBIl4O1lRwEwhzV+W
4jELD1BcTZq3Hq62y3TEDAMtBciKya9MDw15sAm/Ok2axKBKSzO3DUp9SHK9HG3E
7j+OBDGEHpYuyHrW6ygY5gwYOm3FaymcjK5Lq+R0pzqnpDnt/qylm0trjRWwul05
Xf+zsGqhXCm1ETIvKhFhzNjaMS84lXN3K+Rta5Viu5ecJp94dA7v7hzgZU2b2Q==
=oU7B
-----END PGP SIGNATURE-----

