# grader/ — designer-side

**Nothing in this directory may be rendered into an evaluated system's context. A harness that
does so voids its run.** `harness/audit_containment.py` is the check and it is mandatory before
any score is read.

| file | what it is | authority |
|---|---|---|
| `KEY.md` | the frozen answers, the decoy sets, the measured baselines, the weighting basis, the re-execution protocol | **governs adjudication** |
| `KEY-DX02B.md` | DX02B's adjudication tables and its pre-registered promotion rule | governs DX02B |
| `SCORECARD.md` | the form every grading run must emit | **governs the record** |
| `GRADING.md` | the procedure: five passes, in order | procedure |
| `rubric/items.json` | machine-readable index of gates, items and maxima | index; loses to `KEY.md` and `SCORECARD.md` |
| `check_scorecard.py` | implements `SCORECARD.md`'s checks; exit 0 publishable, exit 1 ungraded | gate |
| `FRAME-DISCIPLINE.md` | coordinate-frame gate — **proposed, unmeasured**; records why shifting the served numbering was rejected | proposal |
| `FIXSPEC.md`, `FIXSPEC-2.md` | two rounds of revision decisions, with the facts behind each | historical record |
| `prompts/` | templates that let an LLM close passes 4 and 5 of `GRADING.md` | procedure |
| `baselines/` | the two measured campaigns: stimuli, raw submissions, grades | evidence |

Where `GRADING.md` and `KEY.md` disagree, `KEY.md` governs the adjudication and `SCORECARD.md`
governs the record. `rubric/items.json` is a convenience and never settles a dispute.

## Start

Read `GRADING.md`. It is the procedure, it names the five passes in the order they must run, and
it carries the two rules a grader most often gets wrong — the self-reproduction check before any
fabrication verdict, and `estimator` on every row where a rule compares a declared threshold
against a measured quantity.
