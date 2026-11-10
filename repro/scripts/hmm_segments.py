import sys, json, statistics
rows=json.load(open(sys.argv[1]))['rows']
W=int(sys.argv[2]) if len(sys.argv)>2 else 9
js={r['mtdt_res']:r['js'] for r in rows if r['js'] is not None}
idx=sorted(js)
# sliding window mean over mTdT residue numbering
sm={}
for i in idx:
    w=[js[j] for j in range(i-W//2,i+W//2+1) if j in js]
    sm[i]=sum(w)/len(w)
vals=sorted(sm.values()); n=len(vals)
thr=vals[int(0.90*n)]
print(f'window={W}  smoothed JS p90 threshold={thr:.4f}  (global mean {statistics.mean(vals):.4f})')
# contiguous runs above threshold
runs=[];cur=None
for i in idx:
    if sm[i]>=thr:
        if cur and i-cur[1]<=3: cur=(cur[0],i)
        else:
            if cur: runs.append(cur)
            cur=(i,i)
    else:
        if cur and i-cur[1]>3: runs.append(cur); cur=None
if cur: runs.append(cur)
hp={r['mtdt_res']:r['hpolmu_res'] for r in rows}
aa={r['mtdt_res']:r['mtdt_aa'] for r in rows}
print(f'\n{len(runs)} runs above p90 (merged across <=3 gaps):')
print(f'{"mTdT span":>14} {"len":>4} {"hPolmu span":>14} {"meanJS":>7} {"maxJS":>7}  seq(mTdT)')
tot=0
for a,b in sorted(runs, key=lambda x:-max(sm[j] for j in idx if x[0]<=j<=x[1])):
    sub=[js[j] for j in idx if a<=j<=b]
    hs=[hp[j] for j in range(a,b+1) if hp.get(j)]
    s=''.join(aa.get(j,'?') for j in range(a,b+1))
    tot+=b-a+1
    print(f'{a:6d}-{b:<7d} {b-a+1:4d} {(str(min(hs))+"-"+str(max(hs))) if hs else "n/a":>14} '
          f'{sum(sub)/len(sub):7.3f} {max(sub):7.3f}  {s}')
print(f'\ntotal residues in runs: {tot} / {len(idx)} ({100*tot/len(idx):.1f}%)')
