import os,re,json
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; C=os.path.join(ROOT,'comparison')
vals=[]
for v in ['v20','v21','v22','v23']:
 f=os.path.join(C,v,'score.txt')
 if not os.path.exists(f):continue
 t=open(f).read(); m=re.search(r'mean_iou=([0-9.]+)',t); top=re.search(r'top_iou=([0-9.]+)',t); side=re.search(r'side_iou=([0-9.]+)',t)
 if m:vals.append({'version':v,'mean':float(m.group(1)),'top':float(top.group(1)) if top else 0,'side':float(side.group(1)) if side else 0})
vals.sort(key=lambda x:x['mean'],reverse=True)
if not vals: raise RuntimeError('no scores')
best=vals[0]
open(os.path.join(ROOT,'comparison','best_version.txt'),'w').write(best['version'])
json.dump(vals,open(os.path.join(ROOT,'comparison','scoreboard.json'),'w'),indent=2)
print('BEST',best,'ALL',vals)