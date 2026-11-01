# Positive control: every HackerTube mention in a month must appear in our extraction (same comment id + video id).
import json,glob,sys
ours=set()
for f in glob.glob('yt/*.jsonl'):
  for l in open(f):
    r=json.loads(l); ours.add((r['id'],r['vid']))
M=[json.loads(l) for l in open('ht/hackertube-data/mentions.jsonl')]
for m in sys.argv[1:] or ['2015-06','2019-03','2023-11']:
  X=[x for x in M if x['month']==m]
  print(m,'HackerTube mentions',len(X),'found',sum((x['hn_comment_id'],x['vid']) in ours for x in X))
