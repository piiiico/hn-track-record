#!/bin/sh
# $1 = data/YYYY/YYYY-MM.parquet ; output yt/YYYY-MM.jsonl (author, time, vid, ownlen, id)
f="$1"; b=$(basename "$f" .parquet); mkdir -p yt pq
[ -s "yt/$b.done" ] && exit 0
curl -sL -m 120 -A "Pico/1.0 (AI agent; pico@amdal.dev)" -o "pq/$b.parquet" "https://huggingface.co/datasets/open-index/hacker-news/resolve/main/$f" || { echo "$b dl-fail" >> yt/errors.txt; exit 0; }
python3 - "$b" <<'PY'
import duckdb,sys,json
b=sys.argv[1]
q=f"""
with c as (
  select id, "by" as author, time, replace(replace(text,'&#x2F;','/'),'&amp;','&') as t
  from 'pq/{b}.parquet' where type=2 and text is not null and (text like '%youtu%')
)
select id, author, epoch(time) as ts, regexp_extract_all(t, '(?:youtube\\.com/watch\\?(?:[^"\\s<]*?&)?v=|youtu\\.be/|youtube\\.com/embed/)([A-Za-z0-9_-]{{11}})', 1) as vids,
  length(regexp_replace(regexp_replace(t,'<a [^>]*>.*?</a>','','g'),'<[^>]+>','','g')) as ownlen
from c
"""
rows=duckdb.sql(q).fetchall()
n=duckdb.sql(f"select count(*) from 'pq/{b}.parquet' where type=2").fetchall()[0][0]
with open(f'yt/{b}.jsonl','w') as o:
  for id_,a,ts,vids,ol in rows:
    for v in sorted(set(vids or [])):
      o.write(json.dumps({'id':id_,'author':a,'ts':ts,'vid':v,'ownlen':ol})+'\n')
open(f'yt/{b}.done','w').write(f'{n} comments, {len(rows)} yt-comments\n')
PY
rm -f "pq/$b.parquet"
