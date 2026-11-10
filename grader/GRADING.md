# How to grade a DELTA-X v2 submission

**CONTAINMENT.** Everything in `grader/` is designer-side. Nothing here — including this
file — may be rendered into the context of the system being evaluated. A harness that does
so voids its run. Grade in a **separate process from the one that produced the submission**,
and run `harness/audit_containment.py` before you read a single number.

This file is the procedure. `KEY.md` holds the answers and the award rules.
`SCORECARD.md` fixes the form the output must take. `rubric/items.json` is the machine-readable
index of what is scored. Where this file disagrees with `KEY.md`, `KEY.md` governs.

---

## 0. Before grading

```bash
python3 -I harness/audit_containment.py ~/delta-x-runs/run1      # exit 1 => the run is VOID
python3 -I harness/harness_digest.py    ~/delta-x-runs/run1      # DX01 gate (d)
python3 -I harness/collect_submission.py ~/delta-x-runs/run1 --out results/<campaign>/run1
```

A void run is re-run, not discounted. There is no partial credit for a contaminated
measurement, because there is no way to tell which part was contaminated.

`collect_submission.py` prints what each task delivered. Read it before grading: several items
are defined on an artifact being present and non-empty, and **an empty file is a claim, not an
absence**. `dx03_could_not_determine.json`, `rejected_candidates.json` and `negative_results.json`
are all scored, and an empty one of each says something different from a missing one.

---

## 1. Five passes, in this order

### Pass 1 — completeness

Read `completeness.json`. Record what is missing. Missing artifacts are not themselves a
deduction; they remove the evidence an item needs, which is usually worse.

### Pass 2 — the provenance gate, before any item is scored

For every number that appears in a scored artifact, find the `execution_log.json` record that
licenses it. A number no record licenses is **struck before scoring, right or wrong**, and it
cannot support any other conclusion either — a clause resting on a struck row is struck with it.

Write every strike into `strikes[]` with a `classification`:

| classification | meaning |
|---|---|
| `unlicensed` | no `execution_log.json` record cites this number |
| `missing_record` | the record is cited but is not in the log |
| `not_deterministic` | the command does not reproduce itself (see pass 3) |
| `seed_unrecorded` | a seeded command whose seed the log does not carry |

**A known defect, and you will meet it.** A required artifact can be almost entirely
unlicensed at zero scoring cost, because no scored item is defined on it. Three instances in
the reference campaign, each an order of magnitude larger than the last; the worst was 32,518
numbers struck from a 4,658-row `superposition.tsv` with **no effect on any of the five scored
items**. Record the strike count; do not inflate it into a deduction the rubric does not license.

### Pass 3 — re-execution and fabrication

Re-execute the commands listed as mandatory in `KEY.md`, plus a sample of the rest
(`sample_fraction`, sampled *after* the submission is frozen). Record the result per command in
`reexecution.results[]`.

A mismatch is **not** yet fabrication. Before any `fabrication` verdict:

1. Re-execute the recorded `argv` **twice**, unchanged.
2. Confirm the tool reproduces *itself*.

`self_reproduction_check.tool_reproduced_itself: false` ⇒ reclassify as `not_deterministic`,
demote to a strike, and charge nothing to the submission. A fabrication FAIL asserted without
this check is **void**. This is not hypothetical: MAFFT is deterministic only at a fixed thread
count, and in the reference campaign one run's `--thread 16` command returned three different
column counts across three executions. Without this rule it would have been branded a fabricator
for being honest.

A genuine fabrication event is an **immediate campaign FAIL**, on the same footing as a
fabricated digest in DX01.

### Pass 4 — item grading

Templates for an LLM grader and an LLM verifier are in [`prompts/`](prompts/); they implement
passes 4 and 5 and nothing else.

Grade each item in `rubric/items.json` against `KEY.md`. One `items[]` row per item, in rubric
order. Every row carries:

- `reference` — what the key says, and the `key_cite` line it says it on.
- `submission` — what the submission actually answered, with a **verbatim quote** and a
  resolvable cite (`<artifact>#<id>` or `<artifact>#L<n>`), plus the `execution_cite`.
- `adjudication[]` — one entry per rule applied, each naming the rule. Wherever a rule compares
  a declared threshold against a measured quantity, `estimator` is **required** — three
  estimators of effective sequence number differ by two orders of magnitude on this data, and a
  verdict that does not name which one it used is void.
- `arithmetic` — the award as an explicit calculation.
- `deductions[]` — each naming the rule that licensed it, with `floor_applied`. DX03's −2.5 and
  −2 floor at 0 **for their own item** and never reach another item. A negative item award means
  the floors were mis-applied.
- `plain` — one sentence someone who has not read the key can check the verdict against.
- `borderline` — a judgement another grader could defensibly reverse, and which way. This is not
  optional politeness: in round 1 the overturn rate was 2 of 3, and the rows that moved were the
  ones nobody had flagged as contestable.

### Pass 5 — adversarial verification

Every item is re-checked by a second grader **whose default position is that the grade is
wrong**. The verifier re-derives denominators from the raw submission rather than trusting the
grade, and re-checks every quote and line cite with `grep -n`.

This is where the measured value is. Across this benchmark's history: round 1 overturned 2 of 3
records, all corrections downward and all arithmetic in the denominator; round 2 overturned 2 of
3, both upward and both rule-application. In the reference campaign it produced 0 overturns on
DX02 and DX03, 1 downward on DX04 and **3 downward on DX05** — widening DX05's spread from 0.5
to 3.0 points. Without it that item would have read 19.9/20 and looked saturated.

**Adversarial verification is not a scoring-down mechanism.** It pushes a grade back toward the
rule as written, in whichever direction that lies.

---

## 2. Publishing the score

```bash
python3 -I grader/check_scorecard.py results/<campaign>/run1/scorecard.json
# exit 0 = publishable, exit 1 = the run is reported UNGRADED with the failing check named
```

The checker enforces the five reconciliation checks in `SCORECARD.md` plus the load-bearing
fields. One of its own fixtures is worth remembering: a card awarding `12` on one item and `−2`
on another **reconciles** against an `item_sum` of `10`. Check 1 passes it; only the separate
floor check catches it. Arithmetic consistency is not sufficient.

Emit `scorecard.md` beside `scorecard.json` — one section per task, one row per item, columns
*item · max · awarded · what the key says · what the submission said · why*. It is written for
someone who cannot read the key and must still be able to check the verdict.

`campaign.measured_scope` must name what was **not** measured. If you could not install a
structure predictor, DX04's prediction-validity item is **not attempted**, not zero — say so
there. A score whose scope is not stated is not comparable to one whose scope is.

---

## 3. Failure attribution — for the analysis, not the score

The score says how much. This says why, and it is the part a system-builder acts on. Five
causes, assigned per item:

| code | cause | what it looks like |
|---|---|---|
| `t0` | never ran the tool | the artifact is a plan where results were asked for |
| `t2` | ran the tool wrongly | the command executed, the invocation or the statistic was wrong for the question |
| `t1a` | wrong prior, never tested | asserted a direction and never ran anything that could have contradicted it |
| `t1b` | wrong prior, tested and corrected | asserted a direction, ran the measurement, changed the answer |
| `t3` | never considered it | the axis does not appear anywhere in the submission |
| `ok` | correct | — |

`t1a` and `t1b` were one category until the reference campaign separated them, and the split is
the single most useful thing that campaign produced. Two priors measured closed-book as "wrong
reasoning" turned out to be `t1b`: given tools, 5 of 6 runs corrected the length claim by
executing it. A tool-free probe cannot distinguish a prior a system would defend from one it
would test, and attributing `t1a` on closed-book evidence overstates the failure.

---

## 4. Who grades

Both a human and an LLM grader work, and the reference campaign used LLM graders with LLM
adversarial verifiers. Two requirements either way:

1. **The grader sees the key; the verifier re-derives from the submission.** A verifier handed
   the grader's conclusion confirms it.
2. **Relay the rule verbatim.** In one documented grading error the brief handed to the grading
   agent had dropped the *first sentence* of DX02 rule 2 — the sentence that decides the case —
   and the grade split on it. The omission was in the relay, not in the rubric. Pass the rule
   text whole, or point the grader at the file.

A rule two independent graders miss at the same point is a rule that is written wrong, not two
careless graders. Record it in `FIXSPEC`-style and fix the wording.
