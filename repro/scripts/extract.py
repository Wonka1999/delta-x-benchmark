from Bio.PDB import MMCIFParser, PDBIO, Select
from Bio.Data.IUPACData import protein_letters_3to1 as _p3
import warnings; warnings.filterwarnings('ignore')
t31={k.upper():v for k,v in _p3.items()}
p=MMCIFParser(QUIET=True)
class Prot(Select):
    def __init__(s,ch): s.ch=ch
    def accept_chain(s,c): return c.id==s.ch
    def accept_residue(s,r): return r.id[0]==' ' and r.get_resname() in t31
    def accept_atom(s,a): return a.element!='H' and (a.get_altloc() in (' ','A'))
io=PDBIO()
for pid,ch in [('4QZB','A'),('4M04','A'),('1JMS','A'),('4LZD','A'),('4I27','A'),('4YD1','A'),('2IHM','A'),('6GO5','A'),('5D4B','A')]:
    s=p.get_structure(pid,f'pdb/{pid}.cif')
    io.set_structure(s[0]); io.save(f'chains/{pid}_{ch}.pdb', Prot(ch))
    print(pid,ch,'ok')
