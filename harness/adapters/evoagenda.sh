#!/usr/bin/env bash
# DELTA-X adapter TEMPLATE -- drive your own agent system.
#
# Copy this file, fill in the one marked line, and run:
#   harness/run_campaign.sh --run-id run1 --adapter evoagenda
#
# The contract is in harness/adapters/README.md. This template handles the
# bookkeeping; you supply the invocation.
set -u -o pipefail

PROMPT=""; WORKDIR=""; MODE="tools"; TMO=3600; SESSION=""; OUT=""; MODEL="${DELTAX_MODEL:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt-file) PROMPT="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --timeout-seconds) TMO="$2"; shift 2;;
    --session-file) SESSION="$2"; shift 2;;
    --out-json) OUT="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    -h|--help) awk 'NR>1 && /^#/{sub(/^# ?/,"");print;next} NR>1{exit}' "${BASH_SOURCE[0]}"; exit 0;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
for v in PROMPT WORKDIR OUT; do [ -n "${!v}" ] || { echo "missing --${v,,}" >&2; exit 2; }; done
mkdir -p "$WORKDIR" || exit 1
START=$(date +%s)

# ---------------------------------------------------------------------------
# THE ONE LINE YOU SUPPLY.
#
# Hand "$PROMPT" (a file) to your system, with:
#   - cwd            = $WORKDIR            every read and write stays inside it
#   - tool policy    = $MODE               notools => no shell, no network
#   - session state  = $SESSION            load on entry, save on exit
#   - wall clock     = $TMO seconds
# Write whatever your system returns to "$OUT".
#
# Example shape:
#   ( cd "$WORKDIR" && timeout "$TMO" python -m evo_agenda run \
#        --prompt-file "$PROMPT" --tools "$MODE" --session "$SESSION" \
#        ${MODEL:+--model "$MODEL"} --json ) > "$OUT" 2>&1
#
echo "evoagenda.sh is a TEMPLATE -- fill in the invocation below this line" >&2
exit 2
# ---------------------------------------------------------------------------

RC=$?
ELAPSED=$(( $(date +%s) - START ))
TIMED_OUT=false; [ "$RC" = "124" ] && { TIMED_OUT=true; RC=0; }
echo "evoagenda: mode=$MODE rc=$RC elapsed=${ELAPSED}s timed_out=$TIMED_OUT out=$OUT"
exit $RC
