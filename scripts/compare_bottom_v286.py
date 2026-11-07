import trimesh,numpy as np,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
files=['Hydrofoam_Final_Master_v284_SIDE_CLOSE2.stl','Hydrofoam_Final_Master_v285_PLANING_RELEASE.stl','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.stl']
ms=[trimesh.load_mesh(os.path.join(R,'cad',f),force='mesh') for f in files]
X=np.array([-202.6,-180.1,-135.2,-90.3,-45.4,0,23,45.4,67.9,90.3,112.8,135.2,157.7,180.1,202.6])
T=np.array([20.3,0,0,0,0,0,0,27.7,32.7,33.9,33.9,31.6,28.8,31.6,35.6])
z0=ms[0].bounds[0,2]
print('X TARGET v284 v285 v286')
diffs=[]
for xt,t in zip(X,T):
 vals=[]
 for m in ms:
  x=m.bounds[0,0]+(xt+225)/450*(m.bounds[1,0]-m.bounds[0,0])
  s=m.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
  vals.append(round(np.asarray(s.vertices)[:,2].min()-z0,1) if s is not None else float('nan'))
 diffs.append([abs(v-t) for v in vals])
 print(xt,t,*vals)
print('MAE',np.nanmean(diffs,axis=0))
