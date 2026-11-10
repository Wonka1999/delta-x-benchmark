"""Per-column subfamily-discrimination statistics for a two-subfamily MSA.

Usage: score_cols.py <aln.fasta> <outprefix> [n_perm] [n_boot] [seed]

Statistics per alignment column:
  occ_T, occ_P      weighted non-gap occupancy in each subfamily
  JSD               Jensen-Shannon divergence (base 2, max 1.0) between the two
                    subfamilies' weighted amino-acid distributions, conditioned
                    on non-gap. With equal group priors this is exactly the
                    mutual information between subfamily label and residue identity.
  consT, consP      within-subfamily conservation = 1 - H(p)/log2(20)
  SDP               JSD * min(consT, consP)   (classic specificity-determining
                    position score: must be conserved in BOTH and different)
  gapJSD            JSD of the 2-state (gap / non-gap) distribution

Sequence weights: Henikoff position-based, computed independently inside each
subfamily and normalised to sum to 1 per subfamily, so the 322-vs-167 sampling
imbalance and within-clade redundancy do not drive the statistic.

Nulls:
  NullA  random permutation of subfamily labels over all sequences (pure noise)
  NullB  within-subfamily random split-half JSD (controls for within-family
         heterogeneity / phylogenetic structure) -- the conservative null
Bootstrap: resample sequences with replacement inside each subfamily.
"""
import sys
import numpy as np

aln_path, outpre = sys.argv[1], sys.argv[2]
NPERM = int(sys.argv[3]) if len(sys.argv) > 3 else 200
NBOOT = int(sys.argv[4]) if len(sys.argv) > 4 else 500
SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 20260101

AA = "ACDEFGHIKLMNPQRSTVWY"
GAP = 20
NS = 21
aaidx = {a: i for i, a in enumerate(AA)}
LOG2_20 = np.log2(20.0)


def read_fasta(p):
    ids, seqs, cur, buf = [], [], None, []
    for line in open(p):
        line = line.rstrip()
        if line.startswith(">"):
            if cur is not None:
                seqs.append("".join(buf))
            cur = line[1:].split()[0]
            ids.append(cur)
            buf = []
        else:
            buf.append(line)
    seqs.append("".join(buf))
    return ids, seqs


ids, seqs = read_fasta(aln_path)
L = len(seqs[0])
assert all(len(s) == L for s in seqs), "ragged alignment"
N = len(ids)
M = np.full((N, L), GAP, dtype=np.int8)
for i, s in enumerate(seqs):
    M[i] = [aaidx.get(c.upper(), GAP) for c in s]   # X/B/Z/-/. all -> GAP state
grp = np.array([0 if i.split("|")[0] == "TDT" else 1 for i in ids])
print("rows=%d cols=%d TDT=%d POLM=%d" % (N, L, (grp == 0).sum(), (grp == 1).sum()),
      file=sys.stderr)


def henikoff(Msub):
    """Position-based sequence weights, normalised to sum 1."""
    n, l = Msub.shape
    w = np.zeros(n)
    for c in range(l):
        col = Msub[:, c]
        cnt = np.bincount(col, minlength=NS)
        nz = cnt > 0
        r = nz.sum()
        if r <= 1:
            continue
        w += 1.0 / (r * cnt[col])
    s = w.sum()
    return w / s if s > 0 else np.full(n, 1.0 / n)


def col_profiles(Msub, w):
    """-> (freq[L,20] over non-gap, occupancy[L])"""
    l = Msub.shape[1]
    cnt = np.zeros((l, NS))
    for a in range(NS):
        cnt[:, a] = ((Msub == a) * w[:, None]).sum(axis=0)
    occ = cnt[:, :20].sum(axis=1)
    f = np.divide(cnt[:, :20], np.where(occ > 0, occ, 1)[:, None])
    return f, occ, cnt[:, GAP]


def jsd(p, q, alpha=0.01):
    """row-wise JSD base 2 with additive pseudocount (uniform over 20)."""
    p = (p + alpha / 20.0) / (1.0 + alpha)
    q = (q + alpha / 20.0) / (1.0 + alpha)
    m = 0.5 * (p + q)
    def kl(a, b):
        with np.errstate(divide="ignore", invalid="ignore"):
            t = a * np.log2(a / b)
        return np.nansum(np.where(a > 0, t, 0.0), axis=1)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def entropy_norm(p, alpha=0.01):
    p = (p + alpha / 20.0) / (1.0 + alpha)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = -np.nansum(np.where(p > 0, p * np.log2(p), 0.0), axis=1)
    return h / LOG2_20


def score(Mt, Mp):
    wt, wp = henikoff(Mt), henikoff(Mp)
    ft, ot, gt = col_profiles(Mt, wt)
    fp, op, gp = col_profiles(Mp, wp)
    J = jsd(ft, fp)
    ct, cp = 1 - entropy_norm(ft), 1 - entropy_norm(fp)
    gj = np.zeros(len(J))
    P = np.vstack([ot, gt]).T
    Q = np.vstack([op, gp]).T
    Pm = (P + 0.005) / (1.01)
    Qm = (Q + 0.005) / (1.01)
    Mm = 0.5 * (Pm + Qm)
    gj = 0.5 * (Pm * np.log2(Pm / Mm)).sum(1) + 0.5 * (Qm * np.log2(Qm / Mm)).sum(1)
    return dict(J=J, ot=ot, op=op, ct=ct, cp=cp, gj=gj, sdp=J * np.minimum(ct, cp))


Mt, Mp = M[grp == 0], M[grp == 1]
obs = score(Mt, Mp)
rng = np.random.default_rng(SEED)

# ---- NullA: permute labels ----
nt = Mt.shape[0]
nullA = np.zeros((NPERM, L))
for b in range(NPERM):
    perm = rng.permutation(N)
    nullA[b] = score(M[perm[:nt]], M[perm[nt:]])["J"]

# ---- NullB: within-subfamily split halves ----
nullB = np.zeros((2 * NPERM, L))
for b in range(NPERM):
    pt = rng.permutation(nt)
    nullB[b] = score(Mt[pt[:nt // 2]], Mt[pt[nt // 2:]])["J"]
    npp = Mp.shape[0]
    pp = rng.permutation(npp)
    nullB[NPERM + b] = score(Mp[pp[:npp // 2]], Mp[pp[npp // 2:]])["J"]

# ---- bootstrap ----
boot = np.zeros((NBOOT, L))
for b in range(NBOOT):
    bt = rng.integers(0, nt, nt)
    bp = rng.integers(0, Mp.shape[0], Mp.shape[0])
    boot[b] = score(Mt[bt], Mp[bp])["J"]

np.savez_compressed(outpre + ".npz", **obs, grp=grp, nullA=nullA, nullB=nullB,
                    boot=boot, M=M, ids=np.array(ids))
print("saved", outpre + ".npz", file=sys.stderr)
