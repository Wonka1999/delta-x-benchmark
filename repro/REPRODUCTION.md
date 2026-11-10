# Reproduction

> **Paths.** This document was written against the private working tree. On release `agent_facing/` became `tasks/` and `repro/data/` became `data/`; nothing else moved. See `docs/PATH-MAP.md`. The text is otherwise unedited.

**CONTAINMENT.** Designer-side. This file names structure accessions and the cross-species
numbering rule, both of which are scored. Nothing in it may be rendered into an evaluated
agent's context.

Every number in `grader/KEY.md` was produced on 2026-11-05 on this machine, except where a
later measurement date is stated below. This file records how to re-derive them.

## Inputs

`repro/data/`, checksums in `repro/MANIFEST.sha256`:

| File | Content |
|---|---|
| `TDT.curated.fasta` | 322 species-unique DNTT sequences, 460–591 aa |
| `POLM.curated.fasta` | 165 species-unique POLM sequences, 451–616 aa |
| `refs.fasta` | `mTdT\|P09838` 510, `hTdT\|P04053` 509, `bTdT\|P06526` 509, `hPolmu\|Q9NP87` 494, `mPolmu\|Q9JIW4` 496, `hPollam\|Q9UGP5` 575, `hPolbeta\|P06746` 335 |

**165 versus 167 — the composition rule.** `POLM.curated.fasta` holds **165** sequences,
and 165 is the number every agent-facing brief states. The key's `n = 167` is the
*analysis* set: `repro/scripts/build_combined.py` appends the two canonical Pol mu
references from `refs.fasta` (`Q9NP87`, `Q9JIW4`), because the curated pull carries
non-canonical isoforms (`A0ACP2AK91` 588 aa, `Q5NCI3` 511 aa). The combined alignment is
therefore 322 + 165 + 2 = 489 sequences. Every Pol mu number in the key was computed on
the 167-sequence analysis set and stands as measured.

Built from UniProt REST on 2026-11-05: `(gene:DNTT)` and `(gene:POLM)` restricted to
`taxonomy_id:7742`, `length:[400 TO 700]`, then one sequence per species (longest),
450–620 aa, ≤5 X. A re-run against a later UniProt release will not be byte-identical;
re-derive the key if the counts change materially.

## Tool paths on this machine

```
mafft     /home/hew/anaconda3/envs/bioflow_mafft/bin/mafft          7.525/7.526
hmmer     /home/hew/anaconda3/envs/bioflow_hmmer/bin/{hmmbuild,hmmalign,hmmsearch}   3.4
hhmake    /usr/bin/hhmake                                           HHsuite 3.1.0
pydca     /home/hew/anaconda3/envs/bioflow_pydca/bin/{plmdca,mfdca}
esmfold   /home/hew/anaconda3/envs/bioflow_esm/bin/python           torch 2.1.2+cu121
protenix  /home/hew/anaconda3/envs/protenix/bin/protenix
foldseek  /home/hew/anaconda3/envs/bioflow_foldseek/bin/foldseek
USalign   /home/hew/anaconda3/envs/bioflow_usalign/bin/
python    /home/hew/anaconda3/bin/python                            Bio, numpy, scipy, pandas, sklearn, torch
```

## Determinism

**Deterministic, byte-identical on re-run:** HMMER 3.4, `hhmake` (HHsuite 3.1.0),
mfDCA (closed-form), plmDCA (L-BFGS from fixed init), TMalign/USalign, foldseek, all
coordinate/`SEQRES`/contact parsing, ESMFold (eval mode, no sampling, given the same
`facebook/esmfold_v1` checkpoint).

**Deterministic only at a fixed thread count — MAFFT.** Corrected 2026-11-08; the
previous entry listing MAFFT as unconditionally byte-identical was wrong, and under the
re-execution protocol in `KEY.md` it would have branded an honest multithreaded run a
fabricator. Measured on `repro/data/POLM.curated.fasta` plus the two appended canonical
references (167 sequences), same binary, same input, same flags:

| invocation | two consecutive runs |
|---|---|
| `mafft --auto --quiet --thread 8` | **differ** |
| `mafft --auto --quiet --thread 1` | **identical** |
| `--thread 8` vs `--thread 1` | differ |

Downstream drift from one re-run at `--thread 8`: alignment columns 1546 → 1543,
`hmmbuild eff_nseq` 1.302 → 1.312, Henikoff core-column median Neff 160.9 → 161.2. The
conclusions do not move; the bytes do. Two consequences. **For the key:** any MAFFT-derived
number must record its thread count, and a re-derivation at a different thread count
reproduces the finding, not the digits. **For grading:** a MAFFT mismatch is a fabrication
event only if the command reproduces itself under its own recorded `argv` — see the
self-reproduction check in `KEY.md`'s re-execution protocol. `--auto` additionally selects
its strategy by input size, so changing the sequence count changes the algorithm.

**Seeded:** split-half membership `default_rng(1000+rep)`, rarefaction `default_rng(7)`,
PF00072 control subsample `default_rng(11)`. A seed set inside a script never appears in
`argv`, which is why `DX03.md` §3 and `DX04.md` §3 require a `seed` field on the
`execution_log.json` record itself; `KEY.md`'s re-execution protocol classifies a seeded
mismatch against this list.

**Not deterministic:** the literature axis. WebSearch result sets and WebFetch
summarisation both vary run to run, and three fetches failed on this run (ScienceDirect
403, Cell 403, PubMed cookie wall).

## Runtimes

MAFFT 6–23 s per alignment · column scoring ~66 s · plmDCA ~3 min per 510-column
subfamily at 16 threads · mfDCA ~50 s · hmmsearch of 2 profiles against 94 GB UniRef90
at 48 threads 26 min · RCSB search + download ~1 min · all superpositions <1 min ·
ESMFold ~3 min for both chains on the A100 plus a one-off 2.6 GB weight download.

## Scripts

`repro/scripts/` holds the scripts behind the sequence, profile-HMM and structural
numbers. They were written during the reproduction run and carry absolute scratchpad
paths; adjust the input paths before re-running. `RERUN.sh` drives the structural axis.

## Effective-sequence re-measurement (2026-11-08)

Three estimators of effective sequence number, re-measured on the frozen data in
`repro/data/`, Pol mu taken as the 167-sequence analysis set:

| estimator | TdT | Pol mu |
|---|---|---|
| `hmmbuild` `eff_nseq` (entropy-weighted) | 0.899 | 1.302 |
| `hhmake` `NEFF` (HH-suite profile diversity) | 2.6 | 2.7 |
| Henikoff position-based per-column Neff, core columns (occupancy >= 0.5) | median 321.4, min 144.7, 100 % of core columns >= 25 | median 160.9, min 86.4, 100 % of core columns >= 25 |

**Alignment provenance.** These three were computed on **per-subfamily MAFFT `--auto`
alignments**, not inside the 489-sequence combined pipeline that produced the key's
numbers. The key's Pol mu `eff_nseq` of 1.17 came from the combined pipeline; the 1.302
above is an independent per-subfamily re-measurement of the same quantity. Both are the
same order and carry the same conclusion: do not overwrite the key's 1.17 — both stand,
each cited with the alignment it was computed on.

The three estimators disagree by two orders of magnitude on identical data, which is the
reason this table exists: a declared adequacy floor is only interpretable against the
estimator it is written on, and must be adjudicated against that estimator and no other.

**Derivation status — scripted 2026-11-08.** `repro/scripts/neff_estimators.py` emits all
three estimators from `repro/data/` in one pass: it rebuilds the two analysis sets (Pol mu as
165 curated + the two canonical references, matching `build_combined.py`), aligns each with
MAFFT `--auto`, reads `eff_nseq` from the `hmmbuild` output, `NEFF` from the `hhmake` profile,
and computes Henikoff position-based weights in closed form, summing them over the non-gap rows
of each column. It prints the input checksums it ran against.

```
python3 -I repro/scripts/neff_estimators.py repro/data <work_dir>
sha256  c0c254f731fd1751b20c1f4bd549ddb28bdf7e48d9acd1b1038866419c73ec3a  repro/scripts/neff_estimators.py
```

Re-run 2026-11-08 at `--thread 8`, against the first measurement: `hhmake` NEFF **2.6 / 2.7**
and the Henikoff core-column medians **321.4 / 161.2** reproduce; `hmmbuild eff_nseq` lands at
**0.899 / 1.312** against **0.899 / 1.302** first time. The Pol mu drift is the MAFFT thread
non-determinism recorded above, not a code difference. **Report these rows with their thread
count, and treat the digits as reproducible to the finding, not to the byte, unless the
alignment step is pinned at `--thread 1`.** The conclusion the rule-4 adjudication rests on —
that run3's primary floor of Neff(c) >= 25 is cleared by every core column in both subfamilies,
by more than an order of magnitude — is invariant across every run measured.

## Baseline provenance — BASELINE-v2-clean

Measured 2026-11-08. Three independent runs of Claude Opus 5, driven through the headless
CLI from a clean `/tmp` working directory that carried no project `CLAUDE.md`, with all
tools blocked. Only DX01 and DX02 were run; DX03, DX04 and DX05 were not
measured.

**DX02 is tool-free by design and was validly measured. DX01 was not.** As DX01 stood at
measurement time, section 3.5 demanded one unconditional SHA-256 digest while section 2
blocked every tool, so the gate was unsatisfiable under the measurement condition — which
is why all three runs FAILed it. That FAIL is a harness artefact, not a capability result:
all three declared the digest incomputable and supplied a canonicalisation rule, and none
fabricated one. Section 3.5 now takes a two-form conditional commitment, so the criterion
these runs FAILed no longer exists. DX01 as it **now reads** is tool-free and would be
measured validly under this condition; DX01 **as measured** was not, and this file no
longer claims otherwise.

**DX01 and DX02 were both revised after this measurement.** DX02 went from 20 points to 10,
its null-hypothesis and abandon-condition items became 0-point PASS/FAIL gates, and four
scoring rules (denominator and rounding, input-side only, quotable sources, outcome
coupling) were added that these runs never saw. The three records are therefore **not a
baseline for the current briefs**; re-grading them under the current rules is an arithmetic
diagnostic. The 10-point DX02 weight rests on the old 20-point rubric and is not yet earned
— it must not be frozen before a re-run against the current briefs.

Each run emitted its artifacts inline rather than writing files. The raw records and the
measured stimulus are preserved at `grader/baselines/BASELINE-v2-clean/`:

```
prompts/s{1,2,3}.txt                    the MEASURED stimulus - NOT the current briefs
out/run{1,2,3}_s{1,2,3}.{md,json,err}   raw submissions and CLI records
drive.sh                                the clean-room driver
PROVENANCE.md                           SHA-256 of the CURRENT briefs, plus the stimulus drift
```

No digest of the measured briefs exists — they were not hashed before the edits, so
`prompts/` is the only surviving reconstruction of what the three runs read.

Each record was graded once and adversarially re-checked once; the verifier overturned 2
of 3 DX02 records and every correction ran downward.

**This run is not deterministic.** A model's free-text submission varies run to run, so
re-running these three reproduces neither the submissions nor, necessarily, the scores.
The tool paths and seeds above govern the key, not this baseline.

## Caveats on the key

- The loop span tolerance (±6) exists because three mutually incompatible boundaries are
  published for the same element in the same species and frame. Do not narrow it.
- The over-nomination and decoy sets are frozen *as measured here*. If the dataset is
  rebuilt from a different UniProt release, re-measure them before scoring against them.
- `6GO3` and `6GO5` number the same chimera differently (+1 after the loop; 6GO5 runs to
  511 rather than 510), and the paper renumbers one Gln as `393B` to hold the TdT frame.
  Any structural coordinate taken from those entries must state which one.
- Three of six closed-book probes were contaminated by the repository `CLAUDE.md`. The
  baseline numbers in the key that depend on *blinding* are therefore not valid; the
  numbers that depend on *what is named unprompted* are, since contamination only adds.
  This caveat stays. The BASELINE-v2-clean runs above replace the blinding-dependent part of
  that probe set for **DX02 only**, and for DX01 only its conjuncts (a), (b) and (c) — the
  DX01 gate as measured was unsatisfiable, so its FAIL replaces nothing. For DX03, DX04 and
  DX05 the 2026-11-05 probes remain the only evidence and the caveat is still in force.
