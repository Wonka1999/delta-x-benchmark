# Reader pages

Self-contained HTML. No build step, no CDN, no network. Open in a browser.

**CONTAINMENT.** All four contain answers and are explicitly unsafe to feed to a system under
evaluation.

| page | audience |
|---|---|
| `07_for_ml_readers.zh.html` | **start here.** One section per task, each with its brief, a formalised problem statement, the reference answer, the measured baseline, every scored item as a card, and the defects that task exposed. Three levels of depth behind a per-panel button — plain / standard / detailed — defaulting to plain. Written for an ML audience with no biology. Chinese. **It predates the first complete campaign**; a dated banner at the top gives the measured result and names the two of its own judgements the measurement contradicted. Its per-section "projection / not measured" markers mean *as of writing* -- `docs/RESULTS.md` is current. |
| `06_case_walkthrough.zh.html` | the v1.1 case carried end to end in one pass: the brief, the ten task questions, the input/withholding table, the two scoring axes, the anchor table, per-claim provenance. Chinese. |
| `05_worked_example.html` | one submission walked through item-level scoring. English. |
| `04_tdt_polmu_delta_x.html` | the v1.1 design document. English. |

`01_paper_reproduction.html`, `02_benchmark_modules.html` and `03_mechanism_discovery.html` are
three earlier benchmark designs from the same project — paper reproduction, nine modular
BixBench3-style tasks, and an autonomous mechanism-discovery benchmark. They are shipped because
the four pages above link to them and the set only works offline when it stays together. They
are background, not part of DELTA-X.

Pages 04–06 describe **v1.1**, a ten-task, two-axis earlier design that this release supersedes.
They are kept because the reasoning that produced v2 is in them, and because v1.1's measured
results are what fixed v2's scoring granularity. Do not score anything against them.
