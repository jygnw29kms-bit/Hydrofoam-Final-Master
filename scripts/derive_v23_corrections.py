import os, json, statistics
from PIL import Image, ImageFilter
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CMP=os.path.join(ROOT,'comparison','v20')

def tmask(im):
 im=im.convert('RGB');m=Image.new('L',im.size,0);p=im.load();q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y];mx=max(r,g,b);mn=min(r,g,b)
   if (r+g+b)/3<238 or mx-mn>18:q[x,y]=255
 return m.filter(ImageFilter.MedianFilter(5))
def mmask(im):
 im=im.convert('RGB');m=Image.new('L',im.size,0);p=im.load();q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y]
   if r>g*1.25 and r>b*1.35 and r>90:q[x,y]=255
 return m.filter(ImageFilter.MedianFilter(3))
def crop(m):
 b=m.getbbox();return m.crop(b),b
def runs_col(m,x):
 p=m.load();ys=[y for y in range(m.height) if p[x,y]>127]
 if not ys:return []
 rr=[];s=ys[0];last=ys[0]
 for y in ys[1:]:
  if y>last+1:
   if last-s>=2:rr.append((s,last))
   s=y
  last=y
 if last-s>=2:rr.append((s,last))
 return rr
def top_features(m,frac):
 x=min(m.width-1,max(0,round(frac*(m.width-1))));rr=runs_col(m,x);mid=m.height/2
 infos=[{'c':(a+b)/2,'w':b-a+1,'a':a,'b':b} for a,b in rr]
 if not infos:return None
 cen=min(infos,key=lambda z:abs(z['c']-mid))
 ou=[z for z in infos if abs(z['c']-mid)>m.height*.10]
 return {'body_w':cen['w'],'sp_y':statistics.mean([abs(z['c']-mid) for z in ou]) if ou else None,'sp_w':statistics.mean([z['w'] for z in ou]) if ou else None,'env':max(max(abs(z['a']-mid),abs(z['b']-mid)) for z in infos),'n':len(infos)}
def side_height(m,frac):
 x=min(m.width-1,max(0,round(frac*(m.width-1))));rr=runs_col(m,x)
 if not rr:return None
 return max(b for a,b in rr)-min(a for a,b in rr)+1
# target top already rotated by compare script
T,_=crop(tmask(Image.open(os.path.join(CMP,'master_top_crop.png'))))
M,_=crop(mmask(Image.open(os.path.join(ROOT,'renders','v22','assembled_top.png'))))
# physical scale per pixel: both longitudinal bboxes represent 450 mm
st=450.0/T.width; sm=450.0/M.width
ratios={'body':[],'spy':[],'spw':[],'env':[]}
rows=[]
for frac in [i/20 for i in range(2,19)]:
 a=top_features(T,frac);b=top_features(M,frac)
 if not a or not b:continue
 row={'f':frac,'target':a,'model':b}; rows.append(row)
 if a['n']>=3 and b['n']>=3:
  ratios['body'].append((a['body_w']*st)/(b['body_w']*sm))
  if a['sp_y'] and b['sp_y']:ratios['spy'].append((a['sp_y']*st)/(b['sp_y']*sm))
  if a['sp_w'] and b['sp_w']:ratios['spw'].append((a['sp_w']*st)/(b['sp_w']*sm))
 if frac>.58:ratios['env'].append((a['env']*st)/(b['env']*sm))
def med(v,default=1.0):return statistics.median(v) if v else default
# side total vertical profile
TS,_=crop(tmask(Image.open(os.path.join(CMP,'master_side_crop.png'))))
MS,_=crop(mmask(Image.open(os.path.join(ROOT,'renders','v22','assembled_side.png'))))
sts=450.0/TS.width;sms=450.0/MS.width;sr=[]
for frac in [i/20 for i in range(2,18)]:
 a=side_height(TS,frac);b=side_height(MS,frac)
 if a and b:sr.append((a*sts)/(b*sms))
corr={'body_width_scale':max(.82,min(1.18,med(ratios['body']))),'sponson_y_scale':max(.88,min(1.12,med(ratios['spy']))),'sponson_width_scale':max(.82,min(1.18,med(ratios['spw']))),'tail_envelope_scale':max(.85,min(1.15,med(ratios['env']))),'vertical_scale':max(.88,min(1.12,med(sr))),'target_aspect_top':T.height/T.width,'model_aspect_top':M.height/M.width,'target_aspect_side':TS.height/TS.width,'model_aspect_side':MS.height/MS.width,'rows':rows}
out=os.path.join(ROOT,'docs','V23_PROFILE_CORRECTIONS.json');json.dump(corr,open(out,'w'),indent=2)
print(json.dumps({k:v for k,v in corr.items() if k!='rows'},indent=2))