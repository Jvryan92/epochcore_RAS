#!/usr/bin/env bash
set -euo pipefail

cat >test_capsule.json <<'JSON'
{"version":"1.0","capsule_id":"$BASE","trigger":"$TRIG","timestamp":"$TS","provenance":{"founder_note":"$PROV_NOTE","true_north":"locked"},"mesh":{"monetary":["Stripe","MeshCredit","ROI Glyphs"],"governance":["Multisig","PR-vote","Rollback-seal"],"expansion":["MeshSpawn","CivilizationBlock","Compound"]},"actions":["Timestamp","Log","Seal","Archive","Reinject"],"intent":"Forge ultra capsule for ROI + Mesh + Governance"}
JSON
echo "Test capsule written."
