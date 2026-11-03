import json, datetime, math, random, statistics as st, sys
from collections import defaultdict
S={s['id']:s for s in json.load(open('sample.json'))}
# multiple titles per comment id possible: key by (id,title)
S2={(s['id'],s['title']):s for s in json.load(open('sample.json'))}
rows=[]
for l in open('pv.jsonl'):
    cid,title,code,v=json.loads(l)
    if code!=200: continue
    s=S2.get((cid,title));
    if not s: continue
    d=datetime.date.fromisoformat(s['day'])
    def V(k): return v.get((d+datetime.timedelta(days=k)).strftime('%Y%m%d'),0)
    base=st.median([V(k) for k in range(-15,-3)])
    if not (3<=base<=2000): continue
    resp=V(0)+V(1); plac=V(-3)+V(-2)
    lift=math.log((resp+1)/(2*base+1)); pl=math.log((plac+1)/(2*base+1))
    delay=(s['ts']-s['rts'])/3600 if s['rts'] else 99
    rows.append(dict(t=title,a=s['author'],ts=s['ts'],y=d.year,lift=lift,pl=pl,base=base,rs=s['rscore'] or 0,dep=s['depth'],delay=delay,excess=resp-2*base))
print('eligible rows',len(rows),'authors',len(set(r['a'] for r in rows)))
L=sorted(r['lift'] for r in rows); P=sorted(r['pl'] for r in rows)
q=lambda x,p:x[int(p*(len(x)-1))]
print('lift  median %.3f p75 %.3f p90 %.3f | share>log2 %.3f'%(q(L,.5),q(L,.75),q(L,.9),sum(x>math.log(2) for x in L)/len(L)))
print('placebo median %.3f p75 %.3f p90 %.3f | share>log2 %.3f'%(q(P,.5),q(P,.75),q(P,.9),sum(x>math.log(2) for x in P)/len(P)))
ex=sorted(r['excess'] for r in rows); print('excess views (2d) median %d p75 %d p90 %d p99 %d'%(q(ex,.5),q(ex,.75),q(ex,.9),q(ex,.99)))
def qb(x,cuts):
    for i,c in enumerate(cuts):
        if x<c: return i
    return len(cuts)
rsc=sorted(r['rs'] for r in rows); rc=[q(rsc,.25),q(rsc,.5),q(rsc,.75)]
for r in rows:
    r['cell']=(r['y'], qb(r['rs'],rc), min(r['dep'],3), qb(r['delay'],[1,3,12]), qb(r['base'],[20,100,400]))
# exposure gradients
for name,key in [('root-score quartile',lambda r:qb(r['rs'],rc)),('depth',lambda r:min(r['dep'],3)),('hours after story',lambda r:qb(r['delay'],[1,3,12]))]:
    g=defaultdict(list)
    for r in rows: g[key(r)].append(r['lift'])
    print(name, {k:(len(v),round(st.mean(v),3)) for k,v in sorted(g.items())})
# residualise on cell means (cells with >=5 rows; else coarser)
def resid(field):
    cm=defaultdict(list)
    for r in rows: cm[r['cell']].append(r[field])
    cm2=defaultdict(list)
    for r in rows: cm2[r['cell'][1:4]].append(r[field])
    for r in rows:
        c=cm[r['cell']]
        m=st.mean(c) if len(c)>=5 else st.mean(cm2[r['cell'][1:4]])
        r['r_'+field]=r[field]-m
resid('lift'); resid('pl')
by=defaultdict(list)
for r in rows: by[r['a']].append(r)
def spearman(x,y):
    def rk(v):
        o=sorted(range(len(v)),key=lambda i:v[i]); R=[0]*len(v)
        for k,i in enumerate(o): R[i]=k
        return R
    a,b=rk(x),rk(y); n=len(a); ma=sum(a)/n; mb=sum(b)/n
    num=sum((a[i]-ma)*(b[i]-mb) for i in range(n)); den=math.sqrt(sum((v-ma)**2 for v in a)*sum((v-mb)**2 for v in b))
    return num/den
for field in ['r_lift','r_pl','lift']:
    X=[];Y=[]
    for a,rs in by.items():
        if len(rs)<6: continue
        rs.sort(key=lambda r:r['ts']); h=len(rs)//2
        X.append(st.mean(r[field] for r in rs[:h])); Y.append(st.mean(r[field] for r in rs[h:]))
    rho=spearman(X,Y)
    random.seed(1); nulls=[]
    for _ in range(200):
        Yp=Y[:]; random.shuffle(Yp); nulls.append(spearman(X,Yp))
    nulls.sort()
    # top decile of first half -> second half mean vs rest
    o=sorted(range(len(X)),key=lambda i:-X[i]); k=max(1,len(X)//10)
    top=[Y[i] for i in o[:k]]; rest=[Y[i] for i in o[k:]]
    print('%-7s authors %d  earlier-half vs later-half rho %.3f  null95 [%.3f,%.3f]  later mean: top10%% %.3f vs rest %.3f'%(field,len(X),rho,nulls[5],nulls[194],st.mean(top),st.mean(rest)))
json.dump(rows,open('rows.json','w'))
# --- bootstrap over authors (seeded) for r_lift split-half rho and top-decile gap
seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
pairs=[]
for a,rs in by.items():
    if len(rs)<6: continue
    rs.sort(key=lambda r:r['ts']); h=len(rs)//2
    pairs.append((st.mean(r['r_lift'] for r in rs[:h]), st.mean(r['r_lift'] for r in rs[h:]), st.median(r['excess'] for r in rs[h:]), st.mean(r['r_pl'] for r in rs[:h]), st.mean(r['r_pl'] for r in rs[h:])))
random.seed(seed); B=[];G=[];PB=[]
for _ in range(400):
    s=[random.choice(pairs) for _ in pairs]
    B.append(spearman([x[0] for x in s],[x[1] for x in s]))
    PB.append(spearman([x[3] for x in s],[x[4] for x in s]))
    o=sorted(s,key=lambda x:-x[0]); k=max(1,len(o)//10)
    G.append(st.mean(x[1] for x in o[:k])-st.mean(x[1] for x in o[k:]))
B.sort();G.sort();PB.sort()
o=sorted(pairs,key=lambda x:-x[0]); k=max(1,len(o)//10)
print('seed',seed,'authors',len(pairs),'rho r_lift CI95 [%.3f,%.3f] | placebo rho CI95 [%.3f,%.3f] | top10%% later gap (log) %.3f CI95 [%.3f,%.3f]'%(B[10],B[389],PB[10],PB[389],st.mean(x[1] for x in o[:k])-st.mean(x[1] for x in o[k:]),G[10],G[389]))
print('later-half median excess views: top10%% %.0f vs rest %.0f'%(st.median(x[2] for x in o[:k]), st.median(x[2] for x in o[k:])))
