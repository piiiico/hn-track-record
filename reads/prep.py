import duckdb, json, glob, re, urllib.parse, time
t0=time.time()
con=duckdb.connect('wk.duckdb')
con.sql("create or replace table inst as select * from read_json_auto('out/*.jsonl')")
print('inst', con.sql("select count(*) from inst").fetchall(), time.time()-t0)
con.sql("create or replace table idx as select id,parent,type,score,ts,url from read_parquet('out/*.idx.parquet')")
print('idx', con.sql("select count(*) from idx").fetchall(), time.time()-t0)
# normalise article titles in python
rows=con.sql("select distinct art from inst").fetchall()
def norm(a):
    t=urllib.parse.unquote(a).replace(' ','_')
    while t and t[-1] in '.,;:' : t=t[:-1]
    if t.endswith(')') and t.count('(')<t.count(')'): t=t[:-1]
    if re.match(r'^(File|Special|Category|Talk|Wikipedia|Help|Portal|Template|User|Image|Draft|Module|MediaWiki|Book|List_of)[:_]',t,re.I) and not t.lower().startswith('list_of'): return None
    if ':' in t.split('_')[0] and not t.lower().startswith('list_of'): return None
    if not t or len(t)>200: return None
    return t
m=[(a,norm(a)) for (a,) in rows]
import json as _j
with open('artmap.jsonl','w') as f:
    for a,t in m: f.write(_j.dumps({'art':a,'title':t})+'\n')
con.sql("create or replace table artmap as select * from read_json('artmap.jsonl', columns={'art':'VARCHAR','title':'VARCHAR'})")
con.sql("create or replace table inst2 as select i.*, m.title, cast(to_timestamp(i.ts) as date) as day from inst i join artmap m using(art) where m.title is not null")
print('inst2', con.sql("select count(*), count(distinct title), count(distinct author) from inst2").fetchall(), time.time()-t0)
# root resolution
con.sql("create or replace table walk as select id as cid, parent as node, 1 as depth from inst2 group by id, parent")
for k in range(40):
    con.sql("""create or replace table walk as
      select w.cid, case when x.type=1 then x.id when x.id is null then -1 else x.parent end as node,
             w.depth + case when x.type=1 or x.id is null then 0 else 1 end as depth,
             (x.type=1 or x.id is null) as done
      from walk w left join idx x on x.id=w.node""")
    nd=con.sql("select count(*) from walk where not done").fetchall()[0][0]
    con.sql("create or replace table walk as select cid,node,depth from walk")
    if nd==0: break
print('walk iters',k, time.time()-t0)
con.sql("create or replace table roots as select w.cid, w.depth, x.id as root, x.score as rscore, x.ts as rts, x.url as rurl from walk w left join idx x on x.id=w.node and x.type=1")
print('roots', con.sql("select count(*), count(root), median(rscore) from roots").fetchall(), time.time()-t0)
