import os, numpy as np, trimesh, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; m=trimesh.load_mesh(os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v285_PLANING_RELEASE.stl')); tri=np.asarray(m.triangles); out=os.path.join(ROOT,'renders','v285');os.makedirs(out,exist_ok=True)
def proj(name,a,b):
 polys=tri[:,:, [a,b]]; mn=polys.reshape(-1,2).min(0); mx=polys.reshape(-1,2).max(0); w,h=mx-mn; pad=max(w,h)*0.03
 fig,ax=plt.subplots(figsize=(12,6),dpi=100); ax.add_collection(PolyCollection(polys,facecolors='black',edgecolors='none'));ax.set_xlim(mn[0]-pad,mx[0]+pad);ax.set_ylim(mn[1]-pad,mx[1]+pad);ax.set_aspect('equal');ax.axis('off');fig.patch.set_facecolor('white');ax.set_facecolor('white');plt.savefig(os.path.join(out,name),bbox_inches='tight',pad_inches=0);plt.close(fig)
proj('silhouette_top.png',0,1);proj('silhouette_side.png',0,2)
print('PROJECTED')


