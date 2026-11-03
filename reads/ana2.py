# additive backfitting residualisation incl. hour-of-day and weekday (timezone/peak-hour confound)
import json, datetime, math, random, statistics as st, sys
from collections import defaultdict
exec(open('ana.py').read().split("# exposure gradients")[0].replace("print(","(lambda *a,**k:None)("))
for r in rows:
    dt=datetime.datetime.fromtimestamp(r['ts'],datetime.UTC)
    r['f']={'y':r['y'],'rs':qb(r['rs'],rc),'dep':min(r['dep'],4),'del':qb(r['delay'],[0.5,1,2,4,8,24]),'base':qb(r['base'],[10,20,50,100,200,400,1000]),'hr':dt.hour//3,'wk':dt.weekday()>=5,'len':qb(0,[1])}
def backfit(field):
    eff={k:defaultdict(float) for k in rows[0]['f']}
    mu=st.mean(r[field] for r in rows)
    for it in range(15):
        for k in eff:
            acc=defaultdict(list)
            for r in rows:
                pred=mu+sum(eff[j][r['f'][j]] for j in eff if j!=k)
                acc[r['f'][k]].append(r[field]-pred)
            for lv,v in acc.items(): eff[k][lv]=st.mean(v)
    for r in rows: r['b_'+field]=r[field]-mu-sum(eff[j][r['f'][j]] for j in eff)
    return eff
eff=backfit('lift'); backfit('pl')
print('hour-of-day effect (3h buckets UTC):',{k:round(v,2) for k,v in sorted(eff['hr'].items())})
def spearman(x,y):
    def rk(v):
        o=sorted(range(len(v)),key=lambda i:v[i]); R=[0]*len(v)
        for k,i in enumerate(o): R[i]=k
        return R
    a,b=rk(x),rk(y); n=len(a); ma=sum(a)/n; mb=sum(b)/n
    num=sum((a[i]-ma)*(b[i]-mb) for i in range(n)); den=math.sqrt(sum((v-ma)**2 for v in a)*sum((v-mb)**2 for v in b))
    return num/den
by=defaultdict(list)
for r in rows: by[r['a']].append(r)
for seed in [1,2,3]:
  for field in ['b_lift','b_pl']:
    pairs=[]
    for a,rs in by.items():
        if len(rs)<6: continue
        rs.sort(key=lambda r:r['ts']); h=len(rs)//2
        pairs.append((st.mean(r[field] for r in rs[:h]), st.mean(r[field] for r in rs[h:])))
    rho=spearman([p[0] for p in pairs],[p[1] for p in pairs])
    random.seed(seed); B=[]
    for _ in range(400):
        s=[random.choice(pairs) for _ in pairs]; B.append(spearman([x[0] for x in s],[x[1] for x in s]))
    B.sort()
    o=sorted(pairs,key=lambda x:-x[0]); k=max(1,len(o)//10)
    print('seed %d %-6s authors %d rho %.3f CI95 [%.3f,%.3f] later: top10%% %.3f rest %.3f'%(seed,field,len(pairs),rho,B[10],B[389],st.mean(x[1] for x in o[:k]),st.mean(x[1] for x in o[k:])))
# quintiles of earlier-half residual -> later-half residual (and placebo), plus median-based earlier score
for field in ['b_lift','b_pl']:
  for agg in ['mean','median']:
    pairs=[]
    for a,rs in by.items():
        if len(rs)<6: continue
        rs.sort(key=lambda r:r['ts']); h=len(rs)//2
        f=st.mean if agg=='mean' else st.median
        pairs.append((f([r[field] for r in rs[:h]]), st.mean(r[field] for r in rs[h:]), st.median(r['excess'] for r in rs[h:])))
    o=sorted(pairs,key=lambda x:x[0]); n=len(o)
    qs=[o[i*n//5:(i+1)*n//5] for i in range(5)]
    print('%-6s earlier-%-6s quintile -> later mean resid: %s | later median excess views: %s'%(field,agg,' '.join('%.3f'%st.mean(x[1] for x in q) for q in qs),' '.join('%.0f'%st.median(x[2] for x in q) for q in qs)))
