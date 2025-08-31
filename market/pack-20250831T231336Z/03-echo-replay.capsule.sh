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
  "capsule_id": "03-echo-replay",
  "title": "Echo-Theatre Replay Pack",
  "purpose": "Bundle replays/logs → tar.gz + hash",
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "50a5821584f1f0ea6693e9e5b27a640e4fccd93fb5c079992085f14edf418695",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "f9db9db85744bcb3b3185f87bcd2dd90818442354ea39bdf49efe1cbd0005325",
    "size_b64": 608
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2VjaG9fcmVwbGF5fSIKU1JDPSIkezI6LS4vbG9nc30iCm1rZGlyIC1wICIkT1VUIgpUQVI9IiRPVVQvZWNob19yZXBsYXlfJChkYXRlIC11ICslWSVtJWRUJUglTSVTWikudGFyLmd6Igp0YXIgLWN6ZiAiJFRBUiIgIiRTUkMiIDI+L2Rldi9udWxsIHx8IHRhciAtY3pmICIkVEFSIiAtLWZpbGVzLWZyb20gL2Rldi9udWxsClNIQVNVTT0iJChzaGFzdW0gLWEgMjU2ICIkVEFSIiAyPi9kZXYvbnVsbCB8IGF3ayAne3ByaW50ICQxfScpIgpbIC16ICIkU0hBU1VNIiBdICYmIFNIQVNVTT0iJChzaGEyNTZzdW0gIiRUQVIiIHwgYXdrICd7cHJpbnQgJDF9JykiCmVjaG8gIiRTSEFTVU0gICQoYmFzZW5hbWUgIiRUQVIiKSIgfCB0ZWUgIiRUQVIuc2hhMjU2IgplY2hvICJXcm90ZTogJFRBUiAgJFRBUi5zaGEyNTYiCg==
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtZL8QgAuhiqSsZNYwaAAXE0jMzhIpV1wbiKkWKkVcFCwwVaj5Cu1jkoxOi4SSJo
H6K2LM9ChIErZWXn+YbI1xPGPTzzYgTk8jIis6/TAM1XmFZ6yVtBK9+7WEAyLfFB
h3TTteoex9ndx2sDvo1q4cQvJ74Drm711jq/G7qIZjgQlPm738zp2DWodQ1jsFrW
VIRauNBlbhawVHG8X2MrJyFGgsIJruiO50BLd3duZC5zWIiJYfdfGgYQWunIHGAV
diovKX+cc7DP2Yndkp+rJGzInHMwGzVwrqiadmTYywyQweYvda0nMdxdkYGybBhw
98bbsJoXRWwE1dQ3mh4t7A8iIiBlFA==
=8srF
-----END PGP SIGNATURE-----

