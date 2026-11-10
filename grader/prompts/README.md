# Grading prompts

Two templates that let an LLM close the grading loop. They implement `../GRADING.md`; read that
first, because these prompts assume its five passes and its vocabulary.

| file | role |
|---|---|
| `grade_task.md` | one grader per task. Sees the key, the brief and the submission. Emits the `items[]` rows for that task. |
| `verify_item.md` | one verifier per scored row, **default position: the grade is wrong**. Sees the submission and the rule, re-derives, and returns a verdict. |

The division is the point. A verifier handed the grader's conclusion confirms it; a verifier that
re-derives from the submission overturns it when it should. Measured on this benchmark: round 1
overturned 2 of 3 records, all downward and all arithmetic; round 2 overturned 2 of 3, both
upward and both rule-application; the reference campaign overturned 3 of 5 DX05 rows, widening
that item's spread from 0.5 to 3.0 points.

## Running them

One grader per task and one verifier per row, in parallel, is the shape that was measured. Feed
each one only what its template lists — a grader that is also shown the other tasks' keys tends
to import their answers.

**Relay the rule verbatim.** In one documented grading error the text handed to the grading agent
had dropped the *first sentence* of DX02 rule 2 — the sentence that decides the case — and the
grade split on it. The omission was in the relay, not in the rubric. Paste the rule whole, or
give the grader the file path and let it read.

## What these do not do

They do not re-execute commands. Pass 3 of `GRADING.md` — re-execution and the self-reproduction
check — needs a shell on a host with the tools installed, and it is the pass the reference
campaign skipped. If you skip it too, say so in `campaign.measured_scope`; do not let an LLM
assert a fabrication verdict it could not have checked.
