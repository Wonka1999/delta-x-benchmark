# BASELINE-v3-tooled — the first complete DELTA-X v2 campaign (2026-11-10)

**CONTAINMENT.** Designer-side. Rendering any of this into an evaluated agent's context voids
the run.

**Status: COMPLETE.** All five tasks, five scored runs, graded and adversarially verified.
This is the first complete DELTA-X v2 campaign ever measured. All five `scorecards/*.json`
pass `grader/check_scorecard.py`.

**Aborted attempt, recorded because it is a measurement condition and not an agent failure.**
The first DX05 attempt (2026-11-09 23:09–23:10) returned `is_error: true` on all five runs
after two turns each, with the result string *"You've hit your org's monthly spend limit"*.
No DX05 artifact was produced by any run. The first DX04 grading workflow died in the same
minute for the same reason, with zero result lines in its journal. **Neither event is evidence
about any agent**: nothing was attempted and nothing failed on merit. Both were re-launched
after the limit reset on 2026-11-10; the session ids were preserved, so DX05 resumes the same
sessions and the pipeline's "no new data after DX04" condition still holds. Protocol in `PROTOCOL.md`; served stimulus digests in `STIMULUS.txt`;
per-run scorecards in `scorecards/`, all six passing `grader/check_scorecard.py`.

## The campaign — n = 5, all 100 points measured

| run | DX01 | DX02 / 10 | DX03 / 35 | DX04 / 35 | DX05 / 20 | **total / 100** |
|---|---|---|---|---|---|---|
| run1 | PASS | 8.5 | 35 | 35 | 19.5 | **98.0** |
| run2 | PASS | 8.5 | 31 | 35 | 18.5 | **93.0** |
| run3 | PASS | 8.0 | 35 | 33 | 17.0 | **93.0** |
| run4 | PASS | 10.0 | 35 | 33 | 19.5 | **97.5** |
| run5 | PASS | 10.0 | 35 | 32 | 20.0 | **97.0** |

| item | mean | range | as % of its weight |
|---|---|---|---|
| DX02 | 9.00 / 10 | 2.0 | 20.0 % |
| DX03 | 34.20 / 35 | 4.0 | 11.4 % |
| DX04 | 33.60 / 35 | 3.0 | 8.6 % |
| DX05 | 18.90 / 20 | 3.0 | 15.0 % |
| **campaign** | **95.70 / 100** | **5.0** | **5.0 %** |

`dx02b_direction` (report-only, never added): 0.600 / 0.643 / 0.600 / 0.583 / 0.750, range 0.167.

## The result: the benchmark is saturated

**A tooled Opus 5 scores a mean of 95.7 / 100 with a range of 5 points.** Every task is at or
near ceiling. This is the same diagnosis that took DX02 from 20 points to 10 — a low-variance
item is a gate, not a ruler — now applying to **the whole instrument**.

The mechanism is visible in the submissions and it is **rubric publication**, not capability.
In the preserved v2 records all of DX02's discrimination came from rule 2; here **0 of 14
programs fail rule 2**, because the plans carry fields literally named `rule_2_compliance` that
name pLDDT, PAE, own E-value and own TM-score in order to disclaim them. DX03's −2 granularity
penalty fires in **0 of 5**, because each submission's own `granularity_report` floor sits below
its own nomination width. The agents read §4 and engineer against it.

**Both of the measured "wrong approach" failures were corrected by execution.**
- The length claim: untooled 3/3 asserted "longer in TdT" at confidence up to 0.80; tooled
  **5/5** answered *composition, not length*, for the right reason — median difference 0, the
  difference placed in variance and chemical composition, statistic attached.
- The deviation trap: DX02B recorded **5/5** pre-committing to rank the element by
  cross-subfamily deviation. In execution **5/5** used a non-deviation statistic and earned
  15/15. The key sanctions **two** statistics for that item — the order/disorder census *and*
  steric occlusion against bound DNA — and every run used the second.

**This is a negative result for DX02B, and it is the useful kind.** Its premise was that a
wrong approach predicts a wrong execution. On n = 5 it predicted neither failure. Under the
promotion rule pre-registered in `KEY-DX02B.md` §5 this is the "report-only for one more
campaign, then retire" branch. It also weakens the `wrong reasoning` category of the failure
attribution published on page 07, which must be split into *wrong prior never tested* and
*wrong prior tested and corrected*.

## Where the remaining separation actually comes from

Not from the capability the tasks name. The five point spread is carried by:
- **run2 DX03.I1 (8/12)** — a self-inflicted endpoint error: its declared rule is "contiguous
  columns above the 95th background percentile (0.4003)" but its nominated C-terminal residue
  412 scores **0.0679**, below even the background mean; the contiguous run does not exist.
- **DX04.I5** (4 points, awarded 4/4/2/2/1) — the applicability boundary of predicted
  coordinates, the only DX04 item that moved.
- **DX05.I2** (6 points, awarded 6/4.5/3/6/6) — **run2 and run3 declared polarity with
  `"method": "none"`**, no outgroup and no support value, where §5 requires it be *earned* from
  an outgroup. run3 had the two usable outgroups in its own `refs.fasta` and, in its own words,
  "deliberately left [them] out of every alignment".

Adversarial verification: **0 overturns** on DX02 and on DX03 totals; **1 downward** on DX04
plus one run graded fresh; **3 downward** on DX05. Verification widened the DX05 spread from
0.5 to 3.0 points — without it the cohort would have read 19.9 / 20.

## Integrity

- **Fabrication: 0** across all six runs and all five tasks.
- **No scored number was struck anywhere.**
- **Containment: clean on all five runs, every stage.**
- The **MAFFT self-reproduction rule** fired for real: run0's recorded
  `mafft --auto --anysymbol --thread 16`, re-run twice, gave three distinct outputs
  (1745 / 1708 / 1717 columns). Classified `not_deterministic`; **no fabrication verdict**.

## Open defects this campaign exposed

1. **A required artifact can be almost entirely unlicensed at zero scoring cost.** Three
   instances now, growing by an order of magnitude each time: run0 DX03 ~2,132 numbers struck,
   run1 DX03 ~4,622, run1 DX04 **32,518** — the whole of `superposition.tsv`, 4,658 mandatory
   rows with no provenance column at all. No award anywhere depended on them. Either cite-check
   these artifacts or stop requiring them.
2. **The DX01 canonicalisation recipe is not comparable across submissions** — three JSON
   paths, a 3/3 split on hash order, six different digests over byte-identical inputs.
3. **The instrument needs re-cutting, not re-weighting.** Moving weight between items that are
   all at ceiling does not create discrimination. What produced separation here was a published
   rule the agents could optimise against; what the benchmark measured in v2 — the rule-2 trap,
   the deviation trap, the length trap — is now absorbed. The next version has to withhold the
   adjudication rules from the brief, or change what is asked.

## Appendix — the 45-point interim reading (superseded by the table above)

**Both measured tasks are at or near ceiling.** This is the same diagnosis that took DX02 from
20 to 10: a low-variance item is a gate, not a ruler. DX03's 35 points had never been measured
and its weight rested on this key's own analysis; measured, it returns **4 of 5 at full marks**.

**The mechanism is visible and it is rubric publication.** In the preserved v2 records all of
DX02's discrimination came from rule 2; here **0 of 14 programs fail rule 2**, because the plans
carry fields named `rule_2_compliance` that name pLDDT, PAE, own E-value and own TM-score in
order to disclaim them. DX03 is the same shape: the −2 granularity penalty fires in **0 of 5**
because each submission's own `granularity_report` floor (9 residues) sits below its nomination
width (20–35). These runs were written against a published rubric and engineer against it. The
jump from 3.0 / 1.0 / 5.0 measures **rule-awareness as much as capability**.

**The only real separation is run2's DX03.I1 (8 / 12)**, and it is self-inflicted: its declared
rule is "contiguous columns above the 95th background percentile (0.4003)", but its nominated
C-terminal residue 412 scores **0.0679**, below even the background mean 0.2615 — the contiguous
run does not exist, and the endpoint misses ±6 by 12–16 residues in all four comparisons.

**The confidently-wrong length prior is corrected by execution, 5/5.** The untooled baseline
asserted "longer in TdT" 3/3 at confidence up to 0.80. All five tooled runs answered
**composition, not length**, for the right reason — median difference 0 with the difference
placed in variance and chemical composition, statistic attached (SD ratio 8.05, variance ratio
63.5 at Levene p = 2.45e-33, hydrophobic Cliff's δ = 0.964). **This contradicts the failure
attribution published on page 07**, which classified the length claim as wrong reasoning and
asserted that tools would only reach the wrong answer faster. That attribution must be split
into *wrong prior that is never tested* and *wrong prior that is tested and corrected*.

**But the prior itself is still there, and DX02B caught it.** 5 of 5 pre-committed to the
element ranking top by cross-subfamily deviation — which the measured same-protein null defeats
(8.56 Å within one mouse TdT against a cross-family maximum of 7.30 Å). That is the DX04
15-point trap, pre-registered by every run, before DX04 ran. Whether it materialises is exactly
what the pending DX04 grading settles, and it is the first real test of DX02B's premise.

## Integrity results

- **Fabrication: 0 of 6** on DX01; **0 of 5** on DX03. No fabrication event anywhere.
- **No scored number was struck** in any of the five DX03 submissions. run2 carries 2 dangling
  citations (`CMD_A1_mafft_linsi`; no log record bears `--localpair`) costing 7 unscored numbers.
- **Containment: clean on all five**, every stage, by `audit.sh`.
- **The MAFFT self-reproduction rule fired for real.** run0's recorded
  `mafft --auto --anysymbol --thread 16` re-run twice produced three distinct outputs
  (1745 / 1708 / 1717 columns, three SHA-256s). Classified `not_deterministic`; **no fabrication
  verdict**. The 2026-11-08 fix earned its place on the first tooled submission ever graded.
- **Adversarial verification overturned nothing** on DX02 (0 of 6) or on DX03 totals (0 of 5) —
  the first clean rounds after two that each overturned 2 of 3. It did correct run0's provenance
  accounting from "4 numbers struck" to **~2,132 across 4 artifacts**, and run1's to ~4,622,
  without moving an award.

## Defects this run exposed, still open

1. **A required artifact can be almost entirely unlicensed at zero cost.** `column_scores.tsv`
   is mandatory, and in run0 all 530 rows cite a record id that does not exist. Nothing in the
   rubric touches it, because the 12-point item only needs the nomination's own statistics.
2. **The DX01 canonicalisation recipe is not comparable across submissions** — three JSON paths,
   a 3/3 split on hash order, six different digests over byte-identical inputs. Recorded in
   `KEY.md`; the recipe must be fixed by the brief.
3. **DX02 and DX03 need re-weighting on this evidence**, by the same rule that demoted DX02
   once already. Do not act on it before DX04 and DX05 are graded — the 45-point scope is not
   the campaign.
