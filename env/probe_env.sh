#!/usr/bin/env bash
# DELTA-X v2 — probe this host and write a filled-in ENVIRONMENT.md.
#
#   bash env/probe_env.sh [OUTPUT]      # default: ./ENVIRONMENT.md
#
# The file it writes is the one served to the evaluated agent. It must be
# truthful about absences: a tool that is not on this host is written into the
# table as NOT INSTALLED, never omitted and never guessed. The script always
# exits 0 — a missing tool is a fact to record, not an error to fail on.
#
# Dependencies: bash + coreutils. No python, no conda, no network.
#
# Overrides (export before running) for interpreters this script cannot guess:
#   DELTAX_PYTHON            python used for the "scientific Python" row
#   DELTAX_ESMFOLD_PYTHON    python that can import torch + esm/transformers
#   DELTAX_PROTENIX_PYTHON   python that can import protenix

set -u

OUT="${1:-./ENVIRONMENT.md}"
TODAY="$(date +%Y-%m-%d)"

REQUIRED_FOUND=0 ; REQUIRED_TOTAL=0
OPTIONAL_FOUND=0 ; OPTIONAL_TOTAL=0
MISSING=""

NI='**NOT INSTALLED**'

# ---------------------------------------------------------------- helpers ---

# abspath PATH -> absolute path, WITHOUT resolving symlinks.
# Deliberate: `readlink -f` on a venv or conda-env interpreter reports the base
# interpreter it links to, which is a different interpreter with a different
# site-packages. The agent must be handed the path it should actually invoke.
abspath() {
    if [ -z "${1:-}" ]; then return 1; fi
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *)  ( cd "$(dirname -- "$1")" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$(basename -- "$1")" ) ;;
    esac
}

have() { command -v -- "$1" >/dev/null 2>&1; }

# first line of output, trimmed, pipes escaped so the markdown table survives
clean() {
    tr -d '\r' | sed -e 's/[[:space:]]\{1,\}/ /g' -e 's/^ //' -e 's/ $//' -e 's/|/\\|/g' | head -1
}

# tally NAME required|optional found|missing
tally() {
    case "$2" in
        required) REQUIRED_TOTAL=$((REQUIRED_TOTAL + 1))
                  [ "$3" = found ] && REQUIRED_FOUND=$((REQUIRED_FOUND + 1)) ;;
        optional) OPTIONAL_TOTAL=$((OPTIONAL_TOTAL + 1))
                  [ "$3" = found ] && OPTIONAL_FOUND=$((OPTIONAL_FOUND + 1)) ;;
    esac
    [ "$3" = missing ] && MISSING="${MISSING}${MISSING:+, }$1"
    return 0
}

# row LABEL PATH VERSION
row() { printf '| %s | %s | %s |\n' "$1" "$2" "$3" >> "$OUT"; }

note() { printf -- '- %s\n' "$1" >> "$OUT"; }

# ------------------------------------------------------------- the probes ---

NOTES_EXTRA=""
add_note() { NOTES_EXTRA="${NOTES_EXTRA}${NOTES_EXTRA:+%%}$1"; }

probe_mafft() {
    if have mafft; then
        P="$(abspath "$(command -v mafft)")"
        V="$(mafft --version 2>&1 | clean)"
        [ -z "$V" ] && V='version flag produced no output'
        row 'MAFFT' "\`$P\`" "$V" ; tally MAFFT required found
    else
        row 'MAFFT' "$NI" "$NI" ; tally MAFFT required missing
    fi
}

probe_hmmer() {
    # HMMER has no --version; the version is line 2 of any binary's -h banner.
    if have hmmbuild; then
        P="$(abspath "$(command -v hmmbuild)")" ; D="$(dirname -- "$P")"
        V="$(hmmbuild -h 2>&1 | sed -n 's/^# \(HMMER [0-9][^;]*\).*/\1/p' | clean)"
        [ -z "$V" ] && V='present, version string not parsed from -h'
        BINS=''
        for b in hmmbuild hmmalign hmmsearch hmmscan jackhmmer phmmer esl-reformat esl-alimanip; do
            have "$b" && BINS="${BINS}${BINS:+,}$b"
        done
        row 'HMMER' "\`$D/{$BINS}\`" "$V" ; tally HMMER required found
        have esl-reformat || add_note 'The Easel miniapps (`esl-reformat`, `esl-alimanip`) are not on PATH. The Debian/Ubuntu `hmmer` package does not install them; the bioconda `hmmer` package does.'
    else
        row 'HMMER' "$NI" "$NI" ; tally HMMER required missing
    fi
}

probe_hhsuite() {
    if have hhmake || have hhalign; then
        B="$(command -v hhmake 2>/dev/null || command -v hhalign)"
        P="$(abspath "$B")" ; D="$(dirname -- "$P")"
        BINS=''
        for b in hhmake hhalign hhsearch hhblits hhfilter; do
            have "$b" && BINS="${BINS}${BINS:+,}$b"
        done
        V="$("$B" -h 2>&1 | clean)"
        [ -z "$V" ] && V='present, version string not parsed from -h'
        row 'HH-suite' "\`$D/{$BINS}\`" "$V (self-reported)" ; tally HH-suite optional found
        add_note 'HH-suite binaries print their own internal version string, which does not track the package version: the Ubuntu 20.04 `hhsuite` 3.2.0 package prints `HHmake 3.1.0`. Record what the binary prints.'
    else
        row 'HH-suite' "$NI" "$NI" ; tally HH-suite optional missing
    fi
}

probe_pydca() {
    if have plmdca || have mfdca; then
        B="$(command -v plmdca 2>/dev/null || command -v mfdca)"
        P="$(abspath "$B")" ; D="$(dirname -- "$P")"
        BINS=''
        for b in plmdca mfdca pydca; do have "$b" && BINS="${BINS}${BINS:+,}$b"; done
        V=''
        if [ -x "$D/python" ]; then
            V="$("$D/python" -c 'import importlib.metadata as m; print("pydca " + m.version("pydca"))' 2>/dev/null | clean)"
        fi
        if [ -z "$V" ]; then
            V="$(ls -d "$D"/../lib/python*/site-packages/pydca-*.dist-info 2>/dev/null | head -1 | sed -n 's/.*pydca-\(.*\)\.dist-info/pydca \1/p')"
        fi
        [ -z "$V" ] && V='pydca CLI (exposes no --version flag)'
        row 'plmDCA / mfDCA (pydca)' "\`$D/{$BINS}\`" "$V" ; tally pydca optional found
    else
        row 'plmDCA / mfDCA (pydca)' "$NI" "$NI" ; tally pydca optional missing
    fi
}

# torch_probe INTERPRETER -> "torch X+cuY, CUDA available" or empty
torch_probe() {
    [ -x "$1" ] || return 1
    "$1" - <<'PY' 2>/dev/null
import sys
try:
    import torch
except Exception:
    sys.exit(1)
ok = []
try:
    ok.append("CUDA available" if torch.cuda.is_available() else "CUDA NOT available")
except Exception:
    ok.append("CUDA state unknown")
mods = []
for m in ("esm", "transformers"):
    try:
        __import__(m); mods.append(m)
    except Exception:
        pass
print("torch %s, %s%s" % (torch.__version__, ok[0], (", " + "+".join(mods)) if mods else ", no esm/transformers"))
PY
}

probe_esmfold() {
    CAND="${DELTAX_ESMFOLD_PYTHON:-}"
    FOUND=''
    for py in "$CAND" "$(command -v python3 2>/dev/null)" "$(command -v python 2>/dev/null)"; do
        [ -n "$py" ] || continue
        V="$(torch_probe "$py" | clean)"
        if [ -n "$V" ]; then FOUND="$(abspath "$py")"; break; fi
    done
    if [ -n "$FOUND" ]; then
        case "$V" in
            *"no esm/transformers"*)
                row 'ESMFold' "\`$FOUND\`" "$V — torch present, **no folding package**"
                tally ESMFold optional missing
                add_note 'A torch interpreter was found but neither `esm` nor `transformers` imports from it, so ESMFold cannot run. Set `DELTAX_ESMFOLD_PYTHON` if the right interpreter is elsewhere.' ;;
            *)
                row 'ESMFold' "\`$FOUND\`" "$V"
                tally ESMFold optional found ;;
        esac
    else
        row 'ESMFold' "$NI" "$NI" ; tally ESMFold optional missing
    fi
}

probe_protenix() {
    if have protenix; then
        P="$(abspath "$(command -v protenix)")" ; D="$(dirname -- "$P")"
        V=''
        if [ -x "$D/python" ]; then
            V="$("$D/python" -c 'import importlib.metadata as m; print("protenix " + m.version("protenix"))' 2>/dev/null | clean)"
        fi
        [ -z "$V" ] && V='present (version not reported by the CLI)'
        row 'Protenix' "\`$P\`" "$V" ; tally Protenix optional found
    else
        row 'Protenix' "$NI" "$NI" ; tally Protenix optional missing
    fi
}

probe_foldseek() {
    if have foldseek; then
        P="$(abspath "$(command -v foldseek)")"
        V="$(foldseek version 2>&1 | clean)"
        [ -z "$V" ] && V='present, version subcommand produced no output'
        row 'foldseek' "\`$P\`" "$V" ; tally foldseek optional found
    else
        row 'foldseek' "$NI" "$NI" ; tally foldseek optional missing
    fi
}

probe_usalign() {
    if have USalign || have TMalign; then
        B="$(command -v USalign 2>/dev/null || command -v TMalign)"
        P="$(abspath "$B")" ; D="$(dirname -- "$P")"
        BINS=''
        for b in USalign MMalign TMalign TMscore NWalign qTMclust se pdb2fasta cif2pdb; do
            have "$b" && BINS="${BINS}${BINS:+,}$b"
        done
        V="$("$B" -v 2>&1 | sed -n 's/.*(\(Version [0-9A-Za-z.]*\)).*/\1/p' | clean)"
        [ -z "$V" ] && V="$("$B" -h 2>&1 | sed -n 's/.*(\(Version [0-9A-Za-z.]*\)).*/\1/p' | clean)"
        [ -z "$V" ] && V='present, version string not parsed'
        row 'USalign suite' "\`$D/{$BINS}\`" "$V" ; tally USalign optional found
    else
        row 'USalign suite' "$NI" "$NI" ; tally USalign optional missing
    fi
}

probe_python() {
    BEST='' ; BESTV='' ; FALLBACK='' ; FALLBACKV=''
    for py in "${DELTAX_PYTHON:-}" "$(command -v python3 2>/dev/null)" "$(command -v python 2>/dev/null)"; do
        [ -n "$py" ] && [ -x "$py" ] || continue
        V="$("$py" - <<'PY' 2>/dev/null
import sys
out = ["%d.%d.%d" % sys.version_info[:3]]
missing = []
for name, mod in (("numpy","numpy"), ("scipy","scipy"), ("pandas","pandas"), ("biopython","Bio")):
    try:
        m = __import__(mod)
        out.append("%s %s" % (name, getattr(m, "__version__", "?")))
    except Exception:
        missing.append(name)
print(" · ".join(out) + (" · MISSING: " + ", ".join(missing) if missing else ""))
PY
)"
        V="$(printf '%s' "$V" | clean)"
        [ -n "$V" ] || continue
        case "$V" in
            *MISSING*) [ -z "$FALLBACK" ] && { FALLBACK="$(abspath "$py")"; FALLBACKV="$V"; } ;;
            *)         BEST="$(abspath "$py")"; BESTV="$V"; break ;;
        esac
    done
    if [ -n "$BEST" ]; then
        row 'scientific Python' "\`$BEST\`" "$BESTV" ; tally 'scientific Python' required found
    elif [ -n "$FALLBACK" ]; then
        row 'scientific Python' "\`$FALLBACK\`" "$FALLBACKV" ; tally 'scientific Python' required missing
        add_note 'The python found on PATH is missing part of the numeric stack (see the MISSING list in its row). Activate the `delta-x` environment, or set `DELTAX_PYTHON`, before relying on it.'
    else
        row 'scientific Python' "$NI" "$NI" ; tally 'scientific Python' required missing
    fi
}

probe_gpu() {
    if have nvidia-smi; then
        G="$(nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null | head -1 | clean)"
        if [ -n "$G" ]; then
            row 'GPU' '—' "$G (name, total memory, driver)" ; tally GPU optional found
        else
            row 'GPU' '—' '`nvidia-smi` present but reported no device' ; tally GPU optional missing
        fi
    else
        row 'GPU' '—' "$NI (no \`nvidia-smi\`)" ; tally GPU optional missing
    fi
}

# ------------------------------------------------------------------ write ---

OUTDIR="$(dirname -- "$OUT")"
mkdir -p -- "$OUTDIR" 2>/dev/null || true
: > "$OUT" || { echo "probe_env.sh: cannot write $OUT" >&2; exit 0; }

cat >> "$OUT" <<HDR
# DELTA-X v2 — ENVIRONMENT: Tool Manifest

The absolute path and version of every tool named in the task briefs, as measured on the
benchmark host on $TODAY.

## 1. Tools

| tool | absolute path | version |
|---|---|---|
HDR

probe_mafft
probe_hmmer
probe_hhsuite
probe_pydca
probe_esmfold
probe_protenix
probe_foldseek
probe_usalign
probe_python
probe_gpu

cat >> "$OUT" <<'MID'

## 2. Notes

MID

note 'A row reading **NOT INSTALLED** means the tool is absent from this host. It is not hidden from you and it is not a trick: plan around it, and say in your outputs what you could not run.'
note 'Record the version you actually observed in `execution_log.json`. This table is the environment as of the date above, not a guarantee.'
note 'The default `python` on `PATH` may not be the interpreter listed above. Invoke the absolute path.'

# host-specific notes gathered during probing
if [ -n "$NOTES_EXTRA" ]; then
    printf '%s\n' "$NOTES_EXTRA" | tr '%%' '\n' | sed '/^$/d' | while IFS= read -r n || [ -n "$n" ]; do
        [ -n "$n" ] && note "$n"
    done
fi

{
    printf -- '- Probed by `env/probe_env.sh` on `%s` (%s, kernel %s), glibc %s.\n' \
        "$(hostname 2>/dev/null || echo unknown-host)" \
        "$(uname -m)" "$(uname -r)" \
        "$(ldd --version 2>/dev/null | head -1 | sed -n 's/.*[^0-9]\([0-9]\{1,\}\.[0-9]\{1,\}\).*/\1/p')"
    if grep -qm1 avx2 /proc/cpuinfo 2>/dev/null; then
        printf -- '- CPU reports AVX2.\n'
    else
        printf -- '- CPU does **not** report AVX2: the standard foldseek build will not run here.\n'
    fi
    printf -- '- Required tools found: %s of %s. Optional tools found: %s of %s.%s\n' \
        "$REQUIRED_FOUND" "$REQUIRED_TOTAL" "$OPTIONAL_FOUND" "$OPTIONAL_TOTAL" \
        "$([ -n "$MISSING" ] && printf ' Missing: %s.' "$MISSING")"
} >> "$OUT"

printf 'probe_env.sh: required %s/%s found, optional %s/%s found%s; wrote %s\n' \
    "$REQUIRED_FOUND" "$REQUIRED_TOTAL" "$OPTIONAL_FOUND" "$OPTIONAL_TOTAL" \
    "$([ -n "$MISSING" ] && printf ' (missing: %s)' "$MISSING")" \
    "$(abspath "$OUT")" >&2

exit 0
