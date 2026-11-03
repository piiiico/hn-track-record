#!/bin/sh
f="$1"; b=$(basename "$f" .parquet); mkdir -p out pq
[ -s "out/$b.done" ] && exit 0
curl -sL -m 240 -A "Pico/1.0 (AI agent operated by Hakon Amdal; pico@amdal.dev)" -o "pq/$b.parquet" "https://huggingface.co/datasets/open-index/hacker-news/resolve/main/$f" || { echo "$b dl-fail" >> out/errors.txt; exit 0; }
python3 - "$b" <<'PY'
import duckdb,sys,json
b=sys.argv[1]
q=f"""
with c as (
  select id, "by" as author, time, parent, replace(replace(text,'&#x2F;','/'),'&amp;','&') as t
  from 'pq/{b}.parquet' where type=2 and text is not null and text like '%wikipedia.org%'
)
select id, author, epoch(time) as ts, parent, regexp_extract_all(t, 'href="https?://en\\.(?:m\\.)?wikipedia\\.org/wiki/([^"#?]+)', 1) as arts,
  length(regexp_replace(regexp_replace(t,'<a [^>]*>.*?</a>','','g'),'<[^>]+>','','g')) as ownlen
from c
"""
rows=duckdb.sql(q).fetchall()
with open(f'out/{b}.jsonl','w') as o:
  for id_,a,ts,par,arts,ol in rows:
    for v in sorted(set(arts or [])):
      o.write(json.dumps({'id':id_,'author':a,'ts':ts,'parent':par,'art':v,'ownlen':ol})+'\n')
duckdb.sql(f"COPY (select id, parent, type, score, epoch(time) as ts, url from 'pq/{b}.parquet') TO 'out/{b}.idx.parquet' (FORMAT parquet)")
n=duckdb.sql(f"select count(*) from 'pq/{b}.parquet' where type=2").fetchall()[0][0]
open(f'out/{b}.done','w').write(f'{n} comments, {len(rows)} wiki-comments\n')
PY
rm -f "pq/$b.parquet"
