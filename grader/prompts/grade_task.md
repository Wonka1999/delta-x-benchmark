# Grading prompt — one task

Fill the five placeholders and hand the result to a capable model. Expect one of these per task.

---

You are grading one task of a scientific-discovery benchmark. You are **not** solving it, and you
are not being asked whether the submission is impressive. You are assigning each scored item a
number that another grader can check against the same two documents.

## What you are given

1. **The task brief** — what the agent was asked, including section 4, which is the rubric:

```
{{PASTE tasks/DX0N.md VERBATIM}}
```

2. **The answer key for this task** — the frozen, measured answers and the award rules:

```
{{PASTE the relevant section of grader/KEY.md VERBATIM, including every rule it states}}
```

3. **The submission** — the artifacts the run produced, with their filenames:

```
{{PASTE the artifacts, or give file paths and let the grader read them}}
```

4. **The execution log** — `execution_log.json`, which licenses numbers:

```
{{PASTE execution_log.json}}
```

5. **The scorecard schema** — the exact shape your output must take:

```
{{PASTE the items[] record shape from grader/SCORECARD.md}}
```

## Procedure

**Step 1 — the provenance gate, before you score anything.** For every number in a scored
artifact, find the `execution_log.json` record that licenses it. A number no record licenses is
**struck before scoring, right or wrong**, and it cannot support any other conclusion either. A
clause resting on a struck row is struck with it. List every strike with a `classification` of
`unlicensed`, `missing_record`, `not_deterministic` or `seed_unrecorded`.

Do not inflate a strike into a deduction the rubric does not license. If an artifact is almost
entirely unlicensed but no scored item is defined on it, the correct outcome is a large strike
count and no change to any award. Say so.

**Step 2 — grade each item in the brief's section 4, in order.** For each one:

- Quote the key's answer and cite the line.
- Quote the submission **verbatim** and cite it as `<artifact>#<id>` or `<artifact>#L<n>`. A row
  that cannot cite the submission scores **zero**, whatever you believe you read.
- State the award as an explicit calculation in `arithmetic`.
- Name the rule behind every deduction. A deduction with no rule is an opinion and is removed.
- Where a rule compares a declared threshold against a measured quantity, name the `estimator`.
  Three estimators of effective sequence number differ by two orders of magnitude on this data;
  a verdict that does not say which one it used is void.
- Respect item floors. A deduction floors at 0 **for its own item** and never reaches another.
  A negative item award means you mis-applied a floor.
- Write `plain`: one sentence someone who has not read the key could check your verdict against.
- Write `borderline`: a judgement another grader could defensibly reverse, and which way. Leave
  it empty only when the row genuinely admits no defensible reversal. This field is not
  politeness — the rows that get overturned are the ones nobody flagged.

**Step 3 — do not assert fabrication.** If a number looks invented, record it as a strike and
say what would settle it. A fabrication verdict requires re-executing the recorded `argv` twice
and confirming the tool reproduces *itself*, and you cannot do that from text. A fabrication
verdict asserted without that check is void.

## What is not scored

Prose quality, length, breadth, literature coverage, confidence, or whether the submission names
the right tools. Only what the rubric lists.

## Output

A JSON object with `items[]`, `gates[]` and `strikes[]` for this task only, in the schema above.
No prose outside the JSON. If you cannot score an item, emit the row with `awarded: 0`, and say
in `plain` what was missing — never omit the row.
