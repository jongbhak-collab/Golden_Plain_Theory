import re, numpy as np
al='.abcdefghijk'
lines=open('megabiome_enc.txt').read().strip().split('\n')
base=lines[0][5:]
vals=[]
for c,n in re.findall(r'([.a-k])(\d*)',base): vals += [al.index(c)]*(int(n) if n else 1)
NX,NY=26,29; N=NX*NY
assert len(vals)==N, len(vals)
S=np.zeros((51,N),int); S[0]=vals
for t in range(1,51):
    S[t]=S[t-1]
    body=lines[t].split(':',1)[1]
    if body:
        for tok in body.split(','):
            S[t,int(tok[:-1],36)]=al.index(tok[-1])
w=np.array([(t%7)+1 for t in range(51)])
print('SUM', int((S*w[:,None]).sum()))
MB=(S-1).reshape(51,NY,NX)   # -1 missing; time index 0=50ka ... 50=0ka; rows lat 27..41 (south->north), cols lon 117..129.5
np.save('megabiome_117-129.5E_27-41N_50ka-0ka.npy',MB)
