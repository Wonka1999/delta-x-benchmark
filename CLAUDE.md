# CLAUDE.md

Guidance for Claude Code working **on** this repository. It is deliberately free of scored
facts, because a `CLAUDE.md` is auto-injected into any agent started in this tree and one
already contaminated three closed-book probes in this project's history. Keep it that way: no
region names, no residue numbers, no accessions, no measured values.

## What this repository is

DELTA-X v2, a discovery benchmark for scientific agents, released so that a third party can
measure their own system and score it. There is no package and no application: the deliverables
are task briefs, a driver that runs a system through them, a scoring procedure, and two measured
campaigns with their raw records. The Python is stdlib-plus-numpy utilities, not a library.

## The split that is load-bearing

**Agent-visible:** `tasks/`, `data/`, and the prompts the driver composes from them. Nothing else.

**Designer-side:** `grader/`, `repro/`, `docs/`, both READMEs, and this file's siblings. A run
whose transcript touches any of it is void. `docs/CONTAINMENT.md` is the complete list; keep it
complete when you add a file.

Before changing anything under `tasks/`, re-read `docs/CONTAINMENT.md` §"Leak auditing". Two
independent audits of the previous version found ~30 fatal leaks with one shared cause: an
author validated a schema against the real key and shipped the validation as the example.

## Commands

```bash
make help                 # every target
make smoke                # full offline pipeline check, no model called, no tokens spent
make check                # compile + self-tests + scorecard checker + aggregator over the baselines
make prompts              # compose the six prompts and print their digests

harness/run_campaign.sh --run-id run1 --adapter claude_code --work ~/delta-x-runs
python3 -I harness/audit_containment.py ~/delta-x-runs/run1      # exit 1 => the run is VOID
python3 -I grader/check_scorecard.py results/<campaign>/run1/scorecard.json
python3 -I analysis/aggregate.py results/<campaign> --label <name>
```

## Invariants a change must preserve

1. **`harness/build_prompts.py` reproduces the published campaign stimulus byte for byte.**
   All six digests are in `grader/baselines/BASELINE-v3-tooled/STIMULUS.txt` and `make check`
   compares against them. The inputs are part of the invariant: the preamble templates, every
   `tasks/DX*.md`, and `tasks/ENVIRONMENT.example.md`. **Editing any of them changes the
   measurement** — including a typo fix. If you mean to, record the new digests and say which
   campaign they belong to. The comparison is not decoration.
2. **The driver refuses to stage a run inside the repository.** Do not add an escape hatch.
3. **`notools` still grants file writes.** Both adapters do this. The tool-free tasks are scored
   on artifacts; a system that cannot write files delivers nothing and DX01 cannot be scored.
4. **A score without a reconciling per-item scorecard is not a score.** `check_scorecard.py`
   is the gate and `SCORECARD.md` is its specification; change the spec first.
5. **Weights follow measured discrimination, never argument.** An item's weight may be raised
   only against a pre-registered rule with an n, a statistic and a threshold. This rule exists
   because it was broken once and `docs/RESULTS.md` records the cost.

## Document authority

`grader/KEY.md` governs adjudication. `grader/SCORECARD.md` governs the form of the record.
`grader/rubric/items.json` is an index of both and loses to either. `tasks/*.md` are the
stimulus and are frozen per campaign — an edit between runs makes those runs incomparable, so
re-digest and say so in the campaign's `PROVENANCE.txt`.

## Style

Files 200–400 lines typical, 800 maximum. Prose is plain and declarative; the reader is a
collaborator deciding whether to trust a number. State what was measured, with the number, and
state separately what was not. Where a claim is a projection rather than a measurement, say
which it is — the previous version shipped four of those unmarked and they had to be corrected.
