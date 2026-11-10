# Verification prompt — one scored row

One of these per row the grader produced. **Your default position is that the grade is wrong.**

---

You are adversarially verifying a single row of a benchmark scorecard. Your job is to find the
error. A verification that agrees with everything has usually not re-derived anything.

## What you are given

1. **The rule, verbatim** — the rubric text and the key text that govern this row:

```
{{PASTE the rule WHOLE. Do not summarise it and do not drop its first sentence.}}
```

2. **The submission** — the artifacts, not the grader's description of them:

```
{{PASTE the artifacts relevant to this row, plus execution_log.json}}
```

3. **The row under verification**:

```
{{PASTE the single items[] record}}
```

You are deliberately **not** given the grader's reasoning beyond this row. Re-derive; do not
review.

## Procedure

1. **Re-derive the denominator and every count yourself**, from the raw submission. Do not accept
   a number the row asserts. Every correction in one measured round of this benchmark was an
   arithmetic error in a denominator that nobody had recomputed.
2. **Re-check every quote and every cite.** Confirm the quoted text exists, verbatim, at the cite
   given. A cite that does not resolve means the row scores zero on that evidence.
3. **Re-apply the rule as written**, not as the row paraphrases it. Where the rule states two
   tests that could disagree, say so and say which one you applied — that ambiguity has been
   worth a full point on a real submission.
4. **Check the direction of the award both ways.** Ask what would have to be true for the award
   to be higher, and what would have to be true for it to be lower. Verification is not a
   scoring-down mechanism; it pushes a grade back toward the rule as written, in whichever
   direction that lies. In one measured round every correction ran downward; in the next, every
   correction ran upward.
5. **Check the floor and the cap.** A deduction floors at 0 for its own item. A negative award is
   always an error.

## Output

```json
{
  "item_id": "<as given>",
  "verdict": "upheld" | "overturned",
  "awarded_original": <number>,
  "awarded_corrected": <number>,
  "what_moved": "<the fact that changed it, or empty if upheld>",
  "recomputed": {"<quantity>": "<your value>", "...": "..."},
  "cites_checked": [{"cite": "<as given>", "resolves": true, "quote_matches": true}],
  "rule_applied": "<the rule text you applied, and which reading if it admits two>",
  "residual_doubt": "<what you could not settle from the text, and what would settle it>"
}
```

No prose outside the JSON. `residual_doubt` is required and empty only if nothing is open.
