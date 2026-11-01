import json,collections,random,math
random.seed(5)
pop=json.load(open('hit_pop.json'))
def strat_rate(key,bucketf,P):
  # year-standardized takeoff rate per bucket (direct standardization to overall year mix)
  yrs=collections.Counter(p['year'] for p in P); N=len(P)
  out={}
  for b in sorted({bucketf(p[key]) for p in P}):
    num=0;den=0;n=0
    for y,cy in yrs.items():
      g=[p['took'] for p in P if p['year']==y and bucketf(p[key])==b]
      if len(g)>=20: num+=cy*sum(g)/len(g); den+=cy; n+=len(g)
    out[b]=(n, round(num/den,4) if den else None)
  return out
def rank(a):
  s=sorted(range(len(a)),key=lambda i:a[i]); r=[0]*len(a); i=0
  while i<len(s):
    j=i
    while j+1<len(s) and a[s[j+1]]==a[s[i]]: j+=1
    for k in range(i,j+1): r[s[k]]=(i+j)/2
    i=j+1
  return r
def spear(x,y):
  rx,ry=rank(x),rank(y); n=len(x); mx=sum(rx)/n; my=sum(ry)/n
  num=sum((a-mx)*(b-my) for a,b in zip(rx,ry)); den=math.sqrt(sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))
  return num/den if den else 0
def strat_rho(key,P,ykey='took',shuffle=False):
  st=collections.defaultdict(list)
  for p in P: st[p['year']].append(p)
  tot=0;w=0
  for y,rs in st.items():
    x=[r[key] for r in rs]; yy=[r[ykey] for r in rs]
    if shuffle: random.shuffle(x)
    tot+=spear(x,yy)*len(rs); w+=len(rs)
  return tot/w
import sys
P=pop
for key,bf in (('wins',lambda v:min(v,3)),('prior',lambda v:0 if v==0 else (1 if v<5 else (2 if v<20 else 3))),('ownlen',lambda v:0 if v<200 else (1 if v<400 else (2 if v<800 else 3)))):
  obs=strat_rho(key,P); null=sorted(strat_rho(key,P,shuffle=True) for _ in range(40))
  print(key,'rho=%.4f null[min,max]=[%.4f,%.4f]'%(obs,null[0],null[-1]),strat_rate(key,bf,P))
