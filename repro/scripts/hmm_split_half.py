import random, sys, os
random.seed(20251105)
def rd(p):
    out=[];n=None;s=[]
    for l in open(p):
        if l.startswith('>'):
            if n: out.append((n,''.join(s)))
            n=l.strip();s=[]
        else: s.append(l.strip())
    out.append((n,''.join(s))); return out
for fam,src in (('TDT','TDT.curated.fasta'),('POLM','POLM.curated.fasta')):
    rs=rd(src); random.shuffle(rs); h=len(rs)//2
    for tag,sub in (('A',rs[:h]),('B',rs[h:])):
        with open(f'work/{fam}_{tag}.fasta','w') as f:
            for n,s in sub: f.write(n+'\n'+s+'\n')
        print(fam,tag,len(sub))
