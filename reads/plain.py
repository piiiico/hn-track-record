exec(open('ana.py').read().split("def qb(")[0].replace("print(","(lambda *a,**k:None)("))
import statistics as st
from collections import defaultdict
g=defaultdict(list)
for r in rows:
    g['top-level' if r['dep']==1 else 'depth2' if r['dep']==2 else 'depth3+'].append(r['excess'])
    g['<3h' if r['delay']<3 else '3-12h' if r['delay']<12 else '>12h'].append(r['excess'])
for k,v in g.items(): print(k, len(v), 'median excess', st.median(v), 'share>=+100', round(sum(x>=100 for x in v)/len(v),3))
print('rows',len(rows),'authors',len(set(r['a'] for r in rows)))
