#!/usr/bin/env python3
"""Compute the DX01 commitment digest the submission asked the harness to compute.

DX01 §3.5 lets an agent whose tools are blocked commit to its artifacts by
declaring a byte-exact canonicalisation rule instead of a SHA-256 it cannot
compute. This script is the other half of that bargain: it reads the rule the
submission declared and computes the digest under it.

It records the file order it used rather than imposing one. Where the submission
declared no order, that fact is written into the output -- six runs of the same
model put the file list at three different JSON paths and split 3/3 on hash
order, producing six different digests from byte-identical inputs. That is a
defect in DX01's wording, not in any submission, and the `order_note` field is
where it stays visible.

    python3 -I harness/harness_digest.py <run-dir>

Reads <run-dir>/work/prereg_commit.json, writes <run-dir>/out/harness_digest.json.
"""
import hashlib
import io
import json
import os
import sys


def find_list(obj):
    """Return (file list, json path) from the four shapes submissions have used."""
    if not isinstance(obj, dict):
        return [], None
    for path in (("committed_files", "order"), ("committed_files", "files"),
                 ("committed_files",), ("files",), ("canonicalisation", "file_order"),
                 ("canonicalization", "file_order"), ("file_order",)):
        cur = obj
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, list) and cur:
            if all(isinstance(x, str) for x in cur):
                return cur, "/".join(path)
            names = [x.get("path") or x.get("file") or x.get("name")
                     for x in cur if isinstance(x, dict)]
            if all(names):
                return names, "/".join(path)
    return [], None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = os.path.abspath(sys.argv[1])
    if not os.path.isdir(run):
        sys.exit("no such run directory: %s" % run)
    work = os.path.join(run, "work")
    if not os.path.isdir(work):
        sys.exit("%s has no work/ subdirectory -- is it a run directory?" % run)
    out_dir = os.path.join(run, "out")
    os.makedirs(out_dir, exist_ok=True)
    pc = os.path.join(work, "prereg_commit.json")
    if not os.path.exists(pc):
        print("%s: no prereg_commit.json -- DX01 gate (d) has nothing to check"
              % os.path.basename(run))
        return
    try:
        j = json.load(io.open(pc, encoding="utf-8"))
    except Exception as e:                                    # noqa: BLE001
        print("%s: unparseable prereg_commit.json: %s" % (os.path.basename(run), e))
        return
    if isinstance(j, list) and j:
        j = j[0]

    order, where = find_list(j)
    if order:
        note = "order as declared by the submission, read from %s" % where
    else:
        order = sorted(f for f in os.listdir(work)
                       if f.endswith(".json") and f != "prereg_commit.json")
        note = "order NOT declared; harness used ascending filename sort"

    h = hashlib.sha256()
    per, missing = {}, []
    for f in order:
        p = os.path.join(work, os.path.basename(f))
        if not os.path.exists(p):
            missing.append(f)
            continue
        b = io.open(p, "rb").read()
        per[f] = {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
        h.update(b)

    out = {
        "run": os.path.basename(run),
        "order": order,
        "order_note": note,
        "missing": missing,
        "per_file": per,
        "declared_digest": j.get("digest"),
        "declared_status": str(j.get("digest_status"))[:300],
        "commitment_digest": None if missing else h.hexdigest(),
        "computed_by": "harness",
    }
    dest = os.path.join(out_dir, "harness_digest.json")
    io.open(dest, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print("%s digest=%s missing=%s -> %s"
          % (out["run"], out["commitment_digest"], missing or "none", dest))


if __name__ == "__main__":
    main()
