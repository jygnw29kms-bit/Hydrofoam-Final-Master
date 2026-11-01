import os,json,statistics
from PIL import Image,ImageFilter
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; version=open(os.path.join(ROOT,'comparison','best_version.txt')).read().strip(); CMP=os.path.join(ROOT,'comparison','v20')
def tm(im):
 im=im.convert('RGB');m=Image.new('L',im.size,0);p=im.load();q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y];mx=max(r,g,b);mn=min(r,g,b)
   if (r+g+b)/3<238 or mx-mn>18:q[x,y]=255
 return m.filter(ImageFilter.MedianFilter(5))
def mm(im):
 im=im.convert('RGB');m=Image.new('L',im.size,0);p=im.load();q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y]
   if r>g*1.25 and r>b*1.35 and r>90:q[x,y]=255
 return m.filter(ImageFilter.MedianFilter(3))
def cr(m):
 b=m.getbbox();return m.crop(b)
def runs(m,x):
 p=m.load();ys=[y for y in range(m.height) if p[x,y]>127];rr=[]
 if not ys:return rr
 s=last=ys[0]
 for y in ys[1:]:
  if y>last+1:
   if last-s>=2:rr.append((s,last))
   s=y
  last=y
 if last-s>=2:rr.append((s,last))
 return rr
def feat(m,f):
 x=min(m.width-1,max(0,round(f*(m.width-1))));rr=runs(m,x);mid=m.height/2
 if not rr:return None
 I=[((a+b)/2,b-a+1,a,b) for a,b in rr];c=min(I,key=lambda z:abs(z[0]-mid));o=[z for z in I if abs(z[0]-mid)>m.height*.1]
 return {'body':c[1],'spy':statistics.mean([abs(z[0]-mid) for z in o]) if o else None,'spw':statistics.mean([z[1] for z in o]) if o else None,'env':max(max(abs(z[2]-mid),abs(z[3]-mid)) for z in I),'n':len(I)}
T=cr(tm(Image.open(os.path.join(CMP,'master_top_crop.png'))));M=cr(mm(Image.open(os.path.join(ROOT,'renders',version,'assembled_top.png'))));st=450/T.width;sm=450/M.width
R={k:[] for k in ['body','spy','spw','env']}
for f in [i/24 for i in range(2,23)]:
 a=feat(T,f);b=feat(M,f)
 if not a or not b:continue
 if a['n']>=3 and b['n']>=3:
  R['body'].append((a['body']*st)/(b['body']*sm))
  if a['spy'] and b['spy']:R['spy'].append((a['spy']*st)/(b['spy']*sm))
  if a['spw'] and b['spw']:R['spw'].append((a['spw']*st)/(b['spw']*sm))
 if f>.55:R['env'].append((a['env']*st)/(b['env']*sm))
def med(v):return statistics.median(v) if v else 1
corr={'base_version':version,'body_width_scale':max(.92,min(1.08,med(R['body']))),'sponson_y_scale':max(.94,min(1.06,med(R['spy']))),'sponson_width_scale':max(.92,min(1.08,med(R['spw']))),'tail_envelope_scale':max(.93,min(1.07,med(R['env'])))}
json.dump(corr,open(os.path.join(ROOT,'docs','V24_PROFILE_CORRECTIONS.json'),'w'),indent=2);print(corr)