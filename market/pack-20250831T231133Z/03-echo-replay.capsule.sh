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
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "dc2ded3547bdc528e380eff7d2cc17e8af3934d32c0a5675ddc39c994145dcf1",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtYuGQgAhaRR8XjCoJYcKQ7shj5JDlFn
LErm96RxZGlcS3TuPL15sanXW1VXoxa6is0UhlJOkYZGwk/qGOnxx5JxMS9Y9g45
/gurxfEs4xfXcuqpyqhr1Ju6N9jy/aivQLD2pPYhd9k8pLcaxbId83j20U0WkRGq
fqsVwo+wz4dgSPQc1QoVHa11KzqikHq/jyg4qyyjmlXcAEEjYQRxyqGQ/kbqob1I
Pi8Grq8Aek1kkiANKVG1H8AhQT7eR//QvuotGI4d6XZVjv8kieTm7sO/VCqS3WOc
vY49AUpmD658t4Aw2Biw3Voh2nO1KGfDAxlc76Tq8OGVRnLxsfZZc9lY/8yKVQ==
=I499
-----END PGP SIGNATURE-----

