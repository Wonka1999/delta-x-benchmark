"""Per-sequence residue count inside an alignment-column window, by subfamily.
Usage: window.py <aln> <TREF> <PREF> <col_start> <col_end> [label]"""
import sys
import numpy as np

aln, TREF, PREF, a, b = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
label = sys.argv[6] if len(sys.argv) > 6 else ""

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
grp = [i.split("|")[0] for i in ids]
cnt = {"TDT": [], "POLM": []}
for i, s in enumerate(seqs):
    cnt[grp[i]].append(sum(1 for c in s[a:b + 1] if c not in "-."))
print("### window cols %d-%d  %s" % (a, b, label))
for g in ("TDT", "POLM"):
    v = np.array(cnt[g])
    print("  %-5s n=%3d  residues in window: mean=%.2f median=%.0f sd=%.2f min=%d max=%d"
          % (g, len(v), v.mean(), np.median(v), v.std(), v.min(), v.max()))
from collections import Counter
for g in ("TDT", "POLM"):
    print("  %-5s length distribution: %s" % (g, sorted(Counter(cnt[g]).items())))
def getrow(sub):
    return seqs[[i for i, x in enumerate(ids) if sub in x][0]]
def num(row, c0):
    return sum(1 for ch in row[:c0] if ch not in "-.")
tr, pr = getrow(TREF), getrow(PREF)
print("  mTdT  slice: %s   (res %d-%d)" % (tr[a:b + 1], num(tr, a) + 1, num(tr, b + 1)))
print("  hPolmu slice: %s  (res %d-%d)" % (pr[a:b + 1], num(pr, a) + 1, num(pr, b + 1)))
