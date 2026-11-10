import sys, json, math
sys.path.insert(0, 'bin')
from hmmlib import *

variant = sys.argv[1] if len(sys.argv) > 1 else '.enone'
T = parse_hmm(f'work/TDT{variant}.hmm')
P = parse_hmm(f'work/POLM{variant}.hmm')
stoT, _ = read_stockholm(f'work/refs_on_TDT{variant}.sto')
stoP, _ = read_stockholm(f'work/refs_on_POLM{variant}.sto')

refs = ['mTdT|P09838','hTdT|P04053','bTdT|P06526','hPolmu|Q9NP87','mPolmu|Q9JIW4',
        'hPollam|Q9UGP5','hPolbeta|P06746']
maps = {}
for r in refs:
    rtT, ktrT, insT, nkT, nrT = matchstate_map(stoT[r])
    rtP, ktrP, insP, nkP, nrP = matchstate_map(stoP[r])
    maps[r] = dict(T=(rtT, ktrT, insT), P=(rtP, ktrP, insP), nres=nrT)
    nT_match = sum(1 for v in rtT.values() if v is not None)
    nP_match = sum(1 for v in rtP.values() if v is not None)
    print(f'{r:18s} len={nrT:4d}  on TDT: {nT_match:4d} res in match ({nrT-nT_match} in insert), '
          f'on POLM: {nP_match:4d} res in match ({nrP-nP_match} in insert)')
print(f'\nTDT model LENG={T["leng"]}  POLM model LENG={P["leng"]}  diff={P["leng"]-T["leng"]}')

# model-to-model correspondence via each anchor sequence
def pairs_via(r):
    rtT, _, _ = maps[r]['T']; rtP, _, _ = maps[r]['P']
    out = {}
    for i in sorted(rtT):
        if rtT[i] is not None and rtP.get(i) is not None:
            out[rtT[i]] = rtP[i]
    return out

pm = pairs_via('mTdT|P09838')
pp = pairs_via('hPolmu|Q9NP87')
shared = set(pm) & set(pp)
agree = sum(1 for k in shared if pm[k] == pp[k])
off = {}
for k in shared:
    d = pp[k]-pm[k]; off[d] = off.get(d,0)+1
print(f'\nmodel->model map: via mTdT {len(pm)} pairs, via hPolmu {len(pp)} pairs, '
      f'shared k {len(shared)}, identical k\' {agree} ({100*agree/max(1,len(shared)):.1f}%)')
print('offset histogram (hPolmu-anchored k\' minus mTdT-anchored k\'):',
      dict(sorted(off.items(), key=lambda x:-x[1])[:8]))
json.dump({'via_mTdT':{str(k):v for k,v in pm.items()},
           'via_hPolmu':{str(k):v for k,v in pp.items()}},
          open(f'work/model_pairs{variant}.json','w'))
