import ezdxf,json,collections
from shapely.geometry import LineString
from shapely.ops import polygonize,unary_union
p='reference/historical_hydrofoam/hydrofoam_mm.dxf';d=ezdxf.readfile(p)
segments=[]
for e in d.modelspace():
 if e.dxftype()=='LINE':segments.append(LineString([(e.dxf.start.x*1000,e.dxf.start.y*1000),(e.dxf.end.x*1000,e.dxf.end.y*1000)]))
 elif e.dxftype()=='POLYLINE':
  pts=[(v.dxf.location.x*1000,v.dxf.location.y*1000) for v in e.vertices]
  if len(pts)>1:
   if e.is_closed:pts.append(pts[0])
   segments.extend(LineString([a,b]) for a,b in zip(pts,pts[1:]))
print('SEGMENTS',len(segments))
polys=sorted(list(polygonize(unary_union(segments))),key=lambda p:p.area,reverse=True)
print('POLYGONS',len(polys),'TOP',[(round(x.area),tuple(round(z) for z in x.bounds)) for x in polys[:20]])
out={'source':'CNCLoisirs Xavier Maquet hydrofoam_mm.dxf','scale_assumption':'DXF coordinate unit appears metre, multiplied by 1000 to mm; NOT independently verified','polygons':[{'area_mm2':p.area,'outline_mm':list(p.exterior.coords),'bounds_mm':list(p.bounds)} for p in polys if p.area>20]}
with open('docs/HISTORICAL_DXF_EXTRACTED_CONTOURS_WIP.json','w') as f:json.dump(out,f)
print('EXPORTED',len(out['polygons']))
