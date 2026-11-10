# DELTA-X v2 campaign report — <SYSTEM NAME>

<!-- Fill every section. A section you cannot fill is a finding: write "not measured" and
     say why, rather than deleting the heading. A score without a per-item scorecard is not
     a score (grader/SCORECARD.md): publish the scorecards beside this report. -->

**Campaign id:** `<label passed to aggregate.py --label>`
**Date graded (UTC):** `<YYYY-MM-DD>`
**Scorecards:** `<path or release URL of the scorecard.json set>`
**Key digest:** `<sha256 of grader/KEY.md as applied>`

---

## 1. System measured (被测系统)

Name the exact thing measured, not the family it belongs to.
- **Model / system id:** `<exact id, e.g. claude-opus-5-20260101; not "Opus 5">`
- **Version or build:** `<API version, commit, container digest>`
- **Sampling:** `<temperature, top_p, seed, thinking budget — or "provider default", named>`
- **Tools available:** `<the tools the system could actually call, or "none (closed-book)">`

## 2. Harness and adapter (测试框架与适配器)

One line each on what served the briefs and what turned the system's output into artifacts.

- **Harness:** `<name, version, commit>`
- **Adapter:** `<how briefs were served and artifacts collected>`
- **Containment:** `<assert no grader/ material entered the evaluated context, and how you know>`
- **Environment:** `<tool binaries and versions, per the ENVIRONMENT.md the run was composed with>`

## 3. n runs, and why this n (轮数及其理由)

State n and the reason for it. "It is what we could afford" is an acceptable reason; an
unstated reason is not. Name the excluded runs and the rule that excluded them.
- **n scored:** `<n>` — **excluded:** `<run ids + rule, e.g. run0 is a pilot>`
- **Why this n:** `<what the n buys: a range wide enough to separate two systems, or not>`

## 4. Per-run table (逐轮总分表)

Pasted verbatim from `python3 -I analysis/aggregate.py <scorecards> --out-md <file>`,
section 1. Do not retype it and do not edit the numbers.

<!-- paste aggregate.py --out-md section 1 here -->

Every run above must read `reconciles: yes`. A run that does not is reported **ungraded**
and must not be averaged into section 5.

## 5. Campaign summary (总体统计)

Pasted from `aggregate.py` section 2: n, mean, median, min, max, range, sample sd.

<!-- paste aggregate.py --out-md section 2 here -->

One sentence on whether the range is small enough for this mean to separate anything.

## 6. Per-item discrimination (逐项区分度)

Pasted from `aggregate.py` sections 3 and 3b. This is the table the benchmark steers on:
an item at range 0 bought no information in this campaign.

<!-- paste aggregate.py --out-md section 3 / 3b here -->

- **Items at ceiling:** `<list>` — they cost grading effort and returned no signal.
- **Items at floor:** `<list>` — the task may be unanswerable as served, not merely hard.
- **Items absent from some runs:** `<from aggregate.py's presence report>` — say why.

## 7. Integrity roll-up (完整性汇总)

Pasted from `aggregate.py` section 4, plus one line of interpretation.

<!-- paste aggregate.py --out-md section 4 here -->

- **Fabrication events:** `<n>` — each must carry a passing `self_reproduction_check`.
- **Strikes by classification:** `<unlicensed / missing_record / not_deterministic / seed_unrecorded>`
- **Gates failed / caps applied:** `<n, and what each cap did to which run>`

## 8. Reported beside the score (并列报告，不计入总分)

Indices from `campaign.reported_beside[]`. State plainly: **these are never added to the
total.** If you added one, the number you are publishing is not a DELTA-X v2 score.

<!-- paste aggregate.py --out-md section 5 here -->

## 9. What was NOT measured (未测量范围) — mandatory

This section maps to every scorecard's `campaign.measured_scope`, which must name what was
**not** measured. Copy those declarations here and reconcile them against each other.

- **Tasks not run:** `<DXnn, …, or "none">`
- **Rubric rows not scored:** `<item ids, and what share of the 100 points they hold>`
- **Capabilities this says nothing about:** `<e.g. no wet-lab validation, no held-out case>`
- **Scope declarations that disagree across runs:** `<quote them; a silent disagreement is a defect>`

A citation of this campaign that omits this section is a misuse of it.

## 10. Findings this campaign supports (本次测量支持的结论)

Two or three, no more. Each must be checkable against the tables above, with the row that
carries it named. Anything you believe but cannot point at belongs in section 11.

1. `<finding>` — supported by: `<section, row, number>`
2. `<finding>` — supported by: `<section, row, number>`
3. `<finding>` — supported by: `<section, row, number>`

## 11. Known defects of this measurement (本次测量自身的缺陷)

Defects of the measurement, not of the system measured. Specific enough that a reader can
decide what this campaign cannot be used for.

- **Grader variance:** `<adversarial re-check run? overturn rate? on which items?>`
- **Rows that did not discriminate:** `<and whether the weight should move>`
- **Schema or bookkeeping drift:** `<e.g. one rubric row carrying different item_ids across runs>`
- **Contamination risk:** `<project instructions, prior runs, the case in training data>`
- **n too small for:** `<the comparisons this campaign cannot license>`
- **Borderline rows:** `<count of items with a non-empty `borderline` field, and the widest band>`

*Produced with `analysis/aggregate.py` over `<n>` scorecards. The scorecards, not this
report, are the record; this report is a reading of them.*
