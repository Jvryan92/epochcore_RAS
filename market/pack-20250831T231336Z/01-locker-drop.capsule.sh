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
  "session_uuid": "499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1",
  "founder_note": "Founder: John Ryan — 'Sovereign stack, fair-by-design.'",
  "date_utc": "2025-08-31T23:13:36Z",
  "chain_prev": "genesis",
  "manifest_hash": "8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6",
  "provenance": {
    "forge_stamp": "20250831T231336Z",
    "shell": "/bin/bash",
    "signer_hint": "default-gpg-key"
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

iQEzBAABCgAdFiEExbfCYv0tb5XeMPs+PQYNVlSGDtYFAmi01yAACgkQPQYNVlSG
DtbwLwf/el8w5hv6Kz71UcmHmJZnU/V4FIAqU5RnYCVNi2PdKJlYL5towjWdV/lq
ZFcy54fzodkiU1lOBSu80qKO/iqNga7blYzwEtdEmaPhm7vKVonQRDk7rLGWTEE9
9LGgGfivJxSaZUBM/n5wSwf9ErBnJZtiSltmHxUHrBpRpE76ZO/KlylU5hKDbNFA
Yrlga1JPBKWn7K2QJhxIUl5z/rmlk/p+KhnLTx4fIMOG1V44JHJBRLSszanGX9tR
/Sl/IOogiKi2Hehs5oFCkOgcC2giTPjM8VGHpMOl5ceOplOfGGlpqe9AVssBTh+P
XxdkWAiKpDQX6zAaswwBziYARxnZyg==
=2ODZ
-----END PGP SIGNATURE-----

