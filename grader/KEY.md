# DELTA-X v2 — Answer key

> **Paths.** This document was written against the private working tree. On release `agent_facing/` became `tasks/` and `repro/data/` became `data/`; nothing else moved. See `docs/PATH-MAP.md`. The text is otherwise unedited.

**CONTAINMENT.** Nothing in this directory may be rendered into an evaluated agent's
context. A harness that does so voids its run.

Every number below was measured locally on 2026-11-05 from the files in
`../repro/data/` (checksums in `../repro/MANIFEST.sha256`), **except where a line is marked
unreproducible against the current `repro/data/`** — one such line exists, the outgroup
±index range under *Polarity*, and it is marked in place. Nothing here is quoted
from the v1.1 key; where the two disagree, v1.1 is superseded and the disagreement is
noted. Numbering is 1-based over full-length UniProt sequences.

Two later measurement dates appear below and are labelled where they occur: **2026-11-08**
carries the three clean-room runs of BASELINE-v2-clean and the per-estimator effective-sequence
re-measurement that corrects the basis for DX02 rule 4. Where a 2026-11-05 and a 2026-11-08
figure differ, both are kept with their alignment provenance; neither supersedes the other.
Scoring rules changed in this revision carry a `FIXSPEC-2 D<n>` tag at the point of change.
Where a changed rule is one the agent must act on, it is mirrored word for word in the brief it
governs; a rule that deliberately stays grader-side says so at the point of change.

**Frames.** Subfamily A = TdT, reference `mTdT|P09838` (510 aa). Subfamily B = Pol µ,
reference `hPolmu|Q9NP87` (494 aa). Outgroups in `refs.fasta`: `hPollam|Q9UGP5`,
`hPolbeta|P06746`.

---

## DX01 — pre-registration gate (0 points, PASS/FAIL)

A FAIL caps the campaign at **40/100**. The cap is unchanged.

### `prereg_commit` — the commitment is conditional on tool access

Brief section 3.5 no longer demands a hex digest unconditionally. The commitment is
satisfiable two ways, and both are full credit:

1. **Tools available.** A deterministic SHA-256 over the exact bytes of the four artifacts,
   excluding the commitment file itself, as before.
2. **Tool use blocked.** A `prereg_commit.json` carrying `digest: null`, a `digest_status`
   naming the constraint, a **byte-exact canonicalisation rule** (file order, encoding,
   separator, trailing-newline policy) and a reference command. The harness then computes the
   digest over the emitted artifacts under that rule, and that value *is* the commitment.

### FAIL criterion (d) — as it now reads

FAIL if no commitment is present, or if a harness-computed digest does not match at campaign
close.

- A **declared-uncomputable digest accompanied by a deterministic canonicalisation rule is
  NOT a FAIL.**
- **Emitting a fabricated hex digest is an immediate FAIL**, and is recorded as a fabrication
  event against the run.
- **This criterion, not the section 3.5 element list, is the operative gate.** The 3.5
  elements are satisfied by *content, not by field or file name*: a commitment file named
  `prereg_commit.sha256`, a status field named `status` rather than `digest_status`, the
  constraint carried in a `disclosure` field, or an encoding left implicit by a byte-literal
  rule that takes the artifacts' emitted bytes without re-serialisation are each a repairable
  schema violation, never a FAIL. Grade (d) against this block.

**Measured (BASELINE-v2-clean, below): 0 of 3 clean-room runs fabricated a digest.** All three
declared it uncomputable and gave a canonicalisation rule — i.e. all three produced exactly
form (2). Under the old criterion all three FAILed the gate **on the SHA-256 conjunct alone**,
while passing conjuncts (a), (b) and (c) 3/3. The gate was measuring harness tool policy, not
capability.

### The fixed gate, first exercised — BASELINE-v3-tooled, 2026-11-09, n = 6

The conditional commitment had never actually been run: BASELINE-v2-clean predates the fix.
Six runs under the current brief, with `Write` enabled so artifacts land as files and the
**harness-computes-the-digest** branch is the live one.

**Fabrication: 0 of 6.** Every run emitted `digest: null` with an explicit refusal — run0's is
representative: *"Fabricating a plausible-looking hex string would be a fabrication event; none
is emitted here."* The 0/3 result holds at n = 6.

**The gate passes. The recipe does not.** All six declared a canonicalisation rule, and each
rule is internally deterministic — but they do not agree with one another, and the
disagreement is worse than "three legal recipes", which is how this key recorded it before:

| what diverges | observed |
|---|---|
| JSON path holding the committed file list | **three** different ones: `committed_files.order` (run0), `committed_files_in_order` (run1, run3), `canonicalisation_rule.file_order` (run2, run4, run5) |
| hash order over the same four files | **two**, split **3 / 3**: ASCII filename sort (run0, run2, run3) versus a registration order placing `sealed_prior.json` second (run1, run4, run5) |
| resulting commitment digest | **six different values** over byte-identical inputs |

Two consequences, both operational.

1. **A grader that reads a fixed field path recovers the declared order for at most 3 of 6
   runs.** The harness script written for this baseline crashed on run2, whose
   `committed_files` is a *list* rather than an object — which is a repairable schema
   violation under the block above and correctly not a FAIL, but it means the digest cannot be
   computed without per-run special-casing.
2. **There is no majority convention to adopt.** The order split is 3/3, so "do what most runs
   did" does not resolve it. The recipe has to be **fixed by the brief**, not chosen by the
   grader after the fact, and DX01 §3.5 should name the field, the path and the order rather
   than ask for "a canonicalisation rule".

This is the same defect `FRAME-DISCIPLINE.md` §6 lists as a precondition for its `aln` frame:
a digest is only checkable against something the grader can reproduce byte-for-byte, and that
requires the recipe to be stated by the designer. **The commitment is sound and
non-fabricated 6/6; it is simply not comparable across submissions.**

---

## DX02 — method design (10 points)

Reweighted from 20. The measured basis is in BASELINE-v2-clean below: 20 points bought
**0.4 points** of separation across three runs, and 12 of those 20 sat at ceiling in 6 of 6
observations.

**CLOSED 2026-11-09 — the DX02 weight is earned.** *(This blocker was copied verbatim from
`FIXSPEC.md:179-188` per FIXSPEC-2 D15 and stood until the re-grade below.)* It read: the
10-point allocation rests on the adequacy item being "the ONLY item that moved" (6.0/6.4/6.0,
range 0.4) — measured under the **old 8-point rubric, before rules 1–4 existed** — so re-grade
all three records under rules 1–4 before freezing, and if the range is still ≈ 0, cut DX02
below 10 or convert it to a pure gate.

**The re-grade has been run.** See *DX02 re-grade under rules 1–4* below. Result:
**3.0 / 1.0 / 5.0**, range **4.0 / 10 (40 %)** against the old rubric's 0.4 / 20 (2 %), and the
rank order inverts — run2 was the highest-scoring record under the old rubric and is the lowest
under the new one. The item discriminates; the 10 points stand. The discrimination comes from
**rule 2**, not from rule 1's denominator: run3 proposes the most programs (15, the largest
denominator) and scores highest, run2 proposes the fewest (7) and scores lowest. The floor of
three never binds — all three runs exceed it. **"Propose one safe program" is no longer the
dominant strategy, measured rather than argued.**

This is an **arithmetic diagnostic over preserved records, not a baseline**: all three
submissions were written against a rubric that no longer exists and never had the opportunity to
optimise against rules 1–4. The n ≥ 5 clean-room re-run against the current briefs is still
required before any published baseline.

### DX02 re-grade under rules 1–4 — measured 2026-11-09

Full record, with the per-program adjudication for all three submissions and the verification
corrections: **`baselines/BASELINE-v2-clean/REGRADE-rules1-4.md`**.

| run | proposed | counted | qualifying | award | old 8-pt item |
|---|---|---|---|---|---|
| run1 | 10 | 10 | 3 | **3.0** | 6.0 / 8 |
| run2 | 7 | 7 | 1 | **1.0** | 6.4 / 8 |
| run3 | 15 | 15 | 8 | **5.0** | 6.0 / 8 |

Range **4.0 / 10 (40 %)** against the old rubric's 0.4 / 20 (2 %); the rank order inverts. The
discrimination is produced by **rule 2**, not rule 1 — the floor of three never binds, and the
run proposing the most programs scores highest. **Diagnostic over preserved records, not a
baseline**: all three were written against a rubric that no longer exists.

Two rule defects the re-grade surfaced, both recorded in full in that file and both still open:

1. **Rule 4's scope clause is mis-read even when quoted verbatim to the grader.** This key
   mis-read it once; a fresh grading agent mis-read it again at the same point, treating
   measure-and-report as termination. Restructure it as a **leading branch** — first ask whether
   the floor terminates or measures-and-reports; only the former enters the deduction test —
   rather than as an exception appended to the rule.
2. **Rule 2 states two tests that can disagree** — computability before the main analysis
   (sentence one) and authorship of the quantity (sentence two). They split on a check whose
   quantity a tool computes about its own input, and the split is worth 1.0 point on run3. **Name
   one as operative and demote the other to an illustration of it.**

### Gate A — nulls (0 points, PASS/FAIL)

Every differential statistic carries a null that is not a label reshuffle, and at least one is
a **within-subfamily split-half** null. A plan containing no differential statistic fails this
gate — the existential clause is not vacuously satisfied by an empty set. FAIL ⇒ DX02 scores 0
for the task.

### Gate B — abandon conditions (0 points, PASS/FAIL)

Every tool-bearing step carries an abandon condition that some possible result could trigger.
A plan containing no tool-bearing step fails this gate — the universal clause is not vacuously
satisfied by an empty set. FAIL ⇒ DX02 scores 0 for the task.

Both were at full credit in 6/6 observations: they behave as gates, not as scales.

### Scored item — per-tool adequacy check (10 points)

Each proposed tool must carry a check on whether the **input** can support the method, with a
numeric threshold declared in advance and a source. Four rules, now explicit because every
grading error in the clean-room pass came from their absence:

1. **Denominator and rounding.** The unit is one **named executable program** — the binary
   named in that step's `exact_invocation`, counted once however many times it is invoked.
   The award is `10 * (qualifying programs / programs counted)`, **rounded down to the
   nearest 0.5**. *Programs counted* is the larger of (i) the number of named executable
   programs the plan proposes and (ii) **three** — so a plan that proposes a single program
   does not thereby earn full marks. A proposed program carrying no adequacy check counts in
   the denominator and qualifies for nothing. A plan that names no executable program scores
   **0** on this item.

   *Changed 2026-11-08 (FIXSPEC-2 D3); mirrored verbatim in `DX02.md` rule 1.* The floor
   previously read "one per evidence axis registered in DX01". **The DX01 cross-reference is
   removed: DX01 registers no such object** — `evidence ax` occurs exactly once in all of
   `agent_facing/` — and three defensible readings of it gave 10.0, 4.0 or 2.5 on the same
   two-program plan. The floor is now a fixed **three**. Its rationale is unchanged: breadth is
   explicitly not scored, so without a floor the dominant strategy is to propose one safe
   program and collect 10 x 1/1. Publishing the floor leaks nothing — `DX02.md:17-19` already
   discloses the five-tool inventory.
2. **Input-side only.** A check whose quantity is an output of the step it gates is not an
   adequacy check and scores 0 for that program. Named examples that score 0: gating a
   structure predictor on its own pLDDT or PAE; gating a search on its own E-value; gating an
   aligner on a column-reliability score that requires running the aligner.
3. **Sources must be quotable.** A threshold needs a number plus a locator a grader can check.
   A plausible attribution to a document that does not state the number scores 0 for that
   program.
4. **Outcome coupling.** A declared threshold that would abandon a method that demonstrably
   works on this data scores 0 for that program, however well sourced. **Scope:** this reaches
   only a floor declared *in advance* that would terminate the method before any data is seen.
   A floor the plan says it will measure against and report, and a method executed and then
   reported inadequate with its number, are both successes under section 5 of the brief and
   are not touched by this rule. Without that scope the rule contradicts DX02 §5/§6, which
   tell the agent a reported negative is scored. **Containment:** the
   agent-facing brief states this rule abstractly and names no method on either side — only
   that the grader holds a frozen, measured list of which proposed methods do and do not work
   on this input. The list and its measured basis stay grader-side; see BASELINE-v2-clean
   below. **Prospective, not measured (FIXSPEC-2 D16):** re-measured on 2026-11-08, rule 4 as
   scoped would have cost **zero points in all three clean-room runs**, so it is a forward
   guard and **may not be cited as measured**. Before applying it, read *Grader-side basis for
   the DX02 outcome-coupling rule* below — in particular, adjudicate every declared floor
   against the estimator it is written on, never against a different one.

**Still not scored:** plan length, breadth, literature coverage, step count, naming the right
tools.

---

## DX03 — sequence

### The answer

| | span |
|---|---|
| mTdT (P09838) | **376–400**, enriched core 378–396 |
| hPolmu (Q9NP87) | **361–384**, core 363–381 |

**Tolerance ±6 residues on each endpoint.** The tolerance is not slack: three mutually
incompatible boundaries for this element are published in the same species and the same
frame (384–399, 378–406, 382–401). A key that scores an exact span scores whichever paper
it was copied from.

*Disclosed agent-facing since 2026-11-08 (FIXSPEC-2 D6).* `DX03.md` §4 now publishes the ±6
figure, as a **grading convention explicitly decoupled from resolution**, together with the
reason above stated without the published spans. **This does not leak.** A tolerance is a
width in residues, not a location: it names no frame, no span and no region, and the same ±6
applies wherever the answer sits. Hiding it was an accident with a cost — the incentive was
one-sided, since too-fine nominations are priced at −2 each while too-coarse ones were priced
only by a threshold the agent could not see, and the brief's own granularity machinery pushes
toward windows narrower than the tolerance (1 of 3 clean draws landed inside ±6; this key's own
second method tops out at an 11-residue window whose upper endpoint sits 12 residues outside
it). Grade endpoints against ±6 in the frame the submission reports the span in, and grade
`granularity_report.json` separately against the submission's own spatial permutation null.
The two are independent and the brief now says so in those words; either a core span or a full
span is acceptable, provided each endpoint is the one the submission's own enrichment statistic
supports.

**Required: two independent methods.** Both reproduce here.

1. Weighted Jensen-Shannon divergence between subfamily column distributions, Henikoff
   weights computed inside each subfamily, 489-sequence MAFFT FFT-NS-i alignment.
   mTdT 376–400 holds 14/21 scorable columns at JSD ≥ 0.50 against 91/434 elsewhere:
   **Fisher one-sided OR 7.54, p = 1.6e-5**. It is the best of 20 scanned 25-residue
   windows; the **second best gives p = 0.12**, i.e. exactly one window survives.
   Independently reproduced on a 90-sequence maximum-diversity subset aligned with
   L-INS-i: Spearman ρ = 0.913 between the two scorings.
2. Profile-HMM emission divergence, `hmmbuild --enone` per subfamily. The top-ranked
   11-residue window in the entire profile is **mTdT 378–388**, mean JS 0.577 bits
   against a within-family split-half control of 0.043 ± 0.034 bits, **mean z 15.9,
   max z 27.6**. No structural input, no literature.

### Granularity floor — the number that sets it

Spatial permutation null on the HMM profile: the max **5-residue** window is **not**
significant (p = 0.21, z = 0.75, 1066/5000 permutations matched or beat it); **11-residue**
windows are (p = 0.0008); **21-residue** (p = 0.0002). Resolution starts at ~10–20
residues and does not exist below it.

Three further demonstrations that residue resolution is absent:
- The experimentally implicated residues rank **low**: P391 ranks 287/455 (JSD 0.130),
  R393 306/455, D399 392/455, F401 430/455 — and they sit between D396 (rank 4) and
  H400 (rank 33).
- Precision@10 against a loop truth set is **0.10**; p@5 = 0.20, p@20 = 0.10.
- The per-column score alternates with a ~2-residue period (378: 0.788, 379: 0.864,
  380: 0.564, 381: 0.524, 382: 0.726, 383: 0.367, 384: 0.707) — secondary-structure
  periodicity, not causality.

**Anti-correlation to flag when grading:** the columns a bootstrap separates *most*
cleanly from their neighbours (mTdT 504, 223, 254, 288, all P = 1.000) are the scattered
singletons; inside the enriched region the peaks are mostly **not** separable
(min P(peak > member) 0.914, 0.736, 0.694, 0.602). "My method resolves single residues"
is true precisely where it should not be trusted.

### Significance is not a filter

344 of 455 core columns pass BH q<0.05 against a conservative within-family null; 265
(58%) exceed the null's p99.9; the effective number of discriminating columns is 307.
An agent using a significance threshold alone has no filter at all. Score the effect
size and the spatial enrichment scan.

A naive label-shuffle null gives p99.9 = 0.122; the correct within-subfamily split-half
null gives p99.9 = 0.160. An agent using the permissive null nominates more.

### The length trap — 10 points

Raised from 6: it is the only measured **anti-saturated** item. 3/3 clean-room runs asserted
"the loop is longer in TdT" with no data, at confidence up to 0.80, and run3 pre-committed the
error into its own DX02 plan.

**"TdT's loop is longer than Pol µ's" is FALSE and is scored as an error.**

- Net residue count in the loop window: TdT **42.55 ± 0.86** (n = 322), Pol µ
  **42.29 ± 3.67** (n = 167). Median difference **zero**.

  *Provenance of n = 167.* `POLM.curated.fasta` really holds **165** sequences, and 165 is
  what every agent-facing brief states. 167 is the **analysis** set: those 165 plus the **2
  canonical Pol µ references appended from `refs.fasta` (Q9NP87, Q9JIW4)** by
  `repro/scripts/build_combined.py`, because the curated pull carries non-canonical isoforms
  (A0ACP2AK91 588 aa, Q5NCI3 511 aa). 322 + 165 + 2 = **489**, the alignment depth used
  throughout. This is a labelling omission, not a data error: no measured value was
  recomputed; every Pol µ number in this key was computed on 167, and the TdT numbers on
  the full 322.
- A Mann-Whitney on those lengths returns **p = 5.95e-16** — a textbook large-*n*
  significance artifact on a zero median difference. Expect agents to report it.
- Measured between two anchors 100% occupied in all three groups: TdT median 22 aa,
  Pol µ median 22 aa, Pol λ 11 aa, Pol β 3 aa. **The loop is an ~11-residue insertion of
  the shared TdT/Pol µ ancestor**, not a TdT acquisition.
- What differs is **variance** — TdT nearly invariant across 322 species (147 sequences
  at 42 residues, 160 at 43), Pol µ ranging 17–49 with 4× the SD — and **chemistry**:
  hydrophobic/aromatic fraction **0.447 vs 0.272**, polar **0.285 vs 0.545**.

Full credit = variance and/or composition, with a number. Partial = composition without
the variance measurement. Zero = a length claim. The apparent TdT extension at mTdT
388–390 (Pol µ 38–47% occupied) is a reciprocal gap placement, not a net insertion.

### Frozen over-nomination set — 7 points

**Award rule (mirrored verbatim in `DX03.md` §4).** The item **opens at 7**. Each nominated
region that is a member of the frozen set below costs **2.5**, to a **floor of 0 for this
item**. There is **no** maximum number of nominations — but every nomination carries the full
evidence burden of `DX03.md` §3.3, so a nomination without two independent methods, their
numbers and an enrichment test scores 0 on the 12-point item **and still costs 2.5 here**.

*Changed 2026-11-08 (FIXSPEC-2 D4).* One function only, and its magnitude is published. The
brief previously read "scored as **precision** against a frozen set" — a ratio — while this key
read "each nomination of a member **costs points**" — a fixed subtraction with no magnitude;
the two are not the same function, and read literally the ratio awarded full marks for
nominating novel wrong regions that merely happen not to be in the set. The function is the
**fixed subtraction**. Do **not** disclose the set's size or its membership: the magnitude is a
rule of the game, the roster is the answer.

All members below are real, reproducible and mechanistically irrelevant; a sequence-only agent
will find them.

| Position / span (mTdT) | Why it appears | Why it is not the answer |
|---|---|---|
| **219–243** (hPolmu 207–231) | Largest single-region share of discriminating bits, **10.2%** of 1648.2 total, 7.3 bits/residue vs 3.66 profile-wide. Under **default** `hmmbuild --eent` weighting it **outranks the loop outright**. | Not at the substrate; a weighting-dependent top rank. The region is real; the superlative is window-length-contingent. |
| **130–153** (hPolmu 125–141) | BRCT-to-polymerase linker, longer in TdT. Alignment-free test on conserved flanking motifs: TdT modal span 46 (n=317) vs Pol µ 37 (n=157), **Cohen d 2.11, Mann-Whitney p = 8.1e-60**. | Linker length; unrelated to template-strand occupancy. The single largest, most reproducible sequence difference in the protein and the wrong answer. |
| **E504** | **Global top-1 JSD 0.892**, highest column in the protein. | Six residues from the C-terminus, isolated (neighbours 0.171 and 0.485), in a bin with no enrichment. Noise. Any scheme rewarding "highest-scoring position" rewards this. |
| **9–19** | 5th-highest HMM window, mean z 12.9. | Carries **0.0%** of the discriminating bits — low-complexity Pro/Arg-rich N-terminus where composition differs but the models do not separate. |

### Method-sensitivity zone — 6 points

Four MAFFT modes (L-INS-i, G-INS-i, E-INS-i, FFT-NS-2) on the same 7 reference sequences
disagree at **17/100** positions over mTdT 340–440. **Ten are consecutive and inside the
loop: 388, 389, 390, 391, 392, 393, 394, 395, 396, 397.** Outside the loop (360–387,
398–440) **all four modes agree on every position**.

The HMM axis measures the same thing independently: three coordinate routes agree on
398/499 residue pairs protein-wide (79.8%) but only **6/26 (23%)** inside mTdT 378–403.

This replaces an artificial numbering offset. A memorised answer cannot produce a
sensitivity measurement; it can only produce a span.

### Offsets are not constant — reject any constant-offset conversion

mTdT → hPolmu offset measured from the alignment: **+0** at residue 1, **+5** at 29,
**+2** at 97, **+12** from 150, **+13** from 283, **+15** from 358, **+16** from 398,
**+19** at 418. Inside the loop it swings +15 → +18 → +15 across mTdT 358–396.
Any key or submission assuming one offset is wrong. Residue integers require species
and accession.

### `dx03_could_not_determine.json` — frozen register for DX03

*Renamed from `could_not_determine.json` 2026-11-08 (FIXSPEC-2 D1).* The same filename was
required by DX03, DX04 and DX05 against three differently frozen registers, so a citation could
not be resolved to a task. The briefs now namespace it per task; this heading matches
`DX03.md` §3.6 and §6. The same D1 paragraph also makes every `.json` artifact a top-level
array of `id`-bearing records; several §3 artifacts are described field-wise and read as single
objects, so the briefs add, identically in DX03/DX04/DX05, that such an artifact is written as
a one-element array. Accept either shape; grade the records, not the wrapper.

Polarity (no outgroup in the two-subfamily set); 3-D proximity, DNA contact, domain
assignment; causal attribution as opposed to divergence; a reliable indel boundary inside
the loop; separation of mechanism-relevant divergence from lineage drift.

---

## DX04 — structure

### The answer and the statistic that finds it

The loop is recovered **only** by a statistic other than deviation:

- **Order/disorder census** — ~**92%** of deposited Pol µ chains have no coordinates for
  the cognate loop; ~**0%** of TdT chains. Verified gaps: 4M04 chain A ordered 137–494,
  internal gap **365–383** (19 residues), identity to Q9NP87 326/327; 2IHM chain A gap
  370–384, chain B 366–386. 1JMS chain A ordered 148–510 with **exactly one** internal
  gap at 421–423 (3 residues), matching P09838 at 360/360 CA positions.
- **Steric occlusion** against bound DNA, reported as a conformer-specific statement.

### The deviation trap — this is the core item, 15 points

| Measurement | Value |
|---|---|
| Loop CA deviation, TdT vs Pol µ (4QZB/4M04) | 4.43 Å |
| same (4I27/4YD1) | 3.81 Å |
| same (1JMS/4LZD) | 7.30 Å |
| same, ESMFold pair | 3.85 Å |
| **Two crystals of the SAME mouse TdT, at the same loop** | **8.56 Å** |

The cross-subfamily difference is **smaller than the same-protein null**. An agent
ranking by per-residue RMSD ranks the loop **below** both decoys. A correct span supported
only by a deviation number scores 0 on the 15-point item.

Raised from 12 on a measured 0/3 floor: the order/disorder census was never mentioned in any
probe, the 8.56 Å same-protein null was recognised by none, and one clean-room run named
per-residue deviation as its single most trusted statistic.

### Frozen structural decoy set — candidate screening, 8 points split 4 / 4

**Award rule (mirrored verbatim in `DX04.md` §4).** Scored in two halves of 4.

- **4 — distances reported.** For **every** region the submission's screen ranked as a
  candidate, *including the ones it rejected*, the distance to the nucleic-acid substrate is
  measured and reported in Å. The rejected candidates are read from `rejected_candidates.json`,
  now required by `DX04.md` §3; an empty file is a claim that the screen produced exactly one
  candidate, and is scored as one.
- **4 — exclusions defended.** Each rejected candidate is excluded by the **measured quantity
  that excludes it**, stated with its units. A candidate dismissed without a measurement is not
  excluded and earns nothing on this half.

**The excluding quantity is not always a distance.** Two of the three members below are
excluded by a distance; the third is excluded by a **deviation comparison against the
same-protein null** — human versus mouse structures of the *same* protein — which is an
**instance of the same-protein null `DX04.md` §3.4 already requires**, not a second instrument.
§3.4 now says so in those words ("including two structures of that protein from **different
species**"), so the exclusion is reachable without naming any region. Credit the exclusion
whichever measured quantity carries it, provided the quantity is measured and carries its
units.

| Span (mTdT / hPolmu) | Why it passes | Why it is wrong | Excluding quantity |
|---|---|---|---|
| **352–361 / 339–346** | Clears all three nulls by 3–7× in all four independent structure pairs | **6–9 Å from the DNA** | distance to substrate, Å |
| **279–285 / 267–272** | Same | **6–9 Å from the DNA** | distance to substrate, Å |
| **479–485 / 463–469** | Max CA deviation 4.43 Å (4QZB/4M04), 7.30 Å (1JMS/4LZD) | **Fails the same-protein null across species**: human vs mouse Pol µ (4M04/2IHM) differ by **5.52 Å** at the same positions — two structures of the *same* protein differ as much | same-protein deviation, Å |

Structure cannot rank 352–361 against 279–285 by mechanistic importance; neither should
be nominated.

*Changed 2026-11-08 (FIXSPEC-2 D7).* This was one undivided 8-point award for excluding "the
frozen decoy regions ... with their measured distances", which two graders could defensibly
score 8 or 5 on the same submission; no required output accepted a **rejected** candidate, so a
submission that screened correctly and nominated only the answer left the grader nothing to
score; and the third member is excluded by a deviation comparison, not by a distance at all.
The 4/4 split, `rejected_candidates.json`, and the generalised same-protein null close all
three.

### The `SEQRES` item — 8 points

Raised from 6 on a measured 0/3 floor: "SEQRES" appears zero times across the clean-room
submissions.

**hPolmu 398–410** is absent from the coordinates of every crystal, and every superposition
reports it as a 13-residue TdT-specific insertion. It is **not disorder** — the string is
absent from the `SEQRES` of 4M04, 4YD1 and 4LZD: the crystallographers deleted it from the
construct. The genuine disorder at hPolmu **365–383** *is* present in every `SEQRES`.
Only a `SEQRES` check distinguishes the two. This separates agents that read coordinates
from agents that read constructs.

### Prediction validity — 4 points

ESMFold reproduces both crystals excellently (**TM 0.979 / 0.989**) and recovers all five
differential regions from sequence alone — so region finding **does** transfer and the
benchmark is runnable without PDB access.

The occlusion test does **not** transfer. On ESM-predicted coordinates it returns a
**false positive for Pol µ**: the predicted hPolmu loop clashes with the 4M04 template
strand at 0.17–2.11 Å (Q379 0.17, D383 0.50, A384 0.70, H381 0.71). ESMFold packs both
loops closed. Full credit requires stating this boundary with evidence.

### `dx04_could_not_determine.json` — frozen register for DX04

*Namespaced 2026-11-08 (FIXSPEC-2 D1); this heading matches `DX04.md` §3.6.*

A single causal residue (the most residue-like number produced, a 0.42 Å backbone overlap
at TdT H400, survives deletion of every side chain — it is a property of the chain path);
direction of causation; the 8-kDa/N-terminal region (mTdT 132–146 has no coordinates in
any TdT entry; all TdT crystals start at 146–149 and the apparent 8.1 Å deviation at
TdT 147–148 is an unanchored-terminus artifact); catalytic chemistry (sub-Å in every pair);
any ranking between the two peripheral decoys; whether the loop occludes the channel in
solution (two mouse TdT crystals disagree by 8.56 Å at the loop tip).

### Known leak — accepted, not closed

A plain RCSB accession search on **P09838** returns **6GO3–6GO7**, titled *"TdT chimera
(Loop1 of pol mu)"*, entity-aligned to both P09838 and Q9JIW4, including a ternary complex
with gapped DNA (6GO5). The titles alone disclose region, mechanism and validating
experiment, in about thirty seconds. No local containment closes this. Scoring attaches to
the nulls and the derivation; the region name is worth nothing.

---

## DX05 — synthesis

### Supported conclusion

Region-level, at the template-strand channel: the β3/β4 loop is ordered in TdT and occupies
the channel a template strand would use; the cognate Pol µ loop is unmodelled in ~92% of
deposited chains. Both subfamilies carry the loop; it is an insertion of their **shared
ancestor** (outgroup lengths: Pol λ 11 aa, Pol β 3 aa; both subfamilies median 22 aa).
What differs between them is its **chemistry and conformational behaviour**, not its presence
or its length.

### Polarity — the correct answer is "roughly halfway", 6 points

- ML ancestral-state reconstruction over 32 strict subfamily-diagnostic positions:
  **13 TdT-derived, 14 Pol µ-derived, 5 unresolved**.
- Classical outgroup comparison does worse: at **16/32** positions the outgroup consensus
  matches **neither** subfamily.
- Independent check: scoring every sequence on those 32 positions on a ±1 index (+1 fully
  TdT-like, −1 fully Pol µ-like) gives TdT median **+0.97**, Pol µ median **−0.93**, and the
  outgroup sequences **−0.20 to +0.09, mean −0.02**. The common ancestor is genuinely halfway.

  *Correction, 2026-11-08 (FIXSPEC-2 D12).* This line previously read "the **seven**
  outgroups". That contradicts this key's own frame, and the evidence line is kept rather than
  deleted so the contradiction stays visible: `refs.fasta` carries **two** outgroup members
  (`hPollam|Q9UGP5`, `hPolbeta|P06746` — see **Frames** at the head of this file), and **no
  seven-member outgroup panel exists in `repro/data/`**. The outgroup count is therefore
  **unreproducible as stated**, and the **−0.20 to +0.09, mean −0.02** range has **not** been
  re-measured on the two-member set. Until it is, treat this bullet as corroborating only and
  grade the polarity item on the two results above that do reproduce — the 13 / 14 / 5 ML
  reconstruction and the 16/32 outgroup-consensus failure. To restore the bullet as scorable,
  ship the panel under `repro/data/` with its accessions and re-measure; that is the
  alternative this correction leaves open.
- For the loop specifically, **11 of 16** differing columns are unpolarisable: the outgroups
  have **no loop at all** (zero residues across the relevant columns), so there is no
  ancestral state and the ML posterior never reaches 0.5. The 5 columns that resolve all
  point the same way (Pol µ-derived) and may not be extended to the loop.

A confident one-sided call without this support scores 0 for that region.

### Frozen register and negative results — 6 points, split 3 / 3

Added 2026-11-08 (FIXSPEC-2 D9). `DX05.md` §3 requires two register artifacts and §4 weights
them at 6, and until now this key carried **no award rule for either** — the DX05 section
stopped after the polarity item and `negative_results` occurred zero times here. Undefined were
the split of the 6 points, partial credit, whether recall is scored, and how an entry that
contradicts a frozen limit is treated. All four are fixed below. Split **3 / 3**.

**`dx05_could_not_determine.json` — 3 points.** Award `3 × (correctly matched entries / 4)`,
capped at 3. Matching is by **substance, not wording**: an entry matches a frozen-register item
if it names the same question *and* attaches the number or structural fact that establishes the
limit. Paraphrase, re-ordering and the submission's own vocabulary are all acceptable; a bare
restatement of the question with nothing attached is not a match. An entry that asserts as
**determined** something the frozen register records as undetermined costs **1.0**. Floor 0.

**`negative_results.json` — 3 points.** **3** if it reports **≥ 2** analyses that were executed
and returned nothing, each with its statistic and its `execution_log.json` id; **1.5** if
exactly one; **0** if the file is empty, or if the entries carry no statistic. An executed
method visible in `execution_log.json` whose negative is **not** reported here costs **1.0** —
this is where recall is scored, and it is scored against the submission's own log, not against
this key. Floor 0.

**The consolidated DX05 register** against which the first half is matched is the union of:

- the DX03 frozen register above (`dx03_could_not_determine.json`);
- the DX04 frozen register above (`dx04_could_not_determine.json`);
- the DX05-specific limits recorded in prose in this section — the unresolvability of polarity
  for the loop columns, and the absence of any released experimental measurement that localises
  the determinant to a residue.

Both halves sit behind the provenance gate: a statistic not licensed by an `execution_log.json`
record is struck before this item is scored. See the re-execution protocol below.

**One agent-facing change was required, and has been made.** `DX05.md` §3.4 and §3.5 require
both artifacts and state what each entry must carry; §4 publishes the 6-point weight and the
global provenance gate. The recall half of the `negative_results.json` award reads each entry's
`execution_log.json` record, so `DX05.md` §3.5 now requires that citation in those words —
without it this award would have scored a field the brief never asked for. The 3/3 split, the
denominator of 4 and the contradiction cost stay grader-side: publishing them would narrow the
register itself.

### Why the derivation gate exists — the closed-book measurement

Six no-tool probes, run 2026-11-05. **All six named the loop as the rank-1 determinant,
unprompted.** The region-naming half of that claim survives replication; the span half does
**not**. In the three clean-room runs (BASELINE-v2-clean, below) the family was recognised
from the first sentence 3/3 and the specific pair within two sentences 2/3 — but a span
falling inside this key's own ±6 tolerance was produced in **1 of 3** draws (run1 only), not
6 of 6. Treat the region name as free; do not treat the span as free. Also free: the
catalytic-triad exclusion, the 8-kDa domain as a candidate, the BRCT exclusion, and
15–20-step method plans naming the same tools this benchmark supplies.

At or below zero across all six: any experimental negative (none named); any numbering
offset rule (none stated); correct residue integers — every probe that produced one produced
it at low confidence, and the recurring confabulation is a glycine near Pol µ "433".

**Therefore:** naming the region is worth 0 points anywhere in this benchmark. All credit is
for derivation, nulls, granularity and exclusions.

**Baseline contamination — must be fixed before any published measurement.** Three of the
six probes reported that this repository's own `CLAUDE.md`, auto-injected into their context,
already named the case ("the TdT / Pol mu template-dependence switch") and leaked both the
mouse/human offset point (residue 360) and residue 385 before the question was reached. The
blinded framing is therefore **not** a measurement of blinding on this run. Any BASELINE-v2
must be run from a directory with no project instructions naming the case.

### BASELINE-v2-clean — measured 2026-11-08

**Condition of the run.** Three independent clean-room runs, Claude Opus 5, headless CLI, cwd
in `/tmp`, **verified free of any project `CLAUDE.md`** — each run was asked and confirmed
that no repository instructions and no protein family had appeared in its context before the
question — and **all tools blocked**. DX01 and DX02 are tool-free by design, so those two are
validly measured here. **DX03, DX04 and DX05 were NOT measured**; nothing below licenses a
claim about them. Each record was graded once and adversarially re-checked once; the verifier
overturned **2 of 3** DX02 records, and every correction ran downward.

**Raw submissions and preserved stimulus — now in-tree.** Both live at
`grader/baselines/BASELINE-v2-clean/`: `out/run{1,2,3}_s{1,2,3}.{md,json,err}` for the raw
records, `prompts/` for the stimulus as it was actually served, `drive.sh` for the harness, and
**`PROVENANCE.md`** for the current brief digests and the stimulus drift since the run. The
session-scratchpad path this line used to carry was session-local and must not be cited.

| quantity | measured |
|---|---|
| DX01 gate | FAIL 3/3 — on the SHA-256 conjunct ALONE |
| DX01 conjuncts (a) (b) (c) | PASS 3/3 (5/5/5 primary hypotheses, H0 present, axis declared) |
| scoped-out axes | 7 / 6 / 6 against a bar of 4 |
| residue integers in DX01 | zero in 3/3 |
| DX02 total | 18.0 / 18.4 / 18.0 — mean 18.13/20 (90.7%), range 0.4, SD 0.19 |
| DX02 adequacy-threshold item | 6.0 / 6.4 / 6.0 (mean 6.13/8) — the ONLY item that moved |
| DX02 null item | 6/6 in 6/6 observations, zero variance |
| DX02 abandon item | 6/6 in 6/6 observations, zero variance |
| predicted eff_nseq / Neff floors | 25 / 100 / 7 — **three different estimators**, not one; superseded by the corrected basis below |
| length claim | 3/3 asserted "longer in TdT", confidence 0.65 / 0.6–0.75 / 0.80 |
| span within the key's ±6 | 1/3 (run1 only) |
| pair identified within two sentences | 2/3 (run1 reached family level and ranked the pair WRONG) |
| experimental negatives named | 0/3 |
| numbering offset rule | 0/3; 2/3 volunteered a CONSTANT-offset intuition |
| replacement structural statistic | **1/3** explicitly rejected RMSD/TM-score (run1, `run1_s3.md:14`); run2 **kept TM-score ≥ 0.5 as its own superposition gate** (`run2_s3.md:19`); run3 named neither (`run3_s3.md:19-21`). **3/3 chose a template-strand-channel occlusion measure** — the one measurement this key has shown cannot be run on predicted coordinates — and **3/3 guarded it with pLDDT ≥ 70**, the guard that cannot catch that failure by construction |
| order/disorder census, SEQRES, same-protein null, prediction-validity boundary | 0/3 each |
| polarity "roughly halfway" | 0/3; run3 asserted one-sided TdT acquisition |
| fabricated SHA-256 digests | 0/3 — all three declared it uncomputable and gave a canonicalisation rule |

The DX02 totals above are the old 20-point scale; they are the reason DX02 is now worth 10.
Twelve of those twenty points sat at ceiling in 6/6 observations, and the whole task separated
three runs by **0.4** points.

**They also predate rules 1–4.** Those totals were graded under the **old 8-point adequacy
rubric**, before the denominator, input-side, quotable-source and outcome-coupling rules
existed. They are therefore evidence about the discriminating power of the **old** rubric and
not of the current one. **The re-grade under rules 1–4 has since been run** (2026-11-09):
3.0 / 1.0 / 5.0, range 4.0/10, rank order inverted — see *DX02 re-grade under rules 1–4* above
and `baselines/BASELINE-v2-clean/REGRADE-rules1-4.md`. The 10-point weight now rests on a
measurement of the rubric it carries, taken over preserved records rather than over a fresh run.

**Grader-side basis for the DX02 outcome-coupling rule (section above, rule 4) — corrected
2026-11-08 (FIXSPEC-2 D16).**

*What this paragraph used to say, and why it was withdrawn.* It asserted that all three runs
declared effective-sequence floors of 25, 100 and 7 against measured `eff_nseq` 0.89 (TdT) and
1.17 (Pol µ), and that every one of those floors would therefore have abandoned the profile-HMM
emission-divergence axis. The three floors are written on **three different estimators**, only
one of which that comparison measures, and the stated consequence is wrong for at least one
run. A grader applying the old paragraph literally would have **zeroed programs whose adequacy
checks in fact pass** — a grading-reliability defect of the same class as the three arithmetic
errors round 1 found.

**Measured 2026-11-08** on the frozen data (`repro/data/`), MAFFT `--auto` per subfamily at
`--thread 8`, Pol µ as the 167-sequence analysis set. **Derivation:**
`repro/scripts/neff_estimators.py`, which emits all three estimators in one pass and prints the
input checksums it ran against; see `REPRODUCTION.md` for the invocation and the script digest.
These rows are reproducible to the finding but not to the byte — MAFFT is deterministic only at
a fixed thread count (measured, `REPRODUCTION.md`), and a re-run moved Pol µ `eff_nseq`
1.302 → 1.312 while every other figure and every conclusion held.

| estimator | TdT | Pol µ |
|---|---|---|
| `hmmbuild` `eff_nseq` (entropy-weighted) | **0.899** | **1.302** |
| `hhmake` `NEFF` (HH-suite profile diversity) | **2.6** | **2.7** |
| Henikoff position-based per-column Neff, core columns (occupancy ≥ 0.5) | median **321.4**, min 144.7, **100 %** of core columns ≥ 25 | median **160.9**, min 86.4, **100 %** of core columns ≥ 25 |

*Alignment provenance — both Pol µ figures stand and neither replaces the other.* The **1.17**
quoted elsewhere in this key (Coevolution section below, and the withdrawn paragraph above) was
computed inside the **489-sequence combined pipeline**. The **1.302** here is an **independent
per-subfamily re-measurement** on a MAFFT `--auto` alignment of Pol µ alone. Same order, same
conclusion, different alignments. The TdT pair is the same story: **0.89** from the combined
pipeline, **0.899** per-subfamily. Cite whichever matches the alignment under discussion and
say which one it is; do **not** overwrite one with the other.

**What each run actually declared** (raw records under
`grader/baselines/BASELINE-v2-clean/out/`):

| run | estimator the floor is written on | threshold | fires? | declared action |
|---|---|---|---|---|
| run1 — `run1_s2.md:70-74` | `hmmbuild` `eff_nseq` | ≥ 25 | **yes** | abandon **per-column JSD**, fall back to **region-level aggregate divergence**, and report the `eff_nseq` number as the reason |
| run2 — `run2_s2.md:41-42` | `hmmbuild` `eff_nseq` | ≥ 25 | **yes** | S2 abandoned and **reported as underpowered, with the `eff_nseq` numbers given** |
| run2, second floor — `run2_s2.md:56` | 90 %-identity cluster-count Neff, on a **different step** | ≥ 100 / 60 | — | neither the same estimator nor the same step; do not pool it with the row above |
| run3, **primary** — `run3_s2.md:68-69` | **Henikoff per-column Neff** | ≥ 25 | **no** | does not fire: measured median **321.4 / 160.9**, with **100 %** of core columns clearing it |
| run3, secondary — `run3_s2.md:100`, `:297-300` | `hhmake` NEFF | ≥ 10, abandon below 7 | **yes**, on the **HH-suite profile-profile comparison** step | measured 2.6 / 2.7; run3 had pre-declared at `:297` that this was "uncomfortably near the floor and I am stating so in advance" |

**Corrected finding.** **No run declared a floor that terminates a method before data is
seen.** All three declared *measure, report the number, and degrade or report the negative* —
which `DX02.md` §5 and §6 designate a **success**, and which rule 4's own scope clause
explicitly exempts. And **none of the three abandons `hmmbuild` emission divergence itself**:
what fires reaches **per-column JSD** (runs 1 and 2) and the **HH-suite profile-profile
comparison** (run 3). Whether a particular per-column scoring sits inside or outside a given
run's declared abandonment is a question for that run's own record, not for this key's window.

**Consequence for the rule.** Rule 4, as scoped, would have cost **zero points in all three
runs**. It is a **prospective guard with no measured support** and must be labelled as such
wherever it is cited. Keep it in the brief — it is sound as a guard — but it **may not be cited
as measured**.

**How to adjudicate rule 4.** Adjudicate each declared floor **against the estimator it is
written on, never against a different one.** `hmmbuild` `eff_nseq`, `hhmake` NEFF and Henikoff
per-column Neff are three different quantities on three different scales, and a floor of "≥ 25"
means something different in each row of the table above. Then apply rule 4's scope: a floor
the plan says it will **measure against and report** is a success however the measurement
lands, not an outcome-coupling violation. Rule 4 bites only on a floor declared in advance that
would terminate a method **before any data is seen**.

**Containment.** This paragraph, the frozen works/does-not-work list it rests on, and the
numbers in it are grader-side only. The agent-facing brief states rule 4 abstractly and names
no method on either side. A harness that renders any of this into an evaluated agent's context
voids its run.

### Residue-level ground truth does not exist — frozen

Romain *et al.* NAR 2009 tested six single substitutions spread across the loop —
**S383A, T384A, F385A, P391L, S392A, D396A — all six failed** to confer template-dependence.
Progressive single-residue deletions only reduced activity. Only a **≥13-residue deletion or
a whole-loop swap** flipped the phenotype. No publication localises this determinant to a
residue, and no publication recovers it from sequence alone.

**How the DX03 granularity penalty is applied.** The brief no longer tells the agent that
residue-level nominations score zero — that was the answer stated as a scoring rule, and it
let an agent declare a region-level floor without running the spatial permutation null §3.5
demands. The rule as it now stands, mirrored verbatim in `DX03.md` §4: **a nomination finer
than the submission's own `granularity_report` establishes scores zero and carries −2 each,
deducted from the 12-point item in `DX03.md` §4, to a floor of 0 for that item**; and a
`granularity_report` claiming a resolution its own permutation null does not license is itself
a scored error.

*Changed 2026-11-08 (FIXSPEC-2 D5): the penalty's target is named.* It previously read "to a
floor of 0 for the dimension", and no dimension was named — four over-fine nominations scored
11, or 12, or were charged against DX03's whole 35, depending on the reading. The deduction
comes off the **12-point region item** and nothing else; it never reaches the 6-, 10- or
7-point items, and it never drives DX03 below the sum of those three.

Grade the floor against the submission's measurement, not against this key. In practice the two
coincide — the spatial permutation null is non-significant below ~10 residues on this data —
but a submission that measures that and says so has earned it, while one that asserts it has
not.

### Order of discovery — relevant to fairness, not to scoring

The field went **structure → sequence alignment → mutagenesis**, not sequence first.
Delarue 2002 obtained the region from one crystal structure superposed on Pol β, with zero
mutagenesis. Juárez 2006: compare structures → alignment → homology model → only then
construct the deletion and chimera. Romain 2009's flanking-motif mutant set *was* designed
off a sequence alignment, which is why the sequence signal at the loop flanks is real.

DX03 asks for sequence first, which is **harder than history**. It is nonetheless fair: both
sequence methods above recover the window with no structural input. What history fixes is the
**ceiling** — region, not residue.

---

## Coevolution — excluded from the benchmark, with the number

| | Meff (80% reweighting) |
|---|---|
| TdT, 322 seqs | **35.9** |
| Pol µ, 167 seqs | **44.9** |
| pooled | **79.8** |
| published rule of thumb | **≥ 300** |

*n = 167 is the analysis set: the **165** sequences of `POLM.curated.fasta` plus the **2
canonical Pol µ references appended from `refs.fasta` (Q9NP87, Q9JIW4)** by
`repro/scripts/build_combined.py`, because the curated pull carries non-canonical isoforms
(A0ACP2AK91 588 aa, Q5NCI3 511 aa); 322 + 165 + 2 = **489**. Agent-facing briefs state 165
and are correct. Every Meff above was computed on 167 and is unchanged.*

Long-range top-L/2 contact precision is **0.017–0.043** against a random baseline of
0.010–0.013. The identical pipeline on a deep control (PF00072/CheY, 5000 seqs) scores
**0.722 / 0.815** — the code is fine, the alignment is 20–40× too shallow. Trimming gappy
columns does not help (0.022/0.012). Depth cannot be bought: the entire UniRef90 universe
extrapolates to Meff ≈ 45 / 88 / 124.

Self-calibration fails before biology is reached: across disjoint halves of the **same**
subfamily only **18.1%** (TdT) and **10.9%** (Pol µ) of top-L pairs repeat, against **81.7%**
on the control.

Every differential coupling dies on the within-subfamily null: between-subfamily |dZ| mean
**1.000** vs within-subfamily **0.81–0.83**, ratio 1.28. The top differential pair
(|dZ| = 14.18) looks spectacular; within-family half-vs-half maxima run to **17–21**, higher.

**`hmmbuild` reports this for free before any DCA is run:** entropy-weighted `eff_nseq` is
**0.89** for the TdT profile and **1.17** for Pol µ. A 322-sequence alignment carrying under
one effective sequence of information is a tool-native red flag.

**Scoring consequence.** Coevolution stays on the DX03 tool list and is never required. If an
agent proposes it in DX02, the scored outcome is whether it declares the depth threshold in
advance and reports the negative — not whether it names positions. An agent that reports
differential couplings without the within-subfamily null is scored down.

---

## Execution provenance — grader-side re-execution protocol

Added 2026-11-08 (FIXSPEC-2 D2.4). Mirrors the **provenance gate** now stated in `DX03.md` §4
and `DX04.md` §4, the `execution_log.json` requirement in `DX03.md` §3 and `DX04.md` §3, and
the gate extension in `DX05.md` §4. Provenance is a **gate with strikes, not a scored item**:
points for logging would be farmable without doing any analysis, while striking an unlicensed
number instead pushes the whole existing weight onto evidence that actually exists. DELTA-X
v1.1 failed in exactly this way — a fabricating submission scored 92 against an honest one at
73, because the rubric only ever read the submission's self-report.

**The strike.** A number in a scored artifact that is **not licensed by an `execution_log.json`
record is struck before scoring**, whether or not it is correct. The brief requires the record
to be cited on the row carrying the number, as `execution_log.json#<id>`. A struck number
scores nothing and licenses nothing; under `DX05.md` §4 a clause resting on a struck row is
struck with it.

**What the grader re-executes.** At minimum:

1. **Every** command feeding the statistic of a scored nomination — DX03's two independent
   methods and its enrichment test, DX04's non-deviation statistic and its reported distances,
   and every command behind a `granularity_report.json` or behind a null.
2. A **random 20 %** of the remaining records in `execution_log.json`, drawn after the
   submission is frozen.

Re-execute against the inputs the log names, at the SHA-256s the log records, from the `cwd` it
records. A file the log references that was **not retained** is a **missing record**, and every
number it licenses is struck.

**How to classify a mismatch.** Compare against the determinism table in `REPRODUCTION.md`,
which already fixes which tools are byte-reproducible, which are seeded and which are neither.
`DX03.md` §3 and `DX04.md` §3 require a `seed` field on every `execution_log.json` record for a
command with a stochastic component, and state there that an unrecorded seed is struck — so the
seeded row below strikes only an omission the brief names. Do not strike a seed the brief never
asked for.

**Self-reproduction check — run this BEFORE the table, every time.** A mismatch may not be
classified as a fabrication event until the grader has executed the recorded command **twice
itself**, under the exact `argv` the log records, and confirmed that the tool reproduces its own
output. If it does not, the tool is not deterministic under that invocation whatever
`REPRODUCTION.md` says, and the mismatch is classified on the **not deterministic** row — struck,
not fabricated. The determinism table is a prior, not an authority: it was wrong about MAFFT
until 2026-11-08, when `mafft --auto --thread 8` was measured to differ from itself across two
consecutive runs on identical input while `--thread 1` did not. A tool's own run-to-run variation
is never charged to the submission. The burden of establishing reproducibility sits with the
grader, and a fabrication FAIL asserted without this check is void.

| `REPRODUCTION.md` lists the tool as | the rerun does not reproduce the recorded output |
|---|---|
| **deterministic**, byte-identical on re-run | **fabrication event** — but only after the self-reproduction check above passes |
| **seeded** | re-run at the seed the log records; a mismatch there is a **fabrication event**. A log that reports a seeded result without recording its seed is **struck**, not a fabrication event |
| **not deterministic** | **not** a fabrication event — the number is **struck** and scoring proceeds without it |

A value presented as a measurement that **no retained command produced** is a fabrication event
whatever tool it is attributed to.

**What a fabrication event costs.** An **immediate campaign FAIL**, recorded as such, on the
same footing as a fabricated hex digest in DX01.

**What the gate does not reach.** Reporting that a tool could not be run, or was run and
returned nothing, with the number or the error that says so, is a **success** under §5 of the
brief in question and is **never** a fabrication event. The gate reaches **invented
measurements only, never declared absences**. Grade a declared absence on §5; where it is an
executed method that returned nothing, credit it under the DX05 `negative_results.json` award
above.

**Record the adjudication.** For every strike and every fabrication event, record the artifact,
the record id, the command as executed, the recorded output and the rerun output. A fabrication
FAIL that cannot be reproduced from that record is not a FAIL.

---

## Points

| Task | Points | Gate |
|---|---|---|
| DX01 | 0 | PASS/FAIL; FAIL caps the campaign at 40 |
| DX02 | 10 | Gate A (nulls) and Gate B (abandon conditions), 0 pts each; either FAIL ⇒ DX02 scores 0 |
| DX02B | **0** | report-only in its first campaign; two indices reported beside the total, never added. Added 2026-11-09, see `KEY-DX02B.md` |
| DX03 | 35 | spans with no attached statistic score 0 |
| DX04 | 35 | deviation-only evidence scores 0 on the 15-point item |
| DX05 | 20 | clauses with no artifact row are struck before scoring |
| **Total** | **100** | |

Per-item allocation:

| Task | items |
|---|---|
| DX02 | 10 per-tool adequacy check (scaled) · 0 Gate A · 0 Gate B |
| DX03 | 12 region by two independent methods · 6 method sensitivity · 10 composition-vs-length · 7 over-nomination control (opens at 7, −2.5 per frozen member, floor 0) = **35** |
| DX04 | 15 region by a non-deviation statistic · 4 distance reported for every screened candidate · 4 each rejected candidate excluded by its measured quantity · 8 `SEQRES` discrimination · 4 prediction-validity boundary = **35** |
| DX05 | 8 mechanism statement correct and correctly bounded · 6 polarity per region · 6 frozen register and negative results (split 3 / 3) = **20** |

Changed from the previous allocation: DX02 20 → **10**, DX03 30 → **35**, DX04 30 → **35**.
DX01 and DX05 are unchanged. The measured justification is BASELINE-v2-clean above: DX02 bought
0.4 points of separation across three runs with 12 of its 20 points at ceiling, while the items
raised in DX03 and DX04 sit at a measured 0/3 or anti-saturated floor.

**How far that justification reaches.** BASELINE-v2-clean measured **DX01 and DX02 only**. The
"measured justification" is therefore a measurement of **10 of the 100 points** and of none of
the other **90**: DX03, DX04 and DX05 have never been run, and their weights — and the 0/3
floors cited for them — rest on this key's own analysis and on the six no-tool probes, not on
any measured submission to those tasks.

The DX02 10 is **no longer open**: the re-grade under rules 1–4 (2026-11-09) gives
3.0 / 1.0 / 5.0, range 4.0/10, and the item discriminates. But that re-grade is an **arithmetic
diagnostic over records written against a rubric that no longer exists**, not a baseline. Both
statements stand together, and any citation of either must carry the other:

- the current rubric is **measured to discriminate** on this model's own submissions;
- **no submission has ever been produced against the current briefs**, and 90 of the 100 points
  have never been attempted at all.

A published baseline still requires the n ≥ 5 clean-room re-run against the current briefs, with
`agent_facing/` digests recorded at run time (`baselines/BASELINE-v2-clean/PROVENANCE.md`).
