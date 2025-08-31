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
  "capsule_id": "10-storefront-snap",
  "title": "Storefront Snapshot",
  "purpose": "Static snapshot skeleton with manifest",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "a522ae74ebd74dbf9acd25e55422173d53133394835cf85e3faede3fb7684ab1",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "aaf0eab3a0403e5b71704745ae3b68ee5f789ec3bc0ff89760fcdaa608bc131f",
    "size_b64": 664
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L3N0b3JlZnJvbnR9IjsgbWtkaXIgLXAgIiRPVVQiCmNhdCA+ICIkT1VUL2luZGV4Lmh0bWwiIDw8SFRNTAo8IWRvY3R5cGUgaHRtbD48bWV0YSBjaGFyc2V0PSJ1dGYtOCI+Cjx0aXRsZT5FUE9DSCBTdG9yZWZyb250IFNuYXBzaG90PC90aXRsZT4KPGgxPkVQT0NIIOKAlCBTbmFwc2hvdDwvaDE+CjxwPlN0YXRpYyBkcm9wOyByZXBsYWNlIHdpdGggeW91ciBjb250ZW50LiBUaGlzIGZpbGUgaXMgZ2VuZXJhdGVkIGJ5IGEgY2Fwc3VsZS48L3A+CkhUTUwKKHNoYTI1NnN1bSAiJE9VVC9pbmRleC5odG1sIiAyPi9kZXYvbnVsbCB8fCBzaGFzdW0gLWEgMjU2ICIkT1VUL2luZGV4Lmh0bWwiKSB8IGF3ayAne3ByaW50ICQxIiAgaW5kZXguaHRtbCJ9JyA+ICIkT1VUL21hbmlmZXN0LnNoYTI1NiIKZWNobyAiV3JvdGU6ICRPVVQvaW5kZXguaHRtbCAgJE9VVC9tYW5pZmVzdC5zaGEyNTYiCg==
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtb4vAf8CIEZx3FOqa5KbsPelKS4/sNg
bLAZ1sKiXS/6jNe1r5cq/gH6B91e7i92cxz0gWALtVIuRCRSNcDRryNj2ZISEDOb
F/LI7zMm5ABDcF5BGpin2Mtb7186y/7VNbw3OrYAC7OCmiBeZc+b2NiZgUCbBrh0
THk58KirrreDx4ozeAGfrC4NQdHBtSFpuO/A2xaer7taK7zCwCknIhBI18H7Yq0+
KHqfnfksZggWvR60BcOgaa4ZnPefAc2st9RLOW5pDyrYl+XJ2aBGr7W6IKgqFOsc
AedxGz+IyZLInl1C+xrLGZuBwQbU6NVGqNxKPr5roeIcDqpib+PKSD1MwQ7ntA==
=0aDn
-----END PGP SIGNATURE-----

