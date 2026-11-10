import json,urllib.request,sys
ids=sys.argv[1:]
q='''query($ids:[String!]!){entries(entry_ids:$ids){
 rcsb_id
 rcsb_entry_info{resolution_combined polymer_entity_count_protein polymer_entity_count_nucleic_acid polymer_composition}
 struct{title}
 polymer_entities{rcsb_id entity_poly{rcsb_entity_polymer_type rcsb_sample_sequence_length}
  rcsb_polymer_entity_container_identifiers{auth_asym_ids reference_sequence_identifiers{database_accession database_name}}
  rcsb_polymer_entity_align{reference_database_accession aligned_regions{entity_beg_seq_id ref_beg_seq_id length}}}
}}'''
req=urllib.request.Request('https://data.rcsb.org/graphql',
 data=json.dumps({'query':q,'variables':{'ids':ids}}).encode(),
 headers={'Content-Type':'application/json'})
d=json.load(urllib.request.urlopen(req))
for e in d['data']['entries']:
    ei=e['rcsb_entry_info']
    print(e['rcsb_id'], 'res=',ei['resolution_combined'],'NA_ent=',ei['polymer_entity_count_nucleic_acid'],'|',ei['polymer_composition'],'|',e['struct']['title'][:85])
    for pe in e['polymer_entities']:
        ids_=pe['rcsb_polymer_entity_container_identifiers']
        acc=[r['database_accession'] for r in (ids_['reference_sequence_identifiers'] or [])]
        al=pe['rcsb_polymer_entity_align'] or []
        regs=[(a['reference_database_accession'],[(r['entity_beg_seq_id'],r['ref_beg_seq_id'],r['length']) for r in a['aligned_regions']]) for a in al]
        print('   ',pe['rcsb_id'],pe['entity_poly']['rcsb_entity_polymer_type'],'len',pe['entity_poly']['rcsb_sample_sequence_length'],'ch',ids_['auth_asym_ids'],acc,regs)
