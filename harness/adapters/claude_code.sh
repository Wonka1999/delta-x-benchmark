#!/usr/bin/env bash
# DELTA-X adapter: Anthropic Claude models through the Claude Code headless CLI.
# Implements the adapter contract in harness/adapters/README.md.
#
#   claude_code.sh --prompt-file P --workdir W --mode tools|notools \
#                  --timeout-seconds N --session-file S --out-json O [--model M]
#
# Requires `claude` on PATH. Permissions are granted with explicit --allowedTools,
# never with --dangerously-skip-permissions.
set -u -o pipefail

PROMPT=""; WORKDIR=""; MODE="tools"; TMO=3600; SESSION=""; OUT=""; MODEL="${DELTAX_CLAUDE_MODEL:-opus}"
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
for v in PROMPT WORKDIR OUT; do
  [ -n "${!v}" ] || { echo "missing --${v,,}" >&2; exit 2; }
done
command -v claude >/dev/null || { echo "claude CLI not on PATH" >&2; exit 2; }

# Tool-free stages still get Write, so artifacts land as files and DX01's
# commitment goes down the harness-computes-the-digest branch.
if [ "$MODE" = "notools" ]; then
  PERMS=(--allowedTools Write
         --disallowedTools Bash Read Edit Glob Grep WebSearch WebFetch Task NotebookEdit)
else
  PERMS=(--allowedTools Bash Read Write Edit Glob Grep WebFetch
         --disallowedTools Task NotebookEdit WebSearch)
fi

RESUME=()
if [ -n "$SESSION" ] && [ -s "$SESSION" ]; then
  SID=$(sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$SESSION" | head -1)
  [ -n "$SID" ] && RESUME=(--resume "$SID")
fi

mkdir -p "$WORKDIR" || exit 1
START=$(date +%s)
( cd "$WORKDIR" && timeout "$TMO" claude -p "${RESUME[@]}" "${PERMS[@]}" \
      --model "$MODEL" --output-format json < "$PROMPT" ) > "$OUT" 2>&1
RC=$?
ELAPSED=$(( $(date +%s) - START ))

# Carry the session id forward so the next stage sees this one.
if [ -n "$SESSION" ]; then
  SID=$(sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$OUT" | head -1)
  [ -n "$SID" ] && printf '{"session_id": "%s"}\n' "$SID" > "$SESSION"
fi

TIMED_OUT=false; [ "$RC" = "124" ] && TIMED_OUT=true
echo "claude_code: model=$MODEL mode=$MODE rc=$RC elapsed=${ELAPSED}s timed_out=$TIMED_OUT out=$OUT"
# A timeout is a measurement condition, not a harness failure: the driver records
# it and the artifacts written before it stand.
[ "$RC" = "124" ] && exit 0
exit $RC
