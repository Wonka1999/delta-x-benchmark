import sys, numpy as np
from Bio.PDB import MMCIFParser
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
import warnings; warnings.filterwarnings('ignore')
t31={k.upper():v for k,v in _p3.items()}
NUC={'DA','DT','DG','DC','DU','A','T','G','C','U'}
pid,pch=sys.argv[1],sys.argv[2]
m=MMCIFParser(QUIET=True).get_structure('x',f'pdb/{pid}.cif')[0]
prot=[r for r in m[pch] if r.id[0]==' ' and r.get_resname() in t31]
nucch={}
for ch in m:
    nr=[r for r in ch if r.get_resname().strip() in NUC]
    if nr: nucch[ch.id]=nr
print(f'## {pid} chain {pch}: {len(prot)} aa; nucleic chains: ' + ', '.join(f'{c}({len(v)}nt)' for c,v in nucch.items()))
hits={}
for ch,nr in nucch.items():
    for r in prot:
        pa=np.array([a.coord for a in r if a.element!='H'])
        for n in nr:
            na=np.array([a.coord for a in n if a.element!='H'])
            d=np.linalg.norm(pa[:,None,:]-na[None,:,:],axis=-1).min()
            if d<=4.0:
                hits.setdefault(r.id[1],[]).append((ch,n.id[1],n.get_resname(),round(float(d),2)))
for k in sorted(hits):
    aa=t31[[r for r in prot if r.id[1]==k][0].get_resname()]
    print(f'  {aa}{k}: ' + '; '.join(f'{c}:{rn}{ri}@{d}A' for c,ri,rn,d in sorted(hits[k],key=lambda x:x[3])[:4]))
print('  CONTACT_SET=',sorted(hits))
