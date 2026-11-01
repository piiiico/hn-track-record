import json,glob,collections,random,math,datetime,duckdb
random.seed(3)
# first-mention comment id per video (same filters as hit_prep)
rows=[]
for f in sorted(glob.glob('yt/*.jsonl')):
  for l in open(f):
    r=json.loads(l)
    if r['author'] and r['ownlen']>=100: rows.append(r)
rows.sort(key=lambda r:(r['ts'],r['id']))
firstid={}
for r in rows:
  if r['vid'] not in firstid: firstid[r['vid']]=r['id']
pop=json.load(open('hit_pop.json'))
ids=sorted({firstid[p['v']] for p in pop})
con=duckdb.connect()
con.sql("create table items as select * from read_parquet('idx/*.parquet')")
con.sql("create table seeds(cid uinteger)")
con.executemany("insert into seeds values (?)",[(i,) for i in ids])
q="""
with recursive anc(cid, cur, depth) as (
  select s.cid, i.parent, 1 from seeds s join items i on i.id=s.cid
  union all
  select a.cid, i.parent, a.depth+1 from anc a join items i on i.id=a.cur where i.type<>1 and a.depth<60 and i.parent is not null
)
select a.cid, a.cur as root, i.score, a.depth from anc a join items i on i.id=a.cur where i.type=1
"""
res=con.sql(q).fetchall()
root={cid:(rt,sc,d) for cid,rt,sc,d in res}
print('seeds',len(ids),'resolved to story',len(root))
for p in pop:
  x=root.get(firstid[p['v']]); p['rscore']=x[1] if x and x[1] is not None else None; p['depth']=x[2] if x else None
json.dump(pop,open('hit_pop_root.json','w'))
