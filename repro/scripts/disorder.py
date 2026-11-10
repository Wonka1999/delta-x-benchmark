import json,urllib.request,sys,collections
ids=sys.argv[2:]; label=sys.argv[1]
q='''query($ids:[String!]!){entries(entry_ids:$ids){rcsb_id
 polymer_entities{rcsb_polymer_entity_container_identifiers{reference_sequence_identifiers{database_accession}}
  polymer_entity_instances{rcsb_polymer_entity_instance_container_identifiers{auth_asym_id}
   rcsb_polymer_instance_feature{type name feature_positions{beg_seq_id end_seq_id}}}}}}'''
def chunks(l,n):
    for i in range(0,len(l),n): yield l[i:i+n]
cov=collections.Counter(); nchain=0
rows=[]
for c in chunks(ids,25):
    req=urllib.request.Request('https://data.rcsb.org/graphql',
      data=json.dumps({'query':q,'variables':{'ids':c}}).encode(),
      headers={'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(req))
    for e in d['data']['entries']:
        for pe in e['polymer_entities']:
            accs=[r['database_accession'] for r in (pe['rcsb_polymer_entity_container_identifiers']['reference_sequence_identifiers'] or [])]
            if label not in accs: continue
            for inst in pe['polymer_entity_instances']:
                feats=inst['rcsb_polymer_instance_feature'] or []
                un=[f for f in feats if f['type']=='UNOBSERVED_RESIDUE_XYZ']
                if not un: continue
                nchain+=1
                segs=[]
                for f in un:
                    for p in f['feature_positions']:
                        b,en=p['beg_seq_id'],p['end_seq_id'] or p['beg_seq_id']
                        segs.append((b,en))
                        for r in range(b,en+1): cov[r]+=1
                rows.append((e['rcsb_id'],inst['rcsb_polymer_entity_instance_container_identifiers']['auth_asym_id'],segs))
print(f'# {label}: {nchain} chains surveyed (coordinates missing per *entity_seq* index, not UniProt)')
# print consensus disordered stretches (>=40% of chains)
thr=0.4*nchain
run=None; out=[]
for r in range(1,max(cov or [1])+2):
    hot = cov[r]>=thr
    if hot and run is None: run=r
    if not hot and run is not None:
        out.append((run,r-1,max(cov[x] for x in range(run,r)))); run=None
for b,e,mx in out:
    if e-b>=2: print(f'   entity_seq {b}-{e} missing in up to {mx}/{nchain} chains ({100*mx/nchain:.0f}%)')
