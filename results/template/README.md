# Campaign template

Copy this directory to `results/<your-campaign-name>/` and fill it in. The empty files below
name what has to exist; `harness/collect_submission.py` creates most of them for you.

| file | produced by |
|---|---|
| `run1/PROVENANCE.txt` | `harness/run_campaign.sh` |
| `run1/artifacts/` | the run itself, copied by `collect_submission.py` |
| `run1/harness/` | the adapter's result records, copied by `collect_submission.py` |
| `run1/SUBMISSION.md`, `completeness.json`, `MANIFEST.sha256` | `collect_submission.py` |
| `run1/scorecard.json` | **you**, following `grader/GRADING.md` |
| `run1/scorecard.md` | **you** — the companion written for someone who cannot read the key |
| `aggregate.md`, `aggregate.csv` | `analysis/aggregate.py` |
| `REPORT.md` | **you**, from `analysis/REPORT_TEMPLATE.md` |

A `scorecard.json` that does not pass `grader/check_scorecard.py` is reported as **ungraded**,
not as a low score.
