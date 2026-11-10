# BASELINE-v3-tooled — protocol

**CONTAINMENT.** Designer-side. Nothing here may be rendered into an evaluated agent's
context. A harness that does so voids its run.

Started 2026-11-09. **Status: in progress.** No score may be quoted from this directory until
`scorecard.json` exists per `grader/SCORECARD.md` and the containment audit below has passed.

## What makes this different from BASELINE-v2-clean

BASELINE-v2-clean blocked every tool:

```
--disallowed-tools Bash Read Write Edit Glob Grep WebSearch WebFetch Task NotebookEdit
```

and its stimulus opened with *"Tool use is blocked for this task. Produce every required
artifact INLINE in your reply."* That is why it measured DX01 and DX02 and **nothing else**:
DX03, DX04 and DX05 require execution, so 90 of the 100 points were never attempted. Its
`s3` stage was a closed-book saturation probe, **not** a DX03 submission, and must never be
read as one.

This run gives the agent a real shell for the three execution tasks and tells it so in terms
that cannot be misread — the failure mode being guarded against is an agent that writes a plan
where results were asked for because it did not realise it could run anything.

## Stage map

| stage | task | tools | timeout | why |
|---|---|---|---|---|
| `s1` | DX01 | `Write` only | 2400 s | no data is released; the task is what you commit to before evidence |
| `s2` | DX02 | `Write` only | 2400 s | method pre-registration; the brief forbids running anything |
| `s2b` | DX02B | `Write` only | 2400 s | approach audit, added 2026-11-09; report-only in its first campaign |
| `s3` | DX03 | `Bash Read Write Edit Glob Grep WebFetch` | 6600 s | sequence execution |
| `s4` | DX04 | same | 8400 s | structure execution; PDB access is allowed by the brief |
| `s5` | DX05 | same | 3600 s | synthesis over the agent's own artifacts |

`Write` is allowed in the no-tool stages so artifacts land as files and the pipeline can carry
them forward. It also puts DX01's commitment on the **harness-computes-the-digest** branch,
which is the branch the fixed gate was written for and which has never been exercised.

One session per run, resumed across stages, so each task sees its own predecessors exactly as
the pipeline intends. Tool permissions are re-asserted per stage.

## The tool prompt

Every tooled stage carries this preamble above the verbatim brief:

- **"YOU HAVE A REAL SHELL. THIS IS NOT A SIMULATION, AND NOTHING HERE IS HYPOTHETICAL."**
- the tool manifest from `agent_facing/ENVIRONMENT.md`, absolute paths included;
- the served data paths and their sequence counts;
- *"Do NOT describe an analysis you did not run. Do NOT hand in a plan where results are asked
  for."*
- the provenance gate stated as a consequence: a number no recorded command produced is struck
  before scoring, right or wrong, and cannot support any other conclusion;
- *"If a tool fails or returns nothing, that is a legitimate result"* — so the prompt does not
  push toward inventing output;
- a wall-clock budget, with instructions to deliver partial artifacts rather than overrun;
- a containment clause forbidding reads outside the working directory.

The preamble is operational only. It names no region, statistic, threshold or expected result.

## Containment

Run from `…/scratchpad/baseline_v3/work/run<N>/`, outside the repository tree, so this repo's
`CLAUDE.md` — which names the pilot case — is not injected. The user-level
`~/.claude/CLAUDE.md` is still injected, as it was for BASELINE-v2-clean, so the two are
comparable; it does not name the case.

**Bash makes containment an active problem rather than a structural one.** v2 could not read
anything; v3 can. `audit.sh` therefore greps every transcript and artifact for
`EvoAgenda|KEY\.md|delta_x_v2|grader/|SCORECARD|FRAME-DISCIPLINE|agent_facing|BASELINE-v2|REGRADE`.
**Any hit voids that run.** The audit is mandatory before any score is read.

## Stimulus provenance

The briefs on disk no longer match the digests BASELINE-v2-clean recorded "for the next
baseline" — they were edited later the same evening by the fix round and the record was never
refreshed (corrected in `../BASELINE-v2-clean/PROVENANCE.md`). The digests actually served here
are in `../../../..` → `scratchpad/baseline_v3/PROVENANCE-v3.txt`, copied into this directory as
`STIMULUS.txt`, and cover the briefs, the composed prompts, the data and the harness scripts.

## What this run can and cannot settle

- It **can** give DX01 and DX02 their first measurement against the **current** briefs, which is
  the half of the DX02 blocker that the rules 1–4 re-grade explicitly did not close.
- It **can** give DX03, DX04 and DX05 their first measurement of any kind.
- It **cannot** be called a published baseline at n below 5, and a single pilot run settles
  nothing about discrimination — the quantity that decides weight is the range across runs, not
  any one total.
