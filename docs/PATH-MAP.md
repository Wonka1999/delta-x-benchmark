# Path map — the private layout this release was extracted from

**CONTAINMENT.** Designer-side.

The designer-side documents (`grader/KEY.md`, `grader/FIXSPEC*.md`, `repro/REPRODUCTION.md`,
`docs/DESIGN.zh.md` and the others) were written against the private working tree and are
reproduced here **unedited**, because they are the record of how every number and every rule was
decided. Rewriting a path inside a revision record falsifies the record. Two directories were
renamed on release:

| written as | now at | note |
|---|---|---|
| `agent_facing/` | `tasks/` | the agent-visible briefs |
| `repro/data/` | `data/` | the curated sequence sets, promoted to the top level because the agent is served from them |

Everything else keeps its name: `grader/`, `repro/scripts/`, `repro/MANIFEST.sha256`,
`grader/baselines/`.

Two consequences worth stating:

- **`brief_digests` keys.** The six published scorecards key their `brief_digests` on
  `agent_facing/DX01.md`; `grader/SCORECARD.md` now specifies `tasks/DX01.md`. The checker
  requires the block to be present and does not constrain the prefix, so both validate. Use
  `tasks/` for anything new.
- **Absolute paths in `repro/scripts/`.** Those scripts were written during the reproduction run
  and carry absolute scratchpad paths. Adjust the input paths before re-running them;
  `repro/REPRODUCTION.md` says so and it is still true.
