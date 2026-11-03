import os,sys,math
from PIL import Image,ImageChops,ImageFilter,ImageOps,ImageStat
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; ver=sys.argv[1]; OUT=os.path.join(ROOT,'comparison',ver); os.makedirs(OUT,exist_ok=True); REF=os.path.join(ROOT,'reference')
def norm(m,size=(1200,600)):
 b=m.getbbox()
 if not b:return Image.new('L',size,0)
 c=m.crop(b); c.thumbnail((size[0]-20,size[1]-20),Image.Resampling.LANCZOS); o=Image.new('L',size,0);o.paste(c,((size[0]-c.width)//2,(size[1]-c.height)//2));return o
def model(path):
 im=Image.open(path).convert('RGB'); w,h=im.size; samples=[]
 for x,y in [(5,5),(w-6,5),(5,h-6),(w-6,h-6),(w//2,5)]: samples.append(im.getpixel((x,y)))
 bg=tuple(sum(p[i] for p in samples)/len(samples) for i in range(3)); m=Image.new('L',im.size,0); q=m.load(); p=im.load()
 for y in range(h):
  for x in range(w):
   r,g,b=p[x,y]; d=((r-bg[0])**2+(g-bg[1])**2+(b-bg[2])**2)**0.5
   if d>22:q[x,y]=255
 return m.filter(ImageFilter.MedianFilter(3))
def target(path):return Image.open(path).convert('L').point(lambda x:255 if x>127 else 0)
def iou(a,b):
 a=norm(a);b=norm(b); inter=ImageChops.multiply(a,b); union=ImageChops.lighter(a,b); ia=sum(inter.getdata())/255.; ua=sum(union.getdata())/255.; return (ia/ua if ua else 0),a,b
def best(t,m,name):
 cand=[]
 for ang in [0,90,180,270]:
  r=m.rotate(ang,expand=True)
  for flip in [False,True]:
   q=ImageOps.mirror(r) if flip else r; s,a,b=iou(t,q); cand.append((s,ang,flip,a,b))
 s,ang,flip,a,b=max(cand,key=lambda z:z[0]); ov=Image.new('RGB',a.size,(25,25,25));op=ov.load();ap=a.load();bp=b.load()
 for y in range(a.height):
  for x in range(a.width):
   A=ap[x,y]>127;B=bp[x,y]>127;op[x,y]=(245,220,30) if A and B else ((40,220,80) if A else ((240,55,55) if B else (25,25,25)))
 ov.save(os.path.join(OUT,name+'_overlay_v6.png'));return s,ang,flip
rt=model(os.path.join(ROOT,'renders',ver,'assembled_top.png')); rs=model(os.path.join(ROOT,'renders',ver,'assembled_side.png')); tt=target(os.path.join(REF,'final_master_top_mask_v4.png')); ts=target(os.path.join(REF,'final_master_side_mask_v4.png'))
a=best(tt,rt,'top'); b=best(ts,rs,'side'); mean=(a[0]+b[0])/2; open(os.path.join(OUT,'score_v6.txt'),'w').write(f'top_iou={a[0]:.6f} rot={a[1]} flip={a[2]}\nside_iou={b[0]:.6f} rot={b[1]} flip={b[2]}\nmean_iou={mean:.6f}\n'); print(ver,a,b,mean)
