from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v25_station_fit.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('v25_parts','v27_parts').replace('v25_STATION_FIT','v27_SIDE_IMAGE_FIT').replace('V25_IMAGE_MEASUREMENTS','V27_IMAGE_MEASUREMENTS').replace('V25_PART_AUDIT','V27_PART_AUDIT').replace('V25_SAVED','V27_SAVED').replace('Hydrofoam_Final_Master_v25','Hydrofoam_Final_Master_v27')
# insert side-mask extraction after top target setup
anchor="mask=target_mask(top); bb=mask.getbbox()"
insert="""mask=target_mask(top); bb=mask.getbbox()
# side orthographic target -> exact upper/lower silhouette curves
side=Image.open(os.path.join(CMP,'master_side_crop.png')).convert('RGB')
smask=target_mask(side); sbb=smask.getbbox(); smask=smask.crop(sbb); SW,SH=smask.size; spix=smask.load(); SS=450.0/max(1,SW-1)
side_top=[]; side_bottom=[]
for i in range(31):
 sx=round(i*(SW-1)/30); ys=[yy for yy in range(SH) if spix[sx,yy]>127]
 if ys:
  topy=min(ys); boty=max(ys); side_top.append(8+(SH-1-topy)*SS); side_bottom.append(8+(SH-1-boty)*SS)
 else:
  side_top.append(None); side_bottom.append(None)
def fill_side(v,default):
 known=[i for i,x in enumerate(v) if x is not None]; out=[]
 for i,x in enumerate(v):
  if x is not None: out.append(x); continue
  lo=max([k for k in known if k<i],default=None); hi=min([k for k in known if k>i],default=None)
  if lo is None and hi is None: out.append(default)
  elif lo is None: out.append(v[hi])
  elif hi is None: out.append(v[lo])
  else:
   t=(i-lo)/(hi-lo); out.append(v[lo]*(1-t)+v[hi]*t)
 return out
side_top=fill_side(side_top,70); side_bottom=fill_side(side_bottom,8)
"""
s=s.replace(anchor,insert)
# replace body height formula in the station loop
old="h=(8 + 39*math.sin(math.pi*min(max(x/365.0,0),1))**0.78)*VSC[i]\n z=31+h*.18\n bodysec.append((x,0,z,w,h))"
new="""# master side profile: subtract canopy bubble from body top in canopy zone
 target_top=side_top[i]; target_bottom=side_bottom[i]
 canopy_bump=18.0*math.exp(-((x-140.0)/75.0)**2)
 body_top=target_top-canopy_bump
 body_bottom=target_bottom+10.0
 h=max(6.0,(body_top-body_bottom))*VSC[i]
 z=(body_top+body_bottom)/2.0
 bodysec.append((x,0,z,w,h))"""
if old not in s: raise RuntimeError('body formula anchor missing')
s=s.replace(old,new)
# replace sponson center/height formula
old2="h=max(7,38*max(.28,taper)**.55)*VSC[i]; sec.append((x,sgn*spy[i],29,w,h))"
new2="h=max(7,38*max(.28,taper)**.55)*VSC[i]; bottom=side_bottom[i]+1.0; z=bottom+h/2.0; sec.append((x,sgn*spy[i],z,w,h))"
if old2 not in s: raise RuntimeError('sponson anchor missing')
s=s.replace(old2,new2)
# fin apex uses side master top profile at x~405
s=s.replace("App.Vector(403,y,135)","App.Vector(403,y,max(112,side_top[27]))").replace("App.Vector(402,y,136)","App.Vector(402,y,max(112,side_top[27]))")
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v27_side_image_fit.py').write_text(s,encoding='utf-8')
print('PATCHED_V27')