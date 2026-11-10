# Start here

**CONTAINMENT.** Everything under `docs/` is designer-side. It names the case and some of its
scored facts. Do not place it, or any part of it, in the context of a system being evaluated.

Three paths. Pick one.

---

## A. "I want to see what this is" — 15 minutes

1. [`docs/pages/07_for_ml_readers.zh.html`](pages/07_for_ml_readers.zh.html) — open it in a
   browser. One section per task, three levels of depth behind a button (plain / standard /
   detailed), defaulting to plain. Written for an ML audience with no biology.
2. [`docs/RESULTS.md`](RESULTS.md) — what has actually been measured, and what the measurement
   says is wrong with the benchmark.
3. [`tasks/DX03.md`](../tasks/DX03.md) — one real task brief, start to finish. It is five pages
   and it is the fastest way to see what "derive it, do not name it" means in practice.

## B. "I want to run my system against it" — half a day, then compute time

```bash
# 1. tools. DX01/DX02/DX02B need none; DX03 needs the light tier; DX04 wants a GPU.
conda env create -f env/environment.yml && conda activate delta-x
bash env/probe_env.sh ./ENVIRONMENT.md       # writes what THIS host really has

# 2. plumbing, free
harness/run_campaign.sh --run-id smoke --adapter stub --work ~/delta-x-runs --stages s1,s2
python3 -I harness/collect_submission.py ~/delta-x-runs/smoke --out /tmp/smoke-sub

# 3. your adapter. One executable, one page of contract.
cp harness/adapters/evoagenda.sh harness/adapters/mysystem.sh   # fill in one line
harness/run_campaign.sh --run-id t1 --adapter mysystem --work ~/delta-x-runs --stages s1

# 4. the real thing, n>=5 runs. One run settles nothing: the quantity that
#    decides whether an item discriminates is the RANGE across runs.
for i in 1 2 3 4 5; do
  harness/run_campaign.sh --run-id run$i --adapter mysystem \
      --work ~/delta-x-runs --environment ./ENVIRONMENT.md
done
```

Read [`harness/adapters/README.md`](../harness/adapters/README.md) before writing the adapter —
the four things people get wrong are listed there, and three of them silently change what is
being measured rather than failing.

## C. "I want to grade a submission" — read two files

1. [`grader/GRADING.md`](../grader/GRADING.md) — the five-pass procedure, in order.
2. [`grader/SCORECARD.md`](../grader/SCORECARD.md) — the form the output must take.

Then:

```bash
python3 -I harness/audit_containment.py  ~/delta-x-runs/run1    # exit 1 => VOID, re-run it
python3 -I harness/collect_submission.py ~/delta-x-runs/run1 --out results/mine/run1
#  ... grade, emitting results/mine/run1/scorecard.json ...
python3 -I grader/check_scorecard.py results/mine/run1/scorecard.json
python3 -I analysis/aggregate.py results/mine --label mine \
        --compare grader/baselines/BASELINE-v3-tooled/scorecards
```

---

## The five things that make this benchmark different

1. **Recognition is subtracted, not punished.** The case is not blinded — blinding was measured
   and it failed, 3 of 3. Instead every item is defined so that knowing the answer is worth
   nothing: a correct span with no statistic attached scores 0.
2. **Numbers must be licensed.** A number no recorded command produced is struck before
   scoring. Honest negatives score; invented positives fail the campaign.
3. **The obvious statistic is wrong.** DX04 is built around a measured trap: screening by
   per-residue deviation ranks two mechanistically irrelevant regions ahead of the right one,
   and the same protein's own two crystals differ by more at that position than the two
   subfamilies do.
4. **Resolution is a scored claim.** The data supports ~10–20 residues and no finer; a
   nomination finer than the submission's own permutation null licenses is deducted.
5. **The score is a list, not a number.** A total that is not accompanied by a reconciling
   per-item scorecard may not be published.

## A warning about the published rubric

This repository publishes the scoring rules **with** the tasks. The reference campaign measured
what that does: submissions came back carrying fields named after the rules, DX02's rule 2 went
from being the entire source of discrimination to failing 0 of 14 times, and the benchmark
saturated at a mean of 95.7/100.

If you want a measurement that discriminates, **do not hand your system `grader/`, and consider
whether the §4 blocks in `tasks/` should be withheld too.** Section 4 of each brief is the
rubric. It ships inside the task because the task was designed to be answerable in good faith —
not because publishing it is free. [`docs/RESULTS.md`](RESULTS.md) has the numbers.
