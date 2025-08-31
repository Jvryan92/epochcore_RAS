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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "cab07db4890fccca3546d4c156366ef3fee768706e7d159f29585d5782d26b5f",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
Dtb55Qf/atkInIYdeNAKBQ8jIQ3HGv+ZJP7xyEXjT0TV5h9l9Av5islNlrdvx3FN
n7PPEjsvEDHGBVowYd1nNcVMvd+RbxQIvRaBO1vvy39c4DRjec6UXKDUrwppEvbT
vzQAYbHWknY2VyBOGRMj/5A832fFmR+QsiAbX/Y1dyM8pJjszXXDniAeEGHrvpvg
txV1WED1hGSXgtuOA3soZdRVLQfMbG6Np2+Wmj1ApsVZ4VBeAFFRDkRoQZnwJ6Gm
c1Zy95sdWi5rYbxuK9P2EgP+jQorjFLLW65OrgOLlk1wwOmxt10ThjfFsd6q2Grz
ErmGUfULM9+jmw8ZoFYRfpObPGU2/g==
=E/XX
-----END PGP SIGNATURE-----

