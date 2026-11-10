import sys, re, numpy as np, subprocess, os
from Bio.PDB import PDBParser
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
import warnings; warnings.filterwarnings('ignore')
t31={k.upper():v for k,v in _p3.items()}
US='/home/hew/anaconda3/envs/bioflow_usalign/bin/TMalign'

def chain_res(pdb):
    s=PDBParser(QUIET=True).get_structure('x',pdb)[0]
    ch=list(s)[0]
    return [r for r in ch if r.id[0]==' ' and 'CA' in r]

def run(p1,p2,tag):
    mat=f'aln/mat_{tag}.txt'
    out=subprocess.run([US,p1,p2,'-m',mat],capture_output=True,text=True).stdout
    lines=out.splitlines()
    i=[k for k,l in enumerate(lines) if l.startswith('(":" denotes')][0]
    s1,mid,s2=lines[i+1],lines[i+2],lines[i+3]
    # rotation matrix
    M=open(mat).read().splitlines()
    k=[j for j,l in enumerate(M) if l.strip().startswith('m ')][0]
    rows=[list(map(float,M[k+1+j].split()[1:5])) for j in range(3)]
    tvec=np.array([r[0] for r in rows]); R=np.array([r[1:] for r in rows])
    r1,r2=chain_res(p1),chain_res(p2)
    stats=re.search(r'Aligned length=\s*(\d+), RMSD=\s*([\d.]+), Seq_ID=n_identical/n_aligned=\s*([\d.]+)',out)
    tms=re.findall(r'TM-score=\s*([\d.]+)',out)
    i1=i2=0; pairs=[]; gaps1=[]; gaps2=[]
    cur1=[];cur2=[]
    for c1,cm,c2 in zip(s1,mid,s2):
        if c1!='-' and c2!='-':
            A=r1[i1]['CA'].coord; B=r2[i2]['CA'].coord
            d=np.linalg.norm((R@A+tvec)-B)
            pairs.append((r1[i1].id[1],t31[r1[i1].get_resname()],r2[i2].id[1],t31[r2[i2].get_resname()],d))
            if cur1: gaps1.append(cur1); cur1=[]
            if cur2: gaps2.append(cur2); cur2=[]
            i1+=1;i2+=1
        elif c1!='-':
            cur1.append(r1[i1].id[1]); i1+=1
        else:
            cur2.append(r2[i2].id[1]); i2+=1
    if cur1: gaps1.append(cur1)
    if cur2: gaps2.append(cur2)
    return dict(out=out,pairs=pairs,gaps1=gaps1,gaps2=gaps2,stats=stats.groups(),tms=tms,r1=r1,r2=r2)

if __name__=='__main__':
    p1,p2,tag=sys.argv[1],sys.argv[2],sys.argv[3]
    res=run(p1,p2,tag)
    print(f'# {p1} (S1) vs {p2} (S2)   aligned={res["stats"][0]} RMSD={res["stats"][1]} seqid={res["stats"][2]} TM1={res["tms"][0]} TM2={res["tms"][1]}')
    arr=np.array([p[4] for p in res['pairs']])
    print(f'# per-residue CA deviation: mean={arr.mean():.2f} median={np.median(arr):.2f} p90={np.percentile(arr,90):.2f} max={arr.max():.2f}')
    print('# --- S1-only segments (present in S1, no structural counterpart in S2) ---')
    for g in res['gaps1']:
        if len(g)>=1: print(f'   S1 {g[0]}-{g[-1]}  (len {len(g)})')
    print('# --- S2-only segments ---')
    for g in res['gaps2']:
        if len(g)>=1: print(f'   S2 {g[0]}-{g[-1]}  (len {len(g)})')
    print('# --- aligned pairs with CA deviation >= 3.0 A, contiguous runs ---')
    runs=[];cur=[]
    for p in res['pairs']:
        if p[4]>=3.0: cur.append(p)
        else:
            if len(cur)>=2: runs.append(cur)
            cur=[]
    if len(cur)>=2: runs.append(cur)
    for r in runs:
        ds=[x[4] for x in r]
        print(f'   S1 {r[0][0]}-{r[-1][0]} / S2 {r[0][2]}-{r[-1][2]}  len{len(r)}  maxdev={max(ds):.2f} meandev={sum(ds)/len(ds):.2f}')
    with open(f'aln/prof_{tag}.tsv','w') as f:
        f.write('s1_resnum\ts1_aa\ts2_resnum\ts2_aa\tCA_dev_A\n')
        for p in res['pairs']: f.write(f'{p[0]}\t{p[1]}\t{p[2]}\t{p[3]}\t{p[4]:.3f}\n')
    print(f'# profile written: aln/prof_{tag}.tsv')
