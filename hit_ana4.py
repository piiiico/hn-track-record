exec(open('hit_ana2.py').read().split("obs=strat_rho('disc'")[0])
sub=[p for p in pop if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
for name,f in (('zero',lambda p:p['prate']==0),('mid(0,0.1)',lambda p:0<p['prate']<0.1),('top>=0.1',lambda p:p['prate']>=0.1)):
  g=[p['took'] for p in sub if f(p)]; print(name,len(g),'raw rate %.4f'%(sum(g)/len(g)))
g=[p['took'] for p in pop]; print('all',len(g),'%.4f'%(sum(g)/len(g)))
