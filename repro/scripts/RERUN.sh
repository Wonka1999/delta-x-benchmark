#!/usr/bin/env bash
# DELTA-X structural-divergence axis - full reproduction
# cwd must be .../dx_repro/struct ; refs.fasta is one level up
set -euo pipefail
US=/home/hew/anaconda3/envs/bioflow_usalign/bin
FS=/home/hew/anaconda3/envs/bioflow_foldseek/bin/foldseek
PY=/home/hew/anaconda3/bin/python
ESMPY=/home/hew/anaconda3/envs/bioflow_esm/bin/python

# 1. discover structures (RCSB search API, by UniProt accession)
#    see q_tdt.json / the inline loop in the transcript; produces the entry lists
# 2. metadata
$PY -I meta.py 4I27 4QZB 5D4B 1JMS 4M04 4YD1 4LZD 2IHM 6GO5 6GO3
# 3. fetch
mkdir -p pdb; for ID in 4I27 4QZB 5D4B 1JMS 4M04 4YD1 4LZD 2IHM 6GO5 6GO3; do
  curl -s -o pdb/$ID.cif https://files.rcsb.org/download/$ID.cif; done
# 4. verify author numbering == UniProt numbering
$PY -I chk.py
# 5. extract protein-only chains
$PY -I extract.py
# 6. superposition + per-residue deviation profiles
$PY -I profile.py chains/4QZB_A.pdb chains/4M04_A.pdb 4QZB_4M04
$PY -I profile.py chains/4I27_A.pdb chains/4YD1_A.pdb 4I27_4YD1
$PY -I profile.py chains/1JMS_A.pdb chains/4LZD_A.pdb 1JMS_4LZD
# nulls
$PY -I profile.py chains/4QZB_A.pdb chains/1JMS_A.pdb NULL_TdT
$PY -I profile.py chains/4M04_A.pdb chains/2IHM_A.pdb NULL_PM
# 7. foldseek structure-aware alignment
mkdir -p fs && cd fs && $FS easy-search ../chains/4QZB_A.pdb ../chains/4M04_A.pdb res.tsv tmp \
  --format-output "query,target,fident,alnlen,qstart,qend,tstart,tend,evalue,bits,alntmscore,lddt,qaln,taln,qcov,tcov" \
  -e 1000 --exhaustive-search 1 && cd ..
# 8. DNA contacts
$PY -I contacts.py 4QZB A ; $PY -I contacts.py 4M04 A
# 9. ESMFold (HuggingFace facebook/esmfold_v1; needs transformers+accelerate+omegaconf in bioflow_esm)
$ESMPY -I esm/run_esm_hf.py esm/refs.json
$PY -I profile.py esm/mTdT_cat.pdb esm/hPolmu_cat.pdb ESM_ESM
$PY -I profile.py esm/mTdT_cat.pdb chains/4QZB_A.pdb NULL_ESM
# 10. steric-occlusion test (TdT superposed on Pol mu, distance to Pol mu template strand)
$PY -I clash.py ; $PY -I clash2.py
# 11. order/disorder census across all PDB entries
$PY -I disorder.py P09838 1JMS 1KDH 1KEJ 4I27 4I28 4I29 4I2A 4I2B 4I2C 4I2D 4I2E 4I2F 4I2G 4I2H 4I2I 4I2J 4IQT 4IQU 4IQV 4IQW 4QZ8 4QZ9 4QZA 4QZB 4QZC 4QZD 4QZE 4QZF 4QZG 4QZH 4QZI 5D46 5D49 5D4B
$PY -I disorder.py Q9NP87 4LZD 4LZG 4M04 4M0A 4YCX 4YD1 4YD2 5TWP 5TWQ 5TWR 5TWS 5TXX 5TXZ 5TYB 5TYC 5TYD 5TYE 5TYF 5TYG 5VZ7 5VZ8 5VZ9 5VZA 5VZB 6AEC 6AEH 6AK5 6AK6 6IPD 6IPE 6P1M 6P1N 6VEZ 6VF0 7CO6 7CO8 7KSS 7KST 9CQ3 9I04
