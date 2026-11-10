#!/usr/bin/env python3
"""Effective-sequence estimators behind the DX02 rule-4 adjudication in grader/KEY.md.

Three estimators, because the three BASELINE-v2-clean runs wrote their adequacy floors on
three different ones and the key previously adjudicated all three against only the first:

  1. hmmbuild eff_nseq      -- HMMER's entropy-weighted effective sequence count (run1, run2)
  2. hhmake NEFF            -- HH-suite profile diversity                        (run3 secondary)
  3. Henikoff per-column Neff -- position-based weights, summed over non-gap rows (run3 primary)

Deterministic: MAFFT has no stochastic component, HMMER 3.4 and hhmake are deterministic, and
the Henikoff computation is closed-form. Note that MAFFT --auto selects its strategy by input
size, so changing the sequence count changes the algorithm and therefore the numbers.

Pol mu is the 167-sequence ANALYSIS set: the 165 curated sequences plus the two canonical
references appended from refs.fasta (Q9NP87, Q9JIW4), matching build_combined.py.

Usage:  python3 -I neff_estimators.py <data_dir> <work_dir>
"""
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np

AA = "ACDEFGHIKLMNPQRSTVWY"
MAFFT = "/home/hew/anaconda3/envs/bioflow_mafft/bin/mafft"
HMMBUILD = "/home/hew/anaconda3/envs/bioflow_hmmer/bin/hmmbuild"
HHMAKE = "/usr/bin/hhmake"
OCCUPANCY_FLOOR = 0.5  # a column is "core" when at least half the rows carry a residue


def read_fasta(path):
    out, name, buf = [], None, []
    for line in Path(path).read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                out.append((name, "".join(buf)))
            name, buf = line[1:], []
        else:
            buf.append(line.strip())
    if name is not None:
        out.append((name, "".join(buf)))
    return out


def write_fasta(path, records):
    with open(path, "w") as fh:
        for header, seq in records:
            fh.write(f">{header}\n{seq}\n")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv):
    proc = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"FAILED {' '.join(argv)}\n{proc.stderr[-2000:]}")
    return proc


def henikoff_percolumn_neff(aln_path):
    """Henikoff position-based weights, normalised to sum to the sequence count, then summed
    over the non-gap rows of each column. This is run3's primary estimator."""
    seqs = [s.upper() for _, s in read_fasta(aln_path)]
    matrix = np.array([list(s) for s in seqs])
    n_seq, n_col = matrix.shape
    residue = np.isin(matrix, list(AA))

    weights = np.zeros(n_seq)
    for col in range(n_col):
        mask = residue[:, col]
        if not mask.any():
            continue
        values, counts = np.unique(matrix[mask, col], return_counts=True)
        per_residue = dict(zip(values, 1.0 / (len(values) * counts)))
        weights[mask] += [per_residue[x] for x in matrix[mask, col]]
    weights = weights / weights.sum() * n_seq

    neff = np.array([weights[residue[:, c]].sum() for c in range(n_col)])
    occupancy = residue.mean(axis=0)
    return neff, occupancy, n_seq, n_col


def main():
    data = Path(sys.argv[1] if len(sys.argv) > 1 else
                "/home/hew/python/EvoAgenda/benchmark/delta_x_v2/repro/data")
    work = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    work.mkdir(parents=True, exist_ok=True)

    refs = dict(read_fasta(data / "refs.fasta"))
    sets = {
        "TDT": read_fasta(data / "TDT.curated.fasta"),
        "POLM167": read_fasta(data / "POLM.curated.fasta") + [
            ("POLM|Q9NP87|REFhPolmu", refs["hPolmu|Q9NP87"]),
            ("POLM|Q9JIW4|REFmPolmu", refs["mPolmu|Q9JIW4"]),
        ],
    }

    print("input checksums")
    for name in ("TDT.curated.fasta", "POLM.curated.fasta", "refs.fasta"):
        print(f"  {sha256(data / name)}  {name}")

    for label, records in sets.items():
        raw, aln = work / f"{label}.fa", work / f"{label}.aln.fasta"
        write_fasta(raw, records)
        with open(aln, "w") as fh:
            subprocess.run([MAFFT, "--auto", "--quiet", "--thread", "8", str(raw)],
                           stdout=fh, check=True)

        run([HMMBUILD, "--amino", "--informat", "afa",
             "-o", str(work / f"{label}.hmmbuild.log"),
             str(work / f"{label}.hmm"), str(aln)])
        eff_nseq = next(l.split()[1] for l in (work / f"{label}.hmm").read_text().splitlines()
                        if l.startswith("EFFN"))

        run([HHMAKE, "-i", str(aln), "-o", str(work / f"{label}.hhm"), "-M", "50", "-v", "0"])
        hh_neff = next(l.split()[1] for l in (work / f"{label}.hhm").read_text().splitlines()
                       if l.upper().startswith("NEFF"))

        neff, occupancy, n_seq, n_col = henikoff_percolumn_neff(aln)
        core = neff[occupancy >= OCCUPANCY_FLOOR]

        print(f"\n{label}: n={n_seq} alignment_columns={n_col} core_columns={len(core)}")
        print(f"  hmmbuild eff_nseq         {float(eff_nseq):.3f}")
        print(f"  hhmake NEFF               {float(hh_neff):.1f}")
        print(f"  Henikoff per-column Neff  core median {np.median(core):.1f} "
              f"min {core.min():.1f} max {core.max():.1f} "
              f"fraction >= 25: {(core >= 25).mean():.3f}")
        print(f"  (all columns)             median {np.median(neff):.1f} "
              f"fraction >= 25: {(neff >= 25).mean():.3f}")


if __name__ == "__main__":
    main()
