import json,collections,random,statistics
import sys; random.seed(int(sys.argv[1]))
pop=json.load(open('hit_pop_root.json'))
# recompute prate (same as hit_ana2) by importing disc fields: recompute quickly
exec(open('hit_ana2.py').read().split("obs=strat_rho('disc'")[0].replace("pop=json.load(open('hit_pop.json'))","pop=json.load(open('hit_pop_root.json'))"))
random.seed(int(sys.argv[1]))
R={q['v']:q.get('rscore') for q in json.load(open('hit_pop_root.json'))}
for p in pop: p['rscore']=R.get(p['v'])
P=[p for p in pop if p.get('rscore') is not None]
print('with root score',len(P),'of',len(pop))
# takeoff by root-score quartile
qs=statistics.quantiles([p['rscore'] for p in P],n=4); print('root score quartiles',qs)
def rq(s): return 0 if s<=qs[0] else (1 if s<=qs[1] else (2 if s<=qs[2] else 3))
for b in range(4):
  g=[p['took'] for p in P if rq(p['rscore'])==b]; print('rootQ',b,len(g),'takeoff %.4f'%(sum(g)/len(g)))
sub=[p for p in P if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
top=[p for p in sub if p['prate']>=0.1]; zero=[p for p in sub if p['prate']==0]
print('median root score: top %s zero %s all %s'%(statistics.median(p['rscore'] for p in top),statistics.median(p['rscore'] for p in zero),statistics.median(p['rscore'] for p in P)))
# stratified (year x root quartile) rate ratio top vs zero, direct standardization to zero-bucket mix
cells=collections.defaultdict(lambda:[[],[]])
for p in top: cells[(p['year'],rq(p['rscore']))][0].append(p['took'])
for p in zero: cells[(p['year'],rq(p['rscore']))][1].append(p['took'])
def mh(cells):
  num=0;den=0
  for k,(t,z) in cells.items():
    if not t or not z: continue
    n=len(t)+len(z); a=sum(t); b=len(t)-a; c=sum(z); d=len(z)-c
    num+=a*len(z)/n; den+=c*len(t)/n
  return num/den if den else None
print('Mantel-Haenszel risk ratio top vs zero, strata year x rootQ: %.3f'%mh(cells))
# author-cluster bootstrap of MH RR
byA=collections.defaultdict(list)
for p in top+zero: byA[p['author']].append(p)
A=list(byA); bs=[]
for _ in range(1000):
  cs=collections.defaultdict(lambda:[[],[]])
  for a in (random.choice(A) for _ in A):
    for p in byA[a]:
      cs[(p['year'],rq(p['rscore']))][0 if p['prate']>=0.1 else 1].append(p['took'])
  r=mh(cs); 
  if r: bs.append(r)
bs.sort(); print('bootstrap 95%% [%.3f, %.3f]'%(bs[int(.025*len(bs))],bs[int(.975*len(bs))-1]))
# unadjusted MH with year only for comparison
c2=collections.defaultdict(lambda:[[],[]])
for p in top: c2[p['year']][0].append(p['took'])
for p in zero: c2[p['year']][1].append(p['took'])
print('MH RR year-only: %.3f'%mh(c2))
