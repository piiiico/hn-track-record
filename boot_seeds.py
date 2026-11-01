# Seeded author-cluster bootstrap (1000 reps) of the raw rate ratio top(>=0.1) vs zero; usage: python3 boot_seeds.py SEED
import sys,random,collections
exec(open('hit_ana2.py').read().split("obs=strat_rho('disc'")[0])
random.seed(int(sys.argv[1]))
sub=[p for p in pop if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
byA=collections.defaultdict(list)
for p in sub: byA[p['author']].append(p)
A=list(byA)
def rr(S):
  t=[p['took'] for a in S for p in byA[a] if p['prate']>=0.1]; z=[p['took'] for a in S for p in byA[a] if p['prate']==0]
  return (sum(t)/len(t))/(sum(z)/len(z)) if t and z and sum(z) else None
bs=sorted(x for x in (rr([random.choice(A) for _ in A]) for _ in range(1000)) if x)
print('seed',sys.argv[1],'RR=%.3f 95%%=[%.3f,%.3f] reps=%d authors=%d'%(rr(A),bs[int(.025*len(bs))],bs[int(.975*len(bs))-1],len(bs),len(A)))
