"""Build the two-subfamily input: curated TDT + curated POLM + canonical Pol mu refs."""
from Bio import SeqIO
out = []
for r in SeqIO.parse('TDT.curated.fasta', 'fasta'):
    out.append((r.id, str(r.seq)))
for r in SeqIO.parse('POLM.curated.fasta', 'fasta'):
    out.append((r.id, str(r.seq)))
refs = {r.id.split('|')[0]: str(r.seq) for r in SeqIO.parse('refs.fasta', 'fasta')}
# the curated POLM pull carries non-canonical human/mouse isoforms (A0ACP2AK91 588aa,
# Q5NCI3 511aa); add the canonical accessions the report must be numbered against.
out.append(('POLM|Q9NP87|REFhPolmu', refs['hPolmu']))
out.append(('POLM|Q9JIW4|REFmPolmu', refs['mPolmu']))
with open('msa_axis/combined.fasta', 'w') as f:
    for i, s in out:
        f.write('>%s\n%s\n' % (i, s))
print(len(out))
