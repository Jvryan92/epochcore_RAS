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
  "capsule_id": "07-fair-balancer",
  "title": "A/B Balancer Capsule",
  "purpose": "Simulate fairness KPIs over params (CSV)",
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "085eb57c056294b25f6905d2f8020b41e2436be04e4737c1639339ddb5f3e291",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "872ffc04ad6a1a80117ac9301d5390509bb203c62b30e18158bc21d9b1e5b99b",
    "size_b64": 428
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2ZhaXJfYmFsYW5jZXJ9IjsgTj0iJHtOOi0xMDAwfSI7IG1rZGlyIC1wICIkT1VUIgpDU1Y9IiRPVVQva3BpLmNzdiI7IGVjaG8gInRyaWFsLGNsZWFuX3BsYXlzLHF1aXRfcmF0ZSxtYXRjaF9kZWx0YSIgPiAiJENTViIKZm9yIGkgaW4gJChzZXEgMSAiJE4iKTsgZG8KICBjcD0kKChSQU5ET00lMTArMSkpOyBxcj0kKChSQU5ET00lMjApKTsgbWQ9JCgoUkFORE9NJTUpKQogIGVjaG8gIiRpLCRjcCwkcXIsJG1kIiA+PiAiJENTViIKZG9uZQplY2hvICJXcm90ZTogJENTViIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtY2fgf/b6yAnpVJaIKz6GkqNTlXfloU0mGss5dJ7e3R6vXURS1E9p4lKFCH+yGA
i6LhWa+rrJM8qg4XigX92b1GMY0RDx0VjMQ7hPt5xgCqhGSCMRj7YVAWyKkgFBPD
PGlLs0WPeOhDfJsIcXAgh1NhSnkZe1CvPSw/otO5RTOIg4Hk/+dk8KfUx7dktMHA
LtLHVSX8hpvxudRoflvdcz7zywqGcuziXweCybDNC7NNMkS/NCalHRMVkyQ/D4ss
dyP/wAarRwEvL8me9aMLxZOiBaIG6UM0AuNzepX4TkISq+wug/v23FaJ/ywljSVZ
r56fJPd3bXNvKnUwuYMoNzeFNubaTQ==
=rIBF
-----END PGP SIGNATURE-----

