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
  "capsule_id": "01-locker-drop",
  "title": "LockerCode Dropper",
  "purpose": "Generate redeem codes & CSV/JSON (offline, rate-limit friendly)",
  "session_uuid": "381224d5-12dc-4e48-bfc6-8deba6502c75",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:45Z",
  "chain_prev": "genesis",
  "manifest_hash": "0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335",
  "provenance": {
    "forge_stamp": "20250831T231345Z",
    "shell": "/bin/bash",
    "signer_hint": "epoch-test@example.com"
  },
  "payload": {
    "encoding": "base64",
    "entry": "bash",
    "sha256": "5fdf3a784f430f77c488fd283a64ad502716ed1a9291ed401f80b3c3cc571807",
    "size_b64": 624
  }
}
<<PAYLOAD>>
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApPVVQ9IiR7MTotb3V0L2xvY2tlcl9kcm9wfSI7IENPVU5UPSIke0NPVU5UOi0xMDAwfSI7IFBSRUZJWD0iJHtQUkVGSVg6LUVQT0NIfSIKbWtkaXIgLXAgIiRPVVQiCkNTVj0iJE9VVC9jb2Rlcy5jc3YiOyBKU09OPSIkT1VUL2NvZGVzLmpzb25sIgo6ID4gIiRDU1YiOyA6ID4gIiRKU09OIgplY2hvICJjb2RlLGlzc3VlZF9hdCIgPj4gIiRDU1YiCmZvciBpIGluICQoc2VxIDEgIiRDT1VOVCIpOyBkbwogIGM9IiRQUkVGSVgtJChkYXRlIC11ICsleSVtJWQpLSRSQU5ET00kUkFORE9NIgogIHRzPSIkKGRhdGUgLXUgKyVZLSVtLSVkVCVIOiVNOiVTWikiCiAgZWNobyAiJGMsJHRzIiA+PiAiJENTViIKICBwcmludGYgJ3siY29kZSI6IiVzIiwidHMiOiIlcyJ9XG4nICIkYyIgIiR0cyIgPj4gIiRKU09OIgpkb25lCmVjaG8gIldyb3RlOiAkQ1NWICAkSlNPTiIK
</CAPSULE>
-----BEGIN PGP SIGNATURE-----

iQFLBAABCgA1FiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01ykXHGVwb2NoLXRl
c3RAZXhhbXBsZS5jb20ACgkQPQYNVlSGDtbTdAgAjMZSH17zxaWKAe5wbMp7X2Mn
lkTC6GrX1ZOQA3B11C5unxjSj1s9tOiQW/h9Cff1WDY0vx+NrbF0myy3aa/Tcsw3
HAUMlGKkpgTqoO5Ns/6S6wQlpT72bTs+EAwYWT5P5Is79gVMdCgmrkpJpOo9qXXK
Oz4CkSOBWsx+qM/MAZy8WDHYD2Px1nALG105MRRr5a5x8o8cEqYWQSsvgpxgtNVf
FnQl3tPursY6zmSSVlHU35sk+K1dRnx9kTEbaCMOWnnEtneFzegkcNvosu8rxM5w
NQAFqwfN2Rh9WT2iPHxaFX80L3doEYKG9IN9hWPsKBpjgLekgWMLrTO44mFfNQ==
=i1nx
-----END PGP SIGNATURE-----

