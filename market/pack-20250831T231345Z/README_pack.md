# EPOCH5 Capsule Pack — 20250831T231345Z

**Session UUID:** 381224d5-12dc-4e48-bfc6-8deba6502c75  
**Manifest Hash:** 0c0e556bec13f2918eaf1ef2c2448f5c37a0afe1b64a050405f5b6fbedc0f335  
**Founder Note:** Founder: John Ryan — 'Sovereign stack, fair-by-design.'  
**Forged at (UTC):** 2025-08-31T23:13:45Z

## Files
- `pack_manifest.json` (canonical list)
- `pack_manifest.sha256`
- `*.capsule.sh` (10 self-contained, signed executables)

## Verify
```bash
# verify manifest
sha256sum -c pack_manifest.sha256   # (macOS) shasum -a 256 -c pack_manifest.sha256

# verify one capsule
./01-locker-drop.capsule.sh verify
```

## Run a capsule
```bash
./01-locker-drop.capsule.sh run out/locker
./04-meshcredit-kiosk.capsule.sh run out/meshcredit
```
