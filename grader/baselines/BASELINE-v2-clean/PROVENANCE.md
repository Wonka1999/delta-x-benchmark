# BASELINE-v2-clean — preserved record

Copied 2026-11-08 from a session scratchpad that would otherwise have been reclaimed.
Designer-side under the repository containment rule: nothing here may be rendered into an
evaluated agent's context.

## What is here

| Path | Content |
|---|---|
| `prompts/s{1,2,3}.txt` | the **measured stimulus** — the agent-facing text as it stood at measurement time, NOT the current briefs |
| `out/run{1,2,3}_s{1,2,3}.{md,json,err}` | the three runs' raw submissions and CLI records |
| `drive.sh` | the driver used for the clean-room runs |

## Stimulus drift — the records are NOT a baseline for the current briefs

The briefs were edited **after** this measurement. `prompts/` is therefore the only surviving
copy of what the three runs actually read, and it differs from `agent_facing/` today:

- DX01 §3.5 demanded one unconditional SHA-256; it is now a two-form conditional commitment.
  §4 criterion (d) and §6 were also rewritten. The gate criterion these runs FAILed no longer
  exists.
- DX02 was 20 points with six-point null and abandon items; it is now 10 points with those two
  items converted to 0-point PASS/FAIL gates, plus four scoring rules (denominator and rounding,
  input-side only, quotable sources, outcome coupling) that these runs never saw.
- Drift not recorded in `FIXSPEC.md`: `prompts/s2.txt` reads `optionally a coevolution package`
  and `451-620 aa`; `agent_facing/DX02.md` now reads `a coevolution package` and `451-616 aa`.
- DX03 30 -> 35 and DX04 30 -> 35; these runs never reached DX03-DX05.

Consequence: re-grading these records under the current rules is an arithmetic **diagnostic**,
not a baseline. The runs optimised against a rubric that no longer exists. A weight decision
needs a fresh run against the current briefs.

## Digest of the current briefs, for the next baseline block

Recorded 2026-11-08, so that a future baseline can state whether its stimulus matches.

```
0f5fd72cfd378826426f77c87cd34335e5c243b867ca49b7afddcc495bf8c896  agent_facing/DX01.md
25aecd18bbc855e91049fe29c8e201c320008de1a72d299409f2dcaaf514b6b0  agent_facing/DX02.md
b5a37a7bf92ab2bd4bb62fb0586aeeacf4b66bd848bafc11b3fa79dd4c4d1574  agent_facing/DX03.md
bdbdc7efc4e2f0f9732d4aebe4ef1af37b41c7a15c3e074d72e637f9cf554a45  agent_facing/DX04.md
a8704ff6a3b32328deca6dc82272fe94c667b3fd0b73fdd1a6d957d86e7bb4ad  agent_facing/DX05.md
```

No digest of the *measured* briefs exists: they were not hashed before the edits. `prompts/` is the only reconstruction.

### Superseded — corrected 2026-11-09

**The block above was already stale when it was written.** It was recorded on 2026-11-08
"so that a future baseline can state whether its stimulus matches", but the fix round edited
all five briefs later the same evening (mtimes 22:18–22:45) and the block was never refreshed.
Every one of the five digests above is therefore **not** what is on disk.

The current digests, recorded 2026-11-09 and verified against the stimulus actually fed to
BASELINE-v3-tooled:

```
a252eda0ab30c4cf95299444613e33a09a1cec0587711e1a2f78ae9dae0d7c76  agent_facing/DX01.md
e252d2d99481dd72d00a4e5cdf31aac1af427184249a1edaa2d71dca78e6a384  agent_facing/DX02.md
fb8aef3c025e7397146725b16ae1c967ed85160ecf65d280c3403521ff307cb3  agent_facing/DX03.md
a706fc642593cd163e98a664ee2ecadb772d051c9d6db9ce9adbdd58cdc438d1  agent_facing/DX04.md
e89f467917d874ef0c0940c9d8bd504e1b4744d38de2ce176115a10d35f15d40  agent_facing/DX05.md
7b6e5039f5aafee84cf9be66fe4ee71049d4ed35a2aef368b53aac3d4b0236f7  agent_facing/ENVIRONMENT.md
```

**The lesson is the one this benchmark keeps re-learning.** A digest recorded for a future
comparison is worthless unless something re-checks it at the moment of use; nothing did, and
the only reason it surfaced is that the next baseline hashed the briefs before serving them
rather than trusting the record. A stimulus digest belongs in the run's own
`scorecard.json` (`brief_digests`, `SCORECARD.md`), computed at serve time — not in a prose
block that has to be remembered.

## Re-grade under the current rules — 2026-11-09

`REGRADE-rules1-4.md` (this directory) re-grades all three DX02 records under the current
10-point rubric: **3.0 / 1.0 / 5.0**, range **4.0/10 (40 %)** against the old rubric's
0.4/20 (2 %), rank order inverted. This closes the **STILL OPEN** DX02 weight blocker in
`KEY.md`.

It remains an **arithmetic diagnostic over the preserved records**, for the reason stated under
*Stimulus drift* above: these three submissions were optimised against a rubric that no longer
exists. The digests listed above are still the ones a fresh baseline must match.
