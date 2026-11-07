import os, numpy as np, trimesh, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
m=trimesh.load_mesh(os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.stl'),force='mesh')
out=os.path.join(ROOT,'renders','v286')
os.makedirs(out,exist_ok=True)
tri=np.asarray(m.triangles)
c=m.bounds.mean(axis=0)
tri=tri-c
span=max(m.extents)
for name,elev,azim in [('assembled_iso_sw.png',24,-135),('assembled_top_sw.png',90,-90),('assembled_side_sw.png',0,-90),('assembled_front_sw.png',0,180)]:
 fig=plt.figure(figsize=(12,8),dpi=130)
 ax=fig.add_subplot(111,projection='3d')
 pc=Poly3DCollection(tri,linewidths=0.05,edgecolors=(0.25,0.25,0.25,0.2))
 pc.set_facecolor((0.82,0.84,0.86,1))
 ax.add_collection3d(pc)
 lim=span*0.56
 ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_zlim(-lim*0.35,lim*0.35)
 ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_box_aspect((1,1,0.5))
 fig.patch.set_facecolor((0.95,0.95,0.95))
 plt.tight_layout(pad=0)
 plt.savefig(os.path.join(out,name),bbox_inches='tight',pad_inches=0)
 plt.close(fig)
print('V286_RENDERED')
