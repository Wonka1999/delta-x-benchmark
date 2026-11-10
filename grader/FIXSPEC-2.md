# FIXSPEC-2 — round 2 remediation decisions

> **Paths.** This document was written against the private working tree. On release `agent_facing/` became `tasks/` and `repro/data/` became `data/`; nothing else moved. See `docs/PATH-MAP.md`. The text is otherwise unedited.

**CONTAINMENT.** Designer-side. Nothing in this file may be rendered into an evaluated
agent's context.

Authoritative decision record for the round-2 fixes. Supersedes nothing in `FIXSPEC.md`;
it closes the defects that round-1 left open plus those found by the 2026-11-08 readiness
audit (6 dimensions, 36 findings, 24 surviving adversarial verification).

Implementers: apply the **literal replacement text** in this file. Do not paraphrase, do not
improvise a different convention, and do not add any fact about the answer to
`agent_facing/`. Where a decision touches both a brief and `KEY.md`, both sides must end up
stating the same rule in the same terms.

---

## D0 — Standing constraint on every edit below

The benchmark is baseline-subtracted: naming the region is worth **zero**, and every point is
for derivation, nulls, granularity and exclusions. Therefore:

- **Disclosing a rule of the game is required.** A scored quantity the agent cannot see is a
  measurement defect, not containment.
- **Disclosing the answer is forbidden.** No edit may state or narrow: the region, its span,
  the number of differential regions, the identity or count of the frozen decoys, the
  statistic that resolves the composition-versus-length question, a distance, a residue
  integer, the outcome of any null, or a maximum nomination count.
- Any §5 "scientific constraints" sentence that states a **conclusion** the frozen registers
  pay for must be rewritten as an **obligation**. The test: does the sentence tell the agent
  what it will find, or what it must do? Keep the second, delete the first.

---

## D1 — Record identity and citation format  (closes M6)

**Problem.** `DX05.md:27-29` strikes any clause not cited "by file and row", and 10 of the 12
DX03/DX04 artifacts are JSON objects with no record identifier. "Row" is undefined for JSON.
Separately, `could_not_determine.json` is required by DX03, DX04 and DX05 against two
differently frozen registers, with no namespace — a citation cannot be resolved to a task.

**Decision.** Insert this paragraph verbatim at the head of section 3 in **DX03.md**,
**DX04.md** and **DX05.md**, immediately under the `## 3. Required outputs` heading:

> **Record identity and citation.** Every `.json` artifact in this section is a top-level JSON
> **array of records**. Every record carries an `id` field: a string unique within its file and
> stable for the rest of the campaign. Every `.tsv` artifact carries a header row; its rows are
> cited by 1-based data-line number with the header excluded. Cite a JSON record as
> `<filename>#<id>` and a TSV row as `<filename>#L<n>`. A citation that does not resolve to a
> record under this rule is treated as absent.

**Namespacing.** Rename the colliding artifact per task:

| was | becomes | in |
|---|---|---|
| `could_not_determine.json` | `dx03_could_not_determine.json` | DX03 §3.6, §6 |
| `could_not_determine.json` | `dx04_could_not_determine.json` | DX04 §3.6 |
| `could_not_determine.json` | `dx05_could_not_determine.json` | DX05 §3.4, §4, §5 |

`KEY.md` headings at the DX03 and DX04 frozen registers must be renamed to match.

---

## D2 — Execution provenance and fabrication  (new requirement, 2026-11-08)

**Problem.** Nothing in v2 ties a reported number to a command that produced it. The grader
reads the agent's own artifacts and has no way to tell a measured value from an invented one.
DELTA-X v1.1 failed in exactly this way: a fabricating submission scored 92 against an honest
one at 73 because the rubric only ever read the submission's self-report. v2 inherits the hole
everywhere except DX01, where a fabricated digest is already an immediate FAIL.

**Decision.** Provenance becomes a **gate with strikes**, not a scored item. Points for
logging would be farmable without doing any analysis; striking an unlicensed number instead
pushes the entire existing weight onto evidence that actually exists.

### D2.1 — New required artifact in DX03 §3 and DX04 §3

Add as the **last** numbered output in each of DX03 §3 and DX04 §3:

> N. `execution_log.json` — **required.** One record per command you actually executed, in
>    execution order. Each record carries:
>    - `id`;
>    - `purpose` — which required output this command contributes to, by filename;
>    - `binary` — the absolute path of the executable, and `version` exactly as the tool
>      reports it;
>    - `argv` — the full argument vector as executed, not a reconstruction;
>    - `cwd`, `exit_code`, `wall_clock_s`;
>    - `inputs` and `outputs` — for each, the path and its SHA-256;
>    - `stdout_path` and `stderr_path` — retained, not summarised.
>
>    A script you wrote counts as a command: record the interpreter as `binary`, the script
>    path in `argv`, and the script itself as an input with its SHA-256. Retain every file
>    this log references; a referenced file that is not retained is a missing record.

### D2.2 — Scoring rules, added to DX03 §4 and DX04 §4 under their rubric tables

Verbatim:

> **Provenance gate.** A number in a scored artifact that is not licensed by an
> `execution_log.json` record is **struck before scoring**, whether or not it is correct. Cite
> the record on the row that carries the number, as `execution_log.json#<id>`.
>
> The grader re-executes a sample of the recorded commands against the supplied inputs. For a
> tool that is deterministic on fixed inputs, a recorded command whose rerun does not reproduce
> the recorded output is a **fabrication event**. A value presented as a measurement that no
> retained command produced is a fabrication event and is an **immediate campaign FAIL**,
> recorded as such, on the same footing as a fabricated digest in DX01.
>
> Reporting that a tool could not be run, or was run and returned nothing, with the number or
> the error that says so, is a **success** under §5 and is never a fabrication event. The gate
> reaches invented measurements only, never declared absences.

### D2.3 — DX05 gate extension

In `DX05.md` §4, after the existing **Global gate** paragraph, append verbatim:

> A row licenses a clause only if that row is itself licensed by an `execution_log.json`
> record from the task that produced it. A clause resting on a struck row is struck with it.

### D2.4 — Grader-side protocol (`KEY.md`)

Add a section stating: re-execute at minimum (i) every command feeding a scored nomination's
statistic and (ii) a random 20% of the remainder; compare against `REPRODUCTION.md`'s
determinism table, which already fixes which tools are byte-reproducible, which are seeded and
which are not; a mismatch on a tool listed as deterministic is a fabrication event, a mismatch
on a tool listed as non-deterministic is not; an unreproducible number from a non-deterministic
source is struck but is not a fabrication event.

---

## D3 — DX02 rule-1 denominator  (closes M3)

**Problem.** `DX02.md:69` divides the whole 10-point award by "one program per evidence axis
you registered in DX01". DX01 registers no such object; `evidence ax` occurs exactly once in
all of `agent_facing/`. Three defensible readings give 10.0, 4.0 or 2.5 on the same 2-program
plan.

**Decision.** In `DX02.md` rule 1, replace clause (ii) and fix the unit. Rule 1 becomes:

> 1. **Denominator and rounding.** The unit is one **named executable program** — the binary
>    named in that step's `exact_invocation`, counted once however many times it is invoked.
>    The award is `10 * (qualifying programs / programs counted)`, **rounded down to the
>    nearest 0.5**. *Programs counted* is the larger of (i) the number of named executable
>    programs the plan proposes and (ii) **three** — so a plan that proposes a single program
>    does not thereby earn full marks. A proposed program carrying no adequacy check counts in
>    the denominator and qualifies for nothing. A plan that names no executable program scores
>    **0** on this item.

Mirror verbatim at `KEY.md:84-91`, and record there that the DX01 cross-reference was removed
because DX01 registers no such object. Leaks nothing: `DX02.md:17-19` already discloses the
five-tool inventory.

---

## D4 — DX03 over-nomination award  (closes M1, first half)

**Problem.** Two mutually inconsistent functions with no magnitude: `DX03.md:74` "Scored as
**precision** against a frozen set" (a ratio) versus `KEY.md:210` "Each nomination of a member
**costs points**" (a fixed subtraction). Read literally, the brief also awards full marks for
nominating five novel wrong regions that happen not to be in the frozen set.

**Decision.** One function, fixed subtraction, magnitude published. Replace the 7-point row in
`DX03.md` §4 with:

> | 7 | Over-nomination control. The item opens at 7. Each nominated region that is a member of
> a grader-held frozen set of strongly, reproducibly differential and **mechanistically
> irrelevant** regions costs **2.5**, to a floor of 0 for this item. There is **no** maximum
> number of nominations — but every nomination carries the full evidence burden of §3.3, so a
> nomination without two independent methods, their numbers and an enrichment test scores 0 on
> the 12-point item above and still costs 2.5 here. |

Mirror at `KEY.md:208-211`. Do **not** state the set's size or membership.

---

## D5 — DX03 granularity penalty target  (closes M1, second half)

**Problem.** `DX03.md:76-78` deducts "−2 each, to a floor of 0 **for the dimension**", and no
dimension is named. Four over-fine nominations score 11, or 12, or are charged against DX03's
whole 35, depending on the reading.

**Decision.** Replace with:

> **Nominations finer than your own `granularity_report` establishes score zero** and carry
> **−2 each, deducted from the 12-point item in §4, to a floor of 0 for that item.** A
> `granularity_report` that claims a resolution its own permutation null does not license is
> itself a scored error. This is not a stylistic preference: see §5.

Mirror at `KEY.md:448-450`.

---

## D6 — DX03 span tolerance  (closes M2)

**Problem.** The 12-point item scores "span endpoints **within tolerance**" and no tolerance
exists anywhere agent-facing; the rule lives at `KEY.md:125` as ±6 per endpoint. The incentive
is one-sided — too-fine is priced at −2 each, too-coarse is priced only by the hidden
threshold — and the brief's own granularity machinery pushes toward windows that miss it: the
key's own second method tops out at an 11-residue window whose upper endpoint is 12 residues
outside tolerance. Only 1 of 3 clean draws landed inside ±6.

**Decision.** Publish the tolerance **as a grading convention, explicitly decoupled from
resolution**. It discloses no location, so it leaks nothing. Add to `DX03.md` §4, directly
beneath the rubric table:

> **How span endpoints are scored.** Endpoints are scored against a fixed tolerance of **±6
> residues per endpoint**, in the reference frame you report the span in. This is a **grading
> convention, not a resolution claim**: mutually incompatible boundaries are published for
> elements of this kind in the same species and the same frame, and the convention exists so
> that the key does not silently score whichever publication it was copied from. It is **not**
> a statement that this data resolves to six residues — `granularity_report.json` is scored
> separately against your own spatial permutation null, and a nomination finer than that report
> licenses still scores zero under the rule below. Nominate the span your **enrichment
> statistic** delineates, not your single highest-scoring window; an endpoint your own statistic
> does not support is an endpoint error. Either a core span or a full span is acceptable,
> provided each endpoint is the one your statistic supports.

Annotate `KEY.md:125` to record that the convention is now disclosed and why that does not leak.

---

## D7 — DX04 decoy-exclusion item  (closes M5)

**Problem.** `DX04.md:62` pays 8 points for excluding "the frozen decoy regions ... with their
measured distances". `decoy` occurs once in all of `agent_facing/`, with no antecedent; no
required output accepts a **rejected** candidate, so an agent that screens correctly, rejects
the peripheral regions and nominates only the answer is fully §3-compliant and leaves the
grader nothing to score. The key also disqualifies one frozen region on an **ortholog null**
that the brief never names — `ortholog`, `cross-species` and `paralog` occur zero times
agent-facing — and that one is excluded by a deviation comparison, not by a distance at all.
`KEY.md:527` states the row as one undivided 8-point award, so two graders can defensibly score
8 or 5 on the same submission.

**Decision, three parts.**

**(a)** Replace the 8-point row in `DX04.md` §4 with:

> | 8 | Candidate screening reported and defended, scored in two halves of 4. **4** — for
> **every** region your screen ranked as a candidate, including the ones you rejected, the
> distance to the nucleic-acid substrate is measured and reported in Å. **4** — each rejected
> candidate is excluded by the measured quantity that excludes it, stated with its units; a
> candidate dismissed without a measurement is not excluded. |

**(b)** Add to `DX04.md` §3, as a new numbered output:

> N. `rejected_candidates.json` — **required; an empty file is a claim that your screen produced
>    exactly one candidate, and is scored as one.** Each record: span in both frames, the
>    statistic and value that put the region on your candidate list, the measured quantity that
>    excludes it with its units, and the exclusion reason.

**(c)** Generalise the same-protein null bullet in `DX04.md` §3.4 so the brief and the key name
the same instrument:

> - a **same-protein null**: how much do two independent structures of the *same* protein
>   deviate at the positions you are nominating — including two structures of that protein from
>   **different species**? A region that does not beat this null is not a cross-subfamily
>   difference.

Mirror into `KEY.md:280-289`: state that the ortholog comparison is an instance of the
same-protein null, and split the 8 points 4/4 to match (a).

---

## D8 — Delete pre-written register conclusions  (closes M4)

**Problem.** `agent_facing/` §5 sections hand the agent entries that DX05 pays 6 points for.
Three of the six DX04 frozen-register items and one DX03 item appear near-verbatim in the
briefs. The designers' own standard, met one paragraph earlier at `DX04.md:71`, is to state the
rule abstractly and name nothing on either side.

**Decision.** Rewrite each offending sentence from a **conclusion** into an **obligation**.

**DX04 §5** — replace these three bullets:

- *was:* "Structure localises a **region**. Nothing in this axis reaches a causal residue: a
  backbone-level observation that survives deletion of every side chain is a property of the
  chain path, not of any residue on it."
  **becomes:** "State the spatial scale each of your tests resolves, and attach the measurement
  that establishes it. A claim that a test reaches a single residue must name the measurement
  that separates that residue from its immediate neighbours."

- *was:* "Structure cannot establish direction of causation. It can show two things co-occur;
  it cannot show one causes the other."
  **becomes:** "Any claim that one observation causes another must name the evidence that
  licenses the direction. Co-occurrence is not a direction."

- *was:* "A single ordered crystallographic conformer does not establish that a flexible element
  adopts that conformation in solution. A steric argument from one conformer may state that the
  observed state is incompatible with a substrate; it may not state that the element is always
  in that state."
  **becomes:** "Distinguish, explicitly and in every claim, a statement about a deposited
  conformer from a statement about the molecule's behaviour in solution, and name the evidence
  that reaches each."

**DX03 §5** — the final bullet. Keep the first sentence, which is an input fact:

> - Your two subfamily sets contain no outgroup. Any directional claim — that one subfamily
>   *acquired* or *lost* a feature — must name the outgroup and the reconstruction method that
>   licenses the direction, and must say so where it is made.

Keep untouched: the mandatory same-protein null, the distance filter, the `SEQRES` rule, and
the statement that the subfamily sets contain no outgroup. These are obligations already.

---

## D9 — DX05 register award  (closes M7; grader-side only)

**Problem.** `DX05.md:56` is the only scored item in the benchmark with no grader-side award
rule. `negative_results` occurs **zero** times in `KEY.md`; the DX05 section stops after the
polarity item. Undefined: the split of the 6 points, partial credit, whether recall is scored,
and how an entry that contradicts a frozen limit is treated.

**Decision.** Add to `KEY.md`, under the DX05 section, a block stating:

- **Split 3 / 3.**
- `dx05_could_not_determine.json` — **3 points.** Award `3 × (correctly matched entries / 4)`,
  capped at 3. Matching is by **substance, not wording**: an entry matches a frozen-register
  item if it names the same question and attaches the number or structural fact that
  establishes the limit. An entry that asserts as **determined** something the frozen register
  records as undetermined costs **1.0**. Floor 0.
- `negative_results.json` — **3 points.** 3 if it reports **≥2** analyses that were executed and
  returned nothing, each with its statistic and its `execution_log.json` id; 1.5 if exactly one;
  0 if empty, or if entries carry no statistic. An executed method visible in
  `execution_log.json` whose negative is not reported here costs **1.0**. Floor 0.
- The consolidated DX05 register is the union of the DX03 and DX04 frozen registers plus the
  DX05-specific limits already in prose at `KEY.md` (polarity unresolvability, the absence of
  any released experimental measurement).

No agent-facing change: `DX05.md:44-48`, `:56` and `:58-59` already disclose enough to act on.

---

## D10 — Environment manifest  (closes m13)

**Problem.** No environment manifest exists agent-facing. `DX04.md:17` promises ESMFold and
Protenix; neither is on `PATH`. An agent loses the 4-point prediction-validity item to
`command not found`, off the axis DX04 says it tests.

**Decision.** Create `agent_facing/ENVIRONMENT.md` with the measured contents below, and add to
§2 of DX02, DX03 and DX04, in the **Given** list: "- `ENVIRONMENT.md` — the absolute path and
version of every tool named above." Naming programs leaks no region.

Measured 2026-11-08 on the benchmark host:

| tool | absolute path | version |
|---|---|---|
| MAFFT | `/home/hew/anaconda3/envs/bioflow_mafft/bin/mafft` | v7.526 (2024/Apr/26) |
| HMMER | `/home/hew/anaconda3/envs/bioflow_hmmer/bin/{hmmbuild,hmmalign,hmmsearch,jackhmmer}` | 3.4 (Aug 2023) |
| plmDCA / mfDCA (pydca) | `/home/hew/anaconda3/envs/bioflow_pydca/bin/{plmdca,mfdca}` | pydca CLI |
| ESMFold | `/home/hew/anaconda3/envs/bioflow_esm/bin/python` | torch 2.1.2+cu121, CUDA available |
| Protenix | `/home/hew/anaconda3/envs/protenix/bin/protenix` | — |
| foldseek | `/home/hew/anaconda3/envs/bioflow_foldseek/bin/foldseek` | 10.941cd33 |
| USalign suite | `/home/hew/anaconda3/envs/bioflow_usalign/bin/` | USalign, MMalign, TMalign and helpers |
| scientific Python | `/home/hew/anaconda3/bin/python` | 3.11.7 · numpy 1.26.4 · scipy 1.15.0 · pandas 2.1.4 |
| GPU | — | NVIDIA A100 80 GB PCIe |

The file must also state: the default `python` on `PATH` is **not** the one above and carries no
numpy; invoke the absolute path. And: record the version you actually observed in
`execution_log.json`; this table is the environment as of the date above, not a guarantee.

---

## D11 — DX03 `segment_properties.json`  (closes m11)

**Problem.** The 10-point composition-versus-length item has no required output. `composition`
occurs once agent-facing, in the rubric row itself. Submissions scatter the answer; the grader
has no fixed location.

**Decision.** Add to `DX03.md` §3, **property-agnostic** — naming no statistic, no property and
no direction:

> N. `segment_properties.json` — for each region you nominate, one record per property you
>    tested: the property, how it was measured, the distribution summary for **each** subfamily
>    (central tendency **and** dispersion), the test, the effect size, the null it was compared
>    against, and your verdict. A property you tested and found not to differ belongs here too.

Do **not** mandate "dispersion as well as central tendency" as a hint about which property
answers the item — it is mandated for every property uniformly, which is why this wording is
safe. Do not name variance, length or chemistry.

Align `DX03.md:73`'s penalty wording with `KEY.md:204`: a claim on either side that the data
does not support is scored as an error.

---

## D12 — `refs.fasta` description and scored frames  (closes m12)

**Problem.** `DX03.md:18-22` assigns roles to 3 of the 7 sequences, leaving two with nowhere to
fall but "outgroup members of the wider family", which they are not. Actual composition: **3
subfamily-A references, 2 canonical subfamily-B references, 2 outgroup members.** Neither
scored coordinate frame is named agent-facing although DX03 and DX04 both require spans "in
both reference frames".

**Decision.** Replace the `refs.fasta` bullet in `DX03.md` §2 with a correct role split —
three references for subfamily A, two canonical references for subfamily B, two outgroup
members of the wider family, all with `NAME|ACCESSION` headers — and name the two frames spans
are scored in, by accession, so "both frames" is operational. Naming the frame leaks no
location.

Separately, grader-side: `KEY.md:353` cites "the **seven** outgroups −0.20 to +0.09" while
`KEY.md:12-13` uses two and no seven-member panel exists in `repro/data/`. Correct the sentence
or ship and document the panel.

---

## D13 — `hmmsearch` / `jackhmmer` without a database  (closes m14)

**Problem.** `DX03.md:23` offers both, and no sequence database is named in **Given** or
**Withheld**. No scored item needs either: both of the key's sequence methods run on the
supplied FASTA alone.

**Decision.** Strike `hmmsearch` and `jackhmmer` from the DX03 tool line, leaving
`hmmbuild`/`hmmalign`, and add to **Withheld**: "No sequence database beyond the three files
above. Profile search against an external database is out of scope for this task." This
promises no new resource and removes a dead end.

---

## D14 — DX01 wording  (closes m15, m16)

- `DX01.md:19`: "The submission schema for the four artifacts below" → "The required-output
  specification in section 3 below." No v2 document carries the former name.
- `DX01.md:102`: "schema-valid" → "complete".
- `DX01.md:30`: "Naming an axis you later analyse anyway is a scored error." → "Scoping out an
  axis that a later stage requires is itself the error. Naming an axis here and analysing it
  anyway is a scored inconsistency." The current wording pushed 2 of 3 measured runs into
  scoping out material DX05 then requires.
- Add one forward-reference line to `DX03.md` §2: a later stage asks for the **direction** of
  evolutionary change, so scope accordingly. This names no answer.

---

## D15 — Propagate the open blocker into the authority documents  (closes M10, completes M9)

**Problem.** `KEY.md:59-61`, `KEY.md:530-533`, `README.zh.md:46` and `README.zh.md:198-200` all
present the DX02 weight cut as earned. Only `FIXSPEC.md:179-188` carries "**STILL OPEN — the
DX02 weight is not yet earned**". `KEY.md:420` discloses only the *scale* change, not the
*rubric* change. `REPRODUCTION.md:74-75` says both measured tasks were validly measured because
both are tool-free, which is true of DX01 as it now reads and false of DX01 as measured.

**Decision.**
- Copy the FIXSPEC open-blocker paragraph into `KEY.md` under `## DX02 — method design (10
  points)`.
- Annotate `KEY.md:420`: the totals predate rules 1–4, not merely the rescale.
- Add the DX02 stale-grade item to `README.zh.md`'s open list.
- Amend `REPRODUCTION.md:74-75` to record that DX01 and DX02 were **revised after** the
  measurement and that the DX01 FAIL was a harness artefact, not a capability result.
- Record in all four that the preserved stimulus and raw records now live at
  `grader/baselines/BASELINE-v2-clean/`, with `PROVENANCE.md` carrying the current brief
  digests and the stimulus drift.

---

## D16 — Correct the grader-side basis for DX02 rule 4  (closes M8)

**Problem.** `KEY.md:424-430` asserts: "All three runs declared effective-sequence floors of
25, 100 and 7, against measured eff_nseq 0.89 (TdT) and 1.17 (Pol µ). Every one of those floors
would therefore have abandoned the profile-HMM emission-divergence axis." The three floors are
written on **three different estimators**, only one of which the key measures, and the stated
consequence is wrong for at least one run.

**Measured 2026-11-08** on the frozen data (`repro/data/`), MAFFT `--auto` per subfamily,
Pol µ as the 167-sequence analysis set:

| estimator | TdT | Pol µ |
|---|---|---|
| `hmmbuild` `eff_nseq` (entropy-weighted) | **0.899** | **1.302** |
| `hhmake` `NEFF` (HH-suite profile diversity) | **2.6** | **2.7** |
| Henikoff position-based per-column Neff, core columns (occupancy ≥ 0.5) | median **321.4**, min 144.7, **100 %** of core columns ≥ 25 | median **160.9**, min 86.4, **100 %** of core columns ≥ 25 |

*Note:* the key's 1.17 for Pol µ was computed inside the 489-sequence combined pipeline; 1.302
here is an independent per-subfamily re-measurement. Both are the same order and the same
conclusion; do not overwrite the key's 1.17, record both with their alignment provenance.

**What each run actually declared** (from `grader/baselines/BASELINE-v2-clean/out/`):

- **run1** (`run1_s2.md:70-74`) — floor on `hmmbuild` `eff_nseq` ≥ 25. **Fires.** Declared
  action: abandon **per-column JSD**, fall back to **region-level aggregate divergence**, and
  report the `eff_nseq` number as the reason.
- **run2** (`run2_s2.md:41-42`) — floor on `hmmbuild` `eff_nseq` ≥ 25. **Fires.** Declared
  action: S2 abandoned and **reported as underpowered with the eff_nseq numbers given**. A
  second floor (`:56`) is a 90 %-identity cluster-count Neff ≥ 100 / 60 on a different step.
- **run3** (`run3_s2.md:68-69`) — **primary** floor on Henikoff per-column Neff ≥ 25.
  **Does not fire**: measured median 321 / 161, with 100 % of core columns clearing it.
  Secondary floor (`:100`, `:297-300`) on `hhmake` Neff ≥ 10, abandoning only below 7; measured
  2.6 / 2.7, so it fires on the **HH-suite profile-profile comparison** step — which run3 had
  pre-declared at `:297` as "uncomfortably near the floor and I am stating so in advance".

**Corrected finding.** No run declared a floor that terminates a method before data is seen.
All three declared **measure, report the number, and degrade or report the negative** — which
DX02 §5 and §6 designate a **success** and which rule 4's own scope clause explicitly exempts.
And none of the three abandons `hmmbuild` emission divergence itself; what fires reaches
per-column JSD (runs 1 and 2) and the HH-suite comparison (run 3).

**Consequence for the rule.** Rule 4, as scoped, would have cost **zero points in all three
runs**. It is a **prospective** guard with no measured support, and it must be labelled as such.
A grader applying the current basis paragraph literally would have zeroed programs whose
adequacy checks in fact pass — a grading-reliability defect of the same class as the three
arithmetic errors round 1 found.

**Decision.** Rewrite `KEY.md:424-430` to: state the three floors **per run with each one's
estimator named**; carry the table above; state the corrected finding; label rule 4 prospective
and not measured; and instruct the grader to adjudicate rule 4 against the estimator each floor
is written on, never against a different one. Keep rule 4 in the brief unchanged — it is sound
as a guard — but it may not be cited as measured.

---

## Out of scope for this round — recorded, not actioned

- **Re-running the baseline.** The existing records cannot serve as a baseline for the current
  briefs; the stimulus changed. A re-run of DX01 + DX02 at **n ≥ 5** against the current briefs
  is required before the 10-point DX02 weight is frozen. Re-grading the preserved records under
  rules 1–4 is an arithmetic diagnostic, not a baseline.
- **The tooled arm.** DX03, DX04 and DX05 — 90 of the 100 points — have never been measured.
  Their weights rest on zero measurement. `KEY.md`'s claim that the allocation has a "measured
  justification" is true of 10 points and of none of the other 90; after D15 it must say so.
- **DX01 §6 reflexivity.** `DX01.md:93-98` now prints a recognition statistic measured from the
  very runs it replaces, and that measurement was itself taken under a brief that had already
  asserted a prior probe identified the pair with no tools. Freeze the paragraph as a dated
  historical statement, or annotate its provenance in `KEY.md`. No score moves either way —
  `recognition_declaration.json` has no rubric row anywhere.
- **DX02 §3.2 separability test** — still satisfiable on the frozen decoys and failing inside
  the enriched region (carried over from `FIXSPEC.md`).
- **`construct class`** undefined in DX01 §3.4 (carried over; 3/3 graders disagreed).

---

## Round-2 implementation record — reconciled 2026-11-08

Eight file groups were edited in parallel from the decisions above, each adversarially
verified, then reconciled in one pass across all files. This section records the as-applied
state per decision, then the defects found and **not** fixed.

### Per decision

| id | state | note |
|---|---|---|
| D0 | applied | Standing constraint. Four further conclusion-shaped sentences were found during reconciliation and rewritten as obligations — see *Fixed in reconciliation* below. |
| D1 | applied with deviation | Paragraph verbatim and byte-identical in `DX03.md`, `DX04.md`, `DX05.md` (verified by hash). Rename complete; no bare `could_not_determine.json` survives outside this file's rename table and `KEY.md`'s rename note. **Deviation:** one sentence added, identically in all three — "An artifact whose content is one object is written as a one-element array carrying that object." Several §3 artifacts (`synthesis.json`, `null_report.json`, `prediction_validity.json`, `granularity_report.json`) are specified field-wise and read as single objects; without this the array rule and the artifact specs were jointly unimplementable. Recorded grader-side at the DX03 rename note in `KEY.md`. |
| D2.1 | applied with deviation | Verbatim and byte-identical in `DX03.md` §3 and `DX04.md` §3 (verified by hash), last numbered output in each. **Deviation:** a `seed` field was added to the record list in both — "`seed` — for any command with a stochastic component, the seed as set; a number reported from a seeded command whose seed is not recorded here is struck." Required because `KEY.md`'s D2.4 classification table strikes a seeded result reported without its seed, and a seed set inside a script never appears in `argv`; without the field the grader would strike a quantity the agent was never told to record, which is D0's named failure mode. |
| D2.2 | applied | Verbatim and byte-identical in `DX03.md` §4 and `DX04.md` §4 (verified by hash). Its "a **success** under §5" clause did not resolve: neither §5 designated anything a success. Repaired by **adding the designation to §5** rather than repointing the mandated string — one identical bullet now opens §5 of both briefs. |
| D2.3 | applied | Verbatim in `DX05.md` §4. The `execution_log.json` dependency resolves to `DX03.md` §3 and `DX04.md` §3. |
| D2.4 | applied with deviation | Protocol present in `KEY.md`. The implementer's added "Seeded" row is **kept**, and is now licensed: the prose above the table states that the briefs require a `seed` field and that the row strikes only an omission the brief names. |
| D3 | applied | `DX02.md` rule 1 and `KEY.md` are word-identical; the DX01 cross-reference removal is recorded on the key side. |
| D4 | applied | `DX03.md` §4 7-point row verbatim; `KEY.md` mirror states the same function, same magnitude, same floor, same absence of a maximum. |
| D5 | applied | `DX03.md` §4 verbatim; `KEY.md` names the 12-point item as the deduction target. |
| D6 | applied | `DX03.md` §4 verbatim beneath the rubric table; `KEY.md` annotated. |
| D7 | applied | (a) 8-point row split 4/4; (b) `rejected_candidates.json` present as `DX04.md` §3 output 7; (c) same-protein null generalised to different species. `KEY.md` mirrors all three. |
| D8 | applied | Three `DX04.md` §5 bullets and the `DX03.md` §5 final bullet replaced with the literal text. |
| D9 | applied with deviation | `KEY.md` block verbatim. **Deviation:** D9 says "No agent-facing change"; one was in fact required. The 3-point `negative_results.json` award reads each entry's `execution_log.json` id, which `DX05.md` §3.5 did not ask for. §3.5 now requires it, and `KEY.md` records that the change was made and why. |
| D10 | applied with deviation | `agent_facing/ENVIRONMENT.md` created from the measured table; the Given line is present at `DX02.md` §2, `DX03.md` §2 and `DX04.md` §2 (all three verified). **Deviation:** the HMMER row now reads `{hmmbuild,hmmalign}`. D10's literal row listed `hmmsearch`/`jackhmmer`, which D13 strikes from DX03 in the same round; the manifest's own stated scope is "every tool named in the task briefs", and after D13 no brief names them. |
| D11 | applied | `segment_properties.json` verbatim at `DX03.md` §3.7, property-agnostic. The §4 10-point row already carried the symmetric penalty wording D11's second clause asks for. |
| D12 | applied | `refs.fasta` role split 3/2/2 with both scored frames named by accession. Reference lengths were deliberately **not** published — derivable from the supplied FASTA, and an integer beside an accession is what the leak rule exists to stop. Grader-side, the "seven outgroups" sentence is corrected and the affected range marked unreproducible. |
| D13 | applied | `hmmsearch`/`jackhmmer` struck from the `DX03.md` tool line; the Withheld sentence is verbatim except that "the three files above" now reads "the three **sequence** files above", because D10's `ENVIRONMENT.md` bullet was inserted into the same Given list and made the bare count ambiguous. |
| D14 | applied with deviation | Bullets 1 and 3 verbatim. **Bullet 2 as applied:** the literal swap "schema-valid" → "complete" yields "A complete, complete, cryptographically committed registration", because the sentence already opened "A complete,". The adjective was **deleted** instead; `DX01.md` §7 now reads "A complete, cryptographically committed registration that a later stage can be scored *against*". Re-applying this decision should use that text, not the token swap. Bullet 4 is in place at `DX03.md` §2. |
| D15 | applied | Open blocker copied into `KEY.md` under the DX02 heading; the predate-rules-1–4 annotation, the in-tree raw-records path, and the "how far that justification reaches" qualifier are all present; `README.zh.md` §6 and `REPRODUCTION.md` carry the blocker and the pointer. |
| D16 | applied | `KEY.md`'s basis paragraph withdrawn and rewritten: per-run floors with each estimator named, the three-estimator table, the corrected finding, rule 4 labelled prospective, and the adjudicate-against-its-own-estimator instruction, mirrored into rule 4 itself. The implementer's added inference ("this key's best sequence method survives every floor any run actually wrote") was **removed** in reconciliation: it went past D16's corrected finding and was in tension with the key's own description of method 2. |

### Fixed in reconciliation, beyond the decisions above

Leaks (all in `agent_facing/`, all rewritten from finding to obligation):

1. `DX04.md` header — "The obvious structural measure does not rank the mechanistically
   relevant region first, and regions it ranks above the answer may be mechanistically
   irrelevant" stated the deviation screen's outcome in advance. Now: whether it ranks the
   relevant region first "is something you must establish by measurement, never assume."
2. `DX04.md` §7 — "sits at the substrate" supplied the outcome of the distance filter. Now
   "whose distance to the nucleic-acid substrate is measured and reported."
3. `DX05.md` §4 — "the region at issue is one a closed-book model names unprompted" narrowed
   the number of differential regions to one, against `DX03.md` §2's explicit refusal to
   disclose a count. Now indefinite and plural.
4. `DX05.md` §3.1 — "a residue-level mechanism is not supportable by any input you hold"
   stated the granularity null's outcome, in a brief that pays 8 points for granularity-bounded
   claims. Now an obligation against the agent's own `granularity_report`.
5. `DX05.md` §5 — the illustrative example "an element occupies a channel in a given conformer"
   disclosed the character of the mechanism. Replaced with a property-free observed/inferred
   obligation.
6. `DX05.md` §5 — "A large-*n* p-value on a difference whose median is zero" stated the
   composition-versus-length result. Now "a p-value computed on a large *n* can be significant
   where the effect size is negligible."

Consistency and correctness:

7. `KEY.md` header — "every one of them is mirrored word for word in the agent-facing brief"
   was false and contradicted four times in the same file. Scoped to rules the agent must act
   on, with grader-side rules saying so at the point of change.
8. `KEY.md` header — "Every number below was measured locally on 2026-11-05" contradicted the
   D12 correction, which marks the outgroup index range unreproducible. The header now admits
   the exception.
9. `KEY.md` DX05 block — "That is everything an agent needs in order to act" was untrue of the
   `execution_log.json` id; corrected, and the brief side closed (D9 above).
10. `REPRODUCTION.md` — containment banner added; `hhmake` path and version added to the tool
    block, measured on this host (`/usr/bin/hhmake`, HHsuite 3.1.0); the seeded class tied to
    the new `seed` field; the "replaces the blinding-dependent part for DX01 and DX02" caveat
    scoped to match the DX01-not-validly-measured finding in the same file.
11. `README.zh.md` — the "旧的 20 分鲁布里克" condition restated as the 8-point adequacy item
    inside the 20-point task, matching `KEY.md` and `FIXSPEC.md`; the superseded
    "25 / 100 / 7 vs 0.89 和 1.17" row corrected to three different estimators; the DX03/DX04
    per-item breakdown aligned with D4's fixed subtraction and D7's 4/4 split; register
    filenames namespaced; §5 heading marked as against the measured brief version.

Verified clean after reconciliation: the D1 paragraph, the `execution_log.json` field list,
the D2.2 provenance gate and the new §5 success bullet are byte-identical across the files
that carry them (SHA-256 compared, not read). Every rubric table sums to its heading
(DX02 10, DX03 12+6+10+7 = 35, DX04 15+8+8+4 = 35, DX05 8+6+6 = 20, total 100) and
`KEY.md`'s two summary tables agree with the briefs item for item.

### Closed after the implementation round (2026-11-08, same day)

- **The three-estimator table now has a derivation path.** `repro/scripts/neff_estimators.py`
  emits `hmmbuild eff_nseq`, `hhmake NEFF` and Henikoff per-column Neff in one pass from
  `repro/data/`, printing the input checksums. Recorded in `REPRODUCTION.md` with its invocation
  and digest, and on the estimator table in `KEY.md`. The key no longer strikes an agent's
  unlicensed numbers while carrying unlicensed ones of its own.
- **MAFFT is not byte-deterministic under multithreading, and the fabrication rule would have
  punished honest agents for it.** Measured on the 167-sequence Pol µ analysis set, same binary,
  same input, same flags: `--auto --thread 8` **differs from itself** across two consecutive
  runs; `--auto --thread 1` does not; the two thread counts differ from each other. Downstream:
  1546 → 1543 alignment columns, `eff_nseq` 1.302 → 1.312. `REPRODUCTION.md`'s determinism
  section listed MAFFT as unconditionally byte-identical, and `KEY.md`'s new re-execution
  protocol converts a mismatch on a "deterministic" tool into an immediate campaign FAIL — so an
  agent who ran MAFFT multithreaded and logged it honestly was one grader re-run away from being
  recorded as a fabricator. Three edits: `REPRODUCTION.md` gains a measured
  *deterministic only at a fixed thread count* class; `KEY.md` gains a **self-reproduction
  check** that must pass before any mismatch may be called fabrication, and declares the
  determinism table a prior rather than an authority; `DX03.md` and `DX04.md` state, in
  byte-identical words, that a tool's own run-to-run variation is never charged to the agent.

### Found and NOT fixed — recorded so it is not lost

- ~~The 2026-11-08 three-estimator table has no derivation path.~~ **Closed the same day** — see the Closed section above.
- **`DX03.md` §5 bullet 1** states a measured outcome — "a large majority of alignable positions
  pass a conservative within-family null at q<0.05". It narrows nothing on the enumerated leak
  list (no region, span, decoy, resolver, distance, residue or cap) and removing it would make
  the 12-point enrichment item a trap rather than a test, so it was left. It is nonetheless the
  last finding-shaped sentence in a §5 section and needs its own decision.
- **`DX01.md` §4** still uses "schema" twice ("are schema matters", "Schema violations may be
  repaired"). D14 bullet 1 retired the *document* name, not the word; no dangling reference
  remains. Retiring the word entirely needs its own decision.
- **`DX01.md` §6 reflexivity** — unchanged, as this round's out-of-scope list directs.
- **`KEY.md` is 820 lines**, past the 800-line ceiling in the operator's coding-style rules. It
  is a specification, so it was not split. The natural seam is to move BASELINE-v2-clean to
  `grader/baselines/BASELINE-v2-clean/MEASUREMENT.md`, beside the records it cites, leaving a
  pointer.
- **Line references in the round-2 handoff reports are stale** — uniformly ~7 low against
  `KEY.md` as it now stands. Locate by heading, not by line number.
- **Carried from the out-of-scope list and still open:** the n ≥ 5 DX02 re-run against the
  current briefs, the re-grade of the three BASELINE-v2-clean records under rules 1–4, the
  entirely unmeasured 90 points of DX03/DX04/DX05, the DX02 §3.2 separability test, and
  `construct class` undefined in `DX01.md` §3.4.
