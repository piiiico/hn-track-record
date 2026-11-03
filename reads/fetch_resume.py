import json, urllib.request, urllib.parse, datetime, concurrent.futures as cf, time, sys
S=json.load(open('sample.json'))
S.sort(key=lambda s:s['author'])
import random
random.seed(7)
au=sorted(set(x['author'] for x in S)); random.shuffle(au); rank={a:i for i,a in enumerate(au)}
S.sort(key=lambda s:(rank[s['author']],s['ts']))
import os
done=set()
if os.path.exists('pv.jsonl'):
    for l in open('pv.jsonl'):
        try: x=json.loads(l); done.add((x[0],x[1]))
        except Exception: pass
S=[s for s in S if (s['id'],s['title']) not in done]
print('remaining',len(S),flush=True)
OUT=open('pv.jsonl','a')
UA="Pico/1.0 (AI agent operated by Hakon Amdal; pico@amdal.dev) hn-reads-study"
def get(s):
    d=datetime.date.fromisoformat(s['day'])
    a=(d-datetime.timedelta(days=15)).strftime('%Y%m%d'); b=(d+datetime.timedelta(days=1)).strftime('%Y%m%d')
    t=urllib.parse.quote(s['title'],safe='')
    u=f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{t}/daily/{a}/{b}"
    for k in range(6):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=30)
            items=json.load(r)['items']
            return s['id'],s['title'],200,{i['timestamp'][:8]:i['views'] for i in items}
        except urllib.error.HTTPError as e:
            if e.code==404: return s['id'],s['title'],404,{}
            if e.code==429: time.sleep(1.5+k*2); continue
            return s['id'],s['title'],e.code,{}
        except Exception as e:
            time.sleep(1)
    return s['id'],s['title'],-1,{}
t0=time.time(); res=[]
with cf.ThreadPoolExecutor(8) as ex:
    for i,r in enumerate(ex.map(get,S)):
        res.append(r); OUT.write(json.dumps(r)+'\n'); OUT.flush()
        if i%500==0: print(i, time.time()-t0, flush=True)

from collections import Counter
print(Counter(r[2] for r in res), time.time()-t0)
