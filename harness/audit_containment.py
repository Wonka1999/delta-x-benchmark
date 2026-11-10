#!/usr/bin/env python3
"""DELTA-X v2 containment audit. MANDATORY before any score is read.

    python3 -I harness/audit_containment.py <run-dir> [<run-dir> ...]

The repository holds the answer key, the frozen decoy sets, the measured
baselines and the scoring rules. A run whose transcript or artifacts show the
agent reached any of that has not been measured -- it has been told. Such a run
is VOID, and the correct response is to re-run it, not to discount it.

Two checks, and one thing deliberately not checked.

1. Designer-side material by name. The files under `grader/`, the reproduction
   record and the reader pages, by the names they would appear under.
2. Any absolute path into the repository.

Not checked: the run directory's own path. An agent that logs its own cwd is not
a leak, and an earlier grep-based version of this audit voided a clean run for
exactly that -- the harness happened to live under a directory whose name also
appears in pattern 1. Every occurrence of the run path is removed before matching.

Exit 0 = clean. Exit 1 = at least one run is void.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAMES = re.compile(
    r"KEY\.md|KEY-DX02B|SCORECARD\.md|FRAME-DISCIPLINE|FIXSPEC|check_scorecard"
    r"|REPRODUCTION\.md|DESIGN\.zh|BASELINE-v\d|REGRADE|grader/"
    r"|for_ml_readers|case_walkthrough|worked_example|delta_x_v2")

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".ipynb_checkpoints"}
SKIP_EXT = {".pyc", ".pyo", ".so", ".o", ".pdb", ".cif", ".npy", ".npz",
            ".png", ".jpg", ".pdf", ".gz", ".zip", ".pt", ".bin"}
MAX_BYTES = 64 * 1024 * 1024
EXAMPLES = 5


def text_of(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    return raw.decode("utf-8", "replace")


def audit(run):
    run = os.path.abspath(run)
    if not os.path.isdir(run):
        print("%s: not a directory" % run)
        return False
    name = os.path.basename(run)

    inside = (run + os.sep).startswith(REPO + os.sep)
    data_dir = os.path.join(run, "work", "data")
    name_hits, path_hits = [], []

    for root, dirs, files in os.walk(run):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if os.path.abspath(root).startswith(data_dir):
            continue
        for f in files:
            p = os.path.join(root, f)
            if os.path.splitext(f)[1].lower() in SKIP_EXT:
                continue
            body = text_of(p)
            if body is None:
                continue
            # The run's own location is not evidence of anything.
            body = body.replace(run, "<RUN>")
            rel = os.path.relpath(p, run)
            for m in NAMES.finditer(body):
                s = max(0, m.start() - 40)
                name_hits.append((rel, m.group(0),
                                  body[s:m.end() + 40].replace("\n", " ")))
            idx = body.find(REPO)
            while idx != -1:
                path_hits.append((rel, REPO,
                                  body[max(0, idx - 20):idx + len(REPO) + 40].replace("\n", " ")))
                idx = body.find(REPO, idx + 1)

    void = bool(name_hits or path_hits or inside)
    if not void:
        print("%s  containment OK" % name)
        return True

    print("%s  CONTAINMENT BREACH -- RUN IS VOID" % name)
    if inside:
        print("    the run directory is inside the repository (%s)" % REPO)
    for label, hits in (("designer-side names", name_hits), ("repository path", path_hits)):
        if not hits:
            continue
        files_hit = sorted({h[0] for h in hits})
        print("    %s: %d hit(s) in %d file(s)" % (label, len(hits), len(files_hit)))
        for rel, tok, ctx in hits[:EXAMPLES]:
            print("      %s: %r ... %s" % (rel, tok, ctx[:120]))
        if len(hits) > EXAMPLES:
            print("      ... %d more" % (len(hits) - EXAMPLES))
    return False


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ok = True
    for d in sys.argv[1:]:
        ok = audit(d) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
