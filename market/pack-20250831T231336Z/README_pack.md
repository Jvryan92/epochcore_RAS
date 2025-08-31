# EPOCH5 Capsule Pack — 20250831T231336Z

**Session UUID:** 499fb4d1-b5e0-41bb-9785-d1ba3e5a7bd1  
**Manifest Hash:** 8e7f8b60a9ea57f5a072b539e13d0255eaa0e874124d7b497351f99f2d99bfa6  
**Founder Note:** Founder: John Ryan — 'Sovereign stack, fair-by-design.'  
**Forged at (UTC):** 2025-08-31T23:13:36Z

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
