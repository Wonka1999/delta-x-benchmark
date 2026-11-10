"""Greedy max-diversity subset selection on 4-mer profiles, per subfamily.
Usage: make_reduced.py <combined.fasta> <n_tdt> <n_polm> <out.fasta>
Refs (P09838, P04053, P06526, Q9NP87, Q9JIW4) are force-included as seeds.
"""
import sys
import numpy as np
from Bio import SeqIO

inp, n_t, n_p, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
FORCE = {"P09838", "P04053", "P06526", "Q9NP87", "Q9JIW4"}
AA = "ACDEFGHIKLMNPQRSTVWY"
idx = {a: i for i, a in enumerate(AA)}


def kprofile(s, k=3):
    v = np.zeros(20 ** k, dtype=np.float32)
    for i in range(len(s) - k + 1):
        w = s[i:i + k]
        if all(c in idx for c in w):
            j = 0
            for c in w:
                j = j * 20 + idx[c]
            v[j] += 1
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


recs = list(SeqIO.parse(inp, "fasta"))
groups = {"TDT": [], "POLM": []}
for r in recs:
    groups[r.id.split("|")[0]].append(r)

picked = []
for g, n in (("TDT", n_t), ("POLM", n_p)):
    rs = groups[g]
    P = np.vstack([kprofile(str(r.seq)) for r in rs])
    sel = [i for i, r in enumerate(rs) if r.id.split("|")[1] in FORCE]
    if not sel:
        sel = [0]
    while len(sel) < n:
        d = 1.0 - P @ P[sel].T          # cosine distance to every picked seq
        mind = d.min(axis=1)
        mind[sel] = -1
        sel.append(int(np.argmax(mind)))
    picked += [rs[i] for i in sel]
    print(g, "selected", len(sel), file=sys.stderr)

with open(out, "w") as f:
    for r in picked:
        f.write(">%s\n%s\n" % (r.id, str(r.seq)))
print("wrote", len(picked), "to", out, file=sys.stderr)
