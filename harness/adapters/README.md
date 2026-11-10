# Adapter contract

An adapter is the only thing you write to put a new system through DELTA-X v2. It is a single
executable that runs **one task** and returns. The driver (`harness/run_campaign.sh`) handles
staging, ordering, timeouts, snapshots and provenance; the adapter handles nothing but talking
to your system.

## Interface

```
<adapter> --prompt-file <path> --workdir <path> --mode <tools|notools> \
          --timeout-seconds <int> --session-file <path> --out-json <path> [--model <id>]
```

| argument | obligation |
|---|---|
| `--prompt-file` | the complete task prompt, UTF-8, up to ~40 KB. Feed it verbatim. Do not summarise it, prepend to it, or split it. |
| `--workdir` | the agent's working directory. **Every command and every file write happens inside it.** Refuse anything that escapes by absolute path or `..`, and say so in the transcript rather than silently rewriting it. |
| `--mode notools` | the system gets **no** shell, no network, no file execution. It may still write the artifact files. DX01, DX02 and DX02B are measured this way by design — they test what is committed before evidence. A system that runs tools here is not being measured on the thing the task tests. |
| `--mode tools` | the system gets a real shell in the workdir, and network access where the brief allows it. DX03, DX04 and DX05. |
| `--timeout-seconds` | hard wall clock for this task. On expiry, stop cleanly, keep what is on disk, report `timed_out: true`. A timeout is a measurement condition, not a harness error. |
| `--session-file` | conversation continuity across tasks. Load prior state on start, write updated state on exit. The six tasks are sequential and each must see its predecessors — DX05 is defined on the agent's own DX01–DX04 artifacts. |
| `--out-json` | a result record: model id, mode, turns, tool calls, exit reason, `timed_out`, wall-clock seconds, token usage if available, final text, and the path of a full transcript. |
| `--model` | passed through verbatim. Pin it for any published measurement. |

Exit 0 when the task completed **or** timed out gracefully. Non-zero only on a configuration
error — a missing key, an unreadable prompt. The driver treats non-zero as "this stage did not
run", and the stages that follow still execute.

## Shipped adapters

| adapter | drives | notes |
|---|---|---|
| `claude_code.sh` | Anthropic models via the Claude Code headless CLI | uses explicit `--allowedTools`, never `--dangerously-skip-permissions`. `notools` still permits `Write`, so artifacts land as files and DX01's commitment goes down the harness-computes-the-digest branch. |
| `openai_agent.py` | OpenAI / OpenAI-compatible endpoints | an agentic loop with a bash tool and a file-write tool. Needs `pip install openai` and `OPENAI_API_KEY`; honours `OPENAI_BASE_URL`. Pin `--model` for any published measurement — the built-in default drifts. `--self-test` runs 30 offline checks without an API key. |
| `stub.sh` | nothing — it fabricates minimal artifacts | for testing your installation end to end without spending a token. Its output is **not** a submission and will not survive grading. |
| `evoagenda.sh` | your system | a template. Fill in one line. |

## Writing your own

Copy `evoagenda.sh`. The only thing you must supply is the command that hands a prompt to your
system with a working directory and a tool policy. Four things people get wrong:

1. **Tool policy is per task, not per campaign.** If your system cannot be told "no tools for
   this one", say so in the campaign report; DX01/DX02/DX02B then measure something else and
   the result is not comparable to a run that blocked them.
2. **Artifacts must be real files with the exact filenames the brief gives.** A system that
   returns everything in its final message delivers nothing. If your system is bad at writing
   files, give it a `write_file` tool rather than hoping; `openai_agent.py` does exactly that.
3. **Continuity is not optional.** Starting each task fresh changes what DX02B and DX05 measure
   — both are defined against the system's own earlier commitments.
4. **Do not grant access to this repository.** The repository holds the answer key. Stage the
   run outside it (the driver refuses otherwise) and let `harness/audit_containment.py` check.

## Checking an adapter before spending anything

```bash
harness/run_campaign.sh --run-id smoke --adapter stub --work ~/delta-x-runs --stages s1,s2
python3 -I harness/collect_submission.py ~/delta-x-runs/smoke --out /tmp/smoke-sub
python3 -I harness/audit_containment.py  ~/delta-x-runs/smoke
```

Then swap `--adapter stub` for yours and re-run with `--stages s1` only. If DX01 produces five
JSON files in the workdir, the plumbing is right.
