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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "aecb7bb15cb7ee691a973b81a67a558395746da7457b3b9ef4cb9ed6c672ce47",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtZFkwgAhrBoNnsDVbDXu5ZGgDjE1G02y4dCdlWHwtuLsIq0iGgpkiAx5fnLDjtc
afg0kCAy8Z7z5b8WYkFSm35e1tRrc/L8gLipoNjf4g5KlQUbiGyeEKy/tTdWPa7o
JL0snVPyv2uj9BBjwYarzK67Ik8u2bRQIf9jmxxYoNkulu1UA4X+FOqRw8hAj0OB
FkawhJ0YhP2HP8i73DaF0NOf+nXHZuP9aKJp52Rzejm/P6sCKOuGnZ9guetbE/aK
BOFauSeht6T9q1nkL0dWo8LC03kKX6Pj5r8/VOwwjGhCEOwrigTY7148g/D90XZd
6uIvGVSNUvFlq8L6cERN8MnUBzrLEw==
=WCqy
-----END PGP SIGNATURE-----

