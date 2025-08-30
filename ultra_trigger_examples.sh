#!/usr/bin/env bash
# Usage examples for the Ultra Trigger Pack Batch Forge script

# Make sure the script is executable
chmod +x ultra_trigger_pack_batch.sh

# Full-send (all 10 triggers)
echo -e "\n\n=== Example 1: Full Send (all 10 triggers) ==="
./ultra_trigger_pack_batch.sh --batch full-send --dry-run

# ROI burst preset (revenue, metrics, pricing, prizes, compounding)
echo -e "\n\n=== Example 2: ROI Burst Preset ==="
./ultra_trigger_pack_batch.sh --batch roi-burst --dry-run

# Governance hardening preset
echo -e "\n\n=== Example 3: Governance Hardening Preset ==="
./ultra_trigger_pack_batch.sh --batch gov-harden --dry-run

# Mesh expansion preset
echo -e "\n\n=== Example 4: Mesh Expansion Preset ==="
./ultra_trigger_pack_batch.sh --batch mesh-expand --dry-run

# Custom multi-pick (by number)
echo -e "\n\n=== Example 5: Custom Multi-Pick ==="
./ultra_trigger_pack_batch.sh --pick "1 3 8 10" --dry-run

# Mathematical analysis of the trigger system
echo -e "\n\n=== Example 6: Mathematical Analysis ==="
python scripts/trigger_system_math_analysis.py --no-viz
