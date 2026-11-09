import json,collections,os,math
from shapely.geometry import Polygon
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=json.load(open(os.path.join(R,'docs','HISTORICAL_DXF_EXTRACTED_CONTOURS_WIP.json')))
ps=[Polygon(p['outline_mm']) for p in d['polygons']]
contains=[];invalid=[];duplicates=[]
for i,p in enumerate(ps):
 if not p.is_valid:invalid.append(i)
 for j,q in enumerate(ps):
  if i==j:continue
  if p.contains(q):contains.append((i,j))
  if i<j and p.equals(q):duplicates.append((i,j))
areas=sorted([(i,round(p.area,1),tuple(round(x,1) for x in p.bounds)) for i,p in enumerate(ps)],key=lambda x:-x[1])
report={'source':d['source'],'units':'unverified: input coordinates multiplied by 1000','polygon_count':len(ps),'invalid_polygon_indices':invalid,'nested_contours':contains,'duplicate_contours':duplicates,'largest_contours':areas[:20],'manufacturing_status':'BLOCKED: nested cutouts and physical scale unverified; DO NOT export 1:1 cutting templates'}
p=os.path.join(R,'docs','HISTORICAL_DXF_GEOMETRY_QA.json');open(p,'w').write(json.dumps(report,indent=2))
print('QA',len(ps),'invalid',len(invalid),'nested',len(contains),'duplicates',len(duplicates));print('TOP',areas[:5]);print('SAVED',p)
