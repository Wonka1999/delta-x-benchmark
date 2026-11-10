import numpy as np, subprocess, sys
from Bio.PDB import MMCIFParser, PDBParser
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
import warnings; warnings.filterwarnings('ignore')
t31={k.upper():v for k,v in _p3.items()}
US='/home/hew/anaconda3/envs/bioflow_usalign/bin/TMalign'
NUC={'DA','DT','DG','DC','DU'}
BB={'N','CA','C','O'}
def mat(p1,p2,tag):
    subprocess.run([US,p1,p2,'-m',f'aln/m_{tag}.txt'],capture_output=True)
    M=open(f'aln/m_{tag}.txt').read().splitlines()
    k=[j for j,l in enumerate(M) if l.strip().startswith('m ')][0]
    rows=[list(map(float,M[k+1+j].split()[1:5])) for j in range(3)]
    return np.array([r[1:] for r in rows]), np.array([r[0] for r in rows])
pm=MMCIFParser(QUIET=True).get_structure('p','pdb/4M04.cif')[0]
T=np.vstack([np.array([a.coord for a in n if a.element!='H'])
             for ch in pm for n in ch if n.get_resname().strip() in NUC and ch.id=='T'])
def report(mov,tag,span):
    R,t=mat(mov,'chains/4M04_A.pdb',tag)
    st=PDBParser(QUIET=True).get_structure('m',mov)[0]
    ch=list(st)[0]
    print(f'\n--- {mov} Loop1 region {span[0]}-{span[1]} vs Pol mu 4M04 template strand T ---')
    print('res   all-atom  backbone-only')
    for r in ch:
        if r.id[0]!=' ' or r.get_resname() not in t31: continue
        if not (span[0]<=r.id[1]<=span[1]): continue
        A=np.array([a.coord for a in r if a.element!='H']); A=(R@A.T).T+t
        B=np.array([a.coord for a in r if a.get_name() in BB]); B=(R@B.T).T+t
        da=np.linalg.norm(A[:,None]-T[None],axis=-1).min()
        db=np.linalg.norm(B[:,None]-T[None],axis=-1).min()
        flag='  <== steric overlap' if db<3.2 else ('  < vdW' if da<3.2 else '')
        print(f'{t31[r.get_resname()]}{r.id[1]:<4} {da:7.2f}  {db:9.2f}{flag}')
report('chains/4QZB_A.pdb','c1',(378,403))
report('esm/mTdT_cat.pdb','c2',(378,403))
print('\n--- CONTROL: ESM-predicted hPolmu own Loop1 365-387 vs 4M04 template ---')
report('esm/hPolmu_cat.pdb','c3',(363,390))
