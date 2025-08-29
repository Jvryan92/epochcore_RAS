# =========================================
# File: agents/run_agent.sh
# Standard entrypoint each agent must implement against.
# Usage: AGENT_ID=lint ./agents/run_agent.sh --task "do X" --depth 1 --parent <run_id>
# Contract: print JSON result to stdout; return nonzero on failure.
# =========================================
#!/usr/bin/env bash
set -euo pipefail

AGENT_ID="${AGENT_ID:-default}"
TASK="${1:-}"; shift || true
# Parse flags
DEPTH=0
PARENT_RUN=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) TASK="$2"; shift 2 ;;
    --depth) DEPTH="$2"; shift 2 ;;
    --parent) PARENT_RUN="$2"; shift 2 ;;
    *) echo "unknown flag $1" >&2; exit 2;;
  esac
done

start_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

# Example routing by agent id. Replace stubs with real commands.
case "$AGENT_ID" in
  lint)
    out="$workdir/report.txt"
    echo "Running ruff/flake8 shell stub" > "$out"
    ;;
  tests)
    out="$workdir/pytest.txt"
    echo "Running pytest shell stub" > "$out"
    ;;
  security)
    out="$workdir/sec.txt"
    echo "Running bandit/gitleaks shell stub" > "$out"
    ;;
  docs)
    out="$workdir/docs.txt"
    echo "Building docs shell stub" > "$out"
    ;;
  *)
    out="$workdir/echo.txt"
    echo "Agent $AGENT_ID echo task: ${TASK:-none}" > "$out"
    ;;
esac

# Hash artifact for sealing
if command -v sha256sum >/dev/null 2>&1; then H=$(sha256sum "$out" | awk '{print $1}'); else H=$(shasum -a 256 "$out" | awk '{print $1}'); fi

jq -n --arg agent "$AGENT_ID" \
      --arg task "${TASK:-}" \
      --arg depth "$DEPTH" \
      --arg parent "$PARENT_RUN" \
      --arg started "$start_ts" \
      --arg finished "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      --arg artifact "$out" \
      --arg sha256 "$H" \
      '{agent:$agent, task:$task, depth:($depth|tonumber), parent:$parent, started:$started, finished:$finished, artifact:$artifact, sha256:$sha256, status:"ok"}'

# Save artifact path for caller
echo "$out" > "$workdir/.artifact_path"
// =========================================
// File: agents/manifest.json
// Declarative registry of swarmable agents
// =========================================
{
  "version": "1.0",
  "defaults": { "timeoutMinutes": 15, "retries": 1 },
  "agents": [
    { "id": "lint",     "desc": "Code style & static checks" },
    { "id": "tests",    "desc": "Run pytest suite" },
    { "id": "security", "desc": "Bandit + secrets scan" },
    { "id": "docs",     "desc": "Docs build/links # =========================================
# File: agents/policies/guardrails.yml
# Recursion & safety limits for the swarm
# =========================================
max_depth: 3            # hard stop for recursive fanout
max_fanout: 6           # max parallel children per node
rate_limit_per_min: 20  # API/task launches per minute (soft)
allow_network: false    # agents must not make external calls unless a job grants it
artifact_kb_limit: 5120 # single artifact size cap (~5MB)
red_flags:
  - "export GITHUB_TOKEN=.*"
  - "aws_secret_access_key"
  - "BEGIN PRIVATE KEY"

# =========================================
# File: scripts/agent_seal.sh
# Append a seal line to ledger/agent_swarm.jsonl (append-only)
# =========================================
#!/usr/bin/env bash
set -euo pipefail
LEDGER="${1:-ledger/agent_swarm.jsonl}"
shift || true
mkdir -p "$(dirname "$LEDGER")"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
payload="$(jq -c --arg ts "$ts" '.ts=$ts' <(cat))"
echo "$payload" >> "$LEDGER"
echo "$payload"
# =========================================
# File: .github/workflows/agent-swarm.yml
# Swarm runner: parallel agents, recursive re-entry, sealing, throttles.
# Triggers: push, PR, nightly, manual, and recursive dispatch.
# =========================================
name: Agent Swarm

on:
  push:
    branches: [ main ]
  pull_request:
  schedule:
    - cron: "17 3 * * *"   # nightly heartbeat
  workflow_dispatch:
    inputs:
      depth: { description: "Recursion depth", required: false, default: "0" }
      parent_run: { description: "Parent run id", required: false, default: "" }
      task: { description: "Optional task for generic agents", required: false, default: "" }

permissions:
  contents: read
  actions: write
  id-token: write

concurrency:
  group: swarm-${{ github.ref }}-${{ github.workflow }}-${{ github.event.inputs.parent_run || github.run_id }}
  cancel-in-progress: false

env:
  MAX_DEPTH: 3
  MAX_FANOUT: 6
  POLICIES: agents/policies/guardrails.yml

jobs:
  matrix-plan:
    runs-on: ubuntu-latest
    outputs:
      plan: ${{ steps.plan.outputs.plan }}
      depth: ${{ steps.depth.outputs.depth }}
    steps:
      - uses: actions/checkout@v4
      - id: depth
        run: |
          D="${{ github.event.inputs.depth || '0' }}"
          echo "depth=$D" >> "$GITHUB_OUTPUT"
      - id: plan
        run: |
          jq -c '.agents' agents/manifest.json | tee plan.json
          echo "plan=$(cat plan.json)" >> "$GITHUB_OUTPUT"

  run-agents:
    needs: matrix-plan
    if: ${{ fromJSON(needs.matrix-plan.outputs.depth) < env.MAX_DEPTH }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      max-parallel: ${{ env.MAX_FANOUT }}
      matrix:
        agent: ${{ fromJson(needs.matrix-plan.outputs.plan) }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup tools
        run: |
          sudo apt-get update -y
          sudo apt-get install -y jq
          chmod +x agents/run_agent.sh scripts/agent_seal.sh

      - name: Execute ${{ matrix.agent.id }}
        id: exec
        env:
          AGENT_ID: ${{ matrix.agent.id }}
        run: |
          set -euo pipefail
          json="$(AGENT_ID="${AGENT_ID}" ./agents/run_agent.sh --task "${{ github.event.inputs.task || '' }}" --depth "${{ needs.matrix-plan.outputs.depth }}" --parent "${{ github.event.inputs.parent_run || '' }}")"
          echo "$json" > result.json
          echo "out=$(jq -r .artifact result.json)" >> "$GITHUB_OUTPUT"
          echo "sha=$(jq -r .sha256 result.json)" >> "$GITHUB_OUTPUT"
          echo "json=$(cat result.json | jq -c .)" >> "$GITHUB_OUTPUT"

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: agent-${{ matrix.agent.id }}-artifact
          path: ${{ steps.exec.outputs.out }}
          if-no-files-found: error
          retention-days: 7

      - name: Seal to ledger (artifact-level)
        run: |
          echo '${{ steps.exec.outputs.json }}' | ./scripts/agent_seal.sh >> /tmp/ledger_lines.jsonl
      - name: Upload ledger fragment
        uses: actions/upload-artifact@v4
        with:
          name: ledger-fragment-${{ matrix.agent.id }}
          path: /tmp/ledger_lines.jsonl
          retention-days: 7

  fold-ledger:
    needs: [run-agents]
    runs-on: ubuntu-latest
    if: ${{ always() }}
    steps:
      - uses: actions/checkout@v4
      - name: Gather fragments
        uses: actions/download-artifact@v4
        with:
          path: _frags
      - name: Fold
        run: |
          mkdir -p ledger
          touch ledger/agent_swarm.jsonl
          find _frags -name 'ledger_lines.jsonl' -exec cat {} \; >> ledger/agent_swarm.jsonl
      - name: Upload consolidated ledger
        uses: actions/upload-artifact@v4
        with:
          name: agent-ledger-consolidated
          path: ledger/agent_swarm.jsonl
          retention-days: 30

  recurse:
    needs: [run-agents, fold-ledger]
    runs-on: ubuntu-latest
    if: ${{ needs.matrix-plan.outputs.depth && fromJSON(needs.matrix-plan.outputs.depth) + 1 < env.MAX_DEPTH }}
    steps:
      - name: Trigger next depth
        uses: actions/github-script@v7
        with:
          script: |
            const depth = Number('${{ needs.matrix-plan.outputs.depth }}') + 1;
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'agent-swarm.yml',
              ref: context.ref.replace('refs/heads/',''),
              inputs: {
                depth: String(depth),
                parent_run: String(context.runId),
                task: ''
              }
            });

