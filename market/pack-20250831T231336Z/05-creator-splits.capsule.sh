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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "8f1d187c4a59eab4bf0c4ce588ad7de9b167c7940ad9df93aff9dd7a5210c9c1",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
Dtb4nwf+OB/u18nU7cvh7zZ5Yv4A60ghNvuSmwvui3fRAKgrohxkZl+rGGQx9Taf
NRczbOn/KQ+KYwFNLz6wPSJ6DBcoh74KyemZoivLWRBWX0vOTv3RgOeymDW2unsp
YSYybpqY228YSLHr6u4EWNevB0IRhdSDrmpltofXHF3cNfg7B7quIOAtYyxicAr/
JqgIAXpmgOL1MdDR7E84waY3jkX4lJXgkurZEw0YV/ZPhtZP/n1BA55xN2tZgZTS
x/15y/oSwPAt/8iAYSWnh8zAZDAliU4GdtjzO/QCFn35lqeLw5jvf1HHZWkN8Y4B
kL3QzOPzxq/CBaQRwHOn0YkvZbPJ1A==
=5iJc
-----END PGP SIGNATURE-----

