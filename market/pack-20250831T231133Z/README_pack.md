# EPOCH5 Capsule Pack — 20250831T231133Z

**Session UUID:** 802a738e-53b9-4f73-947c-65f4ac1bcb94  
**Manifest Hash:** d2c7bffc698e97407e1c081799277f7d25b66c6945aec854373a88d4a0d78e1a  
**Founder Note:** Founder: John Ryan — 'Sovereign stack, fair-by-design.'  
**Forged at (UTC):** 2025-08-31T23:11:33Z

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
