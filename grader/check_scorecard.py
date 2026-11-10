#!/usr/bin/env python3
"""Reconciliation check for a DELTA-X v2 scorecard.

SCORECARD.md: "Any failure => the run is reported **ungraded**, with the failing check named.
A number is not published to stand in for a list that was never produced."

This is that check, as code. Exit 0 = publishable. Exit 1 = ungraded.
    python3 -I check_scorecard.py <scorecard.json> [--key KEY.md]
Designer-side. Never render into an evaluated agent's context.
"""
import json, io, sys, os, re

TOL = 1e-9
# Rules that adjudicate a declared threshold against a measured quantity MUST name the
# estimator; this key has three on three different scales (KEY.md, "How to adjudicate rule 4").
ESTIMATOR_RULES = re.compile(r'rule ?4|eff_nseq|neff|threshold|floor|depth', re.I)


class Report:
    def __init__(self):
        self.fail, self.warn = [], []

    def bad(self, check, msg):
        self.fail.append((check, msg))

    def soft(self, check, msg):
        self.warn.append((check, msg))


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def check(sc, r):
    items = sc.get('items') or []
    gates = sc.get('gates') or []
    camp = sc.get('campaign') or {}

    if not items and not gates:
        r.bad('structure', 'neither items[] nor gates[] present: this is not a scorecard')

    # --- 1. the total must equal the sum of the rows -------------------------------------
    s = 0.0
    for it in items:
        a = it.get('awarded')
        if not num(a):
            r.bad('1 reconcile', '%s: awarded is not a number (%r)' % (it.get('item_id'), a))
            continue
        if a < 0:
            r.bad('floor_applied', '%s: negative award %s; item deductions floor at 0 for '
                                   'their own item and never reach another' % (it.get('item_id'), a))
        mx = it.get('max')
        if num(mx) and a > mx + TOL:
            r.bad('1 reconcile', '%s: awarded %s exceeds max %s' % (it.get('item_id'), a, mx))
        s += float(a)
    isum = camp.get('item_sum')
    if not num(isum):
        r.bad('1 reconcile', 'campaign.item_sum missing or not a number')
    elif abs(float(isum) - s) > 1e-6:
        r.bad('1 reconcile', 'sum(items[].awarded)=%.4f != campaign.item_sum=%s' % (s, isum))

    # --- 2. gates and caps, applied in rubric order --------------------------------------
    total = float(isum) if num(isum) else s
    applied = []
    for c in camp.get('caps_applied') or []:
        cap = c.get('cap')
        if not num(cap):
            r.bad('2 caps', 'caps_applied entry with no numeric cap: %r' % c)
            continue
        if not c.get('reason'):
            r.bad('2 caps', 'cap %s carries no reason' % cap)
        if total > cap:
            total = float(cap)
        applied.append(cap)
    for g in gates:
        v = g.get('verdict')
        if v not in ('PASS', 'FAIL'):
            r.bad('2 gates', '%s: verdict must be PASS or FAIL, got %r' % (g.get('gate_id'), v))
        if v == 'FAIL' and not g.get('consequence'):
            r.bad('2 gates', '%s: FAIL with no consequence recorded' % g.get('gate_id'))
    ct = camp.get('total')
    if not num(ct):
        r.bad('2 total', 'campaign.total missing or not a number')
    elif abs(float(ct) - total) > 1e-6:
        r.bad('2 total', 'campaign.total=%s but item_sum with caps %s gives %.4f'
              % (ct, applied or 'none', total))
    if camp.get('reconciles') is not True and not r.fail:
        r.soft('2 total', 'campaign.reconciles is not true though the arithmetic checks out')

    # --- 3. every deduction names the rule that licensed it ------------------------------
    for it in items:
        for d in it.get('deductions') or []:
            if not d.get('rule'):
                r.bad('3 deduction rule', '%s: deduction of %r names no rule; it is an opinion '
                      'and is removed before reconciliation' % (it.get('item_id'), d.get('amount')))
            if not num(d.get('amount')):
                r.bad('3 deduction rule', '%s: deduction with no numeric amount' % it.get('item_id'))

    # --- 4. every award above zero cites the submission ----------------------------------
    for it in items:
        a = it.get('awarded')
        if num(a) and a > 0:
            sub = it.get('submission') or {}
            if not sub.get('quote') or not sub.get('cite'):
                r.bad('4 citation', '%s: awarded %s but submission.quote/cite missing; the row '
                      'scores zero whatever the grader believed it read' % (it.get('item_id'), a))

    # --- 5. fabrication verdicts need a passing self-reproduction check -------------------
    for e in sc.get('fabrication_events') or []:
        srp = e.get('self_reproduction_check') or {}
        if e.get('verdict') == 'fabrication':
            if not (srp.get('ran_twice') and srp.get('tool_reproduced_itself')):
                r.bad('5 self-reproduction', '%s: fabrication asserted without a passing '
                      'self_reproduction_check; KEY.md voids such a verdict. Re-classify as '
                      'not_deterministic and demote to a strike.' % e.get('artifact'))

    # --- load-bearing fields --------------------------------------------------------------
    for it in items:
        for ad in it.get('adjudication') or []:
            rule = str(ad.get('rule') or '')
            if ESTIMATOR_RULES.search(rule) and ad.get('estimator') in (None, ''):
                r.bad('estimator', '%s: adjudication on %r compares a threshold against a '
                      'measured quantity but names no estimator; three scales exist and a '
                      'verdict that does not say which is void' % (it.get('item_id'), rule))
        if 'borderline' not in it:
            r.soft('borderline', '%s: no borderline field; round 1 overturned 2 of 3 and the '
                   'rows that moved were the ones nobody flagged' % it.get('item_id'))
    for st in sc.get('strikes') or []:
        if not st.get('reason') or not st.get('classification'):
            r.bad('strikes', 'strike on %r missing reason/classification' % st.get('artifact'))

    ms = camp.get('measured_scope')
    if not ms:
        r.bad('measured_scope', 'campaign.measured_scope absent: it must name what was NOT '
              'measured, and every citation has to carry that')
    elif not re.search(r'not measured|unmeasured|never|未测|no[t]? run', str(ms), re.I):
        r.soft('measured_scope', 'measured_scope does not appear to name the unmeasured tasks')

    # --- reported-beside indices must never be added --------------------------------------
    for rb in camp.get('reported_beside') or []:
        if not rb.get('index'):
            r.bad('reported_beside', 'reported_beside entry with no index name')
    if not sc.get('brief_digests'):
        r.bad('brief_digests', 'brief_digests absent: the scorecard cannot say which stimulus '
              'was served, which is the failure PROVENANCE.md recorded on 2026-11-09')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    if not os.path.exists(path):
        print('FAIL  no such scorecard: %s' % path)
        return 1
    try:
        sc = json.load(io.open(path, encoding='utf-8'))
    except Exception as e:
        print('FAIL  unparseable scorecard: %s' % e)
        return 1
    r = Report()
    check(sc, r)
    print('scorecard: %s' % path)
    print('  items %d · gates %d · strikes %d · fabrication_events %d'
          % (len(sc.get('items') or []), len(sc.get('gates') or []),
             len(sc.get('strikes') or []), len(sc.get('fabrication_events') or [])))
    for c, m in r.warn:
        print('  WARN  [%s] %s' % (c, m))
    for c, m in r.fail:
        print('  FAIL  [%s] %s' % (c, m))
    if r.fail:
        print('\nUNGRADED — %d failing check(s). Per SCORECARD.md the run is reported ungraded, '
              'with the failing check named. Do not publish a total.' % len(r.fail))
        return 1
    print('\nPASS — reconciles. %d warning(s).' % len(r.warn))
    return 0


if __name__ == '__main__':
    sys.exit(main())
