import json,urllib.request,concurrent.futures,threading,sys,time
names=[l.strip() for l in open('pop_authors.txt') if l.strip()]
out={}
lock=threading.Lock()
UA={'User-Agent':'Pico/1.0 (AI agent; pico@amdal.dev)'}
def get(u):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20) as r: return json.loads(r.read())
        except Exception as e:
            time.sleep(1+i)
    return 'ERR'
def one(n):
    k=get(f'https://hacker-news.firebaseio.com/v0/user/{n}/karma.json')
    c=get(f'https://hacker-news.firebaseio.com/v0/user/{n}/created.json')
    with lock: out[n]=[k,c]
t0=time.time()
with concurrent.futures.ThreadPoolExecutor(160) as ex:
    for i,_ in enumerate(ex.map(one,names)):
        if i%5000==0: print(i,round(time.time()-t0),flush=True)
json.dump(out,open('karma.json','w'))
err=sum(1 for v in out.values() if v[0]=='ERR' or v[1]=='ERR'); nul=sum(1 for v in out.values() if v[0] is None)
print('done',len(out),'err',err,'null',nul,round(time.time()-t0))
