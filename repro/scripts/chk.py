import sys
from Bio.PDB import MMCIFParser, PPBuilder
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
t31={k.upper():v for k,v in _p3.items()}
from Bio import SeqIO
import warnings; warnings.filterwarnings('ignore')
refs={r.id.split('|')[0]:str(r.seq) for r in SeqIO.parse('../refs.fasta','fasta')}
p=MMCIFParser(QUIET=True)
cases=[('4I27','A','mTdT'),('4QZB','A','mTdT'),('5D4B','A','mTdT'),('1JMS','A','mTdT'),
       ('4M04','A','hPolmu'),('4YD1','A','hPolmu'),('4LZD','A','hPolmu'),('2IHM','A','mPolmu'),
       ('6GO5','A','mTdT'),('6GO3','A','mTdT')]
for pid,ch,ref in cases:
    s=p.get_structure(pid,f'pdb/{pid}.cif')[0][ch]
    res=[r for r in s if r.id[0]==' ' and r.get_resname() in t31]
    if not res: print(pid,'no prot'); continue
    nums=[r.id[1] for r in res]
    seq=''.join(t31[r.get_resname()] for r in res)
    R=refs[ref]
    match=sum(1 for n,a in zip(nums,seq) if 1<=n<=len(R) and R[n-1]==a)
    print(f'{pid} ch{ch} vs {ref}: nres={len(res)} auth range {nums[0]}-{nums[-1]} identity-at-authnum={match}/{len(res)} ({100*match/len(res):.1f}%)')
    # report gaps
    gaps=[(nums[i],nums[i+1]) for i in range(len(nums)-1) if nums[i+1]!=nums[i]+1]
    print('   breaks:',gaps)
