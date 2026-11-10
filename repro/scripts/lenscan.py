"""Scan for alignment regions where the two subfamilies differ in residue COUNT
(net indel length), using the cumulative-occupancy difference and a Mann-Whitney
style effect size on per-sequence residue counts in sliding windows."""
import sys
import numpy as np
from scipy.stats import mannwhitneyu

aln, TREF, PREF = sys.argv[1], sys.argv[2], sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 24

def read_fasta(p):
    ids, seqs, buf, cur = [], [], [], None
    for line in open(p):
        line = line.rstrip()
        if line.startswith(">"):
            if cur is not None: seqs.append("".join(buf))
            cur = line[1:].split()[0]; ids.append(cur); buf = []
        else: buf.append(line)
    seqs.append("".join(buf)); return ids, seqs

ids, seqs = read_fasta(aln)
L = len(seqs[0])
g = np.array([0 if i.split("|")[0] == "TDT" else 1 for i in ids])
A = np.array([[0 if c in "-." else 1 for c in s] for s in seqs], dtype=np.int8)
cum = np.cumsum(A, axis=1)

def getrow(sub): return seqs[[i for i, x in enumerate(ids) if sub in x][0]]
tr, pr = getrow(TREF), getrow(PREF)
def num(row, c): return sum(1 for ch in row[:c] if ch not in "-.")

rows = []
for a in range(0, L - W):
    b = a + W
    cnt = cum[:, b - 1] - (cum[:, a - 1] if a > 0 else 0)
    t, p = cnt[g == 0], cnt[g == 1]
    diff = t.mean() - p.mean()
    sd = np.sqrt((t.var() + p.var()) / 2) + 1e-9
    rows.append((a, b - 1, diff, diff / sd, t.mean(), p.mean(), t.std(), p.std()))

rows = np.array(rows)
print("### sliding-window net length difference, window=%d cols, aln=%s" % (W, aln))
print("### (positive = TdT has more residues than Pol mu in that window)")
print("  rank  cols          dLen   Cohen_d  TdT_mean(sd)   Polmu_mean(sd)  mTdT_P09838   hPolmu_Q9NP87")
order = np.argsort(-np.abs(rows[:, 3]))
seen = []
r = 0
for i in order:
    a, b = int(rows[i, 0]), int(rows[i, 1])
    if any(abs(a - s) < W for s in seen):
        continue
    seen.append(a); r += 1
    print("  %4d  %5d-%-7d %6.2f  %6.2f   %5.2f(%.2f)   %5.2f(%.2f)    %-13s %s"
          % (r, a, b, rows[i, 2], rows[i, 3], rows[i, 4], rows[i, 6], rows[i, 5], rows[i, 7],
             "%d-%d" % (num(tr, a) + 1, num(tr, b + 1)),
             "%d-%d" % (num(pr, a) + 1, num(pr, b + 1))))
    if r >= 12: break
