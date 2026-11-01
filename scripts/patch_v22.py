from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v21_image_driven.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("v21_parts","v22_parts").replace("v21_IMAGE_DRIVEN","v22_IMAGE_FIT").replace("V21_IMAGE_MEASUREMENTS","V22_IMAGE_MEASUREMENTS").replace("V21_PART_AUDIT","V22_PART_AUDIT").replace("V21_SAVED","V22_SAVED").replace("Hydrofoam_Final_Master_v21","Hydrofoam_Final_Master_v22")
s=s.replace("rec={'x':i*15.0,'body_w':None,'sp_y':None,'sp_w':None}","rec={'x':i*15.0,'body_w':None,'sp_y':None,'sp_w':None,'env':None}")
s=s.replace("infos=[((a+b)/2.0,b-a+1,a,b) for a,b in rr]","infos=[((a+b)/2.0,b-a+1,a,b) for a,b in rr]\n  rec['env']=max(max(abs(z[2]-mid),abs(z[3]-mid)) for z in infos)*SY")
s=s.replace("body_w=fill('body_w',90); spy=fill('sp_y',137); spw=fill('sp_w',58)","body_w=fill('body_w',90); spy=fill('sp_y',137); spw=fill('sp_w',58); env=fill('env',235)\nsp_known=[i for i,r in enumerate(raw) if r['sp_y'] is not None]; body_known=[i for i,r in enumerate(raw) if r['body_w'] is not None]\nsp_start=max(15,(min(sp_known)*15-15) if sp_known else 30); sp_end=min(420,(max(sp_known)*15+15) if sp_known else 390)\nbody_start=max(0,(min(body_known)*15-10) if body_known else 0); body_end=min(450,(max(body_known)*15+10) if body_known else 360)")
s=s.replace("if x<35 or x>390: continue\n  taper=min((x-35)/40.0,(390-x)/45.0,1.0)","if x<sp_start or x>sp_end: continue\n  taper=min((x-sp_start)/35.0,(sp_end-x)/40.0,1.0)")
# body taper uses image-derived extents
s=s.replace("end=min(x/42.0,(450-x)/75.0,1.0)","end=min(max(0.05,(x-body_start)/38.0),max(0.05,(body_end-x)/58.0),1.0)")
# Replace manual rear surfaces block with image-envelope-driven sweep.
start=s.index("# master rear surfaces:")
end=s.index("# exact identity motor arch shape")
new=r'''# Rear surfaces: outer edge is read from the Final Master silhouette envelope.
for side,sgn in [('L',-1),('R',1)]:
    ids=list(range(18,31,2))
    outeredge=[(xs[i],sgn*max(125,min(241,env[i]))) for i in ids]
    inneredge=[]
    for i in reversed(ids):
        # root line stays around central tail/sponson inner region
        root=max(body_w[i]*0.40,42)
        inneredge.append((xs[i],sgn*root))
    tailpoly=inneredge+outeredge
    tail=fillet(prism(tailpoly,41,2.0),0.8)
    # split aft 45% as control surface, fixed forward portion stays structurally separate
    cutx=365
    b=tail.BoundBox; pad=8
    fixed=tail.common(Part.makeBox(cutx-b.XMin+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(b.XMin-pad,b.YMin-pad,b.ZMin-pad)))
    ctrl=tail.common(Part.makeBox(b.XMax-cutx+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(cutx,b.YMin-pad,b.ZMin-pad)))
    add('RearFixed_'+side,'Rear fixed '+side,fixed)
    add('OuterControl_'+side,'Outer control '+side,ctrl)
    # inner pitch strip follows central trailing edge
    pitch=[(330,sgn*34),(366,sgn*40),(405,sgn*52),(446,sgn*64),(449,sgn*49),(406,sgn*36),(365,sgn*28)]
    add('Pitch_'+side,'Pitch '+side,fillet(prism(pitch,42,2.0),0.7))
'''
s=s[:start]+new+s[end:]
# fin lateral position follows target envelope near x=375
s=s.replace("y=sgn*177", "i_fin=25; y=sgn*max(150,min(205,env[i_fin]*0.78))")
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v22_image_fit.py').write_text(s,encoding='utf-8')
print('PATCHED_V22')