"""Compare two scorings in mTdT P09838 residue space."""
import sys
import numpy as np
from scipy.stats import spearmanr

def load(npz, aln, TREF, PREF):
    d = np.load(npz, allow_pickle=True)
    ids, seqs, buf, cur = [], [], [], None
    for line in open(aln):
        line = line.rstrip()
        if line.startswith(">"):
            if cur is not None: seqs.append("".join(buf))
            cur = line[1:].split()[0]; ids.append(cur); buf = []
        else: buf.append(line)
    seqs.append("".join(buf))
    tr = seqs[[i for i, x in enumerate(ids) if TREF in x][0]]
    pr = seqs[[i for i, x in enumerate(ids) if PREF in x][0]]
    J, ot, op = d["J"], d["ot"], d["op"]
    res = {}
    pm = {}
    n = 0
    np_ = 0
    for c, ch in enumerate(tr):
        if ch not in "-.": n += 1
        if pr[c] not in "-.": np_ += 1
        if ch not in "-." and ot[c] >= .8 and op[c] >= .8:
            res[n] = J[c]; pm[n] = np_ if pr[c] not in "-." else None
    return res, pm

A, pmA = load("msa_axis/auto_scores.npz", "msa_axis/combined.auto.aln", "TDT|P09838", "POLM|Q9NP87")
B, pmB = load("msa_axis/linsi_scores.npz", "msa_axis/reduced90.linsi.aln", "TDT|P09838", "POLM|Q9NP87")
common = sorted(set(A) & set(B))
a = np.array([A[k] for k in common]); b = np.array([B[k] for k in common])
rho, p = spearmanr(a, b)
print("### mTdT residues scorable in BOTH alignments: %d (auto %d, linsi %d)"
      % (len(common), len(A), len(B)))
print("### Spearman rho between FFT-NS-i(489 seq) and L-INS-i(90 seq) JSD = %.3f (p=%.2g)" % (rho, p))
print("### Pearson r = %.3f" % np.corrcoef(a, b)[0, 1])
for N in (10, 20, 30, 50, 100):
    ta = set(np.array(common)[np.argsort(-a)][:N])
    tb = set(np.array(common)[np.argsort(-b)][:N])
    print("  top-%-3d overlap: %2d/%d (%.0f%%)  Jaccard=%.2f"
          % (N, len(ta & tb), N, 100 * len(ta & tb) / N, len(ta & tb) / len(ta | tb)))
# residue-level pair-number mapping check
print("\n### Pol mu number assigned to the same mTdT residue by each alignment (top-30 auto)")
print("  mTdT  hPolmu(auto)  hPolmu(linsi)  JSD_auto JSD_linsi  agree?")
for k in np.array(common)[np.argsort(-a)][:30]:
    k = int(k)
    print("  %4d  %-13s %-14s %.3f    %.3f      %s"
          % (k, pmA.get(k), pmB.get(k), A[k], B[k],
             "YES" if pmA.get(k) == pmB.get(k) else "NO"))
