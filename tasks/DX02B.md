# DELTA-X v2 — DX02B: Expectation Pre-Commitment

**Capability under test** — whether the agent commits, before any data moves, to what its
own frozen plan should produce: the value each statistic must take under each branch, the
control that would retire the statistic it relies on most, and the resolution it expects to
earn.

## 1. Objective

Convert the frozen DX02 plan into numbered, confidence-bearing expectations that a later
stage can be held against — the value expected under each branch of each hypothesis, the
control that would invalidate the plan's single most load-bearing statistic, the spatial
resolution the plan expects to earn, the portability of each measurement, and the plan's
single most likely failure.

This stage is a **commitment, not an analysis**. Nothing is computed here.

## 2. Inputs

Served **after your DX02 plan is frozen and before any DX03 or DX04 input is released.**

**Given**
- Your own DX01 registration and your frozen DX02 artifacts — `method_plan.json`,
  `granularity_declaration.json`, `power_budget.json` — returned to you unchanged.
- The same inventory DX02 was given of what DX03/DX04 will supply: two subfamily FASTA sets
  of stated size (**322** and **165** sequences, species-unique, 451–616 aa), seven reference
  sequences, and the tool list (MAFFT, HMMER, a coevolution package, a structure predictor,
  a structural aligner).
- `ENVIRONMENT.md` — the absolute path and version of every tool named above.

**Withheld**
- All data. No sequences, structures, alignments, literature access or experimental
  measurements. Tool use is blocked at the harness level; the transcript is retained.
- The DX03 and DX04 briefs. You have nothing here that DX02 did not already have.

**The frozen plan stays frozen.** This task MUST NOT add, remove or edit a step of
`method_plan.json`. Where a commitment below is inconsistent with the frozen plan, the
inconsistency is recorded against the **commitment**, never against the plan. Versioned,
explicit amendments to your own prior are permitted and are recorded as new versions, never
as edits — the DX01 §5 rule is unchanged here.

## 3. Required outputs

**Record identity and citation.** Every `.json` artifact in this section is a top-level JSON
**array of records**. Every record carries an `id` field: a string unique within its file and
stable for the rest of the campaign. An artifact whose content is one object is written as a
one-element array carrying that object. Records in §3.1, §3.2 and §3.4 MUST cite the frozen
plan step they commit for, as `method_plan.json#<id>`; a citation that does not resolve to a
record in your frozen plan is treated as absent.

**Every commitment in this task MUST carry a number and a stated confidence in [0,1].** A
commitment carrying neither is not a commitment — see the strike rule in §4. `confidence` is
the probability you would assign to the commitment being borne out, on your own calibration;
it is recorded as stated and is never adjusted upward or downward by the grader.

1. `branch_expectations.json` — one record per statistic your frozen plan proposes to report:
   - `plan_step`, `statistic`, `units`.
   - `expected_if_true` — the value expected if the hypothesis that step discriminates holds.
     A point value or an interval with both ends stated. Where the statistic is a difference
     or a comparison between the two groups, state its **sign** as well as its magnitude.
   - `expected_if_false` — the value expected if it does not.
   - `confidence` — one for each of the two expectations.
   - `separation` — whether the two expected values can be told apart given the dispersion
     you expect the measurement to carry, stated as a number.

2. `invalidation_control.json` — exactly one record, for the single statistic in your frozen
   plan you would least want to lose:
   - `plan_step` and `statistic`, with one sentence on why this one is load-bearing.
   - `control_measurement` — the measurement that would show this statistic is dominated by
     something other than the difference you are chasing. It MUST be computable from the
     inputs DX03/DX04 have been declared to supply.
   - `stop_value` — the value of that control measurement, with units, at or beyond which you
     stop trusting the statistic. A direction with no number is not a stop value.
   - `confidence`.
   - `action_on_stop` — what you report if that value is reached.

3. `resolution_commitment.json` — exactly one record:
   - `finest_scale` — the finest spatial scale, **in residues**, at which you expect your
     evidence to support a claim, as a number.
   - `setting_measurement` — the measurement that will establish that floor, with the test and
     the null it will be compared against.
   - `confidence`.
   - `if_floor_is_coarser` — what you report if the measurement sets a floor coarser than the
     one committed here.

4. `portability_commitment.json` — one record per measurement in your frozen plan that could
   be run on either an experimentally determined input or a computationally predicted one:
   - `transfers` — `yes`, `no` or `unknown`, each with a `confidence`.
   - `deciding_evidence` — the observation that would settle it, and the value at which it
     settles each way.
   - A measurement marked `transfers: yes` with no deciding evidence named is recorded as
     unsupported.

5. `pre_mortem.json` — exactly one record. Assume the campaign is over and the plan failed:
   - `most_likely_reason` — **one** reason, not a list. A ranked list is adjudicated on its
     first entry only.
   - `first_observation` — the observation you expect to see first, the value that would show
     it, and the stage at which it would appear.
   - `confidence`.

## 4. Evaluation — 0 points in this campaign, reported beside the total

- **No weight.** This task carries no points in its first campaign. Its result is computed and
  reported **beside** your campaign score, never added to it — the same footing `delta_over_prior`
  has in DX01 §4.
- **Strike rule — a gate, not points.** A commitment carrying no number, or no confidence in
  [0,1], is struck before adjudication and reported as **absent**, not as wrong. An interval
  with both ends stated is a number; "higher", "substantial", "sufficient", "comparable" are
  not.
- **Direction and calibration are what is adjudicated.** Each surviving commitment is
  adjudicated `right_direction`, `undetermined` or `wrong` against measurements frozen before
  this task was written.
- **A confidently wrong commitment is scored as an error, not merely as unrewarded.**
  A commitment adjudicated `wrong` at a stated confidence of **0.60 or above** is recorded as
  an error — the same treatment a later stage of this campaign gives a claim its own data does
  not support. Where confidence is stated as a band, the **lower bound** of the band is
  the stated confidence.
- **Hedging is not free.** A commitment whose `expected_if_true` and `expected_if_false`
  overlap, or whose interval is wide enough that no possible result could fall outside it, is
  adjudicated `undetermined` and still counts in the denominator.
- Two indices are reported: `dx02b_direction` — surviving commitments adjudicated
  `right_direction`, over surviving commitments; and `dx02b_errors` — the count of
  confidently wrong commitments.

**Not scored:** prose quality, verbosity, the number of plan steps covered, literature
coverage, or whether the commitments are impressive. Only the direction of the number and the confidence
attached to it are adjudicated.

## 5. Scientific constraints

- A commitment is a number you could be wrong about. A statement no result could contradict is
  struck under §4, not credited as caution.
- The two branch expectations for a statistic MUST be separable by the measurement that will
  produce them. A statistic whose two branches predict the same value does not discriminate,
  and committing to it as though it did is itself the error.
- A stop value MUST be reachable by some possible result. A stop value no result could trigger
  is the same defect `DX02.md` Gate B rejects in an abandon condition.
- Confidence is a statement about your own uncertainty, not an intensifier, and MUST remain
  textually distinguishable from the factual claim (DX01 §5).
- Do **not** manufacture a number you have no basis for in order to clear the strike rule. Low
  confidence is available, and a low-confidence commitment that turns out wrong is not an error
  under §4.
- A commitment may be made about a step you expect to abandon. Committing to the value at
  which you would abandon it is the point of §3.2, and a commitment that is later borne out
  by an abandonment is not thereby a failed commitment.
- Nothing committed here may be revised once DX03 input is released. An edit to a committed
  record after evidence release voids the campaign, exactly as in DX01 §4.

## 6. Success condition

A set of numbered expectations — separable under the two branches, each carrying a confidence
you would defend, each tied to a step of the plan you have already frozen — such that any
divergence between what you expected and what you later measure is visible as a number rather
than as a change of mind.
