import json,collections,random,math,glob,datetime
exec(open('hit_ana.py').read().split('import sys')[0])
# discoveries: prior videos where author was FIRST mentioner and which took off before t0
rows=[]
for f in sorted(glob.glob('yt/*.jsonl')):
  for l in open(f):
    r=json.loads(l)
    if r['author'] and r['ownlen']>=100: rows.append(r)
rows.sort(key=lambda r:(r['ts'],r['id']))
byv=collections.defaultdict(list)
for r in rows: byv[r['vid']].append(r)
def mon(ts): return datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%Y-%m')
takeoff={}
for v,ms in byv.items():
  A=set();Mo=set()
  for r in ms:
    A.add(r['author']);Mo.add(mon(r['ts']))
    if len(A)>=3 and len(Mo)>=3: takeoff[v]=r['ts'];break
firsts=collections.defaultdict(list)  # author -> [(ts_first, vid)]
for v,ms in byv.items(): firsts[ms[0]['author']].append((ms[0]['ts'],v))
for a in firsts: firsts[a].sort()
for p in pop:
  p['disc']=sum(1 for ts,v in firsts[p['author']] if ts<p['ts'] and v in takeoff and takeoff[v]<p['ts'])
  p['ndisc_tries']=sum(1 for ts,v in firsts[p['author']] if ts<p['ts'])
obs=strat_rho('disc',pop); null=sorted(strat_rho('disc',pop,shuffle=True) for _ in range(40))
print('disc rho=%.4f null=[%.4f,%.4f]'%(obs,null[0],null[-1]),strat_rate('disc',lambda v:min(v,3),pop))
# discovery hit-rate among authors with >=5 prior first-mentions: their prior hit rate vs next
sub=[p for p in pop if p['ndisc_tries']>=5]
for p in sub: p['prate']=p['disc']/p['ndisc_tries']
obs=strat_rho('prate',sub); null=sorted(strat_rho('prate',sub,shuffle=True) for _ in range(40))
print('prior discovery hit-rate (authors with>=5 prior first-mentions, n=%d) rho=%.4f null=[%.4f,%.4f]'%(len(sub),obs,null[0],null[-1]),
      strat_rate('prate',lambda v:0 if v==0 else (1 if v<0.1 else 2),sub))
# tenure on sample
sv=set(json.load(open('samp_vids.json')))
S=[p for p in pop if p['v'] in sv]
ok=[]
for p in S:
  try: u=json.load(open(f"users/{p['author']}.json"))
  except Exception: u=None
  if u and 'created' in u:
    p['ten']=max(0,(p['ts']-u['created'])/86400/365.25); ok.append(p)
print('tenure sample',len(S),'with user',len(ok))
obs=strat_rho('ten',ok); null=sorted(strat_rho('ten',ok,shuffle=True) for _ in range(200))
print('tenure rho=%.4f null95=[%.4f,%.4f]'%(obs,null[5],null[194]),strat_rate('ten',lambda v:0 if v<1 else (1 if v<3 else (2 if v<7 else 3)),ok))
