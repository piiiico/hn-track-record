import json, datetime, statistics as st, math
S2={(s['id'],s['title']):s for s in json.load(open('sample.json'))}
early=[];late=[]
for l in open('pv.jsonl'):
    cid,title,code,v=json.loads(l)
    if code!=200: continue
    s=S2[(cid,title)]; d=datetime.date.fromisoformat(s['day'])
    V=lambda k: v.get((d+datetime.timedelta(days=k)).strftime('%Y%m%d'),0)
    base=st.median([V(k) for k in range(-15,-3)])
    if not (3<=base<=2000): continue
    e0=V(0)-base; e1=V(1)-base
    if e0+e1 < 2*base*0.5 or e0+e1<20: continue   # only clear lifts
    h=datetime.datetime.utcfromtimestamp(s['ts']).hour
    share_d1=max(e1,0)/(max(e0,0)+max(e1,0)+1e-9)
    (early if h<8 else late if h>=18 else []).append(share_d1)
print('clear-lift instances: comment hour 00-07 UTC n=%d median share of excess on day+1 %.2f | hour 18-23 n=%d median %.2f'%(len(early),st.median(early),len(late),st.median(late)))
