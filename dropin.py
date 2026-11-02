# Build dropin/ files for the HackerTube data pack + rising.jsonl (Pico, AI agent, 2026-11-02).
# Track record = the note's definition (hit_ana2.py): earlier videos this person was FIRST to link
# (>=100 chars own text), counted before the comment; a hit = one of those that had already reached
# HackerTube's rule (>=3 people, >=3 months) before the comment. Nothing after the comment is used.
import json,glob,collections,datetime,bisect,random,sys,os
HT=sys.argv[1] if len(sys.argv)>1 else 'ht/hackertube-data'
OUT=sys.argv[2] if len(sys.argv)>2 else 'dropin'
os.makedirs(OUT,exist_ok=True)
rows=[]
for f in sorted(glob.glob('yt/*.jsonl')):
  for l in open(f):
    r=json.loads(l)
    if r['author'] and r['ownlen']>=100: rows.append(r)
rows.sort(key=lambda r:(r['ts'],r['id']))
END=rows[-1]['ts']
def mon(ts): return datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%Y-%m')
byv=collections.defaultdict(list)
for r in rows: byv[r['vid']].append(r)
takeoff={}
for v,ms in byv.items():
  A=set();Mo=set()
  for r in ms:
    A.add(r['author']);Mo.add(mon(r['ts']))
    if len(A)>=3 and len(Mo)>=3: takeoff[v]=r['ts'];break
firsts=collections.defaultdict(list)
for v,ms in byv.items(): firsts[ms[0]['author']].append((ms[0]['ts'],v))
for a in firsts: firsts[a].sort()
def record(author,ts,exclude=None):
  n=0;h=0
  for t,v in firsts.get(author,()):
    if t>=ts: break
    if v==exclude: continue
    n+=1
    if v in takeoff and takeoff[v]<ts: h+=1
  return n,h
def tier(n,h):
  if n<5: return 'short'          # fewer than 5 earlier first picks: no record yet
  if h==0: return 'zero'
  return 'scout' if h/n>=0.10 else 'low'
# --- 1. mentions
byid={}
for r in rows: byid[(r['id'],r['vid'])]=r
idts={r['id']:r for r in rows}
out=[];miss=0;tiers=collections.Counter()
for l in open(f'{HT}/mentions.jsonl'):
  m=json.loads(l)
  r=byid.get((m['hn_comment_id'],m['vid'])) or idts.get(m['hn_comment_id'])
  if not r: miss+=1; out.append({'hn_comment_id':m['hn_comment_id'],'vid':m['vid'],'found':False}); continue
  n,h=record(r['author'],r['ts'],exclude=m['vid'])
  t=tier(n,h); tiers[t]+=1
  out.append({'hn_comment_id':m['hn_comment_id'],'vid':m['vid'],'found':True,
              'first_to_link':byv[m['vid']][0]['id']==r['id'],
              'earlier_first_picks':n,'earlier_hits':h,
              'earlier_hit_rate':round(h/n,4) if n else None,'tier':t})
with open(f'{OUT}/trackrecord-mentions.jsonl','w') as o:
  for x in out: o.write(json.dumps(x)+'\n')
print('mentions',len(out),'not found',miss,dict(tiers))
# --- 2. videos
vids=[json.loads(l) for l in open(f'{HT}/videos.jsonl')]
mby=collections.defaultdict(list)
for x in out: mby[x['vid']].append(x)
vt=collections.Counter();vo=[]
for v in vids:
  vid=v['vid'];ms=byv.get(vid)
  rec={'vid':vid,'found':bool(ms)}
  if ms:
    f=ms[0];n,h=record(f['author'],f['ts'],exclude=vid);t=tier(n,h);vt[t]+=1
    rec.update({'first_comment_id':f['id'],'first_month':mon(f['ts']),
      'first_recommender':{'earlier_first_picks':n,'earlier_hits':h,'earlier_hit_rate':round(h/n,4) if n else None,'tier':t},
      'scout_mentions':sum(1 for x in mby[vid] if x.get('tier')=='scout')})
  vo.append(rec)
with open(f'{OUT}/trackrecord-videos.jsonl','w') as o:
  for x in vo: o.write(json.dumps(x)+'\n')
print('videos',len(vo),'found',sum(x['found'] for x in vo),dict(vt),'with>=1 scout mention',sum(1 for x in vo if x.get('scout_mentions')))
# --- 3. rising: first mention 2024-01..end, not yet at the rule, recommender scout tier at the time
lo=datetime.datetime(2024,1,1,tzinfo=datetime.UTC).timestamp()
cand=[];ctrl_pool=[]
for v,ms in byv.items():
  f=ms[0]
  if f['ts']<lo or v in takeoff: continue
  n,h=record(f['author'],f['ts'])
  t=tier(n,h)
  row={'vid':v,'first_comment_id':f['id'],'first_month':mon(f['ts']),'earlier_first_picks':n,'earlier_hits':h,
       'people_so_far':len({r['author'] for r in ms}),'months_so_far':len({mon(r['ts']) for r in ms})}
  if t=='scout': cand.append(row)
  elif t=='zero': ctrl_pool.append(row)
cand.sort(key=lambda r:(r['first_month'],r['first_comment_id']))
# control: same first-month mix, drawn from first picks whose recommender had >=5 earlier first picks and 0 hits
random.seed(20261102)
pm=collections.defaultdict(list)
for r in ctrl_pool: pm[r['first_month']].append(r)
need=collections.Counter(r['first_month'] for r in cand);ctrl=[]
for m,k in sorted(need.items()):
  pool=sorted(pm[m],key=lambda r:r['first_comment_id'])
  ctrl+=random.sample(pool,min(k,len(pool)))
def meta(v):  # optional: YouTube oEmbed title/channel fetched into oe/<vid>.json (null if deleted/private/unembeddable)
  try: j=json.load(open(f'oe/{v}.json')); return {'title':j.get('title'),'channel':j.get('author_name')}
  except Exception: return {'title':None,'channel':None}
with open(f'{OUT}/rising.jsonl','w') as o:
  for r in cand: o.write(json.dumps({**r,**meta(r['vid']),'group':'rising'})+'\n')
  for r in ctrl: o.write(json.dumps({**r,**meta(r['vid']),'group':'control'})+'\n')
print('data ends',datetime.datetime.fromtimestamp(END,datetime.UTC).isoformat())
print('rising',len(cand),'control',len(ctrl),'control pool',len(ctrl_pool))
print('rising already >=2 people',sum(r['people_so_far']>=2 for r in cand),'control',sum(r['people_so_far']>=2 for r in ctrl))
