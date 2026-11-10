# DELTA-X v2 — ENVIRONMENT: Tool Manifest

The absolute path and version of every tool named in the task briefs, as measured on the
benchmark host on 2026-11-08.

## 1. Tools

| tool | absolute path | version |
|---|---|---|
| MAFFT | `/home/hew/anaconda3/envs/bioflow_mafft/bin/mafft` | v7.526 (2024/Apr/26) |
| HMMER | `/home/hew/anaconda3/envs/bioflow_hmmer/bin/{hmmbuild,hmmalign}` | 3.4 (Aug 2023) |
| plmDCA / mfDCA (pydca) | `/home/hew/anaconda3/envs/bioflow_pydca/bin/{plmdca,mfdca}` | pydca CLI |
| ESMFold | `/home/hew/anaconda3/envs/bioflow_esm/bin/python` | torch 2.1.2+cu121, CUDA available |
| Protenix | `/home/hew/anaconda3/envs/protenix/bin/protenix` | — |
| foldseek | `/home/hew/anaconda3/envs/bioflow_foldseek/bin/foldseek` | 10.941cd33 |
| USalign suite | `/home/hew/anaconda3/envs/bioflow_usalign/bin/` | USalign, MMalign, TMalign and helpers |
| scientific Python | `/home/hew/anaconda3/bin/python` | 3.11.7 · numpy 1.26.4 · scipy 1.15.0 · pandas 2.1.4 |
| GPU | — | NVIDIA A100 80 GB PCIe |

## 2. Notes

- The default `python` on `PATH` is **not** the interpreter listed above and carries no
  numpy. Invoke the absolute path.
- Record the version you actually observed in `execution_log.json`. This table is the
  environment as of the date above, not a guarantee.
