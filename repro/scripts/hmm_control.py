import sys, math, json, statistics
sys.path.insert(0,'bin'); from hmmlib import *
MT='mTdT|P09838'
def jsprofile(hA,hB,stoA,stoB,anchor):
    A=parse_hmm(hA); B=parse_hmm(hB)
    sA,_=read_stockholm(stoA); sB,_=read_stockholm(stoB)
    ra,_,_,_,_=matchstate_map(sA[anchor]); rb,_,_,_,_=matchstate_map(sB[anchor])
    out={}
    for i in sorted(ra):
        ka,kb=ra[i],rb.get(i)
        if ka and kb: out[i]=js_div(probs(A['match'][ka]),probs(B['match'][kb]))
    return out
sets={
 'TDT_A vs TDT_B (within-TdT control)': ('work/TDT_A.hmm','work/TDT_B.hmm','work/refs_on_TDT_A.sto','work/refs_on_TDT_B.sto',MT),
 'POLM_A vs POLM_B (within-Polmu control)': ('work/POLM_A.hmm','work/POLM_B.hmm','work/refs_on_POLM_A.sto','work/refs_on_POLM_B.sto','hPolmu|Q9NP87'),
 'TDT_A vs POLM_A (half-size cross)': ('work/TDT_A.hmm','work/POLM_A.hmm','work/refs_on_TDT_A.sto','work/refs_on_POLM_A.sto',MT),
 'TDT vs POLM (full)': ('work/TDT.enone.hmm','work/POLM.enone.hmm','work/refs_on_TDT.enone.sto','work/refs_on_POLM.enone.sto',MT),
}
prof={}
for name,args in sets.items():
    p=jsprofile(*args); prof[name]=p
    v=sorted(p.values()); n=len(v)
    print(f'{name:42s} n={n:4d} mean={statistics.mean(v):.4f} median={v[n//2]:.4f} '
          f'p95={v[int(.95*n)]:.4f} p99={v[int(.99*n)]:.4f} max={max(v):.4f}')
json.dump({k:{str(a):b for a,b in v.items()} for k,v in prof.items()}, open('work/control_profiles.json','w'))
# z-score real signal against within-family control
ctrl=list(prof['TDT_A vs TDT_B (within-TdT control)'].values())+list(prof['POLM_A vs POLM_B (within-Polmu control)'].values())
mu=statistics.mean(ctrl); sd=statistics.pstdev(ctrl)
real=prof['TDT vs POLM (full)']
print(f'\ncontrol (within-family) JS: mean={mu:.4f} sd={sd:.4f}')
z={i:(v-mu)/sd for i,v in real.items()}
W=9
sm={i:statistics.mean([z[j] for j in range(i-W//2,i+W//2+1) if j in z]) for i in z}
top=sorted(sm.items(), key=lambda x:-x[1])[:40]
print('top 9-residue-window mean z (mTdT numbering):')
seen=[];
for i,s in top:
    if any(abs(i-j)<9 for j in seen): continue
    seen.append(i); print(f'  mTdT {i-4}-{i+4}  z={s:.2f}')
    if len(seen)>=10: break
