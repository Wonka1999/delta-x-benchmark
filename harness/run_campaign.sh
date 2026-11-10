#!/usr/bin/env bash
# DELTA-X v2 campaign driver.
#
# Runs one system through the six tasks in order, in a clean-room working
# directory OUTSIDE this repository, and leaves a submission a grader can score.
#
#   harness/run_campaign.sh --run-id run1 --adapter claude_code [options]
#
# Options
#   --run-id <id>         required; names the run directory and the submission
#   --adapter <name>      adapters/<name>.sh or adapters/<name>.py, or an absolute path
#   --stages s1,s2,...    default s1,s2,s2b,s3,s4,s5
#   --work <dir>          run root; default $DELTAX_WORK or ~/delta-x-runs
#   --environment <path>  ENVIRONMENT.md for this host (see env/probe_env.sh)
#   --model <id>          passed through to the adapter verbatim
#   --dry-run             compose prompts, stage data, print the plan, run nothing
#
# CONTAINMENT. The working directory must not be inside this repository, and the
# adapter must not be given access to it. The repository holds the answer key; an
# agent that reads it has not been measured. harness/audit_containment.py is the
# check, and it is not optional -- run it before reading any score.
set -u -o pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID=""; ADAPTER="claude_code"; STAGES="s1,s2,s2b,s3,s4,s5"
WORK="${DELTAX_WORK:-$HOME/delta-x-runs}"; ENVFILE=""; MODEL=""; DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --run-id) RUN_ID="$2"; shift 2;;
    --adapter) ADAPTER="$2"; shift 2;;
    --stages) STAGES="$2"; shift 2;;
    --work) WORK="$2"; shift 2;;
    --environment) ENVFILE="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    -h|--help) awk 'NR>1 && /^#/{sub(/^# ?/,"");print;next} NR>1{exit}' "${BASH_SOURCE[0]}"; exit 0;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -n "$RUN_ID" ] || { echo "--run-id is required" >&2; exit 2; }

# ---- containment: the run must not happen inside the repository -------------
mkdir -p "$WORK" || exit 1
WORK="$(cd "$WORK" && pwd)"
case "$WORK/" in
  "$REPO"/*) echo "REFUSING: --work ($WORK) is inside the repository ($REPO)." >&2
             echo "The repository carries the answer key. Use e.g. --work ~/delta-x-runs." >&2
             exit 3;;
esac

# ---- resolve the adapter ----------------------------------------------------
if [ -x "$ADAPTER" ]; then
  ADAPTER_CMD="$ADAPTER"
elif [ -f "$REPO/harness/adapters/$ADAPTER.sh" ]; then
  ADAPTER_CMD="bash $REPO/harness/adapters/$ADAPTER.sh"
elif [ -f "$REPO/harness/adapters/$ADAPTER.py" ]; then
  ADAPTER_CMD="${DELTAX_PYTHON:-python3} $REPO/harness/adapters/$ADAPTER.py"
else
  echo "no adapter '$ADAPTER' -- see harness/adapters/README.md" >&2; exit 2
fi

RUN="$WORK/$RUN_ID"
mkdir -p "$RUN"/{prompts,out,work/data,artifacts}

# ---- compose the stimulus ---------------------------------------------------
ENVARG=""; [ -n "$ENVFILE" ] && ENVARG="--environment $ENVFILE"
# shellcheck disable=SC2086
${DELTAX_PYTHON:-python3} -I "$REPO/harness/build_prompts.py" \
    --repo "$REPO" --out "$RUN/prompts" --data-dir ./data $ENVARG || exit 1

cp "$REPO"/data/*.fasta "$RUN/work/data/" || exit 1

# ---- freeze what was actually served ---------------------------------------
{
  echo "run_id: $RUN_ID"
  echo "adapter: $ADAPTER    model: ${MODEL:-adapter default}"
  echo "stages: $STAGES"
  echo "started_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "repo_commit: $(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo 'not a git checkout')"
  echo "=== briefs served ==="; (cd "$REPO" && sha256sum tasks/*.md)
  echo "=== stimulus actually fed ==="; (cd "$RUN" && sha256sum prompts/*.txt)
  echo "=== data served ==="; (cd "$RUN/work" && sha256sum data/*.fasta)
  echo "=== harness ==="; (cd "$REPO" && sha256sum harness/run_campaign.sh harness/build_prompts.py)
} > "$RUN/PROVENANCE.txt"

timeout_for(){ case "$1" in s1|s2|s2b) echo 2400;; s3) echo 6600;; s4) echo 8400;; s5) echo 3600;; *) echo 3600;; esac; }
mode_for(){    case "$1" in s1|s2|s2b) echo notools;; *) echo tools;; esac; }

if [ "$DRY" = "1" ]; then
  echo "--- dry run ---"; echo "repo:    $REPO"; echo "run dir: $RUN"
  echo "adapter: $ADAPTER_CMD"
  for st in ${STAGES//,/ }; do
    echo "  $st  mode=$(mode_for "$st")  timeout=$(timeout_for "$st")s  prompt=$RUN/prompts/$st.txt"
  done
  exit 0
fi

# ---- run the stages in order, one resumable session ------------------------
SESSION="$RUN/out/session.json"
for st in ${STAGES//,/ }; do
  P="$RUN/prompts/$st.txt"
  [ -f "$P" ] || { echo "$RUN_ID $st: no prompt, skipped"; continue; }
  T="$(timeout_for "$st")"; M="$(mode_for "$st")"
  MODELARG=""; [ -n "$MODEL" ] && MODELARG="--model $MODEL"
  echo "[$(date +%T)] $RUN_ID $st start  mode=$M timeout=${T}s"
  # shellcheck disable=SC2086
  $ADAPTER_CMD --prompt-file "$P" --workdir "$RUN/work" --mode "$M" \
      --timeout-seconds "$T" --session-file "$SESSION" \
      --out-json "$RUN/out/${st}.json" $MODELARG \
      > "$RUN/out/${st}.stdout" 2> "$RUN/out/${st}.stderr"
  rc=$?
  # snapshot every artifact that exists at the end of this stage
  SNAP="$RUN/artifacts/$st"; mkdir -p "$SNAP"
  (cd "$RUN/work" && find . -maxdepth 3 -type f \
      \( -name '*.json' -o -name '*.tsv' -o -name '*.csv' -o -name '*.md' -o -name '*.txt' \) \
      ! -path './data/*' -exec cp --parents {} "$SNAP/" \; ) 2>/dev/null
  n=$(find "$RUN/work" -maxdepth 3 -type f ! -path "*/data/*" 2>/dev/null | wc -l)
  echo "[$(date +%T)] $RUN_ID $st done rc=$rc files=$n"
done

echo "finished_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN/PROVENANCE.txt"
echo
echo "run directory: $RUN"
echo "next:"
echo "  python3 -I $REPO/harness/audit_containment.py $RUN   # MANDATORY before any score"
echo "  python3 -I $REPO/harness/harness_digest.py $RUN     # DX01 commitment digest"
echo "  python3 -I $REPO/harness/collect_submission.py $RUN --out $REPO/results/<name>/$RUN_ID"
