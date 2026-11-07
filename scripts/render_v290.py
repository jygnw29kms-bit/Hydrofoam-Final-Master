import os, numpy as np, trimesh, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
m=trimesh.load_mesh(os.path.join(R,'cad','Hydrofoam_Final_Master_v290_EXACT_IMAGE_REBUILD.stl'),force='mesh')
out=os.path.join(R,'renders','v290');os.makedirs(out,exist_ok=True)
tri=np.asarray(m.triangles)-m.bounds.mean(axis=0)
span=max(m.extents)
for name,elev,azim in [('assembled_iso.png',28,-130),('assembled_top.png',90,-90),('assembled_side.png',0,-90),('assembled_front.png',0,180)]:
 fig=plt.figure(figsize=(11,8),dpi=115)
 ax=fig.add_subplot(111,projection='3d')
 pc=Poly3DCollection(tri,linewidths=0,edgecolors='none');pc.set_facecolor((.74,.77,.8,1));ax.add_collection3d(pc)
 lim=span*.56
 ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_zlim(-lim*.36,lim*.36)
 ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_box_aspect((1,1,.5))
 fig.patch.set_facecolor((.97,.97,.97));plt.tight_layout(pad=0)
 plt.savefig(os.path.join(out,name),bbox_inches='tight',pad_inches=0);plt.close(fig)
print('RENDER_V290_DONE')
