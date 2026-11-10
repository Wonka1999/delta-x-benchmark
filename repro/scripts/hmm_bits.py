import sys, math, json, csv, statistics
sys.path.insert(0,'bin'); from hmmlib import *
T=parse_hmm('work/TDT.enone.hmm'); P=parse_hmm('work/POLM.enone.hmm')
aT,_=read_stockholm('work/all_on_TDT.sto'); aP,_=read_stockholm('work/all_on_POLM.sto')
MT,MP='mTdT|P09838','hPolmu|Q9NP87'
# anchor: mTdT residue -> kT, kP ; hPolmu residue via POLM model
rtT_m,_,_,_,_=matchstate_map(aT[MT]); rtP_m,_,_,_,_=matchstate_map(aP[MT])
_,ktrT_p,_,_,_=matchstate_map(aT[MP]); _,ktrP_p,_,_,_=matchstate_map(aP[MP])

tdt=[n for n in aT if n.startswith('TDT|')]; pol=[n for n in aT if n.startswith('POLM|')]
print(f'{len(tdt)} TdT seqs, {len(pol)} Pol mu seqs')
# per-sequence residue->k maps
mapsT={n:matchstate_map(aT[n])[1] for n in tdt+pol}   # k_to_res
mapsP={n:matchstate_map(aP[n])[1] for n in tdt+pol}
rawT={n:''.join(c for c in aT[n] if c not in '.-').upper() for n in tdt+pol}

lpT={k:[(-x)/math.log(2) for x in T['match'][k]] for k in T['match']}   # log2 prob
lpP={k:[(-x)/math.log(2) for x in P['match'][k]] for k in P['match']}
AAI={a:i for i,a in enumerate(AA)}

rows=[]; tot=0.0
for i in sorted(rtT_m):
    kT=rtT_m[i]; kP=rtP_m[i]
    if not kT or not kP: continue
    def grp(names):
        v=[]
        for n in names:
            rT=mapsT[n].get(kT); rP=mapsP[n].get(kP)
            if not rT or not rP: continue
            a=rawT[n][rT-1]
            if a not in AAI: continue
            v.append(lpT[kT][AAI[a]]-lpP[kP][AAI[a]])
        return v
    vt=grp(tdt); vp=grp(pol)
    if len(vt)<50 or len(vp)<30: continue
    d=statistics.mean(vt)-statistics.mean(vp)
    tot+=d
    rows.append(dict(mtdt_res=i, hpolmu_res=ktrP_p.get(kP), kT=kT, kP=kP,
                     dbits=d, nT=len(vt), nP=len(vp),
                     aa_tdt=rawT[MT][i-1] if i<=len(rawT.get(MT,'')) else None))
print(f'positions scored: {len(rows)}   total discriminating bits = {tot:.1f}')
json.dump(rows, open('work/dbits.json','w'))
rows2=sorted(rows,key=lambda r:-r['dbits'])
cum=0; 
for frac in (0.25,0.5,0.75,0.9):
    s=0;n=0
    for r in rows2:
        s+=r['dbits']; n+=1
        if s>=frac*tot: break
    print(f'  {frac*100:.0f}% of discriminating bits carried by top {n} positions ({100*n/len(rows):.1f}% of scored positions)')
