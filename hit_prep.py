import json,glob,collections,random
random.seed(11)
rows=[]
for f in sorted(glob.glob('yt/*.jsonl')):
  for l in open(f):
    r=json.loads(l)
    if r['author'] and r['ownlen']>=100: rows.append(r)
rows.sort(key=lambda r:(r['ts'],r['id']))
print('mentions(ownlen>=100)',len(rows))
byv=collections.defaultdict(list)
for r in rows: byv[r['vid']].append(r)
# takeoff time: first time the video satisfies >=3 distinct authors AND >=3 distinct months
import datetime
def mon(ts): return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m')
takeoff={}
for v,ms in byv.items():
  A=set();Mo=set()
  for r in ms:
    A.add(r['author']);Mo.add(mon(r['ts']))
    if len(A)>=3 and len(Mo)>=3: takeoff[v]=r['ts'];break
print('videos',len(byv),'took off',len(takeoff))
# author histories
hist=collections.defaultdict(list)
for r in rows: hist[r['author']].append(r)
pop=[]
for v,ms in byv.items():
  f=ms[0]; y=int(mon(f['ts'])[:4])
  if y<2010 or y>2023: continue
  prior=[r for r in hist[f['author']] if r['ts']<f['ts'] and r['vid']!=v]
  pv={r['vid'] for r in prior}
  known_wins=sum(1 for pvid in pv if pvid in takeoff and takeoff[pvid]<f['ts'])
  later_auth={r['author'] for r in ms[1:] if r['author']!=f['author']}
  pop.append(dict(v=v,author=f['author'],ts=f['ts'],year=y,ownlen=f['ownlen'],prior=len(pv),wins=known_wins,
                  took=1 if v in takeoff else 0,later=len(later_auth)))
print('population (first mention 2010-2023)',len(pop),'takeoff rate %.4f'%(sum(p['took'] for p in pop)/len(pop)))
json.dump(pop,open('hit_pop.json','w'))
samp=random.sample(pop,min(9000,len(pop)))
auth=sorted({p['author'] for p in samp})
open('samp_authors.txt','w').write('\n'.join(a for a in auth if a)+'\n')
json.dump([p['v'] for p in samp],open('samp_vids.json','w'))
print('sample',len(samp),'authors',len(auth))
