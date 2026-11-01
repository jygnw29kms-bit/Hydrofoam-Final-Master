import os,json,statistics
from PIL import Image,ImageFilter
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; best=open(os.path.join(ROOT,'comparison','best_version.txt')).read().strip(); CMP=os.path.join(ROOT,'comparison','v20')
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
def crop(m): return m.crop(m.getbbox())
def runs(m,f):
 x=min(m.width-1,max(0,round(f*(m.width-1))));p=m.load();ys=[y for y in range(m.height) if p[x,y]>127]
 if not ys:return []
 rr=[];s=l=ys[0]
 for y in ys[1:]:
  if y>l+1:
   if l-s>=2:rr.append((s,l))
   s=y
  l=y
 if l-s>=2:rr.append((s,l))
 return rr
def feat(m,f):
 rr=runs(m,f);mid=m.height/2
 if not rr:return None
 I=[((a+b)/2,b-a+1,a,b) for a,b in rr];c=min(I,key=lambda z:abs(z[0]-mid));o=[z for z in I if abs(z[0]-mid)>m.height*.10]
 return {'body':c[1],'spy':statistics.mean([abs(z[0]-mid) for z in o]) if o else None,'spw':statistics.mean([z[1] for z in o]) if o else None,'env':max(max(abs(z[2]-mid),abs(z[3]-mid)) for z in I),'n':len(I)}
def sideh(m,f):
 rr=runs(m,f)
 if not rr:return None
 return max(b for a,b in rr)-min(a for a,b in rr)+1
T=crop(tmask(Image.open(os.path.join(CMP,'master_top_crop.png'))));M=crop(mmask(Image.open(os.path.join(ROOT,'renders',best,'assembled_top.png'))));Ts=crop(tmask(Image.open(os.path.join(CMP,'master_side_crop.png'))));Ms=crop(mmask(Image.open(os.path.join(ROOT,'renders',best,'assembled_side.png'))))
st=450/T.width;sm=450/M.width;sts=450/Ts.width;sms=450/Ms.width
rows=[]
for i in range(31):
 f=i/30;a=feat(T,f);b=feat(M,f); shT=sideh(Ts,f);shM=sideh(Ms,f)
 r={'body':1,'spy':1,'spw':1,'env':1,'vert':1}
 if a and b:
  if a['n']>=1 and b['n']>=1:r['env']=max(.90,min(1.10,(a['env']*st)/(b['env']*sm)))
  if a['n']>=3 and b['n']>=3:
   r['body']=max(.90,min(1.10,(a['body']*st)/(b['body']*sm)))
   if a['spy'] and b['spy']:r['spy']=max(.94,min(1.06,(a['spy']*st)/(b['spy']*sm)))
   if a['spw'] and b['spw']:r['spw']=max(.90,min(1.10,(a['spw']*st)/(b['spw']*sm)))
 if shT and shM:r['vert']=max(.92,min(1.08,(shT*sts)/(shM*sms)))
 rows.append(r)
# smooth ratios; missing/default 1 values retained but softened toward neighbors
def smooth(k):
 v=[r[k] for r in rows];return [sum(v[max(0,i-1):min(31,i+2)])/len(v[max(0,i-1):min(31,i+2)]) for i in range(31)]
out={'base_version':best,'body':[round(x,5) for x in smooth('body')],'spy':[round(x,5) for x in smooth('spy')],'spw':[round(x,5) for x in smooth('spw')],'env':[round(x,5) for x in smooth('env')],'vert':[round(x,5) for x in smooth('vert')]}
json.dump(out,open(os.path.join(ROOT,'docs','V26_STATION_CORRECTIONS.json'),'w'),indent=2);print('V26_CORRECTIONS_FROM',best)
