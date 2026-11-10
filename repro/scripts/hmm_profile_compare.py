import sys, math, json, csv
sys.path.insert(0,'bin')
from hmmlib import *

V = sys.argv[1] if len(sys.argv)>1 else '.enone'
T = parse_hmm(f'work/TDT{V}.hmm'); P = parse_hmm(f'work/POLM{V}.hmm')
stoT,_ = read_stockholm(f'work/refs_on_TDT{V}.sto'); stoP,_ = read_stockholm(f'work/refs_on_POLM{V}.sto')
MT, MP = 'mTdT|P09838', 'hPolmu|Q9NP87'

rtT_m, ktrT_m, insT_m, _, _ = matchstate_map(stoT[MT])   # mTdT on TDT model
rtP_m, ktrP_m, insP_m, _, _ = matchstate_map(stoP[MT])   # mTdT on POLM model
rtT_p, ktrT_p, insT_p, _, _ = matchstate_map(stoT[MP])   # hPolmu on TDT model
rtP_p, ktrP_p, insP_p, _, _ = matchstate_map(stoP[MP])   # hPolmu on POLM model

# residue-level cross-species correspondence, two independent routes
via_T = {}   # mTdT i -> hPolmu j  through TDT model
for i,k in rtT_m.items():
    if k is not None and ktrT_p.get(k):
        via_T[i] = ktrT_p[k]
via_P = {}   # through POLM model
for i,k in rtP_m.items():
    if k is not None and ktrP_p.get(k):
        via_P[i] = ktrP_p[k]
both = set(via_T)&set(via_P)
ident = sum(1 for i in both if via_T[i]==via_P[i])
print(f'mTdT<->hPolmu residue correspondence: via TDT model {len(via_T)}, via POLM model {len(via_P)}, '
      f'both {len(both)}, agreeing {ident} ({100*ident/len(both):.1f}%)')

# consensus correspondence: prefer agreement
corr = {i: via_T[i] for i in both if via_T[i]==via_P[i]}

rows=[]
for i in sorted(rtT_m):
    kT = rtT_m[i]; kP = rtP_m[i]
    pT = probs(T['match'][kT]) if kT else None
    pP = probs(P['match'][kP]) if kP else None
    js = js_div(pT,pP) if (pT and pP) else None
    rows.append(dict(
        mtdt_res=i, mtdt_aa=stoT[MT].replace('.','').replace('-','')[i-1].upper(),
        kT=kT, kP=kP,
        hpolmu_res=corr.get(i) or via_T.get(i) or via_P.get(i),
        corr_agree = 'both' if i in corr else ('T' if i in via_T else ('P' if i in via_P else 'none')),
        icT=info_content(pT) if pT else None,
        icP=info_content(pP) if pP else None,
        js=js,
        mi_T = math.exp(-T['trans'][kT][1]) if kT else None,   # M->I at TDT node
        mi_P = math.exp(-P['trans'][kP][1]) if kP else None,
    ))
with open('work/percol'+V+'.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

jsv=[(r['js'],r) for r in rows if r['js'] is not None]
js_only=[x[0] for x in jsv]
js_only_s=sorted(js_only)
n=len(js_only)
import statistics
print(f'\nPaired match positions with JS defined: {n} of {len(rows)} mTdT residues')
print(f'JS divergence (bits): mean={statistics.mean(js_only):.4f} median={statistics.median(js_only):.4f} '
      f'p90={js_only_s[int(.9*n)]:.4f} p95={js_only_s[int(.95*n)]:.4f} p99={js_only_s[int(.99*n)]:.4f} max={max(js_only):.4f}')
print(f'mTdT residues in TDT-model insert (no kT): {sum(1 for r in rows if r["kT"] is None)}')
print(f'mTdT residues in POLM-model insert (no kP): {sum(1 for r in rows if r["kP"] is None)}')
json.dump({'rows':rows}, open('work/percol'+V+'.json','w'))
