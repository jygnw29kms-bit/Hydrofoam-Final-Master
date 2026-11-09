import os,json
import trimesh,numpy as np
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
out=[]
for side in ('left','right'):
 cy=-119 if side=='left' else 119
 for half,xa,xb in [('front',-135,-14),('rear',-6,135)]:
  h=trimesh.load_mesh(os.path.join(R,'print','v306_faceted_float_modules',f'float_{side}_{half}.stl'),force='mesh')
  vertices=np.asarray(h.vertices);tri=vertices[np.asarray(h.faces)]
  for x in (xa+15,xb-15):
   y=cy
   u=tri[:,1,:2]-tri[:,0,:2];v=tri[:,2,:2]-tri[:,0,:2];w=np.array([x,y])-tri[:,0,:2]
   den=u[:,0]*v[:,1]-u[:,1]*v[:,0]
   ok=np.abs(den)>1e-8
   a=np.zeros(len(den));b=np.zeros(len(den))
   a[ok]=(w[ok,0]*v[ok,1]-w[ok,1]*v[ok,0])/den[ok]
   b[ok]=(u[ok,0]*w[ok,1]-u[ok,1]*w[ok,0])/den[ok]
   inside=ok&(a>=-1e-7)&(b>=-1e-7)&(a+b<=1+1e-7)
   zvals=tri[:,0,2]+a*(tri[:,1,2]-tri[:,0,2])+b*(tri[:,2,2]-tri[:,0,2])
   zs=np.sort(zvals[inside])
   z=float(zs[0]) if len(zs) else None
   rec=dict(side=side,half=half,x_mm=x,y_mm=y,hull_lower_z_mm=z,
      skid_upper_z_mm=-7.7,vertical_gap_mm=(z+7.7 if z is not None else None),
      intersections=len(zs))
   out.append(rec);print(rec)
assert len(out)==8
with open(os.path.join(R,'docs','V308_MOUNTING_HEIGHTS.json'),'w') as f:json.dump(out,f,indent=2)
