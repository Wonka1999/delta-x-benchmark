# DELTA-X v2 — DX02B answer key (approach pre-commitment)

> **Paths.** This document was written against the private working tree. On release `agent_facing/` became `tasks/` and `repro/data/` became `data/`; nothing else moved. See `docs/PATH-MAP.md`. The text is otherwise unedited.

**CONTAINMENT.** Designer-side. Nothing here may be rendered into an evaluated agent's
context. A harness that does so voids its run.

Added 2026-11-09. **Status: specification, not yet measured.** No submission has been graded
under it, and it moves **no weight** — see §4. Authority: `KEY.md` holds every measurement
cited below and governs every adjudication of fact; this file defines only the DX02B task,
its adjudication and its promotion experiment. Where the two disagree, `KEY.md` governs.
`SCORECARD.md` governs the record: DX02B emits its own itemised rows under the same three
rules, and its total is reported beside the campaign total, never inside it.

---

## 1. What this task measures, and why it exists

DX02B is served after `method_plan.json` is frozen and before any DX03/DX04 input is
released. It asks for five numbered, confidence-bearing commitments: expected values under
both branches, the invalidation control for the load-bearing statistic and its stop value,
the resolution the plan expects to earn, per-measurement portability to predicted inputs, and
a one-reason pre-mortem.

The task exists because **four measured failures in BASELINE-v2-clean are failures of
approach, and every one of them only becomes visible after 90 points of execution have been
spent.** All four were already fixed before the agent touched any data, and none of them is
reachable by any item in DX01–DX02.

**(a) Length direction.** `KEY.md`, *The length trap*: 3/3 clean-room runs asserted "the loop
is longer in TdT" with no data, at confidence **0.65 / 0.6–0.75 / 0.80**, and run3
pre-committed the error into its own DX02 plan as a "≥10 residues longer" expectation. The
measurement: net residue count TdT **42.55 ± 0.86** (n = 322) vs Pol µ **42.29 ± 3.67**
(n = 167), **median difference zero**; Mann-Whitney **p = 5.95e-16** on that zero difference.
What differs is **variance** (4× SD) and **chemistry** (hydrophobic/aromatic **0.447 vs
0.272**, polar **0.285 vs 0.545**).

**(b) Replacement structural statistic.** `KEY.md`, BASELINE-v2-clean table: **3/3 chose a
template-strand-channel occlusion measure**, and **3/3 guarded it with `pLDDT ≥ 70`**. Only
**1/3** explicitly rejected RMSD/TM-score (run1); run2 kept TM-score ≥ 0.5 as its own
superposition gate. *Prediction validity* records that the occlusion test does **not** transfer
to predicted coordinates — ESMFold packs both loops closed and returns a false positive for
Pol µ at **0.17–2.11 Å** — while region finding does transfer (**TM 0.979 / 0.989**). A pLDDT
guard cannot catch a confident false positive by construction. The control that does catch the
class is the same-protein null: two crystals of the **same** mouse TdT differ by **8.56 Å** at
the loop, against cross-subfamily deviations of **4.43 / 3.81 / 7.30 / 3.85 Å**.

**(c) Polarity.** `KEY.md`, *Polarity*: ML ancestral-state reconstruction gives **13
TdT-derived / 14 Pol µ-derived / 5 unresolved**, and classical outgroup comparison fails at
**16/32** positions. The intuitive answer — TdT later acquired the element — was asserted
one-sidedly by run3 and reached correctly by **0/3**.

**(d) Reproducible mistaken for resolvable.** `KEY.md`, *Granularity floor*: the spatial
permutation null makes the best **5-residue** window **non-significant** (p = 0.21, z = 0.75,
1066/5000), **11-residue** significant (p = 0.0008), **21-residue** p = 0.0002. The
separability tests agents name pass cleanly on isolated noise columns (mTdT 504, 223, 254,
288, all **P = 1.000**) and fail inside the real region (**0.914 / 0.736 / 0.694 / 0.602**).
3/3 allowed themselves residue granularity. Significance screening cannot save them:
**344 of 455** core columns pass BH q < 0.05.

---

## 2. Adjudication, per commitment

Adjudicate **direction only**. A commitment is `right_direction`, `undetermined` or `wrong`.
Magnitude is never required to match; a commitment with the right sign and an order-of-magnitude
miss is `right_direction`. The grader cites the submission record on every adjudication
(`SCORECARD.md` rule 3).

### C1 — `branch_expectations.json`

Adjudicated per record, against `KEY.md`.

| statistic class in the frozen plan | measured truth | `right_direction` | `wrong` |
|---|---|---|---|
| any net length / residue-count comparison of the differential element | median difference **zero**; TdT 42.55 ± 0.86, Pol µ 42.29 ± 3.67 | expects no net difference, or a difference inside ±1 residue, or declines to predict a sign and says why | expects a signed net difference ≥ 1 residue either way; "longer in TdT" is the measured modal error |
| any dispersion / variance comparison | TdT near-invariant across 322 species (147 at 42 aa, 160 at 43), Pol µ 17–49, **4× SD** | expects the larger dispersion in Pol µ | expects equal dispersion, or the larger dispersion in TdT |
| any composition comparison | hydrophobic/aromatic **0.447 vs 0.272**; polar **0.285 vs 0.545** | expects a composition difference with the right sign on either axis | expects no composition difference |
| any per-position significance count | **344/455** pass BH q < 0.05; 265 (58 %) exceed p99.9 | expects a large majority of positions to clear significance, i.e. that significance does not filter | expects significance to select a small set |
| any directional / polarity statistic | **13 / 14 / 5**; outgroup consensus matches neither at **16/32** | expects a roughly symmetric or unresolved split, or declines with a stated reason | expects a one-sided acquisition by either subfamily |
| any cross-subfamily deviation statistic (RMSD, TM, per-residue CA) | same-protein null **8.56 Å** exceeds every cross-subfamily value (4.43 / 3.81 / 7.30 / 3.85) | expects the cross-subfamily value **not** to exceed a same-protein comparison | expects the differential element to rank top by deviation |

A statistic class not in the table is adjudicated `undetermined` unless `KEY.md` carries a
measurement for it. **Do not invent an adjudication**; an unmeasured class is reported as
unmeasured, and the denominator of `dx02b_direction` excludes it.

### C2 — `invalidation_control.json`

The question is whether the named control could detect that the chosen statistic is dominated
by something other than the cross-subfamily difference.

- `right_direction` — the control is a **null of the same quantity on a comparison that carries
  no cross-subfamily signal** (same protein, same subfamily, two structures of one protein,
  split halves of one set), with a numeric stop value in the statistic's own units. Credit is
  for the **class**, not for reproducing 8.56 Å or 0.160.
- `undetermined` — a control that is input-side adequacy only (depth, coverage, occupancy,
  model confidence). These are real checks and DX02 already scores them; they cannot detect
  this failure class, so they neither earn nor cost here.
- `wrong` — a control whose quantity is produced by the step it gates, or whose stop value no
  possible result could reach. Measured instance: a model-confidence guard offered as the
  control for a statistic that fails by returning a **confident** false positive (3/3 runs).
- Struck — no numeric stop value.

### C3 — `resolution_commitment.json`

Against `KEY.md`, *Granularity floor* and *Residue-level ground truth does not exist*.

- `right_direction` — `finest_scale` ≥ **10 residues**, with a `setting_measurement` that is a
  **spatial** null (a permutation or sliding-window null over position), not a reproducibility
  or bootstrap test. The floor measured on this data is ~10–20 residues; the independent
  experimental record is the same shape — six single substitutions all failed, only a
  ≥13-residue deletion or a whole-loop swap flipped the phenotype.
- `undetermined` — a scale committed with no measurement named, or a measurement that cannot
  set a spatial floor.
- `wrong` — `finest_scale` of 1–5 residues, **or** any scale justified by a reproducibility
  statistic presented as a resolution statistic. This is the conflation `DX03.md` §5 already
  scores as an error, committed in advance.

### C4 — `portability_commitment.json`

Against `KEY.md`, *Prediction validity*.

- `right_direction` — region-level localisation marked `transfers: yes` (measured: TM 0.979 /
  0.989, all five differential regions recovered from sequence alone), **and** any contact,
  clash, occlusion or packing statistic marked `no` or `unknown` with deciding evidence named.
- `undetermined` — `unknown` throughout with deciding evidence named; the agent has not
  committed, but it has not asserted the false thing either.
- `wrong` — a contact/clash/occlusion statistic marked `transfers: yes`, especially when the
  deciding evidence offered is a per-residue model-confidence threshold: the measured failure
  is a confident false positive at **0.17–2.11 Å** on predicted Pol µ coordinates, which such a
  threshold passes.

### C5 — `pre_mortem.json`

There is no single correct pre-mortem and this item is **never** adjudicated `wrong` on its
content. Adjudicate only:

- `right_direction` — the named reason is a failure of **inference** (resolution claimed beyond
  the data; a statistic that does not survive its own null; a direction asserted without an
  outgroup; a measurement that does not transfer to the input it will be run on), and the
  `first_observation` carries a value and a stage.
- `undetermined` — the named reason is an **operational** failure (tool crashes, wall-clock,
  file formats, environment). These are real but are not what this task is for.
- Struck — no number on the first observation.

C5's value is diagnostic rather than discriminative; report it, and weight it at zero inside
`dx02b_direction` if the promotion experiment in §5 shows it uncorrelated.

---

## 3. Scoring rule

Stated in full, and mirrored in `DX02B.md` §4 wherever the agent must act on it.

1. **Strike gate — not points.** A commitment carrying no number, or no confidence in [0,1],
   **is not a commitment**. It is struck before adjudication and recorded in `strikes[]` as
   **absent**, never as `wrong`. An interval with both ends stated is a number; "higher",
   "substantial", "sufficient", "comparable" are not. A struck commitment leaves the
   denominator of `dx02b_direction`; it does not fill it with a zero.
2. **Adjudication is direction, not magnitude.** Each surviving commitment is
   `right_direction`, `undetermined` or `wrong` per §2. Prose, breadth and step coverage are
   not scored.
3. **Confidently wrong is an error.** A commitment adjudicated `wrong` at a stated confidence
   of **≥ 0.60** is recorded in `dx02b_errors` as an **error**, not merely as unrewarded —
   the treatment `DX03.md` §4 gives a composition-versus-length claim the data does not
   support. Where confidence is stated as a band, the **lower bound** of the band is the
   stated confidence.
   *Basis for 0.60, and its limit.* The three measured wrong-direction length claims sat at
   0.65, 0.6–0.75 and 0.80 (`KEY.md`, BASELINE-v2-clean). Under the lower-bound reading a
   threshold of 0.60 reaches **3/3**; 0.65 reaches **2/3**. The threshold is therefore set by
   the only confidences this benchmark has measured, n = 3, on one task. It is a convention,
   not a measurement, and must not be cited as one.
4. **Hedging is adjudicated, not rewarded.** A commitment whose two branch expectations
   overlap, or whose interval no possible result could fall outside, is `undetermined` and
   **remains in the denominator**. Without this, "0.5 confidence, wide interval, everywhere"
   scores identically to a correct commitment.
5. **Two reported indices, no total.**
   `dx02b_direction = right_direction / (right_direction + undetermined + wrong)`, over
   surviving commitments; `dx02b_errors` = integer count under rule 3. Both are reported, with
   their denominators, in the scorecard's `campaign.reported_beside[]`. **Neither is added to
   the campaign total** (§4).
6. **Provenance.** Every adjudication cites the submission record it read
   (`SCORECARD.md` rule 3) and the `KEY.md` heading that licensed it. An adjudication citing
   neither is removed before the indices are computed (`SCORECARD.md` rule 2).

---

## 4. Weight: 0 for its first campaign, report-only

**This is a decision, not an omission.** DX02B scores zero in its first campaign; its indices
are reported beside the campaign total and are **not added to it**.

The reason is this benchmark's own rule: **weight follows measured discrimination.** Every
weight currently in `KEY.md`, *Points* was moved on a measurement — DX02 fell 20 → 10 because
it bought **0.4 points** of separation across three runs with 12 of 20 points at ceiling, and
was held at 10 only once the re-grade under rules 1–4 produced **3.0 / 1.0 / 5.0**, a range of
4.0/10. DX02B has never been run. It has no measured range, no measured ceiling and no
measured relation to anything scored. Giving it weight on the strength of the argument in §1
would be exactly the move the DX02 blocker was opened to prevent — and that blocker stood
from `FIXSPEC.md` until a measurement closed it.

The honest form of the claim is: §1 shows these four failures are **real and early**. It does
not show that asking about them **predicts** anything. §5 is the experiment that would.

A first campaign therefore reports:

```
campaign.total            = <DX01 gate> + DX02 + DX03 + DX04 + DX05   (100-point scale, unchanged)
campaign.reported_beside  = [ dx02b_direction = r/n, dx02b_errors = k, delta_over_prior ]
```

A DX02B index may **not** be compared across campaigns served different `DX02B.md` digests,
and may not be cited as a score of anything until §5 has run.

---

## 5. The experiment that would earn it weight

**Hypothesis.** The DX02B index, computed before any DX03 input is released, predicts the
DX03–DX05 subtotal of the same run.

**Design.** `n ≥ 12` paired clean-room campaigns against the current briefs, each run through
DX01 → DX02 → DX02B → DX03 → DX04 → DX05 with `agent_facing/` digests recorded at run time
(`baselines/BASELINE-v2-clean/PROVENANCE.md`). Twelve is the cost: DX03–DX05 have **never been
run at all**, so this experiment cannot reuse any preserved record, and the n ≥ 5 clean-room
re-run `KEY.md` already requires for a published baseline is a prerequisite, not a substitute.

**Statistic.** Spearman ρ between `dx02b_direction` and the DX03+DX04+DX05 subtotal (90
points), with a one-sided permutation test over 10 000 label shuffles. Report per-task ρ for
DX03, DX04 and DX05 separately in the same pass.

**Decision rule, fixed in advance.**

| outcome at n ≥ 12 | decision |
|---|---|
| ρ ≥ 0.60 and permutation p < 0.05 **and** the index's observed range ≥ 0.20 on its own 0–1 scale | **Promote**, up to a cap of **5 points** |
| ρ ≥ 0.60 and p < 0.05 but range < 0.20 | **Do not promote.** A saturated predictor is the DX02 failure mode (12 of 20 points at ceiling in 6/6 observations); keep report-only |
| ρ < 0.60 or p ≥ 0.05 | **Do not promote.** Keep report-only for one further campaign, then retire the task rather than carry an unweighted stage forever |

ρ ≥ 0.60 is chosen so the two conditions cannot contradict each other: at n = 12 the one-sided
Spearman critical value at α = 0.05 is ≈ 0.50, so any ρ clearing 0.60 also clears the
permutation test, and the rule never licenses promotion on an effect the test rejects.

**Where the weight comes from, if it is promoted.** From the task DX02B **predicts**, never
from the campaign total, and never by inflating the total past 100. If the correlation is
carried by DX04 (ρ_DX04 the largest of the three and itself p < 0.05), the promoted points come
out of DX04's 35. If it is carried by more than one task, split the promoted points across the
carrying tasks in proportion to their per-task ρ. A task whose per-task ρ is not individually
significant contributes nothing. If no per-task ρ is individually significant, the pooled
correlation does not license a transfer and the decision is **do not promote**, whatever the
pooled value.

**Pre-registered now, so the result cannot be read backwards.** This section is the
registration. A later revision that changes ρ, n, the range condition or the weight source
after seeing the data must say so in place, and the changed rule may not be cited as this one.

---

## 6. Limits — what this task cannot see

1. **It is a proxy, and the proxy is loose in both directions.** An agent with a correct
   approach can still execute badly: nothing in DX02B touches alignment quality, provenance
   discipline, or whether a command was ever run. And an agent with a wrong approach can still
   land the answer — `KEY.md` records a span inside the ±6 tolerance produced in **1 of 3**
   clean-room draws with **no data at all**, and all six no-tool probes named the region
   unprompted. A high DX02B index is not evidence of a good campaign and a low one is not
   evidence of a bad one, until §5 says otherwise.
2. **It cannot detect a commitment made for the wrong reason.** A model that has memorised this
   system can produce the right direction on C1 and C3 from recall. DX02B has no derivation
   requirement and cannot acquire one — it is served before any data exists to derive from.
   This is the same ceiling `KEY.md` records when it rules that naming the region is worth zero
   everywhere; DX02B's indices are subject to that rule and carry no credit for recall.
3. **Its adjudication inherits `KEY.md`'s own soft spots.** C1's polarity row rests on the two
   reproducible results (13/14/5 and 16/32); the ±1 index corroboration is marked
   **unreproducible as stated** in `KEY.md` and is not used here. If a cited measurement is
   later withdrawn, the corresponding row of §2 is withdrawn with it and the commitment becomes
   `undetermined`, never `wrong`.
4. **It can teach the test.** Five named commitment axes tell an agent which classes of error
   this benchmark watches. The brief is deliberately generic — it names no quantity, no region,
   no residue and no tool-specific guard — and any revision that adds specificity to make
   grading easier re-opens the leak audit that found ~30 fatal leaks in v1.1 and 11 more in its
   rubric. Grading convenience is not a reason to name a quantity in `DX02B.md`.
5. **n = 3 underlies everything in §1.** Four failures at 3/3 are four failures in three runs
   of one model on one case. The failures are real; their **rate** is not established, and no
   claim about frequency may be made from this file.
