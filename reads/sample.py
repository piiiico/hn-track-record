import duckdb, random, json
con=duckdb.connect('wk.duckdb')
# stories linking a wikipedia article
con.sql("""create or replace table wstory as
 select id, cast(to_timestamp(ts) as date) as day, regexp_extract(replace(url,'%28','('), 'wikipedia\\.org/wiki/([^#?]+)',1) as t, score
 from idx where type=1 and url like '%wikipedia.org/wiki/%'""")
con.sql("""create or replace table e as
 select i.id, i.author, i.ts, i.day, i.title, i.ownlen, r.depth, r.root, r.rscore, r.rts, r.rurl
 from inst2 i join roots r on r.cid=i.id
 where i.day >= date '2015-08-01' and i.day <= date '2023-12-29' and r.root is not null and i.author is not null""")
print(con.sql("select count(*) from e").fetchall())
# collisions: other comment instances of same title within +-3 days
con.sql("""create or replace table e2 as
 select e.* from e
 where not exists (select 1 from inst2 j where j.title=e.title and j.id<>e.id and abs(datediff('day', j.day, e.day))<=3)
   and not exists (select 1 from wstory s where lower(replace(s.t,' ','_'))=lower(e.title) and abs(datediff('day', s.day, e.day))<=3)
   and (e.rurl is null or position(lower(e.title) in lower(replace(e.rurl,' ','_')))=0)""")
print(con.sql("select count(*), count(distinct author) from e2").fetchall())
a=con.sql("select author, count(*) n from e2 group by author having count(*)>=8").fetchall()
print('authors>=8', len(a))
random.seed(1103)
authors=[x for x,_ in a]; random.shuffle(authors)
authors=set(authors[:2200])
rows=con.sql("select id,author,ts,cast(day as varchar),title,ownlen,depth,root,rscore,rts from e2").fetchall()
by={}
for r in rows:
    if r[1] in authors: by.setdefault(r[1],[]).append(r)
out=[]
for au,rs in by.items():
    rs.sort(key=lambda r:r[2])
    pick=sorted(random.sample(range(len(rs)), min(8,len(rs))))
    for k in pick:
        r=rs[k]; out.append(dict(id=r[0],author=r[1],ts=r[2],day=r[3],title=r[4],ownlen=r[5],depth=r[6],root=r[7],rscore=r[8],rts=r[9]))
json.dump(out, open('sample.json','w'))
print('sample', len(out), len(by))
