# DELTA-X v2 — installing the tools

Three tiers. Each one says what it buys you, what it costs, and what it cannot do.
Nothing here is required to read the benchmark; Tier 0 is already in the repository.

Everything below was checked on 2026-11-10 against the live conda channels, PyPI and the
upstream project pages. Where a number comes from somebody else's documentation rather
than from a run on our hardware, it says so. Claims we could not check are marked
**unverified** rather than smoothed over.

---

## Tier 0 — bundled. Nothing to install.

Already in the repository, no installation of any kind:

| what | where | needs |
|---|---|---|
| the six task briefs | `tasks/` | nothing |
| the sequence data (487 sequences, 268 KB) | `data/` | nothing |
| the harness (driver, prompt builder, containment audit, collector) | `harness/` | `python3`, stdlib only |
| the scorecard checker | `grader/check_scorecard.py` | `python3`, stdlib only |
| the aggregator | `analysis/aggregate.py` | `python3`, stdlib only |

We checked the imports: `harness/*.py`, `grader/check_scorecard.py` and
`analysis/aggregate.py` import nothing outside the standard library, so
`python3 -I harness/audit_containment.py`, `python3 -I grader/check_scorecard.py` and
`python3 -I analysis/aggregate.py` run on a bare Python 3.9+ with no environment at all.

**DX01, DX02 and DX02B are fully runnable with zero installs.** Those three tasks block tool
use at the harness level — the agent is handed a text brief and nothing else — so an entire
first campaign (the gate, the plan and the commitments) needs no tier below this one.

The one exception inside Tier 0: `repro/scripts/` re-derives the answer key's numbers and
does import `numpy`, `scipy.stats` and `Bio`. That is Tier 1 work, not Tier 0.

---

## Tier 1 — light install. One command, about five minutes.

Covers **DX03 end to end** and the **structural-alignment half of DX04**. No GPU, no model
weights, no external sequence database.

### 1.1 The command

```bash
conda env create -f env/environment.yml
conda activate delta-x
```

`mamba env create -f env/environment.yml` works identically and solves faster. With conda
24.x the libmamba solver is already the default.

### 1.2 What it installs

| package | pinned | channel | note |
|---|---|---|---|
| python | 3.11 | conda-forge | matches the reference host's 3.11.7 |
| mafft | 7.526 | conda-forge | bioconda stops at 7.525 |
| hmmer | 3.4 | bioconda | includes the Easel `esl-*` miniapps |
| hhsuite | 3.3.0 | bioconda | solver picks build `h503566f_15`; see below |
| foldseek | 10.941cd33 | bioconda | same version as the reference host |
| usalign | 20241201 | bioconda | installs USalign, MMalign, TMalign, TMscore and 11 more |
| numpy / scipy / pandas | 1.26.4 / 1.15 / 2.1.4 | conda-forge | matches the reference host |
| biopython | unpinned | conda-forge | resolves to 1.88 |

Verified: every one of those versions exists on the named channel for linux-64, and the
complete set solves — `conda create --dry-run` with exactly these specs succeeded, 65
packages, on 2026-11-10.

Two traps worth knowing before you edit the file:

- **hhsuite is pinned to a Python version in almost every build.** All but the newest
  bioconda build of hhsuite 3.3.0 declare `python 3.6`–`3.9`, so they cannot coexist with
  `python=3.11`. Only build `h503566f_15` (2025-05-28) depends on an unpinned `python`. The
  solver finds it by itself given `python=3.11`; if you drop the Python pin, it may not.
- **Do not add `tmalign`.** The `usalign` package already installs a `TMalign` binary (we
  checked the bioconda recipe's `build.sh`: 15 programs, `TMalign` among them). Installing
  both puts two different `TMalign` on `PATH`.

### 1.3 Debian / Ubuntu without conda

Real distro packages exist for three of the tools, and they are **older** than the pins
above. Measured on an Ubuntu 20.04 host on 2026-11-10 with `apt-cache policy`:

```bash
sudo apt-get update
sudo apt-get install -y mafft hmmer hhsuite python3-numpy python3-scipy python3-biopython
```

| package | Ubuntu 20.04 candidate | conda pin | consequence |
|---|---|---|---|
| mafft | 7.453 | 7.526 | older alignment binary; record the version you ran |
| hmmer | 3.3 | 3.4 | **the `esl-*` miniapps are not on `PATH`** — verified absent on this host |
| hhsuite | 3.2.0 | 3.3.0 | binaries print `3.1.0` as their version — see the troubleshooting table |

`foldseek` and `usalign` have no Debian/Ubuntu package. Install them from conda, or take
foldseek's static build: `wget https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz`
(the upstream README's own instruction; it also ships `arm64` and `gpu` variants).

### 1.4 pydca — separate environment, on purpose

pydca is the coevolution package named in the DX03 brief. It is **not** in
`environment.yml`, and that is not an oversight:

- its released metadata pins `numpy<=1.15.4`, `scipy==1.3.1`, `biopython==1.74`,
  `numba==0.46.0`, `matplotlib==3.0.0` (read from the installed `1.23` dist-info);
- both CLI entry points import `Bio.SubsMat`, which **Biopython removed in 1.80**
  (verified: `pydca/plmdca_main.py` and `pydca/mfdca_main.py` both import
  `sequence_backmapper`, which does `from Bio.SubsMat.MatrixInfo import blosum62`);
- PyPI has sdist only for 1.23 — no wheel — so a C++ compiler is required at install time.

The recipe below is the one **measured working on this host today**: `plmdca compute_fn`
ran to completion on a 60 × 40 test alignment under Python 3.11 and wrote its scores file.

```bash
conda create -n delta-x-pydca -c conda-forge python=3.11 \
    numpy=1.26.4 scipy=1.15 numba matplotlib requests pip cxx-compiler
conda activate delta-x-pydca
pip install "biopython==1.79"     # last release that still ships Bio.SubsMat (cp311 wheel on PyPI)
pip install --no-deps pydca       # --no-deps is load-bearing: it skips the 2019-era pins
plmdca --help                     # entry points: plmdca, mfdca, pydca
```

The reference host instead used a Python **3.7** environment, where plain
`pip install pydca` resolves its own pins. Both work. Do not put either into the `delta-x`
environment.

### 1.5 Verify the install

```bash
mafft --version                     # -> v7.526 (2024/Apr/26)      [writes to stderr]
hmmbuild -h   | sed -n 2p           # -> # HMMER 3.4 (Aug 2023)    [HMMER has no --version]
hmmalign -h   | sed -n 2p           # -> # HMMER 3.4 (Aug 2023)
esl-reformat -h | sed -n 2p         # -> Easel ...
hhmake -h     | head -1             # -> HHmake 3.x               [self-reported, see below]
foldseek version                    # -> 10.941cd33
USalign -v    | sed -n 3p           # -> US-align (Version 2024...)
TMalign -h    | head -5
python -c "import numpy,scipy,pandas,Bio;print(numpy.__version__,scipy.__version__,pandas.__version__,Bio.__version__)"
```

Then write the manifest the agent will actually read:

```bash
bash env/probe_env.sh ./ENVIRONMENT.md
```

`probe_env.sh` reports what *this* host has, writes `NOT INSTALLED` for everything it
does not find, and exits 0 either way. Never hand-edit the result to look complete.

---

## Tier 2 — heavy. GPU, multi-GB weights, real pain.

Needed only for the structure-**prediction** half of DX04. The structural-alignment half
(USalign/TMalign, foldseek, experimental PDB entries) is already covered by Tier 1.

| | ESMFold | Protenix | ColabFold (alternative) |
|---|---|---|---|
| weights download | **8.44 GB** (verified: `facebook/esmfold_v1`, single `pytorch_model.bin`) | not documented upstream (unverified) | AF2 params, auto-downloaded, size not stated upstream |
| disk | ~20 GB with the env and torch | ~15 GB with the env (estimate, unverified) | ~10 GB (estimate, unverified) |
| VRAM, ~500 residues | A100 80 GB on the reference host; smaller cards reportedly need 16–24 GB in fp32 (**unverified**) | **6.1 GB at 500 tokens** (upstream doc, "inference peak memory") | ~16 GB (unverified) |
| runtime, ~500 residues | seconds to a few minutes on an A100 (**unverified**; published figure is 14.2 s for 384 residues on a V100, and that is a secondary source) | unverified | minutes, plus a remote MSA round-trip |
| CPU-only | technically possible, needs tens of GB of RAM and is hours per chain (**unverified**) | upstream says nothing about CPU; assume no | upstream implies yes, "5–10× slower" on Apple Silicon |

### 2.1 ESMFold

The HuggingFace route is the one that does not require building OpenFold:

```bash
conda create -n delta-x-esmfold -c conda-forge python=3.11 pip
conda activate delta-x-esmfold
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate
python - <<'PY'
from transformers import AutoTokenizer, EsmForProteinFolding
tok = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
model = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1").cuda()
model.trunk.set_chunk_size(64)      # cuts activation memory on long chains
PY
```

Verified: `torch-2.1.2+cu121-cp311-cp311-linux_x86_64.whl` exists on the PyTorch cu121
index — that is the exact torch the reference host ran. Verified: the checkpoint is a
single 8.44 GB `pytorch_model.bin`, and the HuggingFace port vendors the parts of OpenFold
it needs, which is why `pip install openfold` is not in the list.

The other route, `pip install "fair-esm[esmfold]"`, pulls in OpenFold and its CUDA
extensions and compiles against your toolchain. It is the painful one. If you have a
working OpenFold already, use it; if you do not, do not start here.

ESMFold needs no MSA and no sequence database — it folds from the single sequence, which
is why it is the cheap predictor for this benchmark.

### 2.2 Protenix

```bash
sudo apt-get install -y kalign hmmer      # upstream's own prerequisite for template / RNA MSA search
pip install --upgrade protenix --index-url https://pypi.org/simple
protenix pred -i examples/input.json -o ./output -n protenix_base_default_v1.0.0
```

Verified from upstream docs: the install command, the `kalign`/`hmmer` prerequisite, the
inference command, the model names, and the inference peak-memory table (6.1 GB at 500
tokens rising to 78.1 GB at 4,000). **Not documented upstream and therefore unverified:**
the required Python and CUDA versions, where the checkpoints come from and how large they
are, whether CPU-only inference works at all. A `Dockerfile` exists in the repository but
no published image name. Budget time for a first run that downloads weights silently.

### 2.3 ColabFold

```bash
curl -fsSL https://pixi.sh/install.sh | sh
git clone https://github.com/YoshitakaMo/localcolabfold.git
cd localcolabfold && pixi install && pixi run setup
```

Upstream asks for CUDA 12.1 or later (its README is self-contradictory about the exact
minimum) and uses the **remote** MMseqs2 server for MSAs by default, so it needs network
access per prediction — it pays for an MSA that ESMFold does not need.

---

## If you cannot install Tier 2

**DX04 is still partially runnable.** Experimental structures plus a structural aligner is
a legitimate, reduced scope:

- the PDB and the RCSB search API are reachable with `curl`; DX04 supplies no accessions on
  purpose, so finding entries is part of the task either way;
- `structures_manifest.json`, `superposition.tsv`, `region_nominations.json` and
  `null_report.json` — including the same-protein and cross-species nulls — are all
  derivable from experimental coordinates with USalign/TMalign and foldseek alone;
- `prediction_validity.json` **cannot be produced**, because there is no prediction to
  validate.

When that happens, the run must say so in its scorecard's `campaign.measured_scope` field,
which the grader requires to name what was *not* measured — `grader/check_scorecard.py`
fails a scorecard whose `measured_scope` is absent, and warns when it does not name the
unmeasured part. The grader records the item as **not attempted**. It is not a zero, and
this document does not assign it a point value: a zero asserts the agent tried and failed,
and that assertion would be false.

Scoring a not-attempted item as zero, or quietly omitting it, voids the comparison against
the published baselines, which were measured under a stated scope of their own.

---

## Docker and offline

The repository ships no Dockerfile and no image, by choice: Tier 0 and Tier 1 are small
enough that a container buys little, and Tier 2's weights dominate any image you would
build. What we can say accurately:

- **Tier 0 offline:** complete. No network, no installs.
- **Tier 1 offline:** `conda env create` needs the network once. For a genuinely air-gapped
  host, build the environment on a connected machine and move it with `conda-pack`, or
  mirror conda-forge and bioconda locally. There is no offline path that avoids both.
- **Tier 2 offline:** pre-download the ESMFold checkpoint on a connected host
  (`huggingface-cli download facebook/esmfold_v1`), copy `HF_HOME`, and run with
  `HF_HUB_OFFLINE=1`. **Unverified here** — we did not run it.
- **DX04 is not an offline task in any case.** Its brief grants network access to the PDB
  and the RCSB search API and withholds the accessions, so a host with no network cannot
  complete it regardless of which tier is installed.

---

## Troubleshooting

| symptom | cause | fix |
|---|---|---|
| `conda env create` fails to solve, or hangs for minutes | channel order, or a package pinned to an old Python. hhsuite's older builds declare `python 3.6`–`3.9` and will not sit next to `python=3.11` | keep the channel order `conda-forge` then `bioconda`, keep `python=3.11`, and add packages to a second environment rather than widening this one. `mamba` reports conflicts far more legibly than conda |
| `torch.cuda.is_available()` is `False`, or `undefined symbol` on `import torch` | a CPU-only torch wheel, or a torch built for a CUDA your driver predates | install from the matching index explicitly: `pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121`, and check the driver with `nvidia-smi`. Never mix a conda `pytorch` with a pip `torch` in one environment |
| `foldseek` dies with `Illegal instruction`, or its GPU mode fails | the standard build needs AVX2 (`grep avx2 /proc/cpuinfo`); upstream states the GPU build needs glibc ≥ 2.17 and NVIDIA driver ≥ 525.60.13, and that bioconda binaries "will not work on older GPU generations (e.g. Volta or Pascal)" | on a non-AVX2 CPU take the ARM64 or an SSE build from mmseqs.com/foldseek; on a pre-Ampere GPU use foldseek's CPU mode |
| `esl-reformat: command not found` while `hmmbuild` works | the Debian/Ubuntu `hmmer` package does not put the Easel miniapps on `PATH` — verified absent on an Ubuntu 20.04 host — and it is 3.3, not 3.4 | install `hmmer=3.4` from bioconda, which ships them |
| `ModuleNotFoundError: No module named 'Bio.SubsMat'` from `plmdca` / `mfdca` | Biopython ≥ 1.80 removed `Bio.SubsMat`; pydca 1.23 still imports it | use the dedicated environment in § 1.4 with `biopython==1.79`. Do not downgrade Biopython inside `delta-x` |
| `hhmake -h` prints `HHmake 3.1.0` on a package labelled 3.2.0 or 3.3.0 | HH-suite binaries carry an internal version string that does not track the package version. Measured here: Ubuntu's `hhsuite` **3.2.0** package prints **3.1.0** | record what the binary prints, which is what `probe_env.sh` does. The bioconda 3.3.0 build's own string was **not verified** by us |

---

## What was and was not verified

**Verified on 2026-11-10** — by `conda search` / `conda create --dry-run` here, by reading
upstream recipes and metadata, or by running the thing: every pin in `environment.yml`
exists on linux-64 and the complete set solves (65 packages); the bioconda `usalign` recipe
installs `USalign`, `MMalign`, `TMalign`, `TMscore` and 11 more; `hhsuite` build
`h503566f_15` is the only one not pinned to Python 3.6–3.9; the ESMFold checkpoint is
8.44 GB and `torch 2.1.2+cu121` has a cp311 linux wheel; Ubuntu 20.04 ships mafft 7.453,
hmmer 3.3 (no `esl-*` on `PATH`) and hhsuite 3.2.0 whose binaries print 3.1.0; pydca 1.23's
pins and its `Bio.SubsMat` import, and that `pip install --no-deps pydca` under Python 3.11
with Biopython 1.79 runs `plmdca compute_fn` to completion; and `probe_env.sh` itself, run
on this host including its missing-tool path.

**Not verified** — treated as claims from other people's documentation, and marked as such
above: Protenix's Python/CUDA requirements, checkpoint source and size; every Tier 2
runtime and VRAM figure for a ~500-residue chain; CPU-only viability for any predictor;
the offline HuggingFace route; the bioconda hhsuite 3.3.0 binaries' self-reported version
string; ColabFold's disk footprint.
