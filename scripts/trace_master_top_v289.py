from PIL import Image
import os,json,math
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
im=Image.open(os.path.join(R,'reference','final_master_top_mask_v4.png')).convert('L')
# uniform 2x sampling removes thumbnail-scale artifacts and keeps silhouette corners
im=im.resize((260,228),Image.Resampling.LANCZOS)
w,h=im.size
pixels=im.load()
a={(x,y) for y in range(h) for x in range(w) if pixels[x,y]>=130}
# Directed boundary edges clockwise around filled squares
edges={}
def edge(p,q):edges.setdefault(p,[]).append(q)
for x,y in a:
 if (x,y-1) not in a:edge((x,y),(x+1,y))
 if (x+1,y) not in a:edge((x+1,y),(x+1,y+1))
 if (x,y+1) not in a:edge((x+1,y+1),(x,y+1))
 if (x-1,y) not in a:edge((x,y+1),(x,y))
paths=[]
while edges:
 start=next(iter(edges));p=start;path=[p]
 for i in range(30000):
  q=edges[p].pop()
  if not edges[p]:del edges[p]
  p=q
  if p==start:break
  path.append(p)
 paths.append(path)
outline=max(paths,key=len)
def dist(p,a,b):
 ax,ay=a;bx,by=b;px,py=p;vx=bx-ax;vy=by-ay
 t=max(0,min(1,((px-ax)*vx+(py-ay)*vy)/(vx*vx+vy*vy+1.e-9)))
 return math.hypot(px-ax-t*vx,py-ay-t*vy)
def simplify(points,tol):
 def rd(ps):
  if len(ps)<3:return ps
  j=max(range(1,len(ps)-1),key=lambda i:dist(ps[i],ps[0],ps[-1]))
  if dist(ps[j],ps[0],ps[-1])<=tol:return [ps[0],ps[-1]]
  return rd(ps[:j+1])[:-1]+rd(ps[j:])
 k=0
 n=len(points)
 for i in range(n):
  if points[i][0]+points[i][1]<points[k][0]+points[k][1]:k=i
 z=points[k:]+points[:k]+[points[k]]
 return rd(z)[:-1]
outline=simplify(outline,0.65)
# Original mask x-image axis is lateral y; image y-axis points aft = model +X.
world=[(-225+450*py/213, (px-130)*480/260) for px,py in outline]
output=os.path.join(R,'reference','top_v4_traced_outline.json')
json.dump({'source':'final_master_top_mask_v4.png','sample':[w,h],'contour':world},open(output,'w'),indent=1)
print('TRACED',len(world),'pts','outline_px',len(outline),'bbox',min(x for x,y in world),max(x for x,y in world),min(y for x,y in world),max(y for x,y in world))
