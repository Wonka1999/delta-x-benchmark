# Results

One directory per campaign, one subdirectory per run.

```
results/
  <campaign-name>/
    REPORT.md                 filled from analysis/REPORT_TEMPLATE.md
    aggregate.md              analysis/aggregate.py --out-md
    aggregate.csv             analysis/aggregate.py --out-csv
    run1/
      PROVENANCE.txt          what was actually served: brief, prompt and data digests
      SUBMISSION.md           completeness index, written by collect_submission.py
      completeness.json
      MANIFEST.sha256
      artifacts/              the submission itself, exactly as the run produced it
      harness/                adapter result records and stage logs
      scorecard.json          the score. Without this there is no score.
      scorecard.md            the human-readable companion
    run2/ ...
```

A campaign is at least five runs. One run settles nothing: the quantity that decides whether an
item measures anything is the **range across runs**.

## Keep the raw records

`artifacts/` is not optional. A score whose submission is not retained cannot be re-checked, and
in this benchmark's history re-checking overturned 2 of 3 grades on two separate occasions — in
one round every correction ran downward, in the other every correction ran upward. A number with
nothing behind it is not a result.

## Before you publish a campaign

```bash
python3 -I harness/audit_containment.py ~/delta-x-runs/run*     # all clean, or the runs are void
for f in results/<campaign>/run*/scorecard.json; do python3 -I grader/check_scorecard.py "$f"; done
python3 -I analysis/aggregate.py results/<campaign> --label "<campaign>" \
        --out-md results/<campaign>/aggregate.md --out-csv results/<campaign>/aggregate.csv \
        --compare grader/baselines/BASELINE-v3-tooled/scorecards
```

`aggregate.py` exits 1 if any scorecard fails its own reconciliation, so it works as a gate.

Then fill `analysis/REPORT_TEMPLATE.md`. The section it will not let you skip is **what was not
measured** — it maps to the scorecard's `measured_scope`, and a score whose scope is not stated
is not comparable to one whose is.

## Published campaigns

Both reference campaigns live under `grader/baselines/` rather than here, because they carry
graded records that quote the key. Their summary is in [`docs/RESULTS.md`](../docs/RESULTS.md).
