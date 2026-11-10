# FAQ

**CONTAINMENT.** Designer-side.

**Do I need a GPU?**
For 65 of the 100 points, no. DX01, DX02, DX02B and DX03 run on the light conda environment.
DX04 wants a structure predictor on a GPU; without one you can still do the structural-alignment
half using experimental PDB entries, and you declare the shortfall in `measured_scope` rather
than taking a zero. See `env/INSTALL.md`.

**How many runs do I need?**
At least five. One run settles nothing here: the quantity that decides whether an item measures
anything is the **range across runs**, not any single total. The reference campaign's whole
conclusion is a statement about a range.

**Can I run only some tasks?**
Yes — `--stages s1,s2`. Then say so in `measured_scope`. A partial score is comparable only to
another partial score of the same scope; that is why the field is mandatory.

**My system can't be told "no tools" for one task. Does that matter?**
Yes. DX01, DX02 and DX02B are defined on what a system commits to *before* it has evidence. A
system that runs tools there is being measured on something else, and its DX01–DX02B results
are not comparable to a run that blocked them. Report it.

**Why is the case not blinded?**
Because blinding was measured and it failed: 3 of 3 tool-free runs recognised the family from
the first sentence. Rather than pretend, every item is defined so recognition is worth nothing —
a correct span with no statistic attached scores 0 — and `recognition_declaration.json` records
what was recognised so credit can be computed net of it.

**Why does the agent get the scoring rubric?**
Because section 4 of each brief tells the agent what a good answer has to carry, and the tasks
were designed to be answerable in good faith. The reference campaign measured what it costs:
submissions came back engineered against the named rules, and the benchmark saturated. If you
want discrimination, consider withholding §4 and re-measuring. `docs/RESULTS.md` has the numbers.

**A number in my submission has no `execution_log.json` record. What happens?**
It is struck before scoring — right or wrong — and it cannot support any other conclusion
either. A clause resting on a struck row is struck with it. This is the single most common way
a good answer scores zero.

**My tool gave a different answer on re-run. Am I a fabricator?**
No, and the grader is required to check before saying so: re-execute your recorded `argv` twice
and confirm the tool reproduces *itself*. If it does not, the result is classified
`not_deterministic` and nothing is charged to you. MAFFT is deterministic only at a fixed thread
count, and this rule exists because without it an honest multithreaded run would have been
branded a fabricator.

**The containment audit flagged my run. Can I just discount it?**
No. Re-run it. There is no way to tell which part of a contaminated run was contaminated, so
there is no partial credit. If you think it is a false positive, the audit prints the matched
token with surrounding context precisely so you can check — one earlier version of it produced
826 false hits from a directory name.

**My prompt digests do not match the published ones. Is something wrong?**
Only if you did not pass `--environment`. The prompts embed the host's tool manifest, so a run
composed against *your* `ENVIRONMENT.md` necessarily differs from one composed against the
reference host's — that is correct, and your campaign's `PROVENANCE.txt` records what you
actually served. `make digests` compares against the published campaign using the shipped
`tasks/ENVIRONMENT.example.md`, and that comparison must keep matching: it is how you find out
that someone edited a brief.

**Can I change the task briefs?**
You can, and then your numbers are not comparable to the published ones. Re-digest the briefs,
record them in your campaign's `PROVENANCE.txt`, and say in your report what you changed. The
published stimulus digests are in `grader/baselines/BASELINE-v3-tooled/STIMULUS.txt`.

**Where do I put my results?**
`results/<campaign-name>/<run-id>/`. `results/template/` has the shape and
`analysis/REPORT_TEMPLATE.md` is the write-up. Keep the raw records — a score without the
submission behind it cannot be re-checked, and in this benchmark's history 2 of 3 grades were
overturned on re-check more than once.

**Is 95.7/100 a good score?**
It is a saturated one. Read it as "this instrument no longer separates systems at this level",
not as "the system is 95.7% of the way to scientific discovery". The per-item table in
`docs/RESULTS.md` is the honest version: 60 of the 100 points did not move at all.
