#!/usr/bin/env bash
# epoch_game_pack.sh — rebuild EVERYTHING from this thread that relates to the video game,
# then compress it into a single tarball + SHA-256. (macOS/Linux compatible)
set -euo pipefail

PKG="${1:-Epoch_Game_Pack.tgz}"
ROOT="${PWD}/epoch_game_pack"
DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- deps ---
command -v jq >/dev/null 2>&1 || { echo "jq is required"; exit 1; }
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum); elif command -v shasum >/dev/null 2>&1; then SHACMD=(shasum -a 256); else echo "need sha256 tool"; exit 1; fi

# --- dirs ---
rm -rf "$ROOT"
mkdir -p "$ROOT"/{docs,design,governance,build,assets/store_kit,checklists,export}

# ===============================
# 1) DESIGN (Mermaid blueprints)
# ===============================
# A) Core playable loop: 90–180s loop, 12–20m mastery, 30–60d arc (from thread)
cat >"$ROOT/design/game_loop.mmd"<<'EOF'
%% Core Playable Loop (EpochCore MMO concept)
flowchart LR
  Spawn((Spawn)) --> Onboard[Onboard: 0→fun <120s]
  Onboard --> Loop1{Core Loop 90–180s}
  Loop1 --> SkillUp[Mastery 12–20m]
  SkillUp --> Progress[Long Arc 30–60d]
  Progress --> Social[Social: squads, assists, ghosts/playlists]
  Social --> Governance[Governance Arena: seasonal]
  Governance --> Reward[Cosmetics, proof-of-play]
  Reward --> Loop1
  %% Ethics: no pay-to-win, cosmetics/time-savers only
EOF

# B) Economy & fairness rules (no P2W, cosmetics/time-savers only)
cat >"$ROOT/design/economy_ethics.mmd"<<'EOF'
%% Economy / Ethics (Fair-by-Design)
flowchart TD
  Money[Monetization] --> Cosmetics[Cosmetics only]
  Money --> TimeSav[Time-savers only]
  Money -.X.-> P2W[Pay-to-Win]:::no
  Proof[Proof-of-Play] --> Cosmetics
  classDef no fill:#fee,stroke:#c33,stroke-width:2px
EOF

# C) Distribution & release ritual (Timestamp → Log → Seal → Archive → Reinject)
cat >"$ROOT/design/release_ritual.mmd"<<'EOF'
%% Release Ritual
sequenceDiagram
  participant Build
  participant Ledger
  participant Archive
  participant Live

  Build->>Ledger: Timestamp
  Ledger-->>Ledger: Log (jsonl + per-line sha)
  Ledger-->>Ledger: Seal (sha256 of capsule)
  Ledger->>Archive: Archive (tgz + sha)
  Archive->>Live: Reinject (publish Crown ref)
EOF

# ======================================
# 2) GOVERNANCE ARENA (seasonal, rollback)
# ======================================
cat >"$ROOT/governance/arena_season.mmd"<<'EOF'
%% Governance Arena — Seasonal Vote with Rollback
flowchart LR
  Proposals[Season Proposals] --> Vote[Weighted Vote (anti-sybil)]
  Vote --> Seal[Seal: result capsule + hash]
  Seal --> Deploy[Season Deploy]
  Deploy --> Monitor[Drift Monitors]
  Monitor -->|Detected| Rollback[One-click Rollback (sealed prev)]
EOF

cat >"$ROOT/governance/arena_protocol.md"<<EOF
# Governance Arena (Seasonal)
- **Anti-sybil**: require on-chain/ledger proofs or invite tiers.
- **Vote Window**: 72h; quorum threshold; tie → founder veto with ledger note.
- **Rollback**: each deploy references prior sealed capsule; revert is a pointer swap.
- **Rewards**: cosmetics only, no power creep; award proof-of-participation.
- **Observability**: drift detectors on economy/optics; red flags auto-seal an exception capsule.
Generated: $DATE_UTC
EOF

# ===============================
# 3) CHECKLISTS (from the thread)
# ===============================
# Game visuals & ship-readiness (exact items referenced)
cat >"$ROOT/checklists/visuals_ship_readiness.md"<<'EOF'
# Visuals & Ship-Readiness
- [ ] Art bible v1 (palette, lighting, materials)
- [ ] Accessibility: colorblind pass; UI font ≥12pt; motion-reduce option
- [ ] Performance budgets: mobile 30/60fps, drawcalls/scene cap, texture atlas
- [ ] VFX safety: photo-sensitive flashes ≤3/s, brightness clamp
- [ ] LODs + impostors; shader variants trimmed
- [ ] Screenshot & trailer kit (store-compliant)
- [ ] Monetization visuals cosmetic-only; odds visible; pity timers
- [ ] Build smoke test matrix (iOS/Android/PC, min/rec HW)
- [ ] Save/restore + crash recovery
- [ ] Final RC checklist signed (design/eng/qa/legal/ops)
EOF

# Boxes to check before push (from thread)
cat >"$ROOT/checklists/todo_boxes.md"<<'EOF'
# Boxes to check before push
- [ ] Core loop fun (90–180s), mid-session mastery (12–20m), long-arc (30–60d)
- [ ] New player 0→fun <120s; curated "Try Build"
- [ ] Fair-by-design (no P2W), cosmetics/time-savers only
- [ ] Social: squads, assist credit, ghosts/playlists
- [ ] Governance Arena seasonal vote (with rollback)
EOF

# Performance budgets (expanded)
cat >"$ROOT/checklists/performance_budgets.md"<<'EOF'
# Performance Budgets
- Target FPS: 60 (mobile high), 30 (mobile min), 60/120 (PC)
- Draw calls/scene cap: __ ; Triangles/scene cap: __ ; Overdraw heatmaps
- Texture atlas plan; streaming budgets (VRAM/IO)
- LOD policy per asset class; impostors for distant sets
- Shader variant trimming; platform feature flags
EOF

# Accessibility specifics (expanded)
cat >"$ROOT/checklists/accessibility.md"<<'EOF'
# Accessibility
- Colorblind-safe palettes and filters
- UI font size scalable (base ≥12pt), readable fonts
- Motion reduction (reduced camera shake/blur)
- Subtitles/captions; high contrast mode
- Remappable controls; hold vs toggle options
EOF

# VFX safety (expanded)
cat >"$ROOT/checklists/vfx_safety.md"<<'EOF'
# VFX Safety
- Flash frequency ≤3 per second
- Brightness clamps for flashes/explosions
- Photosensitivity review on each major build
- Avoid full-screen strobing effects
EOF

# Save/restore + crash recovery notes
cat >"$ROOT/checklists/save_recovery.md"<<'EOF'
# Save/Restore + Crash Recovery
- Atomic save writes; checksum each slot
- Safe fallback on corrupted slot (last-known-good)
- Cloud sync conflict resolution
- Session autosave cadence; crash telemetry + hash of build
EOF

# =======================================
# 4) STORE KIT (screens, copy, compliance)
# =======================================
cat >"$ROOT/assets/store_kit/metadata_template.md"<<'EOF'
# Store Metadata Template
**Title:** EpochCore MMO (Working Title)
**Short Description:** A fair-by-design systems game where your proof-of-play becomes your story.
**Long Description:**
- No pay-to-win. Cosmetics/time-savers only.
- Squad up, assist, govern seasons. Rollback-safe.
- Ledger-sealed updates: Timestamp → Log → Seal → Archive → Reinject.

**Keywords:** strategy, systems, fair-by-design, governance
**Age Rating:** __
**Platforms:** iOS, Android, PC
**Privacy Policy URL:** __
**Support URL:** __
EOF

cat >"$ROOT/assets/store_kit/screenshot_checklist.md"<<'EOF'
# Screenshot & Trailer Kit Checklist
- Aspect ratios prepared (mobile portrait/landscape, PC 16:9)
- Show core loop in first 3s of trailer
- Accessibility and fairness cues visible
- Governance Arena glimpse; cosmetics store (no P2W)
- Include build hash in trailer end card
EOF

# =====================================
# 5) BUILD MATRIX + COMPLIANCE RECORDS
# =====================================
cat >"$ROOT/build/build_matrix.csv"<<'EOF'
platform,device/os,min_spec,rec_spec,notes
iOS,iPhone 11,iOS 15,iOS 17,"30/60 fps targets"
Android,Pixel 5,Android 12,Android 14,"30/60 fps targets"
PC,GTX 1060,Win 10,Win 11 + RTX 3060,"60/120 fps tiers"
EOF

# =====================================
# 6) THREAD-TO-GAME TRACE (provenance)
# =====================================
cat >"$ROOT/docs/thread_trace.md"<<EOF
# Thread → Game Trace
- **Core loop & ladders**: "Game Blueprint → Playable Loop → EpochCore MMO" (compounding stacks; #100 = MMO)
- **Governance Arena**: seasonal vote with rollback
- **Fair-by-design**: no P2W; cosmetics/time-savers only
- **Ship readiness**: visuals checklist, performance budgets, VFX safety, accessibility
- **Release ritual**: Timestamp → Log → Seal → Archive → Reinject
Generated: $DATE_UTC
EOF

# =====================================
# 7) HASH MANIFEST (for every file)
# =====================================
MANIFEST="$ROOT/export/hashes.sha256"
: > "$MANIFEST"
while IFS= read -r -d '' f; do
  # print hash and relative path
  rel="${f#$ROOT/}"
  "${SHACMD[@]}" "$f" | awk -v p="$rel" '{print $1"  "p}' >> "$MANIFEST"
done < <(find "$ROOT" -type f -print0 | sort -z)

# =====================================
# 8) TAR + HASH
# =====================================
tar -czf "$PKG" -C "$ROOT" .
PKG_SHA=$("${SHACMD[@]}" "$PKG" | awk '{print $1}')

# =====================================
# 9) README (quick use)
# =====================================
cat >"$ROOT/README.txt"<<EOF
Epoch Game Pack — compressed artifacts from the thread
Generated: $DATE_UTC

Contents:
- design/          (Mermaid blueprints: core loop, economy ethics, release ritual)
- governance/      (Arena season flow + protocol)
- checklists/      (visuals_ship_readiness, todo_boxes, performance, accessibility, vfx, save_recovery)
- assets/store_kit (metadata + screenshot/trailer checklist)
- build/           (build_matrix.csv)
- docs/            (thread_trace.md)
- export/          (hashes.sha256)

Usage:
- Render Mermaid files with any Mermaid viewer.
- Use checklists to ship RC builds; tie releases to your ledger ritual.
- Verify integrity:  shasum -a 256 -c export/hashes.sha256  (macOS)
                     sha256sum -c export/hashes.sha256       (Linux)

Tarball:
- $PKG
- SHA-256: $PKG_SHA
EOF

# print final pointers
echo "✅ Wrote: $PKG"
echo "SHA-256: $PKG_SHA"
echo "Pack root: $ROOT"
