exec(open('hit_ana2.py').read().split("obs=strat_rho('disc'")[0])
sub=[p for p in pop if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
obs=strat_rho('prate',sub); null=sorted(strat_rho('prate',sub,shuffle=True) for _ in range(200))
print('prate rho=%.4f null95=[%.4f,%.4f] max=%.4f'%(obs,null[5],null[194],null[-1]))
# author-cluster bootstrap of rate ratio top(>=0.1) vs zero bucket (unstandardized)
byA=collections.defaultdict(list)
for p in sub: byA[p['author']].append(p)
A=list(byA)
def rr(sample):
  t=[p['took'] for a in sample for p in byA[a] if p['prate']>=0.1]; z=[p['took'] for a in sample for p in byA[a] if p['prate']==0]
  return (sum(t)/len(t))/(sum(z)/len(z)) if t and z and sum(z) else None
base=rr(A); bs=sorted(x for x in (rr([random.choice(A) for _ in A]) for _ in range(200)) if x)
print('rate ratio top/zero=%.2f author-bootstrap 95%%=[%.2f,%.2f] authors=%d'%(base,bs[5],bs[194],len(A)))
print('top bucket n=%d authors=%d'%(sum(1 for p in sub if p['prate']>=0.1),len({p['author'] for p in sub if p['prate']>=0.1})))
