"""Map scored columns to mouse TdT (P09838) and human Pol mu (Q9NP87) numbering,
call significant columns against the conservative within-family null, cluster
them into regions, describe indel segments, and test neighbour separability.

Usage: report.py <scores.npz> <aln.fasta> <tdt_ref_id_substr> <polm_ref_id_substr>
"""
import sys
import numpy as np

npz, aln_path, TREF, PREF = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = np.load(npz, allow_pickle=True)
J, ot, op, ct, cp, gj, sdp = (d["J"], d["ot"], d["op"], d["ct"], d["cp"],
                              d["gj"], d["sdp"])
nullA, nullB, boot = d["nullA"], d["nullB"], d["boot"]
ids = list(d["ids"])
L = len(J)

def read_fasta(p):
    ids_, seqs, buf, cur = [], [], [], None
    for line in open(p):
        line = line.rstrip()
        if line.startswith(">"):
            if cur is not None: seqs.append("".join(buf))
            cur = line[1:].split()[0]; ids_.append(cur); buf = []
        else: buf.append(line)
    seqs.append("".join(buf)); return ids_, seqs

aids, aseqs = read_fasta(aln_path)
def getrow(sub):
    for i, x in enumerate(aids):
        if sub in x: return aseqs[i]
    raise SystemExit("ref not found: " + sub)

def colmap(row):
    m, n = {}, 0
    for c, ch in enumerate(row):
        if ch not in "-.":
            n += 1; m[c] = n
    return m

tmap = colmap(getrow(TREF))
pmap = colmap(getrow(PREF))
trow, prow = getrow(TREF), getrow(PREF)

OCC = 0.8
scored = (ot >= OCC) & (op >= OCC)
print("### alignment: %s   columns=%d   scorable (occ>=%.2f both)=%d"
      % (aln_path, L, OCC, scored.sum()))

# empirical p from the conservative within-family null, pooled over all columns
nullB_pool = nullB[:, scored].ravel()
nullA_pool = nullA[:, scored].ravel()
print("### null JSD (within-family split-half, pooled over scorable cols, n=%d):"
      % nullB_pool.size)
for q in (50, 90, 95, 99, 99.9):
    print("      p%-5s = %.4f" % (q, np.percentile(nullB_pool, q)))
print("### null JSD (label permutation, pooled): p95=%.4f p99=%.4f p99.9=%.4f"
      % tuple(np.percentile(nullA_pool, [95, 99, 99.9])))
print("### observed JSD on scorable columns: median=%.4f p90=%.4f p99=%.4f max=%.4f"
      % (np.median(J[scored]), np.percentile(J[scored], 90),
         np.percentile(J[scored], 99), J[scored].max()))

# per-column empirical p-value against the per-column within-family null
pval = np.ones(L)
for c in np.where(scored)[0]:
    pval[c] = (1 + (nullB[:, c] >= J[c]).sum()) / (nullB.shape[0] + 1.0)
# BH
sc = np.where(scored)[0]
order = sc[np.argsort(pval[sc])]
m = len(sc)
qval = np.ones(L)
prev = 1.0
for rank in range(m - 1, -1, -1):
    c = order[rank]
    v = pval[c] * m / (rank + 1)
    prev = min(prev, v)
    qval[c] = prev

for thr_name, mask in [
        ("JSD >= 0.30", scored & (J >= 0.30)),
        ("JSD >= 0.40", scored & (J >= 0.40)),
        ("JSD >= 0.50", scored & (J >= 0.50)),
        ("JSD >= 0.60", scored & (J >= 0.60)),
        ("JSD > nullB p99.9", scored & (J > np.percentile(nullB_pool, 99.9))),
        ("BH q<0.05", scored & (qval < 0.05)),
        ("BH q<0.01", scored & (qval < 0.01)),
        ("SDP >= 0.20", scored & (sdp >= 0.20)),
        ("SDP >= 0.30", scored & (sdp >= 0.30))]:
    print("### count %-22s : %4d columns (%.1f%% of scorable)"
          % (thr_name, mask.sum(), 100.0 * mask.sum() / scored.sum()))

def fmt(c):
    return ("%s%s" % (trow[c], tmap.get(c, "-")),
            "%s%s" % (prow[c], pmap.get(c, "-")))

print("\n### TOP 40 scorable columns by JSD")
print("rank  col   mTdT_P09838  hPolmu_Q9NP87   JSD    SDP   consT consP  occT occP  q      TDTtop        POLMtop")
M = d["M"]; grp = d["grp"]
AA = "ACDEFGHIKLMNPQRSTVWY-"
def top2(col, g):
    sub = M[grp == g, col]
    cnt = np.bincount(sub, minlength=21).astype(float)
    cnt[20] = 0
    tot = cnt.sum()
    o = np.argsort(-cnt)[:2]
    return "/".join("%s%.0f%%" % (AA[i], 100 * cnt[i] / tot) for i in o if cnt[i] > 0)

topcols = sc[np.argsort(-J[sc])][:40]
for r, c in enumerate(topcols, 1):
    t, p = fmt(c)
    print("%4d %5d  %-12s %-13s %.3f %.3f  %.2f  %.2f  %.2f %.2f %.3g  %-13s %s"
          % (r, c, t, p, J[c], sdp[c], ct[c], cp[c], ot[c], op[c], qval[c],
             top2(c, 0), top2(c, 1)))

# ---- clustering of high columns into regions (on TdT coordinates) ----
def regions(mask, gap_allow=4):
    cols = np.where(mask)[0]
    out, cur = [], []
    for c in cols:
        if cur and c - cur[-1] - 1 > gap_allow:
            out.append(cur); cur = []
        cur.append(c)
    if cur: out.append(cur)
    return out

for thr, label in [(0.40, "JSD>=0.40"), (0.50, "JSD>=0.50")]:
    mask = scored & (J >= thr)
    regs = regions(mask)
    print("\n### regions at %s (merge gaps<=4 cols): %d regions covering %d columns"
          % (label, len(regs), mask.sum()))
    print("  #  ncol  colspan        mTdT_P09838     hPolmu_Q9NP87   maxJSD  meanJSD")
    for i, rg in enumerate(sorted(regs, key=lambda r: -max(J[r])), 1):
        tn = [tmap[c] for c in rg if c in tmap]
        pn = [pmap[c] for c in rg if c in pmap]
        print("%3d %5d  %5d-%-7d %-15s %-15s %.3f   %.3f"
              % (i, len(rg), rg[0], rg[-1],
                 ("%d-%d" % (min(tn), max(tn))) if tn else "gap",
                 ("%d-%d" % (min(pn), max(pn))) if pn else "gap",
                 max(J[rg]), np.mean(J[rg])))

# ---- indel structure ----
print("\n### subfamily-specific indel segments (>=3 cols, one family occ>=0.8, other <=0.2)")
for name, m_ in [("TdT-present / Polmu-absent", (ot >= 0.8) & (op <= 0.2)),
                 ("Polmu-present / TdT-absent", (op >= 0.8) & (ot <= 0.2))]:
    regs = regions(m_, gap_allow=1)
    regs = [r for r in regs if len(r) >= 3]
    print("  %s : %d segments" % (name, len(regs)))
    for rg in sorted(regs, key=lambda r: -len(r)):
        tn = [tmap[c] for c in rg if c in tmap]
        pn = [pmap[c] for c in rg if c in pmap]
        print("     len=%3d cols %5d-%-6d mTdT %-13s hPolmu %-13s"
              % (len(rg), rg[0], rg[-1],
                 ("%d-%d" % (min(tn), max(tn))) if tn else "(absent)",
                 ("%d-%d" % (min(pn), max(pn))) if pn else "(absent)"))

# ---- neighbour separability ----
print("\n### neighbour separability inside high-scoring regions")
print("For each of the top 15 columns: bootstrap P(JSD_col > JSD_neighbour) over")
print("%d resamples, against the column immediately left and right." % boot.shape[0])
print(" col  mTdT   JSD    JSD(-1) P(>L)   JSD(+1) P(>R)   min(P)  separable?")
for c in topcols[:15]:
    out = []
    for off in (-1, 1):
        n = c + off
        if 0 <= n < L:
            out.append((J[n], float((boot[:, c] > boot[:, n]).mean())))
        else:
            out.append((np.nan, np.nan))
    mn = np.nanmin([out[0][1], out[1][1]])
    print("%5d %5s  %.3f  %.3f  %.3f   %.3f  %.3f   %.3f   %s"
          % (c, tmap.get(c, "-"), J[c], out[0][0], out[0][1], out[1][0], out[1][1],
             mn, "YES" if mn >= 0.95 else "no"))

# how often is the peak of a region distinguishable from all other members
print("\n### within-region peak vs all other members of that region (JSD>=0.40 regions)")
mask = scored & (J >= 0.40)
for i, rg in enumerate(sorted(regions(mask), key=lambda r: -max(J[r])), 1):
    if len(rg) < 2: 
        print("  region %d: single column (%s) - nothing to separate" % (i, tmap.get(rg[0], "?")))
        continue
    pk = rg[int(np.argmax(J[rg]))]
    ps = [float((boot[:, pk] > boot[:, o]).mean()) for o in rg if o != pk]
    print("  region %d mTdT %s-%s : peak col %d (mTdT %s), min P(peak>member)=%.3f -> %s"
          % (i, tmap.get(rg[0], "?"), tmap.get(rg[-1], "?"), pk, tmap.get(pk, "?"),
             min(ps), "peak isolated" if min(ps) >= 0.95 else "peak NOT isolated"))
