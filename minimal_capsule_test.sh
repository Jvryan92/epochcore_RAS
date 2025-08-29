#!/usr/bin/env bash
set -euo pipefail

test_func() {
  echo "{" > test_capsule.json
  echo "  \"version\": \"1.0\"," >> test_capsule.json
  echo "  \"capsule_id\": \"test_id\"," >> test_capsule.json
  echo "  \"trigger\": \"test_trigger\"," >> test_capsule.json
  echo "  \"timestamp\": \"2025-08-29T00:00:00Z\"," >> test_capsule.json
  echo "  \"provenance\": {\"founder_note\": \"test_note\", \"true_north\": \"locked\"}," >> test_capsule.json
  echo "  \"mesh\": {" >> test_capsule.json
  echo "    \"monetary\": [\"Stripe\", \"MeshCredit\", \"ROI Glyphs\"]," >> test_capsule.json
  echo "    \"governance\": [\"Multisig\", \"PR-vote\", \"Rollback-seal\"]," >> test_capsule.json
  echo "    \"expansion\": [\"MeshSpawn\", \"CivilizationBlock\", \"Compound\"]" >> test_capsule.json
  echo "  }," >> test_capsule.json
  echo "  \"actions\": [\"Timestamp\", \"Log\", \"Seal\", \"Archive\", \"Reinject\"]," >> test_capsule.json
  echo "  \"intent\": \"Forge ultra capsule for ROI + Mesh + Governance\"" >> test_capsule.json
  echo "}" >> test_capsule.json
  echo "Test capsule written."
}

test_func
