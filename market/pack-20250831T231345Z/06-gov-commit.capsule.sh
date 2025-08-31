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
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "e952f3b3f22541034b3228740d30957ddcab9b406aec5117911b00a0d5cfd9b3",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
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

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtZVCwgAvgUhpRMIQuAfgOKhIRQhlJcX
M4xCjbYZuRPp3WfEpmijnGlDhPr0BzT5mX2SZ/1/eg7Viq1tK2F2QthxF89J0N0+
mfzR8hV44JSt4KPDbh60jr0Eggs1iSQH3Dej05nDChoVXPaGwdtT1iCqCpcgLyFJ
aJ7p7pvREunpPtXjAvESOUTMsn+g05Fm8Na+5KKVPVimgwngVAJby4GF5zcdtUxK
9M0R5aFyVewCFqWokScmJ8YF8Lmiea1r3kQ8NsfLcsTeZeM7vkgFxWgdolSB4jzP
CxpsoPNJ3b0Y3nhXdrkS7fDYdgHLRJ83XsUyQkqbmH9Mod2UW773KSdg0sJhrw==
=4O0C
-----END PGP SIGNATURE-----

