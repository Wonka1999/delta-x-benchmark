"""Signal-to-noise summary + spatial distribution of high-JSD columns."""
import numpy as np
d = np.load("msa_axis/auto_scores.npz", allow_pickle=True)
J, ot, op, sdp = d["J"], d["ot"], d["op"], d["sdp"]
nullB = d["nullB"]; boot = d["boot"]
ids, seqs, buf, cur = [], [], [], None
for line in open("msa_axis/combined.auto.aln"):
    line = line.rstrip()
    if line.startswith(">"):
        if cur is not None: seqs.append("".join(buf))
        cur = line[1:].split()[0]; ids.append(cur); buf = []
    else: buf.append(line)
seqs.append("".join(buf))
tr = seqs[[i for i, x in enumerate(ids) if "TDT|P09838" in x][0]]
sc = np.where((ot >= .8) & (op >= .8))[0]
Js = J[sc]
tnum = {}
n = 0
for c, ch in enumerate(tr):
    if ch not in "-.": n += 1; tnum[c] = n

print("### SIGNAL CONCENTRATION (scorable n=%d)" % len(sc))
tot = Js.sum()
o = np.sort(Js)[::-1]
for k in (5, 10, 20, 30, 50, 100):
    print("  top-%-4d columns hold %5.1f%% of total JSD mass; their JSD range %.3f-%.3f"
          % (k, 100 * o[:k].sum() / tot, o[k - 1], o[0]))
print("  'effective number of discriminating columns' (exp of Shannon entropy of")
print("   normalised JSD over scorable columns) = %.1f"
      % np.exp(-(Js / tot * np.log(Js / tot)).sum()))
nb = np.percentile(nullB[:, sc].ravel(), 99.9)
print("  within-family null p99.9 = %.3f ; columns above it = %d (%.0f%%)"
      % (nb, (Js > nb).sum(), 100 * (Js > nb).sum() / len(sc)))
print("  ratio median(obs)/median(null) = %.2f ; max(obs)/p99.9(null) = %.2f"
      % (np.median(Js) / np.median(nullB[:, sc].ravel()), Js.max() / nb))

print("\n### SPATIAL DISTRIBUTION along mouse TdT (P09838), 50-residue bins")
print("  bin        n_scorable  n_JSD>=0.5  n_JSD>=0.6  frac>=0.5  maxJSD  top residue")
for lo in range(0, 550, 50):
    cols = [c for c in sc if lo < tnum.get(c, -1) <= lo + 50]
    if not cols: continue
    h5 = sum(1 for c in cols if J[c] >= .5); h6 = sum(1 for c in cols if J[c] >= .6)
    best = max(cols, key=lambda c: J[c])
    print("  %3d-%-6d %9d  %10d  %10d   %6.2f   %.3f   %s%d"
          % (lo + 1, lo + 50, len(cols), h5, h6, h5 / len(cols), J[best], tr[best], tnum[best]))

print("\n### NEIGHBOUR SEPARABILITY, systematic (top-50 columns by JSD)")
top = sc[np.argsort(-J[sc])][:50]
sep_both = sep_any = 0
for c in top:
    ps = []
    for off in (-1, 1):
        nn = c + off
        if 0 <= nn < len(J): ps.append(float((boot[:, c] > boot[:, nn]).mean()))
    if ps and min(ps) >= .95: sep_both += 1
    if ps and max(ps) >= .95: sep_any += 1
print("  columns whose JSD exceeds BOTH immediate neighbours with bootstrap P>=0.95: %d/50" % sep_both)
print("  ... exceeds AT LEAST ONE neighbour with P>=0.95: %d/50" % sep_any)
print("  NOTE: this is rank stability of the point estimate, not evidence that the")
print("  neighbouring residue is mechanistically different.")
print("\n  JSD of each top-10 column vs its +/-3 neighbourhood (all scorable):")
for c in top[:10]:
    nb_ = [(tnum.get(x, '-'), round(float(J[x]), 3)) for x in range(c - 3, c + 4)
           if 0 <= x < len(J) and ot[x] >= .8 and op[x] >= .8]
    print("   mTdT %-4s : %s" % (tnum.get(c, '?'), nb_))
