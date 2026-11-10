# Containment

**The repository holds the answer key.** An agent that reads it has not been measured; it has
been told. This page is the complete list of what must never reach an evaluated system, the
mechanisms that enforce it, and the two ways it has actually been breached in this project's
history.

## Agent-visible, by design

| path | why it is safe |
|---|---|
| `tasks/*.md` | the briefs themselves — this is the stimulus |
| `tasks/ENVIRONMENT.example.md` | tool paths and versions; names nothing scored |
| `data/*.fasta` | the sequences; the filenames and accessions name the subfamilies, deliberately |
| the composed prompts under `<run>/prompts/` | brief + an operational preamble that names no region, statistic, threshold or expected result |

Nothing else.

## Designer-side — a run that touches any of these is VOID

| path | what it leaks |
|---|---|
| `grader/KEY.md` | the frozen answers, the decoy sets, the measured baselines, the weighting basis |
| `grader/KEY-DX02B.md` | per-item adjudication tables naming the correct direction on four axes |
| `grader/GRADING.md`, `grader/SCORECARD.md`, `grader/rubric/` | how every item is adjudicated |
| `grader/FIXSPEC.md`, `grader/FIXSPEC-2.md` | two rounds of revision decisions, with the facts behind them |
| `grader/FRAME-DISCIPLINE.md` | the coordinate-frame gate, and why shifting the served numbering was rejected |
| `grader/baselines/**` | preserved stimuli, raw submissions, grades |
| `repro/REPRODUCTION.md`, `repro/scripts/` | structure accessions, the cross-species +1 numbering rule, scored intervals hardcoded |
| `docs/**`, including this file | names the case and its scored facts |
| `README.md`, `README.zh.md` | the four cross-cutting rules and the measured results |
| any `CLAUDE.md` / `AGENTS.md` naming the case | auto-injected into an agent started in that tree |

"The answers are only in `grader/`" is false and should not be written. Designer-side is the
union of the table above.

## The three mechanisms

1. **The driver refuses to stage a run inside the repository.** `run_campaign.sh` exits 3 if
   `--work` resolves under the repo root. The default is `~/delta-x-runs`.
2. **The prompt is composed, not pointed at.** The agent is handed the brief's text; it is never
   given a path into this tree. The preamble ends with an explicit instruction not to go looking
   for the benchmark's own materials.
3. **`harness/audit_containment.py` is mandatory before any score is read.** It scans every
   transcript and artifact for designer-side filenames and for absolute paths into the
   repository, and refuses the run if the run directory is inside the repo. A breach means
   **re-run**, never "discount it" — there is no way to tell which part of a contaminated run
   was contaminated.

This repository's own `CLAUDE.md` is deliberately written to be safe to inject: it describes
layout and the containment rule, and names no scored fact. Keep it that way.

## Two breaches that actually happened

**1. The project `CLAUDE.md` contaminated a closed-book probe.** Three of six probes run on
2026-11-05 reported reading the case from an auto-injected `CLAUDE.md` before they reached the
question. Consequence: every baseline number that depended on *blinding* was invalidated, while
the numbers that depended on *what is named unprompted* survived, because contamination only
adds. That caveat is still in force for the probes that have not been re-run.

**2. The audit itself produced a false positive and nearly voided a clean run.** An earlier
grep-based version matched the string `EvoAgenda` anywhere in the run — and the harness happened
to live under a directory with that name, so an agent logging its own `cwd` tripped it 826
times. The current audit removes every occurrence of the run's own path before matching, skips
compiled and binary files, and prints the matched token with context so a false positive is
visible rather than fatal. **An audit that cannot be checked is not an audit.**

## Leak auditing when you add to `tasks/`

Two independent audits of the v1.1 task set found roughly thirty fatal leaks, and they shared
one cause: an author validated a schema against the real key and then shipped the validation as
the example. Rules that came out of it:

- Every schema example must come from a single fictional frame, published once, that shares no
  identifier with the real case.
- A task input may not disclose a quantity the rubric scores. A nomination budget equal to the
  number of scorable positives is a leak. A list of assayed positions that is literally the
  anchor table is a leak.
- New task text gets a pattern scan before it ships. `DX02B.md` passed a 40-pattern scan with
  zero hits before it was added; that is the bar.
