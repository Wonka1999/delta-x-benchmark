# DELTA-X v2

**A discovery benchmark for scientific agents, worked out end to end on one real case.**

[中文说明](README.zh.md) · [15-minute path](docs/00_START_HERE.md) · [containment rule](docs/CONTAINMENT.md) · [results so far](docs/RESULTS.md)

---

Most agent benchmarks ask whether a model can retrieve something it was trained on. This one
subtracts that. Every scored item is defined so that **naming the answer is worth zero and
deriving it is worth everything**: a correct region with no statistic attached scores 0, and a
number that no recorded command produced is struck before scoring, right or wrong.

The case is two paralogous enzymes of one eukaryotic nucleotidyltransferase family that differ
in one property — template-dependence of synthesis *in cis*. The agent gets 487 sequences, a
shell, and six tasks. It gets no region names, no region count, and no literature.

The benchmark does not hide which proteins these are. Blinding was measured and it does not
work: in three clean-room runs with no tools, the family was recognised from the first sentence
3 of 3. Recognition is subtracted from the score, never punished.

## What is in here

| | |
|---|---|
| **The tasks** | `tasks/` — six briefs, verbatim, exactly as served to the agent |
| **The data** | `data/` — 322 + 165 species-unique sequences and 7 references, 268 KB, bundled |
| **The harness** | `harness/` — driver, prompt builder, adapters, containment audit, submission collector |
| **The grader** | `grader/` — answer key, scoring rules, scorecard spec and its checker |
| **The tools** | `env/` — one conda command for the light tier, honest instructions for the GPU tier |
| **The reproduction** | `repro/` — every number in the key, re-derivable from the shipped data |
| **The results** | `results/`, `grader/baselines/` — two measured campaigns, with their raw records |

## Quickstart

```bash
git clone <this repo> && cd delta-x
conda env create -f env/environment.yml && conda activate delta-x    # light tier, ~5 min
bash env/probe_env.sh ./ENVIRONMENT.md                               # what this host actually has

# check the plumbing without spending a token
harness/run_campaign.sh --run-id smoke --adapter stub --work ~/delta-x-runs --stages s1,s2

# run a real campaign
harness/run_campaign.sh --run-id run1 --adapter claude_code --model opus \
    --work ~/delta-x-runs --environment ./ENVIRONMENT.md

# score it
python3 -I harness/audit_containment.py  ~/delta-x-runs/run1      # MANDATORY. exit 1 => void
python3 -I harness/collect_submission.py ~/delta-x-runs/run1 --out results/mine/run1
#   ... grade per grader/GRADING.md, emitting results/mine/run1/scorecard.json ...
python3 -I grader/check_scorecard.py results/mine/run1/scorecard.json
python3 -I analysis/aggregate.py results/mine --label "my system" \
        --compare grader/baselines/BASELINE-v3-tooled/scorecards
```

To measure **your own** system, write one adapter — a single executable that hands a prompt to
your agent with a working directory and a tool policy. The contract is one page:
[`harness/adapters/README.md`](harness/adapters/README.md), and `adapters/evoagenda.sh` is a
template with one line to fill in. Adapters for Claude (Claude Code CLI) and for OpenAI /
OpenAI-compatible endpoints ship working.

## The six tasks

| task | capability under test | tools | points |
|---|---|---|---|
| DX01 | forms hypotheses **before** looking at data | none | 0 — gate; a FAIL caps the campaign at 40 |
| DX02 | designs an analysis that *could fail*: thresholds, nulls and abandon conditions declared in advance | none | 10 |
| DX02B | converts the frozen plan into numbered, confidence-bearing expectations | none | 0 — reported beside the score |
| DX03 | **derives** a differential region from sequence, and knows its own resolution | MAFFT, HMMER, coevolution, Python | 35 |
| DX04 | **chooses the right statistic** — the obvious structural screen ranks the right answer behind two wrong ones | structure prediction, structural alignment, PDB | 35 |
| DX05 | combines independent lines into one bounded conclusion, and says where it stops | none | 20 |

DX01, DX02 and DX02B need **no tools at all** and run with zero installs. The weights are not
argued; they were set from a measured clean-room baseline, and DX02 was cut from 20 to 10 when
its old rubric was measured to separate three runs by 0.4 points out of 20.

## Four rules that run across every task

1. **Baseline subtraction.** An item a tool-free model answers for free is worth zero. Naming
   the region is worth zero.
2. **The provenance gate.** A number in a scored artifact that no `execution_log.json` record
   licenses is struck before scoring — right or wrong — and cannot support any other conclusion.
3. **The scorecard is the score.** A total unaccompanied by a per-item scorecard that reconciles
   against its own rows may not be published, cited or compared. `grader/check_scorecard.py`
   is the gate.
4. **Fabrication needs a self-reproduction check.** Before any fabrication verdict the grader
   re-executes the recorded `argv` twice and confirms the tool reproduces *itself*. MAFFT is
   deterministic only at a fixed thread count; without this rule an honest multithreaded run
   would be branded a fabricator.

## Containment — read this before running anything

**This repository holds the answer key.** An agent that reads `grader/` has not been measured;
it has been told.

- The driver **refuses** to stage a run inside the repository.
- `harness/audit_containment.py` is mandatory before any score is read, and a breach voids the
  run — re-run it, do not discount it.
- Do not put a `CLAUDE.md`, `AGENTS.md` or equivalent naming this case anywhere the evaluated
  agent will be started. This repo's own `CLAUDE.md` is written to be safe to inject; the
  designer-side documents are not, and are listed in [docs/CONTAINMENT.md](docs/CONTAINMENT.md).

## Results so far

Two measured campaigns ship with their raw records.

| campaign | system | n | tools | scope | result |
|---|---|---|---|---|---|
| `BASELINE-v2-clean` | Claude Opus 5 | 3 | all blocked | DX01, DX02 only | DX02 3.0 / 1.0 / 5.0 under the current rules |
| `BASELINE-v3-tooled` | Claude Opus 5 | 5 | real shell | all five tasks | **mean 95.70 / 100, range 5.0** |

The headline finding is uncomfortable and it is the reason this is public: **the benchmark is
saturated**, and the mechanism is that the rubric was published with it. Submissions now carry
fields named after the rules — 0 of 14 proposed programs fail DX02's rule 2, and DX03's
granularity penalty fired 0 times in 5 runs. Integrity held across the campaign: 0 fabrication
events, 0 containment breaches, no scored number struck. The next version needs the tasks
re-cut or the adjudication moved out of the brief, not the weights shuffled between items that
are all at ceiling. Details, per-item discrimination and the two negative results in
[docs/RESULTS.md](docs/RESULTS.md).

## Layout

```
tasks/      six task briefs + an ENVIRONMENT.md example        AGENT-VISIBLE
data/       the sequences the agent is given                   AGENT-VISIBLE
harness/    driver, prompt builder, adapters, audits
env/        tool installation, three tiers
grader/     KEY.md, GRADING.md, SCORECARD.md, rubric, baselines DESIGNER-SIDE
repro/      scripts and manifest behind every number in the key DESIGNER-SIDE
analysis/   scorecards -> tables, ranges, per-item discrimination
docs/       start here, containment, scoring, results, FAQ      DESIGNER-SIDE
results/    where your campaigns go
```

## Licence and citation

Code is MIT. The task briefs, data curation, key and documentation are CC BY 4.0. See
[LICENSE](LICENSE) and [CITATION.cff](CITATION.cff). If you publish a measurement, please
include the `measured_scope` field from your scorecard: a score whose scope is not stated is
not comparable to one whose scope is.
