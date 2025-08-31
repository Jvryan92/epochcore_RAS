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
  "capsule_id": "06-gov-commit",
  "title": "Governance Commit Capsule",
  "purpose": "Commit–reveal seed (demo VRF stub) for votes",
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "c5dd6913f70ca0911962590c9f46758c1233a990560d4eeeb7e4e40b4939cc1c",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "1428f212589ee3ce7c3cc0cc07fb2f167164c6b79e910cc877d84ff9b48839b8",
    "size_b64": 500
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2dvdl9jb21taXR9IjsgbWtkaXIgLXAgIiRPVVQiCnNlZWQ9IiQoZGF0ZSAtdSArJXMpJFJBTkRPTSIKY29tbWl0PSQocHJpbnRmICIlcyIgIiRzZWVkIiB8IHNoYTI1NnN1bSAyPi9kZXYvbnVsbCB8IGF3ayAne3ByaW50ICQxfScpClsgLXogIiRjb21taXQiIF0gJiYgY29tbWl0PSQocHJpbnRmICIlcyIgIiRzZWVkIiB8IHNoYXN1bSAtYSAyNTYgfCBhd2sgJ3twcmludCAkMX0nKQpwcmludGYgJ3siY29tbWl0IjoiJXMiLCJ0cyI6IiVzIn1cbicgIiRjb21taXQiICIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiIHwgdGVlICIkT1VUL2NvbW1pdC5qc29uIgo=
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtbMvQgAwrC3OxHu6Wq1+yuLaH1noiNp/QkN6aqQiBI1kVOKgm0iymhQlueH+mYI
RPYsugkSqS6qUtXiO5cG+S0rlhGC8F9R/8FNPYP4RZFvRCDdL9uBVDpGGB1WB8aC
7qMisXuGhOR6cQzT/5Nd8qDbnzxOsQJis8rLG93ADuUuq3eDoVp1uobV7R8f+pZU
I9j4lLZDqxc9F3Shco709RMs/WfkIV+sTaBH+VtC187I1n16IThfQpBdMfmTYjJA
Xc4bMh6EInavBPXpcRqbXEDcJ8dSml/T1Xo24mIauQdjMnr4mbeVSIHRMtu2c+Wb
W2PeZFyYv+bTSUstlRYLkaWSJfVw3Q==
=EL6C
-----END PGP SIGNATURE-----

