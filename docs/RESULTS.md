# Results so far

**CONTAINMENT.** Designer-side. Do not render into an evaluated system's context.

Two campaigns have been measured and both ship with their raw records. Every score below is
backed by a per-item `scorecard.json` that passes `grader/check_scorecard.py`; the totals are
recomputed from the rows by `analysis/aggregate.py` rather than read from the stored total.

---

## BASELINE-v3-tooled — the first complete campaign (2026-11-10)

Claude Opus 5, through the Claude Code headless CLI, real shell on the execution tasks, five
scored runs plus one pilot. All 100 points measured. Raw records, protocol and served stimulus
digests: [`grader/baselines/BASELINE-v3-tooled/`](../grader/baselines/BASELINE-v3-tooled/).

| run | DX01 | DX02 / 10 | DX03 / 35 | DX04 / 35 | DX05 / 20 | **total / 100** |
|---|---|---|---|---|---|---|
| run1 | PASS | 8.5 | 35 | 35 | 19.5 | **98.0** |
| run2 | PASS | 8.5 | 31 | 35 | 18.5 | **93.0** |
| run3 | PASS | 8.0 | 35 | 33 | 17.0 | **93.0** |
| run4 | PASS | 10.0 | 35 | 33 | 19.5 | **97.5** |
| run5 | PASS | 10.0 | 35 | 32 | 20.0 | **97.0** |

**Mean 95.70 / 100. Range 5.0.** Median 97.0, sample sd 2.49.

`dx02b_direction`, reported beside and never added: 0.600 / 0.643 / 0.600 / 0.583 / 0.750.

### The finding: the benchmark is saturated

Across the five runs, **40 of the 100 points carry any variance at all**. The other 60 sit at
ceiling in every run.

| item | max | mean | range | discrimination (range/max) |
|---|---|---|---|---|
| DX04.I5 — prediction-validity boundary | 4 | 2.60 | 3.0 | 0.75 |
| DX05.I2 — polarity with outgroup | 6 | 5.10 | 3.0 | 0.50 |
| DX03.I1 — region nomination | 12 | 11.33 | 4.0 | 0.33 |
| DX02.I1 — per-tool adequacy | 10 | 9.17 | 2.0 | 0.20 |
| DX05.I1 — bounded mechanism statement | 8 | 7.80 | 0.5 | 0.06 |
| DX03.I2, DX03.I3, DX03.I4 | 6, 10, 7 | max | 0 | **at ceiling** |
| DX04.I1, DX04.I2, DX04.I3, DX04.I4 | 15, 4, 4, 8 | max | 0 | **at ceiling** |
| DX05.I3 | 6 | max | 0 | **at ceiling** |

A zero-variance item is a gate, not a ruler. That is the same diagnosis that took DX02 from 20
points to 10 — now applying to the whole instrument.

### The mechanism is rubric publication, not capability

It is visible in the submissions:

- In the preserved tool-free records, **all** of DX02's discrimination came from rule 2
  (adequacy checks must be input-side). Here **0 of 14 proposed programs fail rule 2** — the
  plans carry fields literally named `rule_2_compliance`, which name pLDDT, PAE, the step's own
  E-value and its own TM-score in order to disclaim them one by one.
- DX03's −2 granularity penalty fired **0 times in 5 runs**, because every submission set its
  own `granularity_report` floor below its own nomination width.

The agents read section 4 of the brief and engineer against it. **Publishing the rubric with the
task is not free**, and this is the number that says so.

### Two negative results that contradicted the designers

Both were "wrong reasoning" failures identified from tool-free probes. Given tools, both were
corrected by execution.

- **The length prior.** Untooled, 3 of 3 asserted the element is longer in one subfamily, at
  confidence up to 0.80. Tooled, **5 of 5** answered *composition, not length* — for the right
  reason, with the statistic attached and a median difference of 0.
- **The deviation trap.** DX02B recorded **5 of 5** pre-committing to rank the element by
  cross-subfamily deviation, which is the trap the task is built around. In execution **5 of 5**
  used a non-deviation statistic and earned 15/15.

Consequence for the analysis layer: the failure cause `wrong reasoning` had to be split into
**wrong prior never tested** and **wrong prior tested and corrected**. A tool-free probe cannot
tell them apart, and attributing the first on closed-book evidence overstates the failure. The
split is in [`grader/GRADING.md`](../grader/GRADING.md) §3.

**DX02B's own prediction failed**, and that is the useful part. Its premise was that a wrong
pre-commitment predicts a wrong execution. On n=5 it mispredicted twice. Under its own
pre-registered promotion rule it stays weight-0 and goes on the "report for one more campaign,
then retire" branch.

### Where the 5 points of spread actually came from

Not from the capability each task names.

- **run2, DX03.I1 (8/12)** — a self-inflicted endpoint error. Its own rule was "contiguous
  positions whose per-column effect exceeds the background 95th percentile of 0.4003"; the
  residue it nominated as the endpoint scores **0.0679**, below its own background mean.
- **DX04.I5** (4/4/2/2/1) — the only DX04 item that moved.
- **DX05.I2** (6/4.5/3/6/6) — two runs declared polarity with `"method": "none"`: no outgroup,
  no support value, where the brief requires polarity to be earned from an outgroup. One of
  them had two usable outgroups in its own `refs.fasta` and, in its own words, *"deliberately
  left [them] out of every alignment."*

### Adversarial verification earned its cost

0 overturns on DX02 and on DX03's total, 1 downward on DX04, **3 downward on DX05**. It widened
DX05's spread from 0.5 to 3.0 points. Without it that item would have read 19.9/20 and looked
saturated like the rest.

### Integrity

0 fabrication events across five runs and five tasks. 0 containment breaches. No scored number
struck. The self-reproduction rule fired once and worked as designed: a MAFFT command at
`--thread 16` returned three different column counts over three executions, was classified
`not_deterministic`, and **nothing was charged to the submission**.

---

## BASELINE-v2-clean — tool-free, DX01 and DX02 only (2026-11-08)

Three runs, every tool blocked. It measured DX01 and DX02 and **nothing else** — DX03, DX04 and
DX05 require execution, so 90 of the 100 points were never attempted. Its third stage was a
closed-book saturation probe, not a DX03 submission, and must never be read as one.

Re-graded under the current DX02 rules 1–4: **3.0 / 1.0 / 5.0**, range 4.0/10, against the old
20-point rubric's range of 0.4/20 — and the rank order **inverts**. That re-grade is an
arithmetic diagnostic, not a baseline: those three submissions were written against a rubric
whose rules 1–4 did not yet exist. [`REGRADE-rules1-4.md`](../grader/baselines/BASELINE-v2-clean/REGRADE-rules1-4.md).

---

## Known defects of these measurements

Stated here because a score whose defects are not published is not comparable to one whose are.

1. **No re-execution sampling was performed.** All six scorecards carry
   `reexecution.mandatory_commands: []` and `sample_fraction: 0.0`. The fabrication gate in
   `GRADING.md` pass 3 was *specified* and the self-reproduction rule did fire once, but the
   systematic sample the rule assumes did not run. A future campaign must close this.
2. **A required artifact can be almost entirely unlicensed at zero scoring cost.** Three
   instances, each an order of magnitude larger than the last; the worst struck 32,518 numbers
   from a 4,658-row `superposition.tsv` with no effect on any scored item. Either cite-check
   these artifacts or stop requiring them.
3. **DX01's canonicalisation recipe is not comparable across runs.** Six runs put the committed
   file list at three different JSON paths and split 3/3 on hash order, producing six different
   digests from byte-identical inputs. That is a defect in DX01's wording. `harness_digest.py`
   records the order it used in `order_note` so the defect stays visible.
4. **Metadata contradictions inside the published scorecards**, found by `aggregate.py` and left
   uncorrected so the record stands as graded: the DX02 rubric row carries four different
   `item_id` spellings across six files; `campaign.delta_over_prior` says "DX05 not run" in all
   five runs whose DX05 items are present and scored; run0's `measured_scope` misdescribes the
   other runs; `reported_beside` is `null` in one file and a list in the rest; and run1's DX02
   row has text fields clipped mid-token, so the record of *how* 8.5 was reached is truncated.
   `aggregate.py` reports each rather than papering over it.
5. **n = 5 on one model.** Nothing here says anything about any other system, and one run
   settles nothing: the quantity that decides whether an item discriminates is the range.

## What the next version needs

Not re-weighting. Every item is at or near ceiling, so there is no weight to move from a
discriminating item to a non-discriminating one — there are barely any discriminating items.
The instrument needs **re-cutting**, or the adjudication moved out of the brief. Those are
different fixes and only one of them can be tested cheaply: withhold section 4 and re-measure.
