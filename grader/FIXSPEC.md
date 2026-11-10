# FIXSPEC — authoritative decisions for fixes 1+2+3 (2026-11-08)

> **Paths.** This document was written against the private working tree. On release `agent_facing/` became `tasks/` and `repro/data/` became `data/`; nothing else moved. See `docs/PATH-MAP.md`. The text is otherwise unedited.

Every agent editing a file MUST take its numbers from this file. Do not re-derive, do not
round differently, do not invent wording for a number that is fixed here.

## Evidence this rests on — BASELINE-v2-clean, measured 2026-11-08

Three independent clean-room runs, Claude Opus 5, headless CLI, cwd in /tmp, **verified
free of any project CLAUDE.md** (the run was asked and confirmed no repo instructions and
no protein family appeared in its context), **all tools blocked**. DX01 and DX02 are
tool-free by design, so these two are validly measured; DX03/DX04/DX05 were NOT measured.
Each record graded once and adversarially re-checked once; the verifier overturned 2 of 3
DX02 records and every correction ran downward. Raw submissions:
`/tmp/claude-185725/-home-hew-python-EvoAgenda/f3191739-9044-46f9-9033-89db443abdf7/scratchpad/baseline_v2/out/`
(run{1,2,3}_s{1,2,3}.md).

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
| predicted eff_nseq / Neff floors | 25 / 100 / 7 — against measured 0.89 and 1.17 |
| length claim | 3/3 asserted "longer in TdT", confidence 0.65 / 0.6-0.75 / 0.80 |
| span within the key's +/-6 | 1/3 (run1 only) |
| pair identified within two sentences | 2/3 (run1 reached family level and ranked the pair WRONG) |
| experimental negatives named | 0/3 |
| numbering offset rule | 0/3; 2/3 volunteered a CONSTANT-offset intuition |
| order/disorder census, SEQRES, same-protein null, prediction-validity boundary | 0/3 each |
| polarity "roughly halfway" | 0/3; run3 asserted one-sided TdT acquisition |
| fabricated SHA-256 digests | 0/3 — all three declared it uncomputable and gave a canonicalisation rule |

## FIX 1 — the DX01 hash gate (it fired 3/3 for a harness reason, not a capability one)

DX01 section 2 blocks tool use; section 3.5 demanded a SHA-256; section 4 made a
non-matching hash a FAIL. A tool-free model cannot compute SHA-256. Replace with a
conditional commitment:

- Section 3.5 becomes `prereg_commit`, satisfiable two ways:
  (i) **tools available** — a deterministic SHA-256 over the exact bytes of the four
      artifacts, excluding itself, as before; or
  (ii) **tool use blocked** — a `prereg_commit.json` carrying `digest: null`, a
      `digest_status` naming the constraint, a **byte-exact canonicalisation rule**
      (file order, encoding, separator, trailing-newline policy) and a reference command.
      The harness then computes the digest over the emitted artifacts under that rule and
      that value becomes the commitment.
- Section 4 FAIL criterion (d) becomes: FAIL if no commitment is present, or if a
  harness-computed digest does not match at campaign close.
  **A declared-uncomputable digest accompanied by a deterministic canonicalisation rule is
  NOT a FAIL. Emitting a fabricated hex digest is an immediate FAIL** and is recorded as a
  fabrication event. (Measured: 0/3 fabricated; all three produced exactly form (ii).)
- The 40/100 FAIL cap is unchanged.

Also in DX01 section 6, the blinding claim is overstated and must be corrected to the
measurement: say that in three clean-room runs the family was recognised from the first
sentence in 3/3 and the specific pair within two sentences in **2 of 3**, the third
reaching family level only and ranking the pair wrong, with the correct pair at rank 2.

## FIX 2 — the 165 / 167 provenance (NOT a data error; a labelling omission)

`POLM.curated.fasta` really holds **165** sequences; that number stays in every
agent-facing brief. The key's `n = 167`, `Pol mu, 167 seqs` and the 489-sequence alignment
are the **analysis** set: 165 curated + the **2 canonical Pol mu references appended from
`refs.fasta` (Q9NP87, Q9JIW4)** by `repro/scripts/build_combined.py`, because the curated
pull carries non-canonical isoforms (A0ACP2AK91 588 aa, Q5NCI3 511 aa). 322 + 165 + 2 = 489.

- Every `167` in `grader/KEY.md` gets that parenthetical on first use in its section.
- `REPRODUCTION.md` states the composition rule once, explicitly.
- DX02 section 2 and DX03 section 2 keep 165/322 and add one sentence: `refs.fasta`
  contains two Pol mu references, and adding them to the Pol mu set is a legitimate
  analysis choice that reproduces the key's n.
- Do NOT change any measured value. The numbers were computed on 167 and stay as they are.

## FIX 3 — reweighting, justified by the measured separation

DX02 at 20 points bought 0.4 points of separation across three runs while 12 of its 20
points sat at ceiling in 6/6 observations. New allocation, which MUST sum to 100:

| Task | old | NEW |
|---|---|---|
| DX01 | 0 (gate) | 0 (gate) — unchanged |
| DX02 | 20 | **10** |
| DX03 | 30 | **35** |
| DX04 | 30 | **35** |
| DX05 | 20 | 20 — unchanged |

### DX02 — 10 points, one scaled item and two gates

- **Gate A (0 pts, PASS/FAIL).** Every differential statistic carries a null that is not a
  label reshuffle, and at least one is a **within-subfamily split-half** null. FAIL => DX02
  scores 0 for the task.
- **Gate B (0 pts, PASS/FAIL).** Every tool-bearing step carries an abandon condition that
  some possible result could trigger. FAIL => DX02 scores 0 for the task.
  (Both were at full credit in 6/6 observations: they behave as gates, not as scales.)
- **Scored item — 10 points. Per-tool adequacy check.** Each proposed tool must carry a
  check on whether the INPUT can support the method, with a numeric threshold declared in
  advance and a source. Three rules that were previously implicit and are now explicit,
  because all three grading errors came from their absence:
  1. **Denominator and rounding.** The unit is one **named executable program**, not a plan
     step. Award `10 * (qualifying programs / programs proposed)`, **rounded down to the
     nearest 0.5**.
  2. **Input-side only.** A check whose quantity is an output of the step it gates is not
     an adequacy check and scores 0 for that program. This rule already existed in section
     5 and was applied inconsistently; it now sits in the scoring table. Named examples
     that score 0: gating a structure predictor on its own pLDDT or PAE; gating a search on
     its own E-value; gating an aligner on a column-reliability score that requires running
     the aligner.
  3. **Sources must be quotable.** A threshold needs a number plus a locator a grader can
     check. A plausible attribution to a document that does not state the number scores 0
     for that program.
  4. **Outcome coupling.** A declared threshold that would abandon a method that
     demonstrably works on this data scores 0 for that program, however well sourced.
     **CONTAINMENT — the agent-facing brief states this rule ABSTRACTLY and names no
     method on either side.** The brief says only that the grader holds a frozen list of
     which proposed methods do and do not work on this input, measured, and that a
     threshold which would abandon a working one forfeits that program's credit.
     Grader-side basis, which stays in grader/KEY.md and must NOT appear in
     agent_facing/: all three runs set effective-sequence floors of 25, 100 and 7 against
     measured values of 0.89 and 1.17, so all three would have abandoned the profile-HMM
     emission-divergence axis — the key's best sequence method (top window mTdT 378-388,
     mean z 15.9, max z 27.6) — while correctly abandoning coevolution.
- **Still not scored:** plan length, breadth, literature coverage, step count, naming the
  right tools.

### DX03 — 35 points

| pts | item |
|---|---|
| 12 | region by two independent methods, both numbers attached, enrichment test (unchanged) |
| 6 | method_sensitivity (unchanged) |
| **10** | composition-versus-length resolved correctly, with the statistic (was 6) |
| **7** | over-nomination precision against the frozen set (was 6) |

The composition/length item rises because it is the only measured ANTI-saturated item:
3/3 clean runs asserted "the loop is longer in TdT" with no data at confidence up to 0.80,
and run3 pre-committed the error into its own DX02 plan. The key's measurement: TdT
42.55 +/- 0.86 vs Pol mu 42.29 +/- 3.67, median difference zero. Full credit still requires
variance and/or composition with a number; a length claim is still scored as an error.

### DX04 — 35 points

| pts | item |
|---|---|
| **15** | region found by a statistic other than per-residue deviation (was 12) |
| 8 | distance-to-substrate filter and decoy exclusion (unchanged) |
| **8** | SEQRES discrimination (was 6) |
| 4 | prediction-validity boundary (unchanged) |

Both rises are at a measured 0/3 floor: the order/disorder census was never mentioned in
any probe, "SEQRES" appears zero times, the 8.56 A same-protein null was recognised by
none, and one run named per-residue deviation as its single most trusted statistic.

### DX05 — 20 points, unchanged.

## Post-verification amendments (2026-11-08, after the four-verifier pass)

Four verifiers checked the landed fixes. Eleven containment leaks, one decidability gap in
FIX 1, one false clause in FIX 2 and six design defects in FIX 3 were applied. Two of those
go **beyond this spec's literal text** and are recorded here so the next editor does not read
them as drift:

1. **Rule 1's denominator is now defined**, not just its award expression. `programs counted`
   = max(named executable programs proposed, one per DX01-registered evidence axis), and a
   plan naming no executable program scores 0 rather than being undefined at 0/0. Reason: the
   bare ratio `10 × (qualifying / proposed)` makes the minimal plan optimal — breadth is
   explicitly not scored, so one safe program with one input-side threshold collects 10 × 1/1
   and every additional program can only lower the score. The award expression and the
   round-down-to-0.5 rule are unchanged.
2. **Rule 4's scope is now stated.** It reaches only a floor declared in advance that would
   terminate a method before any data is seen. A floor the plan will measure against and
   report, and a method executed and then reported inadequate with its number, stay successes
   under DX02 §5/§6. Without the scope the rule contradicted the brief's own success
   condition. Containment is unaffected: no method is named on either side.

**STILL OPEN — the DX02 weight is not yet earned.** The 10-point allocation rests on the
adequacy item being "the ONLY item that moved" (6.0/6.4/6.0, range 0.4) — but that was
measured under the **old 8-point rubric, before rules 1–4 existed**. The three
BASELINE-v2-clean records have not been re-graded under the new rules. First-order check on
the raw submissions: run{1,2,3}_s2 propose roughly **9 / 9 / 12** distinct named executable
programs, so rule 1's denominators do differ between runs and the item is not a priori
non-discriminating. That is a count, not a grade. **Before the weights are frozen, re-grade
all three DX02 records under rules 1–4, write the new range and SD into BASELINE-v2-clean,
and if the range is still ≈ 0, cut DX02 below 10 or convert it to a pure gate.** Do not
freeze on the old measurement.

## Out of scope for this pass — record, do not fix

- DX02 section 3.2's granularity requirement can be satisfied by a separability test that
  passes on the key's frozen decoys (E504 etc.) and fails inside the enriched region. Needs
  calibration against a spatial permutation null, or a stated floor in residues.
- "construct class" in DX01 section 3.4 is undefined and graders split on it in 3/3 runs.
- DX01 section 3.1 makes scoping out an axis a later stage needs a scored error, and 2/3
  runs scoped out material DX05 requires.
