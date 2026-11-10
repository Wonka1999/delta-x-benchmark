import sys, json, math
sys.path.insert(0,'bin'); from hmmlib import *
V='.enone'
T=parse_hmm(f'work/TDT{V}.hmm'); P=parse_hmm(f'work/POLM{V}.hmm')
stoT,_=read_stockholm(f'work/refs_on_TDT{V}.sto'); stoP,_=read_stockholm(f'work/refs_on_POLM{V}.sto')
MT,MP='mTdT|P09838','hPolmu|Q9NP87'
rtT_m,ktrT_m,insT_m,_,_=matchstate_map(stoT[MT]); rtP_m,ktrP_m,insP_m,_,_=matchstate_map(stoP[MT])
rtT_p,ktrT_p,insT_p,_,_=matchstate_map(stoT[MP]); rtP_p,ktrP_p,insP_p,_,_=matchstate_map(stoP[MP])

print('== A. mTdT residues falling in POLM-model INSERT states (TdT-specific inserts vs Pol mu model) ==')
runs=[];cur=None
for i in sorted(rtP_m):
    if rtP_m[i] is None:
        if cur and i==cur[1]+1: cur=(cur[0],i)
        else:
            if cur: runs.append(cur)
            cur=(i,i)
print(f'{"mTdT span":>14} {"len":>4}  nearest hPolmu res  seq')
if cur: runs.append(cur)
seq=''.join(c for c in stoT[MT] if c not in '.-' ).upper()
# hPolmu residue adjacent (via POLM model state just before the insert)
for a,b in runs:
    kprev = max([rtP_m[j] for j in range(1,a) if rtP_m.get(j)] or [0])
    jp = ktrP_p.get(kprev)
    print(f'{a:6d}-{b:<7d} {b-a+1:4d}  after hPolmu ~{jp}      {seq[a-1:b]}')

print('\n== B. hPolmu residues falling in TDT-model INSERT states (Pol mu-specific vs TdT model) ==')
seqp=''.join(c for c in stoP[MP] if c not in '.-').upper()
runs=[];cur=None
for i in sorted(rtT_p):
    if rtT_p[i] is None:
        if cur and i==cur[1]+1: cur=(cur[0],i)
        else:
            if cur: runs.append(cur)
            cur=(i,i)
if cur: runs.append(cur)
for a,b in runs:
    kprev=max([rtT_p[j] for j in range(1,a) if rtT_p.get(j)] or [0])
    ip=ktrT_m.get(kprev)
    print(f'hPolmu {a:5d}-{b:<6d} {b-a+1:4d}  after mTdT ~{ip}      {seqp[a-1:b]}')

print('\n== C. TDT-model nodes with high M->I probability (family-wide insert hotspots) ==')
for name,M,ktr,ref in (('TDT',T,ktrT_m,'mTdT'),('POLM',P,ktrP_p,'hPolmu')):
    mi=[(math.exp(-M['trans'][k][1]),k) for k in range(1,M['leng']+1)]
    mi.sort(reverse=True)
    print(f'-- {name} model top 12 M->I nodes ({ref} residue) --')
    print('  '+', '.join(f'k{k}({ref}{ktr.get(k)})={p:.3f}' for p,k in mi[:12]))
