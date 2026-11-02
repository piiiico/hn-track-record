# Positive control: the dropin's record() must reproduce the note's 1.44x on 2010-2023 first picks.
exec(open('dropin.py').read().split('# --- 1. mentions')[0])
c=collections.Counter();k=collections.Counter()
for v,ms in byv.items():
  f=ms[0];y=int(mon(f['ts'])[:4])
  if y<2010 or y>2023: continue
  n,h=record(f['author'],f['ts']);t=tier(n,h);c[t]+=1;k[t]+=v in takeoff
for t in c: print(t,c[t],round(k[t]/c[t],4))
print('scout/zero',round((k['scout']/c['scout'])/(k['zero']/c['zero']),3))
