import numpy as np, subprocess, sys
from Bio.PDB import MMCIFParser, PDBParser
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
import warnings; warnings.filterwarnings('ignore')
t31={k.upper():v for k,v in _p3.items()}
US='/home/hew/anaconda3/envs/bioflow_usalign/bin/TMalign'
NUC={'DA','DT','DG','DC','DU'}

def mat(p1,p2,tag):
    subprocess.run([US,p1,p2,'-m',f'aln/m_{tag}.txt'],capture_output=True)
    M=open(f'aln/m_{tag}.txt').read().splitlines()
    k=[j for j,l in enumerate(M) if l.strip().startswith('m ')][0]
    rows=[list(map(float,M[k+1+j].split()[1:5])) for j in range(3)]
    return np.array([r[1:] for r in rows]), np.array([r[0] for r in rows])

# superpose TdT 4QZB protein onto Pol mu 4M04 protein
R,t = mat('chains/4QZB_A.pdb','chains/4M04_A.pdb','clash')
# TdT protein residues (moving)
tdt = PDBParser(QUIET=True).get_structure('t','chains/4QZB_A.pdb')[0]['A']
# Pol mu DNA chains (fixed)
pm = MMCIFParser(QUIET=True).get_structure('p','pdb/4M04.cif')[0]
dna={}
for ch in pm:
    nr=[r for r in ch if r.get_resname().strip() in NUC]
    if nr: dna[ch.id]=nr

print('Pol mu 4M04 nucleic chains: ', {c:f'{len(v)}nt {v[0].id[1]}-{v[-1].id[1]}' for c,v in dna.items()})
print('\n## After superposing mouse TdT 4QZB protein onto human Pol mu 4M04 protein,')
print('## minimum heavy-atom distance from each TdT residue to each Pol mu DNA strand:')
print('## (negative headroom = steric overlap with where Pol mu holds its DNA)')
rows=[]
for r in tdt:
    if r.id[0]!=' ' or r.get_resname() not in t31: continue
    pa=np.array([a.coord for a in r if a.element!='H'])
    pa=(R@pa.T).T+t
    best={}
    for c,nr in dna.items():
        na=np.vstack([np.array([a.coord for a in n if a.element!='H']) for n in nr])
        best[c]=float(np.linalg.norm(pa[:,None,:]-na[None,:,:],axis=-1).min())
    rows.append((r.id[1],t31[r.get_resname()],best))
for num,aa,b in rows:
    if min(b.values())<4.0:
        print(f'   TdT {aa}{num}: ' + '  '.join(f'{c}={b[c]:.2f}A' for c in sorted(b) if b[c]<6))
print('\n## region summary (min distance to Pol mu TEMPLATE strand T):')
for name,a,bq in [('N-term/8kDa',147,200),('Loop around 280-284',278,288),('348-362',348,362),
                  ('Loop1 (TdT 380-401)',380,401),('Loop2 (TdT 413-425)',413,425),('478-486',478,486)]:
    v=[b['T'] for n,aa,b in rows if a<=n<=bq]
    if v: print(f'   {name}: min={min(v):.2f} A  (n={len(v)} modelled res)')
