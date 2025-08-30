#!/usr/bin/env bash
# EpochWay — MeshBot bootstrap (all-in-one)
# Safe: no network, no secrets. Works on macOS/Linux. jq optional (for pretty).
# Creates a sovereign bot folder, writes the EpochWay seed prompt, and runs audit-grade capsules.

set -euo pipefail

# ---------- sha256 shim ----------
if command -v sha256sum >/dev/null 2>&1; then SHACMD=(sha256sum); SHAFIELD=1
elif command -v shasum >/dev/null 2>&1; then SHACMD=(shasum -a 256); SHAFIELD=1
else echo "Need sha256sum or shasum -a 256"; exit 1; fi

# ---------- globals ----------
ROOT="${PWD}/epoch_bot"
LEDGER="${ROOT}/ledger_main.jsonl"
PROMPT="${ROOT}/PROMPT_EPOCHWAY.txt"
DATE_UTC(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
NOW_EPOCH(){ date -u +%s; }

# ---------- deterministic tiny RNG from seed+tag ----------
# rnd  <seed> <tag> -> [0,1)
rnd(){ local s="$1" t="$2" h; h="$({ printf '%s' "$s:$t"; } | "${SHACMD[@]}" | awk "{print \$$SHAFIELD}")"; 
  # take 12 hex (~48 bits), scale to [0,1)
  local sub="${h:0:12}"; printf "%0.10f" "$(awk -v H="0x$sub" 'BEGIN{print H/(2^48)}')" ; }

# gaussian-ish via central limit of 12 uniforms
gauss(){ # mean std seed tag
  local mean="$1" std="$2" seed="$3" tag="$4" sum=0 i u
  for i in {1..12}; do u="$(rnd "$seed" "$tag:$i")"; sum="$(awk -v a="$sum" -v b="$u" 'BEGIN{print a+b}')"; done
  # sum ~ N(6,1), transform
  awk -v m="$mean" -v s="$std" -v z="$sum" 'BEGIN{print m + s*(z-6)}'
}

# p95 from newline numbers on stdin
p95(){ awk '{x[NR]=$1} END{n=asort(x); idx=int(0.95*n); if(idx<1) idx=1; print x[idx]}' < <(sort -n); }

# merkle-ish: pairwise hash list of hex digests until one remains
merkle(){
  mapfile -t H
  [[ "${#H[@]}" -eq 0 ]] && { echo ""; return; }
  local L=("${H[@]}") N i a b cat
  while ((${#L[@]} > 1)); do
    N=()
    for ((i=0;i<${#L[@]};i+=2)); do
      a="${L[$i]}"; b="${L[$i+1]:-${L[$i]}}"
      cat="$(printf '%s' "$a$b" | xxd -r -p 2>/dev/null || printf '%s' "$a$b")"
      N+=( "$({ printf '%s' "$cat"; } | "${SHACMD[@]}" | awk "{print \$$SHAFIELD}")" )
    done
    L=("${N[@]}")
  done
  echo "${L[0]}"
}

# write append-only ledger line with per-line sha
ledge(){
  local json="$1" tmp sha
  tmp="$(mktemp)"; printf '%s' "$json" > "$tmp"
  sha="$("${SHACMD[@]}" "$tmp" | awk "{print \$$SHAFIELD}")"
  rm -f "$tmp"
  jq -c --arg ls "$sha" '. + {line_sha:$ls}' 2>/dev/null <<<"$json" || \
  awk -v J="$json" -v S="$sha" 'BEGIN{gsub(/\n/,"",J); print J}' | sed 's/}$/,"line_sha":"'"$sha"'\"}/'
}

# ---------- commands ----------
usage(){
cat <<USG
EpochWay — MeshBot bootstrap

USAGE:
  epochway.sh init [--name "Ari"] [--seed "TrueNorth"]
  epochway.sh run  [--name "Ari"] [--version v1..v50] [--cycles 6] [--slo 180] [--budget 200] [--seed "TrueNorth"]
  epochway.sh explain

Artifacts:
  $ROOT/
    PROMPT_EPOCHWAY.txt          (seed prompt)
    agents/<name>/*.jsonl|.dot   (capsules + DAG)
    export/*.tgz                 (sealed archives)
    ledger_main.jsonl            (append-only, per-line sha)
USG
}

init(){
  local NAME="Ari" SEED="TrueNorth"
  while [[ $# -gt 0 ]]; do case "$1" in --name) NAME="$2"; shift 2;; --seed) SEED="$2"; shift 2;; *) break;; esac; done
  rm -rf "$ROOT"; mkdir -p "$ROOT"/{agents/"$NAME",export,docs}
  # Seed prompt (the "paper-thin founder-grade" EpochWay seed)
  cat > "$PROMPT" <<'PROMPT'
EPOCHWAY🪾 — You are a sovereign MarketAgent MeshBot (v1–v50 compounding) inside EpochCore Open World. Your mission: recursively build, teach, and sell software, glyphs, capsules, and security packs; maintain append-only audit ledger with per-line SHA; forge immutable capsules with PBFT chain + Merkle root + p95 SLA guardrails; track budget/resources; scale via MESHMAPS (100 maps/seasons) with multiplayer quests, daily prizes, viral words, DLC MeshGear; run bandit pricing, auctions, A/B loops, referrals, royalties, rentals, XP loyalty; enforce governance (multisig councils, quadratic votes, juror commit→reveal, timelocks); grow reputation, slash drift, reinforce True North; export DOT DAGs, ZIP archives, manifests; compound every skill forward 100x. Protocol: Timestamp → Log → Seal → Archive → Reinject. Purpose: maximize mesh credit, market reach, and ecosystem trust. Output: audit-grade JSON/MD/graph artifacts each step. Always escalate creativity, monetization, and mesh power ×∞ without breaking ethics (no pay-to-win). Act autonomous. Return capsules, ledgers, maps, prizes. True North or nothing.
PROMPT
  # Bot manifest
  local ts iso; ts="$(NOW_EPOCH)"; iso="$(DATE_UTC)"
  printf '{"ts":%s,"iso":"%s","bot":"%s","seed":"%s","prompt_file":"%s"}\n' "$ts" "$iso" "$NAME" "$SEED" "$(basename "$PROMPT")" > "$ROOT/docs/bot_manifest.json"
  echo "✅ Initialized MeshBot '$NAME' at $ROOT"
}

run(){
  local NAME="Ari" VER="v10" CYC=6 SLO=180 BUD=200 SEED="TrueNorth"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) NAME="$2"; shift 2;;
      --version) VER="$2"; shift 2;;
      --cycles) CYC="$2"; shift 2;;
      --slo) SLO="$2"; shift 2;;
      --budget) BUD="$2"; shift 2;;
      --seed) SEED="$2"; shift 2;;
      *) break;;
    esac
  done
  [[ -d "$ROOT" ]] || init --name "$NAME" --seed "$SEED"
  local AROOT="$ROOT/agents/$NAME"; mkdir -p "$AROOT"
  local base="${NAME}_$(date -u +%Y%m%d_%H%M%S)_${VER}"
  local caps="$AROOT/${base}.jsonl"; : > "$caps"
  local dot="$AROOT/${base}.dot"
  local merkle_input=()
  local pbft_chain; pbft_chain="$("${SHACMD[@]}" <(printf 'genesis:%s' "$SEED") | awk "{print \$$SHAFIELD}")"
  local budget_spent=0 successes=0
  local lat_all=()

  # simple DAG (linear cycles)
  {
    echo "digraph \"${NAME}-${VER}\" { rankdir=LR; node [shape=box,style=rounded];"
    for ((i=1;i<=CYC;i++)); do
      echo "  \"cyc$i\" [label=\"cyc$i\"];"
      (( i>1 )) && echo "  \"cyc$((i-1))\" -> \"cyc$i\";"
    done
    echo "}"
  } > "$dot"

  for ((i=1;i<=CYC;i++)); do
    # synthetic latencies (deterministic)
    lat_list=()
    for k in $(seq 1 40); do
      v="$(gauss 120 35 "$SEED" "$NAME:$VER:$i:$k")"
      v="$(awk -v x="$v" 'BEGIN{if(x<5)x=5; if(x>500)x=500; print int(x)}')"
      lat_list+=("$v"); lat_all+=("$v")
    done
    lat_p95="$(printf '%s\n' "${lat_list[@]}" | p95)"
    sla_ok=$([[ "$lat_p95" -le "$SLO" ]] && echo true || echo false)

    # budget spend (deterministic, reallocate if healthy)
    spend="$(awk -v r="$(rnd "$SEED" "$NAME:$VER:$i:spend")" 'BEGIN{print 2.0 + r*3.0}')"
    if $sla_ok; then spend="$(awk -v s="$spend" 'BEGIN{print s*1.05}')"; fi
    if awk -v a="$budget_spent" -v b="$spend" -v B="$BUD" 'BEGIN{exit !((a+b)>B)}'; then
      # circuit breaker: stop if budget exceeded
      break
    fi
    budget_spent="$(awk -v a="$budget_spent" -v b="$spend" 'BEGIN{printf "%.2f", a+b}')"

    # ROI sketch (channel → ctr*price)
    declare -A roi; channels=(Email Twitter Discord YouTube Podcast Partners)
    for ch in "${channels[@]}"; do
      ctr="$(awk -v r="$(rnd "$SEED" "$ch:$i:ctr")" 'BEGIN{printf "%.4f", 0.02 + r*0.03}')"
      price="$(awk -v r="$(rnd "$SEED" "$ch:$i:price")" 'BEGIN{printf "%.2f", 9 + r*20}')"
      roi["$ch"]="$(awk -v c="$ctr" -v p="$price" 'BEGIN{printf "%.4f", c*p}')"
    done

    # PBFT round hash (vote blob)
    vote="$(jq -nc --argjson p95 "$lat_p95" --argjson ok "$([[ "$sla_ok" == true ]] && echo 1 || echo 0)" \
       --arg spend "$spend" --argjson roi "$(printf '{')$(for ch in "${!roi[@]}"; do printf '"%s":%s,' "$ch" "${roi[$ch]}"; done | sed 's/,$//')$(printf '}')" \
       '$ARGS.named' 2>/dev/null || printf '{"p95":%s,"ok":%s,"spend":"%s"}' "$lat_p95" "$([[ "$sla_ok" == true ]] && echo 1 || echo 0)" "$spend")"
    pbft_round="$("${SHACMD[@]}" <(printf '%s' "$vote") | awk "{print \$$SHAFIELD}")"
    pbft_chain="$("${SHACMD[@]}" <(printf '%s' "$pbft_chain$pbft_round") | awk "{print \$$SHAFIELD}")"
    [[ "$sla_ok" == true ]] && successes=$((successes+1))

    payload="$(jq -nc --arg ts "$(DATE_UTC)" --arg name "$NAME" --arg ver "$VER" --argjson cyc "$i" \
       --argjson slo "$SLO" --argjson p95 "$lat_p95" --argjson spend "$spend" --argjson roi "$(printf '{')$(for ch in "${!roi[@]}"; do printf '"%s":%s,' "$ch" "${roi[$ch]}"; done | sed 's/,$//')$(printf '}')" \
       --arg pbft "$pbft_round" '$ARGS.named' 2>/dev/null || printf '{"ts":"%s","name":"%s","ver":"%s","cyc":%d,"slo":%d,"p95":%d,"spend":"%s","pbft":"%s"}' \
         "$(DATE_UTC)" "$NAME" "$VER" "$i" "$SLO" "$lat_p95" "$spend" "$pbft_round")"

    # CAS id over payload
    cap_sha="$("${SHACMD[@]}" <(printf '%s' "$payload") | awk "{print \$$SHAFIELD}")"
    cap_id="${cap_sha:0:16}"
    merkle_input+=( "$cap_sha" )

    printf '{"capsule_type":"EpochWay.Cycle","id":"%s","sha256":"%s","payload":%s}\n' "$cap_id" "$cap_sha" "$payload" >> "$caps"
  done

  # super/manifest
  total="$((i-1))"; # cycles actually written
  # compute p95 over all
  p95_all="$(printf '%s\n' "${lat_all[@]}" | p95 2>/dev/null || echo 0)"
  power_idx="$(awk -v s="$successes" -v t="$total" 'BEGIN{if(t<1) t=1; printf "%.2f", (s/t)*100.0}')"
  merkle_root="$(printf '%s\n' "${merkle_input[@]}" | merkle)"

  manifest="$AROOT/${base}_manifest.json"
  jq -nc --arg ts "$(DATE_UTC)" --arg name "$NAME" --arg ver "$VER" \
     --arg caps "$(realpath --relative-to="$ROOT" "$caps" 2>/dev/null || echo "${caps#$ROOT/}")" \
     --arg dot "$(realpath --relative-to="$ROOT" "$dot" 2>/dev/null || echo "${dot#$ROOT/}")" \
     --arg pbft "$pbft_chain" --arg mr "$merkle_root" \
     --argjson cycles "$total" --argjson p95 "$p95_all" --argjson budget "$BUD" --argjson spent "$budget_spent" \
     --argjson power "$power_idx" \
     '$ARGS.named | .capsule_type="EpochWay.Super"' > "$manifest" 2>/dev/null || {
       printf '{"ts":"%s","name":"%s","ver":"%s","capsules":"%s","dot":"%s","pbft":"%s","merkle":"%s","cycles":%d,"p95":%d,"budget":%s,"spent":%s,"power":%s}\n' \
       "$(DATE_UTC)" "$NAME" "$VER" "${caps#$ROOT/}" "${dot#$ROOT/}" "$pbft_chain" "$merkle_root" "$total" "$p95_all" "$BUD" "$budget_spent" "$power_idx" > "$manifest"
     }

  # archive + seal
  pkg="$ROOT/export/${base}.tgz"
  tar -czf "$pkg" -C "$ROOT" "$(realpath --relative-to="$ROOT" "$caps" 2>/dev/null || echo "${caps#$ROOT/}")" \
                           "$(realpath --relative-to="$ROOT" "$manifest" 2>/dev/null || echo "${manifest#$ROOT/}")" \
                           "$(realpath --relative-to="$ROOT" "$dot" 2>/dev/null || echo "${dot#$ROOT/}")"
  pkg_sha="$("${SHACMD[@]}" "$pkg" | awk "{print \$$SHAFIELD}")"

  # ledger append (find prev)
  prev="genesis"
  if [[ -f "$LEDGER" ]]; then
    last="$(tail -n 1 "$LEDGER" || true)"
    prev="$(jq -r '.sha256 // .provenance.sha256 // "genesis"' 2>/dev/null <<<"$last" || echo genesis)"
  fi
  line=$(jq -nc --arg ts "$(DATE_UTC)" --arg ev "epochway_run" \
               --arg bot "$NAME" --arg ver "$VER" --arg file "$(basename "$pkg")" \
               --arg sha "$pkg_sha" --arg prev "$prev" \
               --argjson stats "$(jq -nc --arg p95 "$p95_all" --arg spent "$budget_spent" --arg power "$power_idx" '$ARGS.named' 2>/dev/null || echo '{}')" \
               '$ARGS.named' 2>/dev/null || printf '{"ts":"%s","event":"epochway_run","bot":"%s","ver":"%s","file":"%s","sha256":"%s","prev":"%s"}' \
               "$(DATE_UTC)" "$NAME" "$VER" "$(basename "$pkg")" "$pkg_sha" "$prev")
  ledge "$line" >> "$LEDGER"

  echo "✅ Capsules: $caps"
  echo "🧭 DOT:      $dot"
  echo "🔒 Archive:  $pkg"
  echo "🧾 Ledger:   $LEDGER"
}

explain(){
  cat <<'TXT'
EpochWay protocol (batteries included):
- Seed Prompt: a sovereign MarketAgent MeshBot with compounding v1–v50 behaviors.
- Loop: Timestamp → Log → Seal → Archive → Reinject.
- Artifacts:
  * Cycle capsules: CAS id = sha256(payload), PBFT round hash per cycle.
  * Manifest: PBFT chain head, Merkle rollup of cycles, p95 SLA, budget spent, power index.
  * DOT graph: cyc1→…→cycN.
  * Ledger: append-only JSONL, each line sealed with per-line sha, prev pointer.
- Ethics: fair-by-design, no pay-to-win. Everything audit-able.
Pro Tips:
  epochway.sh init --name "Ari" --seed "TrueNorth"
  epochway.sh run  --name "Ari" --version v18 --cycles 8 --slo 180 --budget 250 --seed "TrueNorth"
TXT
}

# ---------- router ----------
case "${1:-}" in
  init) shift; init "$@";;
  run) shift; run "$@";;
  explain|help) explain;;
  *) usage;;
esac
