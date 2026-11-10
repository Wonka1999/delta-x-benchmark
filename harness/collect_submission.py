#!/usr/bin/env python3
"""Package a finished run directory into a submission a grader can score.

Copies the artifacts, the execution logs and the provenance record out of the
clean-room working directory, checks which required artifacts each task actually
produced, and writes a manifest with a SHA-256 for every file.

    python3 -I harness/collect_submission.py <run-dir> --out <submission-dir>

Completeness is reported, never scored here. A missing artifact is a fact the
grader needs before reading anything else; several scored items in DX03-DX05 are
defined on an artifact being present and non-empty, and an empty file is not the
same finding as an absent one. Both are distinguished below.
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import sys

REQUIRED = {
    "DX01": ["axis_declaration.json", "sealed_prior.json", "recognition_declaration.json",
             "hypotheses.json", "prereg_commit.json"],
    "DX02": ["method_plan.json", "granularity_declaration.json", "power_budget.json"],
    "DX02B": ["branch_expectations.json", "invalidation_control.json",
              "resolution_commitment.json", "portability_commitment.json", "pre_mortem.json"],
    "DX03": ["alignment_manifest.json", "column_scores.tsv", "nominated_regions.json",
             "method_sensitivity.json", "granularity_report.json",
             "dx03_could_not_determine.json", "segment_properties.json",
             "execution_log.json"],
    "DX04": ["structures_manifest.json", "superposition.tsv", "region_nominations.json",
             "null_report.json", "prediction_validity.json", "dx04_could_not_determine.json",
             "rejected_candidates.json", "execution_log.json"],
    "DX05": ["synthesis.json", "polarity.json", "delta_over_prior.json",
             "dx05_could_not_determine.json", "negative_results.json"],
}
# DX03 and DX04 each require their own execution_log.json, but a single resumed
# session usually appends to one file. One log covering both is accepted; the
# grader checks coverage by the `purpose` field, not by the filename.


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(path):
    """present_nonempty | present_empty | absent, plus the record count if JSON."""
    if not os.path.exists(path):
        return "absent", None
    size = os.path.getsize(path)
    if size == 0:
        return "present_empty", 0
    if path.endswith(".json"):
        try:
            obj = json.load(io.open(path, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            return "present_unparseable", None
        n = len(obj) if isinstance(obj, (list, dict)) else 1
        return ("present_empty" if n == 0 else "present_nonempty"), n
    if path.endswith(".tsv") or path.endswith(".csv"):
        n = max(0, sum(1 for _ in io.open(path, encoding="utf-8", errors="replace")) - 1)
        return ("present_empty" if n == 0 else "present_nonempty"), n
    return "present_nonempty", None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    run = os.path.abspath(a.run_dir)
    work = os.path.join(run, "work")
    if not os.path.isdir(work):
        sys.exit("%s has no work/ subdirectory -- is it a run directory?" % run)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, "artifacts"), exist_ok=True)
    os.makedirs(os.path.join(out, "harness"), exist_ok=True)

    # 1. artifacts, minus the served data
    copied = []
    for root, dirs, files in os.walk(work):
        dirs[:] = [d for d in dirs if d != "data"]
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, work)
            dst = os.path.join(out, "artifacts", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)

    # 2. harness record: provenance, adapter output, stage logs
    for name in ("PROVENANCE.txt",):
        p = os.path.join(run, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(out, name))
    odir = os.path.join(run, "out")
    if os.path.isdir(odir):
        for f in sorted(os.listdir(odir)):
            if f == "session.json":          # a session id is not evidence
                continue
            shutil.copy2(os.path.join(odir, f), os.path.join(out, "harness", f))

    # 3. completeness, per task
    completeness = {}
    for task, names in REQUIRED.items():
        rows = {}
        for n in names:
            state, count = classify(os.path.join(out, "artifacts", n))
            rows[n] = {"state": state, "records": count}
        missing = [n for n, r in rows.items() if r["state"] == "absent"]
        completeness[task] = {"artifacts": rows, "missing": missing,
                              "complete": not missing}

    # 4. manifest
    manifest = {}
    for root, _, files in os.walk(out):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, out)
            if rel in ("MANIFEST.sha256", "completeness.json", "SUBMISSION.md"):
                continue
            manifest[rel] = sha256(p)

    io.open(os.path.join(out, "completeness.json"), "w", encoding="utf-8").write(
        json.dumps(completeness, indent=1))
    with io.open(os.path.join(out, "MANIFEST.sha256"), "w", encoding="utf-8") as fh:
        for rel in sorted(manifest):
            fh.write("%s  %s\n" % (manifest[rel], rel))

    lines = ["# Submission -- %s" % os.path.basename(run), "",
             "%d artifact files, %d files in the manifest." % (len(copied), len(manifest)),
             "", "| task | complete | missing |", "|---|---|---|"]
    for task in ("DX01", "DX02", "DX02B", "DX03", "DX04", "DX05"):
        c = completeness[task]
        lines.append("| %s | %s | %s |" % (
            task, "yes" if c["complete"] else "NO",
            ", ".join(c["missing"]) if c["missing"] else "--"))
    lines += ["", "Empty-but-present artifacts are listed in `completeness.json`; several "
              "scored items treat an empty file as a claim, not as an absence.", "",
              "Grade with `grader/GRADING.md`. Nothing in `grader/` may be shown to the "
              "system that produced this submission."]
    io.open(os.path.join(out, "SUBMISSION.md"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")

    print("submission: %s" % out)
    for task in ("DX01", "DX02", "DX02B", "DX03", "DX04", "DX05"):
        c = completeness[task]
        print("  %-6s %s%s" % (task, "complete" if c["complete"] else "INCOMPLETE",
                               "" if c["complete"] else "  missing: " + ", ".join(c["missing"])))


if __name__ == "__main__":
    main()
