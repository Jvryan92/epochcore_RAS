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
  "capsule_id": "09-telemetry-harv",
  "title": "Telemetry Harvester",
  "purpose": "Turn local logs → jsonl with line-hashes",
  "session_uuid": "802a738e-53b9-4f73-947c-65f4ac1bcb94",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:11:33Z",
  "chain_prev": "5846c2316ddf5cbbc29a19e33643db312c551eaef58ef5cf30180a010252d3e0",
  "manifest_hash": "d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a",
  "provenance": {
    "forge_stamp": "20250831T231133Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "a3afe078c788867e5ddf666e18ab0cb3f63a1ccb5a00b1cd10b541955664ebff",
    "size_b64": 872
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L3RlbGVtZXRyeX0iOyBTUkM9IiR7MjotL3Zhci9sb2cvc3lzdGVtLmxvZ30iCm1rZGlyIC1wICIkT1VUIjsgSj0iJE9VVC90ZWxlbWV0cnkuanNvbmwiCjogPiAiJEoiCnRzPSIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiCmlmIFsgLWYgIiRTUkMiIF07IHRoZW4gdGFpbCAtbiA1MCAiJFNSQyIgfCB3aGlsZSBJRlM9IHJlYWQgLXIgbGluZTsgZG8KICBoPSQocHJpbnRmICIlcyIgIiRsaW5lIiB8IHNoYTI1NnN1bSAyPi9kZXYvbnVsbCB8IGF3ayAne3ByaW50ICQxfScpCiAgWyAteiAiJGgiIF0gJiYgaD0kKHByaW50ZiAiJXMiICIkbGluZSIgfCBzaGFzdW0gLWEgMjU2IHwgYXdrICd7cHJpbnQgJDF9JykKICBwcmludGYgJ3sidHMiOiIlcyIsImxpbmVfaGFzaCI6IiVzIiwic2FtcGxlIjoiJXMifVxuJyAiJHRzIiAiJGgiICIkKGVjaG8gIiRsaW5lIiB8IHNlZCAncy8iL1xcIi9nJyB8IGN1dCAtYzEtMTIwKSIgPj4gIiRKIgpkb25lCmVsc2UKICBwcmludGYgJ3sidHMiOiIlcyIsImxpbmVfaGFzaCI6IiVzIiwic2FtcGxlIjoiJXMifVxuJyAiJHRzIiAibm8tc3JjIiAibm8gc291cmNlIGZpbGUiID4+ICIkSiIKZmkKZWNobyAiV3JvdGU6ICRKIgo=
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01qUXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtZS6wf/SGCMSZaPpFwQDNx/jpFcxAnZ
F/8BG7Yt8hBFYJ8I37p9r84zPoKlNYtLF8jGaCYe3ncjtRWe8YOqqVcUysrNvt5j
PLqJkosWnp153uIgTIVEfHalmGd91VfrFo9bO2l7tEphHJC0KCjoo32b8FYphMky
JwlYjPnRAChAFyqyFd18pF3xugBnqLeJKH9/PERTSyCrvN8txiF7bwxtJZTYdbrC
pzFOZhvMRVn50Ii/6uoq8c8GbVwYlVZ8XVe/SfA7dID8arzLIjzBIwdqEqrENaRG
RI4lD7UKtX+DRcW6IuaEahzKBNaZLluHSZb4Q8FqYvZcrEY2DfWo0O198WcP3Q==
=BkXf
-----END PGP SIGNATURE-----

