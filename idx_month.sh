#!/bin/sh
f="$1"; b=$(basename "$f" .parquet); mkdir -p idx pq2
[ -s "idx/$b.parquet" ] && exit 0
curl -sL -m 180 -A "Pico/1.0 (AI agent; pico@amdal.dev)" -o "pq2/$b.parquet" "https://huggingface.co/datasets/open-index/hacker-news/resolve/main/$f" || { echo "$b dl-fail" >> idx/errors.txt; exit 0; }
python3 -c "
import duckdb
duckdb.sql(\"COPY (select id, parent, type, score from 'pq2/$b.parquet') TO 'idx/$b.parquet' (FORMAT parquet)\")
" || echo "$b copy-fail" >> idx/errors.txt
rm -f "pq2/$b.parquet"
