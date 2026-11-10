"""Occupancy-difference / indel-segment analysis for a two-subfamily MSA."""
import sys
import numpy as np

aln_path, TREF, PREF = sys.argv[1], sys.argv[2], sys.argv[3]
THR = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5

def read_fasta(p):
    ids, seqs, buf, cur = [], [], [], None
    for line in open(p):
        line = line.rstrip()
        if line.startswith(">"):
            if cur is not None: seqs.append("".join(buf))
            cur = line[1:].split()[0]; ids.append(cur); buf = []
        else: buf.append(line)
    seqs.append("".join(buf)); return ids, seqs

ids, seqs = read_fasta(aln_path)
L = len(seqs[0])
grp = np.array([0 if i.split("|")[0] == "TDT" else 1 for i in ids])
occ = np.zeros((2, L))
for g in (0, 1):
    rows = [seqs[i] for i in range(len(ids)) if grp[i] == g]
    A = np.array([[0 if c in "-." else 1 for c in r] for r in rows], dtype=np.int8)
    occ[g] = A.mean(axis=0)

def colmap(row):
    m, n = {}, 0
    for c, ch in enumerate(row):
        if ch not in "-.": n += 1; m[c] = n
    return m
trow = seqs[[i for i, x in enumerate(ids) if TREF in x][0]]
prow = seqs[[i for i, x in enumerate(ids) if PREF in x][0]]
tmap, pmap = colmap(trow), colmap(prow)

d = occ[0] - occ[1]
print("### %s : %d cols. occupancy diff (TdT - Polmu), threshold |d|>%.2f" % (aln_path, L, THR))
print("### core columns (both occ>=0.8): %d ; TdT-only-ish (d>%.2f): %d ; Polmu-only-ish (d<-%.2f): %d"
      % (((occ[0] >= .8) & (occ[1] >= .8)).sum(), THR, (d > THR).sum(), THR, (d < -THR).sum()))

def runs(mask, gap_allow=2, minlen=2):
    cols = np.where(mask)[0]; out, cur = [], []
    for c in cols:
        if cur and c - cur[-1] - 1 > gap_allow: out.append(cur); cur = []
        cur.append(c)
    if cur: out.append(cur)
    return [r for r in out if len(r) >= minlen]

for name, mask in [("TdT-enriched insertion (TdT present, Polmu gapped)", d > THR),
                   ("Polmu-enriched insertion (Polmu present, TdT gapped)", d < -THR)]:
    rs = runs(mask)
    print("\n  %s : %d segments >=2 cols" % (name, len(rs)))
    print("    len  cols            occT  occP   mTdT_P09838      hPolmu_Q9NP87     TdT consensus")
    for r in sorted(rs, key=lambda x: -len(x)):
        tn = [tmap[c] for c in r if c in tmap]
        pn = [pmap[c] for c in r if c in pmap]
        cons = []
        for c in r:
            col = [seqs[i][c] for i in range(len(ids)) if grp[i] == (0 if d[r[0]] > 0 else 1)]
            col = [x for x in col if x not in "-."]
            cons.append(max(set(col), key=col.count) if col else "-")
        print("    %3d  %5d-%-7d %.2f  %.2f   %-16s %-17s %s"
              % (len(r), r[0], r[-1], occ[0][r].mean(), occ[1][r].mean(),
                 ("%d-%d" % (min(tn), max(tn))) if tn else "(absent in mTdT)",
                 ("%d-%d" % (min(pn), max(pn))) if pn else "(absent in hPolmu)",
                 "".join(cons)))

# pairwise ref-only indels: direct mTdT vs hPolmu gap pattern in the big MSA
print("\n### direct mTdT(P09838) vs hPolmu(Q9NP87) indels in this MSA (>=3 residues)")
state = [(1 if trow[c] not in "-." else 0, 1 if prow[c] not in "-." else 0) for c in range(L)]
i = 0
while i < L:
    s = state[i]
    if s in ((1, 1), (0, 0)): i += 1; continue
    j = i
    while j < L and state[j] == s: j += 1
    if j - i >= 3:
        tn = [tmap[c] for c in range(i, j) if c in tmap]
        pn = [pmap[c] for c in range(i, j) if c in pmap]
        who = "mTdT-only" if s == (1, 0) else "hPolmu-only"
        print("    %-12s len=%3d cols %5d-%-6d mTdT %-12s hPolmu %-12s occT=%.2f occP=%.2f  seq=%s"
              % (who, j - i, i, j - 1,
                 ("%d-%d" % (min(tn), max(tn))) if tn else "-",
                 ("%d-%d" % (min(pn), max(pn))) if pn else "-",
                 occ[0][i:j].mean(), occ[1][i:j].mean(),
                 (trow if s == (1, 0) else prow)[i:j]))
    i = j
