"""Minimal HMMER3 .hmm parser + Stockholm match-state mapper."""
import math, re

AA = list("ACDEFGHIKLMNPQRSTVWY")

def parse_hmm(path):
    """Return dict with leng, match[k] (prob dict, k=1..M), ins[k], trans[k], map_[k], cons[k]."""
    lines = open(path).read().splitlines()
    hdr = {}
    i = 0
    while not lines[i].startswith("HMM "):
        parts = lines[i].split(None, 1)
        if len(parts) == 2:
            hdr[parts[0]] = parts[1].strip()
        i += 1
    i += 2  # skip 'HMM' alphabet line and transition header line
    match, ins, trans, map_, cons = {}, {}, {}, {}, {}
    if lines[i].strip().startswith("COMPO"):
        i += 1
    # node 0: insert0 emissions + begin transitions
    ins[0] = [float(x) if x != '*' else math.inf for x in lines[i].split()]
    i += 1
    trans[0] = [float(x) if x != '*' else math.inf for x in lines[i].split()]
    i += 1
    M = int(hdr["LENG"])
    for k in range(1, M + 1):
        f = lines[i].split()
        assert int(f[0]) == k, (k, f[0])
        match[k] = [float(x) if x != '*' else math.inf for x in f[1:21]]
        # optional annotation: MAP CONS RF MM CS
        if len(f) > 21:
            try:
                map_[k] = int(f[21])
            except ValueError:
                map_[k] = None
        if len(f) > 22:
            cons[k] = f[22]
        i += 1
        ins[k] = [float(x) if x != '*' else math.inf for x in lines[i].split()]
        i += 1
        trans[k] = [float(x) if x != '*' else math.inf for x in lines[i].split()]
        i += 1
    return dict(hdr=hdr, leng=M, match=match, ins=ins, trans=trans, map=map_, cons=cons)

def probs(negln):
    """HMMER stores -ln(p). Convert vector to probability list."""
    return [math.exp(-x) if x != math.inf else 0.0 for x in negln]

def js_div(p, q):
    """Jensen-Shannon divergence in bits (0..1)."""
    m = [(a + b) / 2 for a, b in zip(p, q)]
    def kl(x, y):
        s = 0.0
        for a, b in zip(x, y):
            if a > 0 and b > 0:
                s += a * math.log2(a / b)
        return s
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# HMMER's default amino-acid background (Dirichlet / Swiss-Prot derived, as in p7_bg)
BG = dict(zip(AA, [0.0787945,0.0151600,0.0535222,0.0668298,0.0397062,0.0695071,
                   0.0229198,0.0590092,0.0594422,0.0963728,0.0237718,0.0414386,
                   0.0482460,0.0395639,0.0540518,0.0683601,0.0540371,0.0673286,
                   0.0114039,0.0304535]))
BGV = [BG[a] for a in AA]

def info_content(p):
    """Relative entropy to background, bits."""
    s = 0.0
    for a, b in zip(p, BGV):
        if a > 0:
            s += a * math.log2(a / b)
    return s

def read_stockholm(path):
    """Return {name: aligned_seq} concatenating wrapped blocks."""
    seqs = {}
    order = []
    for line in open(path):
        line = line.rstrip("\n")
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        name, _, seq = line.partition(" ")
        seq = seq.strip()
        if not seq:
            continue
        # robust split
        f = line.split()
        name, seq = f[0], f[-1]
        if name not in seqs:
            seqs[name] = []
            order.append(name)
        seqs[name].append(seq)
    return {k: "".join(v) for k, v in seqs.items()}, order

def matchstate_map(aligned_seq):
    """For an hmmalign Stockholm row, return (res_to_k, k_to_res, ins_after_k).
    Match columns = uppercase letters or '-'; insert columns = lowercase or '.'.
    Returns 1-based residue index -> model match state k (or None if in insert),
    and k -> residue index (or None if deletion)."""
    res_to_k, k_to_res, ins_after = {}, {}, {}
    k = 0
    r = 0
    for ch in aligned_seq:
        if ch == '.' or ch.islower():
            if ch != '.':
                r += 1
                res_to_k[r] = None
                ins_after[k] = ins_after.get(k, 0) + 1
        else:
            k += 1
            if ch == '-' or ch == '~':
                k_to_res[k] = None
            else:
                r += 1
                res_to_k[r] = k
                k_to_res[k] = r
    return res_to_k, k_to_res, ins_after, k, r
