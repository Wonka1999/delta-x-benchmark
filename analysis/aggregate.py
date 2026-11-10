#!/usr/bin/env python3
"""Aggregate DELTA-X v2 scorecards into a campaign result.

A score that is not accompanied by a per-item scorecard is not a score
(grader/SCORECARD.md). This tool reads the scorecards, re-derives every total from the
rows rather than trusting the stored one, and reports the number the benchmark actually
steers on: per-item discrimination, range / max.

    python3 -I analysis/aggregate.py <scorecard.json ...|dir> [--out-md P] [--out-csv P]
                                     [--label NAME] [--compare DIR] [--no-gate]

Exit 0 = every scorecard reconciles. Exit 1 = at least one did not, or nothing was read;
the run that did not is named. --no-gate always exits 0.

Designer-side. Reads grading records; never render a scorecard into an evaluated agent's
context. Stdlib only, Python 3.9+.
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys

TOL = 1e-6
SCHEMA_EXPECTED = "delta-x-v2/scorecard/1"
# item_id components that identify the run or the grader's bookkeeping, not the rubric row
NOISE_PART = re.compile(r"^(run\d+|summary|total)$", re.I)
SUBITEM = re.compile(r"^(I\d+)[a-z]$")
MISSING = "--"


def num(x):
    """True for a real number; bool is not a number here."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def fmt(x, nd=2):
    if x is None:
        return MISSING
    if num(x):
        s = ("%%.%df" % nd) % float(x)
        return s.rstrip("0").rstrip(".") if "." in s else s
    return str(x)


def fx(x, nd=2):
    """Fixed decimals, for statistics where trailing zeros carry precision."""
    return ("%%.%df" % nd) % float(x) if num(x) else MISSING


# --------------------------------------------------------------------------- loading


def collect_paths(inputs):
    """Expand files and directories into a sorted list of candidate scorecard paths."""
    paths, missing = [], []
    for raw in inputs:
        p = os.path.abspath(os.path.expanduser(raw))
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.endswith(".json") and "scorecard" in name.lower():
                    paths.append(os.path.join(p, name))
        elif os.path.isfile(p):
            paths.append(p)
        else:
            missing.append(raw)
    return paths, missing


class Run(object):
    """One scorecard, with everything recomputed from its own rows."""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.run_id = self.name
        self.ok = False            # parsed into something usable
        self.reconciles = False    # our recomputation agrees with the stored numbers
        self.problems = []         # loud findings, printed per run
        self.notes = []            # quieter findings (schema drift, odd types)
        self.items = []            # normalised rows
        self.task_totals = {}
        self.item_sum_computed = 0.0
        self.item_sum_stored = None
        self.total_stored = None
        self.total_expected = None
        self.caps = []
        self.gate_label = MISSING
        self.gates_failed = []
        self.strikes = []
        self.fabrications = 0
        self.reported_beside = []
        self.measured_scope = ""

    @property
    def total(self):
        """The total we would publish: recomputed, never the stored one."""
        return self.total_expected if self.total_expected is not None else self.total_stored


def load_run(path):
    """Parse one scorecard. Never raises: a bad file comes back as a Run with problems."""
    r = Run(path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            sc = json.load(fh)
    except json.JSONDecodeError as exc:
        r.problems.append("unreadable JSON: %s" % exc)
        return r
    except OSError as exc:
        r.problems.append("cannot open: %s" % exc)
        return r
    if not isinstance(sc, dict):
        r.problems.append("top level is %s, not an object: not a scorecard"
                          % type(sc).__name__)
        return r

    schema = sc.get("schema")
    if schema != SCHEMA_EXPECTED:
        r.notes.append("schema is %r, expected %r — parsed on a best-effort basis"
                       % (schema, SCHEMA_EXPECTED))
    r.run_id = str(sc.get("submission_id") or r.name)

    items = sc.get("items")
    gates = sc.get("gates")
    if not isinstance(items, list):
        r.problems.append("items[] missing or not a list")
        items = []
    if not isinstance(gates, list):
        if gates is not None:
            r.notes.append("gates[] is not a list; ignored")
        gates = []
    if not items and not gates:
        r.problems.append("neither items[] nor gates[]: this is not a scorecard")
        return r

    _load_items(r, items)
    _load_gates(r, gates)
    _load_integrity(r, sc)
    _load_campaign(r, sc.get("campaign"))

    r.ok = True
    r.reconciles = not r.problems
    return r


def _load_items(r, items):
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            r.problems.append("items[%d] is not an object; skipped" % idx)
            continue
        iid = it.get("item_id") or ("<unnamed item %d>" % idx)
        task = it.get("task")
        if not task:
            task = str(iid).split(".")[0] if "." in str(iid) else "<no task>"
            r.notes.append("%s: no task field; grouped under %r by item_id prefix"
                           % (iid, task))
        awarded, mx = it.get("awarded"), it.get("max")
        if not num(awarded):
            r.problems.append("%s: awarded is %r, not a number — row cannot be summed"
                              % (iid, awarded))
            awarded = None
        if not num(mx):
            r.notes.append("%s: max is %r, not a number" % (iid, mx))
            mx = None
        if awarded is not None:
            if awarded < 0:
                r.problems.append("%s: negative award %s — item deductions floor at 0 for "
                                  "their own item (SCORECARD.md, floor_applied)"
                                  % (iid, fmt(awarded)))
            if mx is not None and awarded > mx + TOL:
                r.problems.append("%s: awarded %s exceeds max %s"
                                  % (iid, fmt(awarded), fmt(mx)))
            r.item_sum_computed += float(awarded)
            r.task_totals[task] = r.task_totals.get(task, 0.0) + float(awarded)
        else:
            r.task_totals.setdefault(task, 0.0)
        deds = it.get("deductions")
        if isinstance(deds, list):
            for d in deds:
                if isinstance(d, dict) and not d.get("rule"):
                    r.notes.append("%s: a deduction of %s names no rule — SCORECARD.md "
                                   "rule 2 removes it before reconciliation"
                                   % (iid, fmt(d.get("amount"))))
        r.items.append({"item_id": str(iid), "task": str(task),
                        "max": mx, "awarded": awarded})


def _load_gates(r, gates):
    dx01 = [g for g in gates if isinstance(g, dict)
            and str(g.get("gate_id", "")).upper().startswith("DX01")]
    for g in gates:
        if isinstance(g, dict) and str(g.get("verdict", "")).upper() == "FAIL":
            r.gates_failed.append((str(g.get("gate_id") or "<unnamed gate>"),
                                   str(g.get("consequence") or "no consequence recorded")))
    if dx01:
        bad = [g for g in dx01 if str(g.get("verdict", "")).upper() != "PASS"]
        r.gate_label = ("PASS %d/%d" % (len(dx01), len(dx01)) if not bad
                        else "FAIL %d/%d" % (len(dx01) - len(bad), len(dx01)))
    elif gates:
        r.gate_label = "no DX01 gate"


def _load_integrity(r, sc):
    strikes = sc.get("strikes")
    if isinstance(strikes, list):
        for s in strikes:
            cls = (s.get("classification") if isinstance(s, dict) else None) or "<unclassified>"
            r.strikes.append(str(cls))
    elif strikes is not None:
        r.notes.append("strikes[] is not a list; ignored")
    fabs = sc.get("fabrication_events")
    if isinstance(fabs, list):
        r.fabrications = len(fabs)
        for f in fabs:
            if not isinstance(f, dict):
                continue
            chk = f.get("self_reproduction_check") or {}
            if str(f.get("verdict", "")).lower() == "fabrication" and not (
                    isinstance(chk, dict) and chk.get("tool_reproduced_itself")):
                r.problems.append("fabrication verdict on %r without a passing "
                                  "self_reproduction_check — void under SCORECARD.md"
                                  % f.get("artifact"))
    elif fabs is not None:
        r.notes.append("fabrication_events[] is not a list; ignored")


def _load_campaign(r, camp):
    if not isinstance(camp, dict):
        r.problems.append("campaign block missing or not an object — nothing to reconcile "
                          "the rows against")
        return
    r.item_sum_stored = camp.get("item_sum")
    r.total_stored = camp.get("total")
    r.measured_scope = str(camp.get("measured_scope") or "")
    if not r.measured_scope:
        r.notes.append("campaign.measured_scope is empty — SCORECARD.md requires it to name "
                       "what was NOT measured")

    caps = camp.get("caps_applied")
    if isinstance(caps, list):
        for c in caps:
            if isinstance(c, dict) and num(c.get("cap")):
                r.caps.append((float(c["cap"]), str(c.get("reason") or "no reason recorded")))
            elif c is not None:
                r.notes.append("caps_applied entry %r carries no numeric cap; ignored in the "
                               "recomputation" % (c,))
    elif caps is not None:
        r.notes.append("caps_applied is not a list; ignored")

    # 1. the total must equal the sum of the rows
    if not num(r.item_sum_stored):
        r.problems.append("campaign.item_sum is %r, not a number" % (r.item_sum_stored,))
    elif abs(float(r.item_sum_stored) - r.item_sum_computed) > TOL:
        r.problems.append("sum(items[].awarded) = %s but campaign.item_sum = %s"
                          % (fmt(r.item_sum_computed, 4), fmt(r.item_sum_stored, 4)))

    # 2. the stored total must follow from item_sum and the caps
    basis = float(r.item_sum_stored) if num(r.item_sum_stored) else r.item_sum_computed
    expected = basis
    for cap, _reason in r.caps:
        expected = min(expected, cap)
    r.total_expected = expected
    if not num(r.total_stored):
        r.problems.append("campaign.total is %r, not a number" % (r.total_stored,))
    elif abs(float(r.total_stored) - expected) > TOL:
        r.problems.append("campaign.total = %s but item_sum %s with caps %s gives %s"
                          % (fmt(r.total_stored, 4), fmt(basis, 4),
                             ("[" + ", ".join(fmt(c) for c, _ in r.caps) + "]")
                             if r.caps else "[]", fmt(expected, 4)))

    # 3. the scorecard's own self-report, checked rather than believed
    claimed = camp.get("reconciles")
    if claimed is False and not r.problems:
        r.notes.append("campaign.reconciles is false but every check here passed")
    if claimed is True and r.problems:
        r.problems.append("campaign.reconciles claims true against the failures above")

    rb = camp.get("reported_beside")
    if isinstance(rb, list):
        for e in rb:
            if isinstance(e, dict):
                r.reported_beside.append(e)
    elif rb is not None:
        r.notes.append("campaign.reported_beside is %r, not a list; ignored"
                       % type(rb).__name__)


# ------------------------------------------------------------------- item aggregation


def canonical_key(item_id, task, singleton_tasks):
    """Rubric-row key for an item_id, with run-specific bookkeeping stripped.

    DX02.I1.run1.SUMMARY / DX02.summary / DX02.I1  ->  DX02.*   (task has one row)
    DX05.I3a, DX05.I3b                             ->  DX05.I3  (sub-items of one row)
    Every merge this performs is printed in the alias map; nothing is merged silently.
    """
    if task in singleton_tasks:
        return "%s.*" % task
    parts = [p for p in str(item_id).split(".") if not NOISE_PART.match(p)]
    if len(parts) >= 2:
        m = SUBITEM.match(parts[1])
        if m:
            parts[1] = m.group(1)
    key = ".".join(parts) if parts else str(item_id)
    return key if key != task else "%s.*" % task


def singleton_tasks(runs):
    """Tasks that contribute exactly one item in every run that has them at all."""
    counts = {}
    for r in runs:
        per = {}
        for it in r.items:
            per[it["task"]] = per.get(it["task"], 0) + 1
        for t, n in per.items():
            counts.setdefault(t, set()).add(n)
    return {t for t, ns in counts.items() if ns == {1}}


def build_item_stats(runs, canonical=False):
    """Per-item rows: mean, range, discrimination, and which runs carried the item."""
    singles = singleton_tasks(runs) if canonical else set()
    rows, order, aliases = {}, [], {}
    for r in runs:
        per_run = {}
        for it in r.items:
            key = (canonical_key(it["item_id"], it["task"], singles) if canonical
                   else it["item_id"])
            if canonical and key != it["item_id"]:
                aliases.setdefault(key, set()).add(it["item_id"])
            if key not in rows:
                rows[key] = {"key": key, "task": it["task"], "maxes": set(),
                             "awards": [], "runs": []}
                order.append(key)
            rec = rows[key]
            rec["task"] = it["task"]
            if it["max"] is not None:
                rec["maxes"].add(float(it["max"]))
            if canonical:  # sub-items of one rubric row add up
                prev = per_run.get(key)
                if prev is not None and it["awarded"] is not None:
                    prev["awarded"] = (prev["awarded"] or 0.0) + float(it["awarded"])
                    continue
            cell = {"run": r.run_id, "awarded": it["awarded"]}
            per_run[key] = cell
            rec["awards"].append(cell)
            rec["runs"].append(r.run_id)

    out = []
    for key in order:
        rec = rows[key]
        vals = [c["awarded"] for c in rec["awards"] if c["awarded"] is not None]
        mx = max(rec["maxes"]) if rec["maxes"] else None
        if canonical:
            # a collapsed row's max is the sum of its sub-items' maxes within one run
            per = {}
            for r in runs:
                tot = 0.0
                seen = False
                for it in r.items:
                    if canonical_key(it["item_id"], it["task"], singles) == key \
                            and it["max"] is not None:
                        tot += float(it["max"])
                        seen = True
                if seen:
                    per[r.run_id] = tot
            if per:
                rec["maxes"] = set(per.values())
                mx = max(per.values())
        rng = (max(vals) - min(vals)) if len(vals) >= 2 else (0.0 if vals else None)
        disc = (rng / mx) if (rng is not None and mx) else None
        mean = statistics.fmean(vals) if vals else None
        label = ""
        if rng is not None and abs(rng) < TOL:
            if mx is not None and mean is not None and abs(mean - mx) < TOL:
                label = "at ceiling"
            elif mean is not None and abs(mean) < TOL:
                label = "at floor"
            else:
                label = "flat"
        out.append({
            "key": key, "task": rec["task"], "max": mx, "mean": mean, "min": min(vals) if vals else None,
            "max_awarded": max(vals) if vals else None, "range": rng, "disc": disc,
            "label": label, "n": len(vals), "runs": rec["runs"],
            "max_varies": len(rec["maxes"]) > 1,
        })
    out.sort(key=lambda d: (-(d["disc"] if d["disc"] is not None else -1.0), d["key"]))
    return out, aliases


def presence_report(runs, stats):
    """item keys that are not present in every run — reported, never dropped."""
    all_runs = [r.run_id for r in runs]
    gaps = []
    for s in stats:
        if len(set(s["runs"])) != len(all_runs):
            absent = [rid for rid in all_runs if rid not in s["runs"]]
            gaps.append((s["key"], absent))
    return gaps


def campaign_stats(runs):
    tots = [r.total for r in runs if num(r.total)]
    if not tots:
        return None
    return {
        "n": len(tots),
        "mean": statistics.fmean(tots),
        "median": statistics.median(tots),
        "min": min(tots),
        "max": max(tots),
        "range": max(tots) - min(tots),
        "sd": statistics.stdev(tots) if len(tots) > 1 else None,
    }


# ------------------------------------------------------------------------- rendering


def table(headers, rows, md=False):
    cells = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in cells:
        for i, c in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(c))
    if md:
        out = ["| " + " | ".join(headers) + " |",
               "|" + "|".join("---" for _ in headers) + "|"]
        out += ["| " + " | ".join(r) + " |" for r in cells]
        return "\n".join(out)
    out = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))]
    out.append("  ".join("-" * w for w in widths))
    out += ["  ".join(c.ljust(widths[i]) for i, c in enumerate(r)) for r in cells]
    return "\n".join(out)


def render(runs, label, compare=None, compare_label="compare", md=False):
    L = []
    h1 = (lambda s: "# " + s) if md else (lambda s: s + "\n" + "=" * len(s))
    h2 = (lambda s: "## " + s) if md else (lambda s: "\n" + s + "\n" + "-" * len(s))
    L.append(h1("DELTA-X v2 campaign — %s" % label))
    L.append("")
    usable = [r for r in runs if r.ok]
    broken = [r for r in runs if not r.ok]

    # 1. per-run totals
    L.append(h2("1. Per-run totals (每轮总分)"))
    tasks = sorted({t for r in usable for t in r.task_totals})
    headers = ["run", "DX01 gate"] + tasks + ["item_sum", "total", "reconciles"]
    rows = []
    for r in usable:
        row = [r.run_id, r.gate_label]
        row += [fmt(r.task_totals.get(t)) if t in r.task_totals else MISSING for t in tasks]
        row += [fmt(r.item_sum_computed), fmt(r.total),
                "yes" if r.reconciles else "NO -- see §1a"]
        rows.append(row)
    L.append(table(headers, rows, md) if rows else "_no usable scorecards_")
    L.append("")
    L.append("item_sum and total are recomputed from items[] and caps_applied; the stored "
             "values are checked against them, not trusted.")

    flagged = [r for r in runs if r.problems]
    if flagged:
        L.append("")
        L.append(h2("1a. RECONCILIATION FAILURES (对账失败)"))
        for r in flagged:
            L.append("")
            L.append("**%s** (`%s`)" % (r.run_id, r.path) if md
                     else "!! %s  (%s)" % (r.run_id, r.path))
            for p in r.problems:
                L.append("  - " + p if md else "   - " + p)
        L.append("")
        L.append("A run listed here is reported **ungraded**, not as a score "
                 "(grader/SCORECARD.md)." if md else
                 "A run listed here is reported ungraded, not as a score (SCORECARD.md).")
    notes = [(r, n) for r in runs for n in r.notes]
    if notes:
        L.append("")
        L.append(h2("1b. Schema notes (结构提示)"))
        for r, n in notes:
            L.append("  - %s: %s" % (r.run_id, n) if md else "   - %s: %s" % (r.run_id, n))

    # 2. campaign summary
    L.append("")
    L.append(h2("2. Campaign summary (总体统计)"))
    st = campaign_stats(usable)
    if st:
        L.append(table(["n", "mean", "median", "min", "max", "range", "sd (sample)"],
                       [[st["n"], fx(st["mean"]), fmt(st["median"]), fmt(st["min"]),
                         fmt(st["max"]), fmt(st["range"]),
                         fx(st["sd"]) if st["sd"] is not None else "n/a (n=1)"]], md))
    else:
        L.append("_no totals could be recomputed_")

    # 3. per-item discrimination
    for canon, title in ((False, "3. Per-item discrimination (逐项区分度)"),
                         (True, "3b. By rubric row, sub-items collapsed (按评分行合并)")):
        stats, aliases = build_item_stats(usable, canonical=canon)
        L.append("")
        L.append(h2(title))
        rows = []
        for s in stats:
            rows.append([s["key"], s["task"], fmt(s["max"]), fx(s["mean"]),
                         fmt(s["range"]),
                         fmt(s["disc"], 3) if s["disc"] is not None else MISSING,
                         s["label"] or "", "%d/%d" % (s["n"], len(usable))])
        L.append(table(["item", "task", "max", "mean", "range", "discrimination",
                        "note", "runs"], rows, md) if rows else "_no items_")
        L.append("")
        L.append("discrimination = range / max. An item with range 0 carried no "
                 "information in this campaign.")
        if canon and aliases:
            L.append("")
            L.append("Aliases merged into a rubric row (每个合并都在此列出):")
            for k in sorted(aliases):
                L.append("  - %s <- %s" % (k, ", ".join(sorted(aliases[k]))))
        gaps = presence_report(usable, stats)
        if gaps:
            L.append("")
            L.append("Items NOT present in every run (未在全部轮次出现 — reported, not "
                     "dropped; their range is over the runs that carried them):")
            for k, absent in gaps:
                L.append("  - %s: absent from %s" % (k, ", ".join(absent)))

    # 4. integrity roll-up
    L.append("")
    L.append(h2("4. Integrity roll-up (完整性汇总)"))
    fab = sum(r.fabrications for r in usable)
    strike_kinds = {}
    for r in usable:
        for c in r.strikes:
            strike_kinds[c] = strike_kinds.get(c, 0) + 1
    gates_failed = [(r.run_id, g, c) for r in usable for g, c in r.gates_failed]
    caps = [(r.run_id, cap, why) for r in usable for cap, why in r.caps]
    L.append(table(["measure", "count"],
                   [["fabrication events", fab],
                    ["strikes", sum(strike_kinds.values())],
                    ["gates failed", len(gates_failed)],
                    ["caps applied", len(caps)]], md))
    if strike_kinds:
        L.append("")
        L.append("Strikes by classification: " +
                 ", ".join("%s %d" % (k, v) for k, v in sorted(strike_kinds.items())))
    if gates_failed:
        L.append("")
        L.append("Gates failed:")
        for rid, g, c in gates_failed:
            L.append("  - %s: %s -> %s" % (rid, g, c))
    if caps:
        L.append("")
        L.append("Caps applied:")
        for rid, cap, why in caps:
            L.append("  - %s: capped at %s (%s)" % (rid, fmt(cap), why))

    # 5. reported-beside
    L.append("")
    L.append(h2("5. Reported beside the score (仅并列报告，不计入总分)"))
    rows = []
    for r in usable:
        for e in r.reported_beside:
            rows.append([r.run_id, str(e.get("index", MISSING)), fmt(e.get("value")),
                         str(e.get("denominator", MISSING)),
                         str(e.get("note", ""))[:60]])
    L.append(table(["run", "index", "value", "denominator", "note"], rows, md) if rows
             else "_none recorded_")
    L.append("")
    L.append("These indices are computed and reported; they are **never added to the "
             "total**." if md else
             "These indices are computed and reported; they are NEVER added to the total.")

    # 6. measured scope
    L.append("")
    L.append(h2("6. Measured scope, as each run declares it (测量范围)"))
    for r in usable:
        L.append("  - %s: %s" % (r.run_id, r.measured_scope or "(not declared)"))

    # 7. comparison
    if compare is not None:
        L.append("")
        L.append(h2("7. Beside %s (对照)" % compare_label))
        a_st, b_st = campaign_stats(usable), campaign_stats([r for r in compare if r.ok])
        if a_st and b_st:
            L.append(table(["campaign", "n", "mean", "range"],
                           [[label, a_st["n"], fx(a_st["mean"]), fmt(a_st["range"])],
                            [compare_label, b_st["n"], fx(b_st["mean"]),
                             fmt(b_st["range"])],
                            ["delta", "", fx(a_st["mean"] - b_st["mean"]),
                             fmt(a_st["range"] - b_st["range"])]], md))
        a_items, _ = build_item_stats(usable, canonical=True)
        b_items, _ = build_item_stats([r for r in compare if r.ok], canonical=True)
        bmap = {s["key"]: s for s in b_items}
        rows = []
        for s in a_items:
            o = bmap.get(s["key"])
            d_mean = (s["mean"] - o["mean"]) if (o and s["mean"] is not None
                                                 and o["mean"] is not None) else None
            d_rng = (s["range"] - o["range"]) if (o and s["range"] is not None
                                                  and o["range"] is not None) else None
            rows.append([s["key"], fx(s["mean"]), fx(o["mean"]) if o else MISSING,
                         fx(d_mean) if d_mean is not None else MISSING, fmt(s["range"]),
                         fmt(o["range"]) if o else MISSING, fmt(d_rng),
                         "" if o else "absent from %s" % compare_label])
        for key in sorted(k for k in bmap if k not in {s["key"] for s in a_items}):
            o = bmap[key]
            rows.append([key, MISSING, fx(o["mean"]), MISSING, MISSING,
                         fmt(o["range"]), MISSING, "absent from %s" % label])
        L.append("")
        L.append(table(["item", "mean A", "mean B", "d mean", "range A", "range B",
                        "d range", "note"], rows, md) if rows else "_no items_")
        L.append("")
        L.append("A = %s, B = %s. Rubric-row keys; see the alias map in 3b." % (label, compare_label))

    if broken:
        L.append("")
        L.append(h2("Files that could not be read (无法读取的文件)"))
        for r in broken:
            L.append("  - %s: %s" % (r.path, "; ".join(r.problems)))
    return "\n".join(L) + "\n"


def write_csv(path, runs):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["run", "item_id", "task", "max", "awarded"])
        for r in runs:
            if not r.ok:
                continue
            for it in r.items:
                w.writerow([r.run_id, it["item_id"], it["task"],
                            "" if it["max"] is None else it["max"],
                            "" if it["awarded"] is None else it["awarded"]])


# ------------------------------------------------------------------------------ main


def load_all(inputs, stream):
    paths, missing = collect_paths(inputs)
    for m in missing:
        print("!! input not found: %s" % m, file=stream)
    runs = [load_run(p) for p in paths]
    seen = {}
    for r in runs:
        seen[r.run_id] = seen.get(r.run_id, 0) + 1
    for r in runs:  # two files may carry the same submission_id; never conflate them
        if seen[r.run_id] > 1:
            r.notes.append("submission_id %r is used by more than one file; the run is "
                           "labelled by filename here" % r.run_id)
            r.run_id = "%s [%s]" % (r.run_id, r.name)
    return runs, missing


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Aggregate DELTA-X v2 scorecards into a campaign result.")
    ap.add_argument("inputs", nargs="+", help="scorecard.json files, or a directory")
    ap.add_argument("--label", default="campaign", help="what to call this campaign")
    ap.add_argument("--out-md", help="write the markdown report here")
    ap.add_argument("--out-csv", help="write tidy long-format CSV here")
    ap.add_argument("--compare", help="a second directory of scorecards to put beside")
    ap.add_argument("--no-gate", action="store_true", help="always exit 0")
    args = ap.parse_args(argv)

    runs, missing = load_all(args.inputs, sys.stderr)
    compare_runs, compare_label = None, "compare"
    if args.compare:
        compare_runs, _ = load_all([args.compare], sys.stderr)
        compare_label = os.path.basename(os.path.normpath(args.compare)) or "compare"
        for r in compare_runs:
            if r.problems:
                print("!! %s (compare set): %s" % (r.run_id, "; ".join(r.problems)),
                      file=sys.stderr)

    if not runs:
        print("!! no scorecards found in: %s" % ", ".join(args.inputs), file=sys.stderr)
        print("   nothing was aggregated; a campaign of zero runs is not a result.",
              file=sys.stderr)
        return 0 if args.no_gate else 1

    sys.stdout.write(render(runs, args.label, compare_runs, compare_label, md=False))
    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as fh:
            fh.write(render(runs, args.label, compare_runs, compare_label, md=True))
        print("\nwrote markdown: %s" % args.out_md)
    if args.out_csv:
        write_csv(args.out_csv, runs)
        print("wrote csv: %s" % args.out_csv)

    checked = runs + [r for r in (compare_runs or [])]
    failed = [r.run_id for r in checked if not r.reconciles]
    if failed:
        print("\nGATE: %d of %d scorecards did not reconcile: %s"
              % (len(failed), len(checked), ", ".join(failed)), file=sys.stderr)
    if missing:
        print("GATE: %d input(s) did not exist" % len(missing), file=sys.stderr)
    return 0 if (args.no_gate or not (failed or missing)) else 1


if __name__ == "__main__":
    sys.exit(main())
