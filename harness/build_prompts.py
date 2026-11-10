#!/usr/bin/env python3
"""Compose the six DELTA-X v2 task prompts that are actually fed to an agent.

A prompt is: an operational preamble + the verbatim task brief from `tasks/`.
The preamble is operational only -- it names no region, statistic, threshold or
expected result. Changing it changes the measurement, so any edit must be
recorded in the campaign's PROVENANCE.txt alongside the new digest.

    python3 -I harness/build_prompts.py --repo <repo root> --out <dir> \
            [--environment <ENVIRONMENT.md>] [--data-dir ./data]

Writes <out>/s1.txt ... <out>/s5.txt and prints one line per prompt built.
"""
import argparse
import hashlib
import io
import os
import sys

# stage tag, brief basename, tools?, wall-clock minutes offered to the agent
STAGES = [
    ("s1",  "DX01",  False, 30),
    ("s2",  "DX02",  False, 30),
    ("s2b", "DX02B", False, 30),
    ("s3",  "DX03",  True,  90),
    ("s4",  "DX04",  True, 120),
    ("s5",  "DX05",  True,  45),
]

NOTOOL = """You are an agent under evaluation in a scientific-discovery benchmark. This is task {n} of {N}.

HOW TO ANSWER
- This task releases no data and requires no tools. Bash and network access are DISABLED for it.
  That is deliberate: this task is testing what you commit to BEFORE you see evidence.
- Write every required artifact as a FILE in your current working directory, using exactly the
  filename the brief gives. Writing it only in your reply does not count as delivering it.
- Follow the brief exactly and deliver every artifact it names.

--- BEGIN TASK BRIEF ---
{brief}
--- END TASK BRIEF ---
"""

TOOLED = """You are an agent under evaluation in a scientific-discovery benchmark. This is task {n} of {N}.

YOU HAVE A REAL SHELL. THIS IS NOT A SIMULATION, AND NOTHING HERE IS HYPOTHETICAL.
- Bash is enabled. The tools listed below are installed on this machine at those absolute
  paths, and **you are expected to actually run them**.
- Do NOT describe an analysis you did not run. Do NOT hand in a plan where results are asked for.
  Every number in a scored artifact must come from a command you actually executed on this host.
- A number that no recorded command produced is **struck before scoring**, whether or not it is
  correct, and it cannot support any other conclusion either.
- If a tool fails or returns nothing, that is a legitimate result: report the error or the empty
  result and carry on. Reporting a real negative is scored as a success. Inventing a value is not.

YOUR INPUT DATA IS ALREADY IN YOUR WORKING DIRECTORY
  {data}/TDT.curated.fasta    322 sequences, subfamily A
  {data}/POLM.curated.fasta   165 sequences, subfamily B
  {data}/refs.fasta             7 reference sequences

{env}

OUTPUT
- Write every artifact as a FILE in your working directory, with exactly the filename the brief
  gives. Artifacts printed only in your reply are not delivered.
- Maintain `./execution_log.json` as a JSON array, one record per command you actually ran, in
  execution order, each with: the artifact it serves, the absolute path of the executable, the
  version the tool reports for itself, the FULL argv as executed, cwd, exit code, wall-clock
  seconds, any random seed, the path and SHA-256 of every input and output file, and the retained
  paths of stdout and stderr. Keep the stdout/stderr files; do not summarise them.

WORKING BUDGET
- You have up to {mins} minutes of wall clock for this task. Prefer delivering every required
  artifact over perfecting any single one. If you run short, deliver partial artifacts and say
  in them what is missing and why.

CONTAINMENT
- Your working directory is the only place you may read from or write to, apart from the tool
  paths above and the public internet where this brief allows it.
- Do not go looking around the filesystem for this benchmark's own materials, answer keys or
  scoring files. Doing so voids this run.

--- BEGIN TASK BRIEF ---
{brief}
--- END TASK BRIEF ---
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="repository root (holds tasks/)")
    ap.add_argument("--out", required=True, help="directory to write s*.txt into")
    ap.add_argument("--environment", default=None,
                    help="ENVIRONMENT.md for this host; default <repo>/tasks/ENVIRONMENT.example.md")
    ap.add_argument("--data-dir", default="./data",
                    help="where the agent will find the FASTA files, as it should see the path")
    a = ap.parse_args()

    tasks = os.path.join(a.repo, "tasks")
    envp = a.environment or os.path.join(tasks, "ENVIRONMENT.example.md")
    if not os.path.isdir(tasks):
        sys.exit("no tasks/ under %s" % a.repo)
    if not os.path.exists(envp):
        sys.exit("no ENVIRONMENT.md at %s -- run env/probe_env.sh first" % envp)
    env = io.open(envp, encoding="utf-8").read().strip()
    if envp.endswith("ENVIRONMENT.example.md"):
        sys.stderr.write(
            "WARNING: composing prompts against the reference host's ENVIRONMENT.example.md.\n"
            "         Tool paths in it almost certainly do not exist on this machine.\n"
            "         Run env/probe_env.sh and pass --environment for a real measurement.\n")

    os.makedirs(a.out, exist_ok=True)
    present = [s for s in STAGES if os.path.exists(os.path.join(tasks, s[1] + ".md"))]
    n_total = len(present)
    for i, (tag, task, tooled, mins) in enumerate(present, 1):
        brief = io.open(os.path.join(tasks, task + ".md"), encoding="utf-8").read().strip()
        text = (TOOLED if tooled else NOTOOL).format(
            n=i, N=n_total, brief=brief, env=env, mins=mins, data=a.data_dir.rstrip("/"))
        dest = os.path.join(a.out, tag + ".txt")
        io.open(dest, "w", encoding="utf-8").write(text)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print("%-4s %-6s %-8s %6d chars  %s" % (
            tag, task, "TOOLED" if tooled else "no-tool", len(text), digest[:16]))


if __name__ == "__main__":
    main()
