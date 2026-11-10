import sys, json, statistics
sys.path.insert(0,'bin'); from hmmlib import *
from Bio import SeqIO
from Bio.Align import PairwiseAligner, substitution_matrices
S={r.id:str(r.seq) for r in SeqIO.parse('refs.fasta','fasta')}
m,p=S['mTdT|P09838'],S['hPolmu|Q9NP87']
al=PairwiseAligner(); al.substitution_matrix=substitution_matrices.load('BLOSUM62')
al.open_gap_score=-11; al.extend_gap_score=-1; al.mode='global'
b=next(iter(al.align(m,p))).aligned
pw={}
for (ms,me),(ps,pe) in zip(b[0],b[1]):
    for o in range(me-ms): pw[ms+o+1]=ps+o+1

T=parse_hmm('work/TDT.enone.hmm'); P=parse_hmm('work/POLM.enone.hmm')
sT,_=read_stockholm('work/refs_on_TDT.enone.sto'); sP,_=read_stockholm('work/refs_on_POLM.enone.sto')
rtT_m,_,_,_,_=matchstate_map(sT['mTdT|P09838']); rtP_m,_,_,_,_=matchstate_map(sP['mTdT|P09838'])
_,ktrT_p,_,_,_=matchstate_map(sT['hPolmu|Q9NP87']); _,ktrP_p,_,_,_=matchstate_map(sP['hPolmu|Q9NP87'])
viaT={i:ktrT_p[rtT_m[i]] for i in rtT_m if rtT_m[i] and ktrT_p.get(rtT_m[i])}
viaP={i:ktrP_p[rtP_m[i]] for i in rtP_m if rtP_m[i] and ktrP_p.get(rtP_m[i])}
allm=set(viaT)|set(viaP)|set(pw)
agree3=sum(1 for i in allm if viaT.get(i)==viaP.get(i)==pw.get(i) and pw.get(i))
print(f'3-way coordinate agreement (HMM-via-TDT / HMM-via-POLM / pairwise): '
      f'{agree3}/{len(allm)} = {100*agree3/len(allm):.1f}%')

rows=json.load(open('work/percol.enone.json'))['rows']
JS={r['mtdt_res']:r['js'] for r in rows if r['js'] is not None}
db={r['mtdt_res']:r['dbits'] for r in json.load(open('work/dbits.json'))}
MU,SD=0.0426,0.0335
TOTB=sum(db.values())

REG=[('Loop1 / template-strand groove insert',378,403),
     ('pre-Loop1 helix (thumb)',364,377),
     ('fingers segment',275,288),
     ('palm/8-kDa boundary segment',219,243),
     ('N-terminal BRCT-proximal extension',5,20),
     ('BRCT-catalytic linker',135,152),
     ('Loop2 / C-terminal segment',414,422),
     ('8-kDa domain segment',88,100),
     ('C-terminal helix',469,483)]
print(f'\n{"region":40s} {"mTdT":>9} {"hPolmu(3-route)":>22} {"meanJS":>7} {"meanZ":>6} {"maxZ":>6} {"%bits":>6} {"map-agree":>9}')
for name,a,bb in REG:
    js=[JS[i] for i in range(a,bb+1) if i in JS]
    zz=[(v-MU)/SD for v in js]
    bits=sum(db.get(i,0) for i in range(a,bb+1))
    cand=[]
    for src in (viaT,viaP,pw):
        hs=[src[i] for i in range(a,bb+1) if i in src]
        cand.append((min(hs),max(hs)) if hs else None)
    ag=sum(1 for i in range(a,bb+1) if viaT.get(i)==viaP.get(i)==pw.get(i) and pw.get(i))
    n=bb-a+1
    lo=min(c[0] for c in cand if c); hi=max(c[1] for c in cand if c)
    print(f'{name:40s} {a:4d}-{bb:<4d} {str(lo)+"-"+str(hi):>22} {statistics.mean(js):7.3f} '
          f'{statistics.mean(zz):6.1f} {max(zz):6.1f} {100*bits/TOTB:5.1f}% {ag}/{n}')
    print(f'{"":40s} routes: viaTDT={cand[0]} viaPOLM={cand[1]} pairwise={cand[2]}')

# localized model-length difference
print('\nLocalized model-length difference (TDT match states vs POLM match states over same span):')
for name,a,bb in REG:
    kT=[rtT_m[i] for i in range(a,bb+1) if rtT_m.get(i)]
    kP=[rtP_m[i] for i in range(a,bb+1) if rtP_m.get(i)]
    if not kT or not kP: continue
    lT=max(kT)-min(kT)+1; lP=max(kP)-min(kP)+1
    print(f'  {name:40s} TDT {lT:3d} states, POLM {lP:3d} states, diff {lP-lT:+d}')
