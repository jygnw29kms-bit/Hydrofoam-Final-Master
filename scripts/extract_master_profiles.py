from PIL import Image
import json, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
ref=os.path.join(ROOT,'reference')
top=Image.open(os.path.join(ref,'final_master_top_mask_v3.png')).convert('L'); tb=top.getbbox(); tp=top.load()
side=Image.open(os.path.join(ref,'final_master_side_mask_v3.png')).convert('L'); sb=side.getbbox(); sp=side.load()
N=81
prof=[]
for i in range(N):
 t=i/(N-1)
 yy=round(tb[1]+t*(tb[3]-tb[1]-1)); xs=[x for x in range(tb[0],tb[2]) if tp[x,yy]>127]
 if xs: l=min(xs); r=max(xs)
 else: l=r=(tb[0]+tb[2])//2
 xx=round(sb[0]+t*(sb[2]-sb[0]-1)); ys=[y for y in range(sb[1],sb[3]) if sp[xx,y]>127]
 if ys: ztop=(sb[3]-1-min(ys))/(sb[3]-sb[1]-1); zbot=(sb[3]-1-max(ys))/(sb[3]-sb[1]-1)
 else: ztop=.45; zbot=.25
 prof.append({'t':t,'left':(l-(tb[0]+tb[2]-1)/2)/(tb[2]-tb[0]-1),'right':(r-(tb[0]+tb[2]-1)/2)/(tb[2]-tb[0]-1),'ztop':ztop,'zbot':zbot})
json.dump({'profiles':prof},open(os.path.join(ref,'master_profiles_v3.json'),'w'),indent=2)
print('PROFILE_READY',len(prof))
