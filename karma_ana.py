import json,collections,glob,datetime,random,math
import numpy as np
rng=np.random.default_rng(7); random.seed(7)
exec(open('hit_ana2.py').read().split("obs=strat_rho('disc'")[0])   # pop + disc/ndisc_tries (same code as published run)
K=json.load(open('karma.json'))
NOW=datetime.datetime(2026,11,2,tzinfo=datetime.UTC).timestamp()
ok=[]
for p in pop:
    k,c=K.get(p['author'],[None,None])
    if isinstance(k,(int,float)) and isinstance(c,(int,float)):
        p['karma']=k; p['ten']=max(0,(p['ts']-c)/86400/365.25); p['kpy']=k/max(0.5,(NOW-c)/86400/365.25); ok.append(p)
print('pop',len(pop),'with karma',len(ok),'missing',len(pop)-len(ok))
def srho(key,P,shuffle=False):
    st=collections.defaultdict(list)
    for p in P: st[p['year']].append(p)
    tot=0;w=0
    for y,rs in st.items():
        x=np.array([r[key] for r in rs],float); yy=np.array([r['took'] for r in rs],float)
        if shuffle: rng.shuffle(x)
        if x.std()==0 or yy.std()==0: continue
        rx=np.argsort(np.argsort(x+rng.random(len(x))*1e-9)); # tie-break randomly (ties tiny effect)
        from_ = np.corrcoef(rx,yy)[0,1]
        tot+=from_*len(rs); w+=len(rs)
    return tot/w
def stdrate(key,bf,P):
    yrs=collections.Counter(p['year'] for p in P); out={}
    for b in sorted({bf(p[key]) for p in P}):
        num=den=n=0
        for y,cy in yrs.items():
            g=[p['took'] for p in P if p['year']==y and bf(p[key])==b]
            if len(g)>=20: num+=cy*sum(g)/len(g); den+=cy; n+=len(g)
        out[b]=(n, round(100*num/den,2) if den else None)
    return out
kb=lambda v:0 if v<1000 else (1 if v<5000 else (2 if v<20000 else (3 if v<50000 else 4)))
for key,bf,lab in (('karma',kb,'karma now <1k,1-5k,5-20k,20-50k,50k+'),('kpy',lambda v:0 if v<200 else (1 if v<1000 else (2 if v<3000 else 3)),'karma/yr <200,200-1k,1-3k,3k+'),('ten',lambda v:0 if v<1 else (1 if v<3 else (2 if v<7 else 3)),'tenure at pick')):
    obs=srho(key,ok); null=sorted(srho(key,ok,True) for _ in range(100))
    print(lab,'| rho=%.4f null95=[%.4f,%.4f]'%(obs,null[2],null[97]),stdrate(key,bf,ok))
# correlation karma vs track record in the >=5 subset
sub=[p for p in ok if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
print('sub n',len(sub),'authors',len({p['author'] for p in sub}))
print('karma by prate bucket (median):',{b:int(np.median([p['karma'] for p in sub if (0 if p['prate']==0 else (1 if p['prate']<0.1 else 2))==b])) for b in (0,1,2)})
# MH risk ratio top(>=.1) vs zero, stratified by year x karma-quartile (within sub)
q=np.quantile([p['karma'] for p in sub],[.25,.5,.75])
for p in sub: p['kq']=int(np.searchsorted(q,p['karma']))
def mh(S,strat):
    st=collections.defaultdict(lambda:[0,0,0,0])
    for p in S:
        if p['prate']>=0.1: g=0
        elif p['prate']==0: g=1
        else: continue
        s=st[strat(p)]; s[2*g]+=p['took']; s[2*g+1]+=1
    num=den=0
    for a,n1,c,n0 in st.values():
        N=n1+n0
        if n1 and n0: num+=a*n0/N; den+=c*n1/N
    return num/den if den else float('nan')
byA=collections.defaultdict(list)
for p in sub: byA[p['author']].append(p)
A=list(byA)
for lab,strat in (('year',lambda p:p['year']),('year x karma quartile',lambda p:(p['year'],p['kq']))):
    base=mh(sub,strat); bs=[]
    for _ in range(200):
        S=[p for a in (A[i] for i in rng.integers(0,len(A),len(A))) for p in byA[a]]
        bs.append(mh(S,strat))
    bs=sorted(x for x in bs if x==x)
    print('MH RR top/zero strat by',lab,'= %.2f [%.2f, %.2f]'%(base,bs[5],bs[194]))
# karma effect inside sub, holding prate bucket
print('within sub, karma-quartile rates (year-std):',stdrate('kq',lambda v:v,sub))
# builder ranking: in sub, top 10% per year by karma vs by prate -> takeoff rate
def topdec(S,key):
    st=collections.defaultdict(list)
    for p in S: st[p['year']].append(p)
    sel=[]
    for y,rs in st.items():
        rs=sorted(rs,key=lambda r:(r[key],random.random()),reverse=True); sel+=rs[:max(1,len(rs)//10)]
    return sel
for key in ('karma','prate','kpy'):
    s=topdec(sub,key); print('sub top-10%% by %s: n=%d took=%.2f%% (sub base %.2f%%)'%(key,len(s),100*sum(p['took'] for p in s)/len(s),100*sum(p['took'] for p in sub)/len(sub)))
s=topdec(ok,'karma'); print('ALL top-10%% by karma: n=%d took=%.2f%% (base %.2f%%)'%(len(s),100*sum(p['took'] for p in s)/len(s),100*sum(p['took'] for p in ok)/len(ok)))
