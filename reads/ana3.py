# robustness: drop later-half rows whose article the author already linked in the earlier half
exec(open('ana2.py').read().split("# quintiles of earlier")[0].split("for seed in [1,2,3]:")[0])
import random
TT={}
for l in open('pv.jsonl'):
    x=json.loads(l)
S2t={}
pairs=[];rep=0;tot=0
for a,rs in by.items():
    if len(rs)<6: continue
    rs.sort(key=lambda r:r['ts']); h=len(rs)//2
    early=rs[:h]; late=rs[h:]
    et=set(r.get('t') for r in early)
    late2=[r for r in late if r.get('t') not in et]
    tot+=len(late); rep+=len(late)-len(late2)
    if not late2: continue
    pairs.append((st.mean(r['b_lift'] for r in early), st.mean(r['b_lift'] for r in late2)))
print('repeated-title later rows dropped', rep, 'of', tot)
rho=spearman([p[0] for p in pairs],[p[1] for p in pairs]); random.seed(1); B=[]
for _ in range(400):
    s=[random.choice(pairs) for _ in pairs]; B.append(spearman([x[0] for x in s],[x[1] for x in s]))
B.sort(); print('no-repeat rho %.3f CI95 [%.3f,%.3f] authors %d'%(rho,B[10],B[389],len(pairs)))
