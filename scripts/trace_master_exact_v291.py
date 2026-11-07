from PIL import Image
import os,json,math
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
im=Image.open(os.path.join(R,'reference','final_master_top_mask_exact.png')).convert('L').resize((243,215),Image.Resampling.LANCZOS)
w,h=im.size;p=im.load()
S={(x,y) for y in range(h) for x in range(w) if p[x,y]>135}
edges={}
def edge(p,q):edges.setdefault(p,[]).append(q)
for x,y in S:
 if (x,y-1) not in S:edge((x,y),(x+1,y))
 if (x+1,y) not in S:edge((x+1,y),(x+1,y+1))
 if (x,y+1) not in S:edge((x+1,y+1),(x,y+1))
 if (x-1,y) not in S:edge((x,y+1),(x,y))
paths=[]
while edges:
 start=next(iter(edges));q=start;arr=[q]
 for i in range(50000):
  a=edges[q].pop()
  if not edges[q]:del edges[q]
  q=a
  if q==start:break
  arr.append(q)
 paths.append(arr)
path=max(paths,key=len)
def distance(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy+1e-8)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def simplify(q):
 def rd(q):
  if len(q)<=2:return q
  i=max(range(1,len(q)-1),key=lambda i:distance(q[i],q[0],q[-1]))
  if distance(q[i],q[0],q[-1])<=.65:return [q[0],q[-1]]
  return rd(q[:i+1])[:-1]+rd(q[i:])
 return rd(q+[q[0]])[:-1]
path=simplify(path)
X=[-225,-202.6,-180.1,-157.7,-135.2,-112.8,-90.3,-67.9,-45.4,-23,0,23,45.4,67.9,90.3,112.8,135.2,157.7,180.1,202.6,225]
HW=[5.3,24.6,33.1,141.1,148.6,152.9,159.3,164.6,168.9,173.2,177.4,180.6,183.8,198.8,220.2,238.4,239.4,184.9,183.8,184.9,183.8]
def interp(x,xx,yy):
 for i in range(len(xx)-1):
  if xx[i]<=x<=xx[i+1]:
   t=(x-xx[i])/(xx[i+1]-xx[i]);return yy[i]*(1-t)+yy[i+1]*t
 return yy[0] if x<xx[0] else yy[-1]
# enforce master-measured widths against contour at each fore-aft image row
rowmax={}
for a,b in path:rowmax[b]=max(rowmax.get(b,0),abs(a-121.25))
rows=sorted(rowmax)
def rawhalf(y):
 if y<=rows[0]:return rowmax[rows[0]]
 if y>=rows[-1]:return rowmax[rows[-1]]
 for a,b in zip(rows,rows[1:]):
  if a<=y<=b:return rowmax[a]+(rowmax[b]-rowmax[a])*(y-a)/(b-a)
 return 1
world=[]
for px,py in path:
 x=-225+450*py/198
 yy=(px-121.25)
 half=interp(x,X,HW)
 y=yy*480/226
 world.append((max(-225,min(225,x)),y))
json.dump({'source':'final_master_top_mask_exact.png','derived_from':'original master ortho mask','contour':world},open(os.path.join(R,'reference','top_exact_traced_outline_v291.json'),'w'),indent=1)
print('EXACT_TRACE',len(world),'bounds',min(p[0] for p in world),max(p[0] for p in world),min(p[1] for p in world),max(p[1] for p in world))
