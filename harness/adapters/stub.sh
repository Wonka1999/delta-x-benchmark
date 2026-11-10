#!/usr/bin/env bash
# DELTA-X adapter: a stub that spends nothing.
#
# It writes a minimal, obviously-fake file for every artifact the task names, so
# you can check the driver, the collector, the containment audit and the
# scorecard checker end to end before paying for a real run.
#
# Its output is NOT a submission. Every artifact says so, and grading one is a
# category error, not a low score.
set -u -o pipefail

PROMPT=""; WORKDIR=""; MODE="tools"; TMO=60; SESSION=""; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt-file) PROMPT="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --timeout-seconds) TMO="$2"; shift 2;;
    --session-file) SESSION="$2"; shift 2;;
    --out-json) OUT="$2"; shift 2;;
    --model) shift 2;;
    *) shift;;
  esac
done
[ -n "$WORKDIR" ] && [ -n "$OUT" ] || { echo "stub: missing --workdir/--out-json" >&2; exit 2; }
mkdir -p "$WORKDIR" || exit 1

# Which artifacts does this prompt ask for? Take them from the brief itself.
names=$(grep -oE '`[a-z0-9_]+\.(json|tsv)`' "$PROMPT" 2>/dev/null | tr -d '`' | sort -u)
n=0
for f in $names; do
  p="$WORKDIR/$f"
  [ -e "$p" ] && continue
  case "$f" in
    *.tsv) printf 'col_a\tcol_b\tstatistic\nSTUB\tSTUB\t0\n' > "$p";;
    *)     printf '[{"id": "stub-1", "note": "STUB ADAPTER OUTPUT - NOT A SUBMISSION"}]\n' > "$p";;
  esac
  n=$((n+1))
done
[ -n "$SESSION" ] && printf '{"stub_session": true}\n' > "$SESSION"
printf '{"adapter": "stub", "mode": "%s", "artifacts_written": %d, "timed_out": false,\n "final_text": "STUB ADAPTER - no model was called"}\n' "$MODE" "$n" > "$OUT"
echo "stub: mode=$MODE wrote $n artifact(s) into $WORKDIR"
exit 0
