exec(open('karma_ana.py').read().split("kb=lambda")[0])
import sys
seed=int(sys.argv[1]); rng=np.random.default_rng(seed); random.seed(seed)
sub=[p for p in ok if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
def topdec_ids(S,key):
    st=collections.defaultdict(list)
    for p in S: st[p['year']].append(p)
    sel=set()
    for y,rs in st.items():
        rs=sorted(rs,key=lambda r:(r[key],random.random()),reverse=True)
        for r in rs[:max(1,len(rs)//10)]: sel.add(id(r))
    return sel
def ratio_boot(S,key):
    sel=topdec_ids(S,key)
    byA=collections.defaultdict(list)
    for p in S: byA[p['author']].append(p)
    A=list(byA)
    def r(ix):
        t=n=tt=nn=0
        for i in ix:
            for p in byA[A[i]]:
                tt+=p['took']; nn+=1
                if id(p) in sel: t+=p['took']; n+=1
        return (t/n)/(tt/nn) if n and tt else float('nan')
    base=r(range(len(A))); bs=sorted(x for x in (r(rng.integers(0,len(A),len(A))) for _ in range(200)) if x==x)
    return base,bs[5],bs[194],len(sel)
for lab,S,key in (('ALL top10 karma',ok,'karma'),('ALL top10 tenure',ok,'ten'),('SUB top10 karma',sub,'karma'),('SUB top10 prate',sub,'prate')):
    b,lo,hi,n=ratio_boot(S,key); print(seed,lab,'n=%d ratio-to-base=%.2f [%.2f, %.2f]'%(n,b,lo,hi),flush=True)
