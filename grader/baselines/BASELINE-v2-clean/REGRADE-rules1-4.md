# DX02 re-grade under rules 1–4 — arithmetic diagnostic, 2026-11-09

**CONTAINMENT.** Designer-side. Nothing here may be rendered into an evaluated agent's context.

**What this is.** The three preserved BASELINE-v2-clean DX02 records (`out/run{1,2,3}_s2.md`),
re-graded under the **current** 10-point rubric (`agent_facing/DX02.md` §4, rules 1–4). This
closes the **STILL OPEN** blocker recorded in `KEY.md` under `## DX02 — method design`.

**What this is not.** A baseline. All three records were written against the **old 20-point
rubric**, in which the adequacy item was worth 8 and rules 1–4 did not exist. They never had the
opportunity to optimise against the rules they are graded under here. A published baseline still
requires the n ≥ 5 clean-room re-run against the current briefs.

**Method.** One grading agent per record, each then attacked by one adversarial verifier whose
default position was that the grade is wrong. Verifiers re-derived the denominator from the raw
`exact_invocation` fields themselves and checked every quote and line cite rather than trusting
the grade.

## Result

| run | programs proposed | counted = max(n,3) | qualifying | arithmetic | award | old 8-pt item |
|---|---|---|---|---|---|---|
| run1 | 10 | 10 | 3 | `10 × 3/10` | **3.0** | 6.0 / 8 |
| run2 | 7 | 7 | 1 | `10 × 1/7 = 1.43 → ` | **1.0** | 6.4 / 8 |
| run3 | 15 | 15 | 8 | `10 × 8/15 = 5.33 → ` | **5.0** | 6.0 / 8 |

**Range 4.0 / 10 (40 %)**, against the old rubric's **0.4 / 20 (2 %)**. Mean 3.0. The rank order
**inverts**: run2 was the highest-scoring record under the old rubric (18.4 total, 6.4/8 on the
adequacy item) and is the lowest under the new one.

**Where the discrimination comes from — rule 2, not rule 1.** run3 proposes the most programs
(15, the largest denominator) and scores highest; run2 proposes the fewest (7) and scores lowest,
because 3 of its 7 gate a program on its own output. **The floor of three never binds** — all
three runs exceed it by a wide margin. The conclusion the floor was introduced to force
("proposing one safe program must not win") is now measured rather than argued: breadth neither
helps nor hurts, and input-side discipline is the whole signal.

## Per-program adjudication

Qualifying = has an adequacy check **and** passes rules 2, 3 and 4.

### run1 — 3 of 10 qualify → 3.0

| binary | step | rules | verdict |
|---|---|---|---|
| `mafft` | S1 | **r2 FAIL** | gated on a column-reliability score of its own alignment — the rubric's literal zero |
| `hmmbuild` | S2 | r2 ✓ r3 ✓ **r4 ✓** | **qualifies** *(corrected on verification — see below)* |
| `hmmlogo` | S2 | r2 ✓ r3 ✓ **r4 ✓** | **qualifies** *(same correction; shares S2's check)* |
| `esl-alistat` | S3 | **r2 FAIL** | check evaluated per candidate indel block; the blocks are S3's own output |
| `esl-alimask` | S3 | **r2 FAIL** | identical to `esl-alistat` |
| `ccmpred` | S4 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — Meff/L floor, measured with `hhfilter` (an independent instrument), page-level locator |
| `hhfilter` | S4 | — | named in an `exact_invocation`, carries no adequacy check: counts in the denominator, qualifies for nothing (rule 1) |
| `colabfold_batch` | S5 | **r2 FAIL** | gated on its own pLDDT and PAE — the rubric's canonical zero |
| `TMalign` | S5 | **r2 FAIL** | gated on its own TM-score, which is also the step's reported statistic |
| `hmmscan` | S6 | **r2 FAIL** | the positive control is emitted by the same `hmmscan` run it gates |

**Verification overturned this grade, 1.0 → 3.0.** The first pass adjudicated the
`eff_nseq ≥ 25` floor **against the estimator it is written on** — `hmmbuild eff_nseq`, measured
0.899 / 1.302, so it fires — thereby avoiding the error this key itself made before 2026-11-08.
It then **failed to apply rule 4's scope clause**. run1's floor is measured-and-reported in both
places it appears: the abandon condition ends *"reporting the `eff_nseq` number as the reason"*
(`run1_s2.md:74`) and falls back to region-level aggregate divergence, and
`run1_s2.md:278` makes the measured `eff_nseq` the headline negative result for S2 while
downgrading its declared granularity. That is degrade-and-report, which DX02 §5 designates a
**success**, not termination before data.

### run2 — 1 of 7 qualifies → 1.0 (upheld)

| binary | step | rules | verdict |
|---|---|---|---|
| `mafft` | S1 | **r2 FAIL** | gated on its own column-reliability score |
| `hmmbuild` | S2, S3 | **r3 FAIL** | `eff_nseq ≥ 25` attributed to a HMMER3 user guide that does not state it |
| `hmmalign` | S2 | **r3 FAIL** | same unsupported attribution |
| `esl-alistat` | S2, S3 | **r3 FAIL** | same, inherited; the binary spans both steps and is counted once |
| `hmmemit` | S3 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — input-side Neff floor, sourced by its **own shown derivation** (`SE = √(p(1−p)/Neff)`; at p = 0.5, Neff = 60 → SE 0.065, so a 0.25 shift is ≈ 3.9 SE) |
| `hmmscan` | S5 | **r2 FAIL** | gated on its own E-value |
| `TM-align` | S7 | **r2 FAIL** | gated on its own TM-score |

**Verification upheld 1.0** and re-derived the denominator independently (7 unique binaries from
the seven `exact_invocation` fields; `mafft` named three times in one string, correctly counted
once). It corrected two things that do not move the award: the grade mis-cited run2's old
adequacy score as 6.0/8 at `KEY.md:563` (correct: **6.4/8**, `KEY.md:564`; :563 is the total
row), and it closed a claimed +1.5 upside on `mafft` that the submission itself forecloses by
naming mean A-vs-B pairwise identity as S1's **own statistic**.

**A rule-3 note worth keeping.** `hmmemit` passes rule 3 on a *derivation it shows its working
for*, with no citation. That is correct under the rule as written — "a number plus a locator a
grader can check" — and the locator here is the arithmetic itself. Three programs in the same
submission fail rule 3 for the opposite reason: a citation to a document that does not state the
number. **A shown derivation is stronger than an unverified attribution**, and the rubric should
keep reading it that way.

### run3 — 8 of 15 qualify → 5.0

| binary | step | rules | verdict |
|---|---|---|---|
| `seqkit` | S0 | **r2 ✓** | **qualifies** *(corrected on verification)* |
| `cd-hit` | S0 | **r2 ✓** | **qualifies** *(same correction)* |
| `mafft` | S1 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — published identity floor, fires on its own, demotes rather than terminates |
| `guidance.pl` | S1 | **r2 FAIL** | gated on its own column-reliability output |
| `hmmsearch` | S2 | **r2 FAIL** | adequacy quantity is the output of the step it gates |
| `esl-weight` | S3 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — derived depth floor on Henikoff per-column Neff, the one estimator measured to **pass in 100 % of core columns** |
| `hmmscan` | S4 | **r2 FAIL** | self-gated on the search's own significance statistics |
| `hmmbuild` | S5 | **r3 FAIL** | `NEFF ≥ 10` attributed to two papers that do not state it, and the attribution misdescribes the statistic's scale |
| `hhmake` | S5 | **r3 FAIL** | same unsupported attribution |
| `hhalign` | S5 | **r3 FAIL** | same; the 95 % figure cites no openable locator |
| `group_sim_sdp.py` | S6 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — input-side, independently gating, correctly derived depth floor |
| `ccmpred` | S7 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — its firing abandons the one method measured as genuinely non-functional here |
| `gremlin_cpp` | S7 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — second binary in the same `exact_invocation`, identical check, counted separately under rule 1 |
| `colabfold_batch` | S8 | **r2 FAIL** | gated on its own pLDDT |
| `USalign` | S8 | r2 ✓ r3 ✓ r4 ✓ | **qualifies** — gated on the confidence of the models it is *given*, which is input-side for an aligner |

**Verification overturned this grade, 4.0 → 5.0.** The first pass ran **two mutually exclusive
readings of rule 2** and never reconciled them: a step-relative reading that passed `esl-weight`
("an alignment-depth property computable before that statistic exists") and, three programs
earlier, a program-relative reading that failed `seqkit` and `cd-hit` ("the block is its product,
not its gate"). The lenient reading is the one the grade states as its governing principle three
separate times. What enabled the slip: **the rubric relayed to the grading agent omitted rule 2's
first sentence** — *"A plan step whose adequacy check cannot be computed before the main analysis
is not an adequacy check"* — and that sentence is the one that decides S0. The omission was in
the brief given to the grader, not in `DX02.md`.

## Two findings about the rules, not about the submissions

**1. Rule 4's scope clause is mis-read even when it is in front of the grader.** This key
mis-read it once (the withdrawn rule-4 basis paragraph, corrected 2026-11-08: one estimator's
measured value applied to floors written on three). A fresh grading agent, with the scope clause
quoted verbatim in its instructions, mis-read it again at the same point — treating
measure-and-report as termination. **A rule two independent graders miss at the same point is a
rule that is written wrong.** The current form is *rule, then exception*, and the exception is
the common case. It should be restructured as a leading branch: **first ask whether the declared
floor terminates the method or measures and reports it; only the former enters the deduction
test.** Restating it more loudly is not a fix.

**2. Rule 2 states two tests that can disagree.** Sentence one is a **computability** test
(computable before the main analysis); sentence two is an **authorship** test (the quantity is an
output of the step it gates). `seqkit`'s ambiguity fraction **passes** the first and **fails** the
second, and which one governs is worth 1.0 point on run3. The ambiguity is in `DX02.md` itself,
not only in the relayed copy. **One of the two must be named as the operative test, with the
other explicitly demoted to an illustration of it.** Until that is decided, graders will diverge
on any check whose quantity a tool computes about its own input.

## Provenance of this record

Grading and verification were performed by subagents reading only
`out/run{1,2,3}_s2.md`, `agent_facing/DX02.md` and the measured estimator table in `KEY.md`. Every
program row above traces to a verbatim quote with a line cite in the agent transcripts under
`subagents/workflows/wf_dfbfb186-4c5/`. Verifiers independently re-enumerated each denominator
from the raw `exact_invocation` fields and re-checked line cites with `grep -n`/`awk`; three
mis-cited line numbers and one mis-cited key line were found and are corrected above.

**Direction of corrections.** Round 1 (2026-11-08, old rubric): 2 of 3 records overturned, all
three corrections **downward**, all arithmetic in the denominator. Round 2 (this record): 2 of 3
overturned, both corrections **upward**, both rule-application rather than arithmetic.
Adversarial verification is not a scoring-down mechanism; it pushes a grade back toward the rule
as written.
