import FreeCAD as App
import Part, Mesh, os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v13')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v13_VISUAL_HULL')
TOP=[(66.271, -138.42), (84.442, -146.971), (100.475, -146.971), (112.233, -154.454), (164.608, -168.349), (269.359, -185.451), (278.979, -183.314), (338.836, -241.033), (364.489, -238.895), (378.385, -223.931), (404.038, -216.45), (422.207, -202.555), (431.827, -185.453), (435.034, -162.999), (431.827, -145.898), (424.345, -132.003), (417.932, -114.901), (411.519, -100.006), (405.106, -86.111), (397.624, -69.009), (390.142, -55.114), (381.592, -39.081), (371.972, -24.117), (361.282, -11.291), (350.593, 2.604), (338.836, 16.499), (327.078, 29.325), (313.184, 41.083), (300.358, 51.772), (284.325, 61.392), (268.292, 71.012), (251.19, 80.632), (235.157, 90.252), (217.0, 98.803), (199.898, 108.423), (181.729, 117.974), (163.56, 126.525), (145.391, 135.075), (127.222, 142.557), (109.053, 149.0), (91.951, 154.344), (73.782, 157.551), (56.68, 156.482), (40.647, 150.069), (28.89, 139.38), (22.477, 124.416), (21.408, 107.314), (24.615, 91.281), (31.028, 73.112), (39.579, 57.079), (48.129, 41.046), (56.68, 25.013), (65.23, 8.98), (69.506, -8.122), (68.437, -27.36), (63.092, -43.393), (59.886, -61.562), (59.886, -80.8), (61.023, -97.902), (64.23, -114.004), (64.23, -128.968)]
SIDE=[(449.435, 48.55), (446.047, 48.55), (446.047, 50.809), (433.1, 50.809), (433.1, 56.456), (422.937, 56.456), (422.937, 59.843), (410.555, 59.843), (405.474, 62.101), (388.54, 62.101), (388.54, 58.714), (376.159, 58.714), (376.159, 56.456), (356.403, 56.456), (356.403, 58.714), (343.456, 58.714), (343.456, 54.198), (331.075, 54.198), (331.075, 50.809), (319.822, 50.809), (319.822, 45.162), (309.095, 45.162), (309.095, 55.327), (297.843, 55.327), (297.843, 64.359), (286.59, 64.359), (286.59, 69.439), (273.643, 69.439), (273.643, 75.086), (259.568, 75.086), (259.568, 79.603), (244.364, 79.603), (244.364, 84.684), (225.738, 84.684), (225.738, 88.072), (204.854, 88.072), (204.854, 91.459), (183.971, 91.459), (183.971, 94.282), (164.216, 94.282), (164.216, 97.105), (141.641, 97.105), (141.641, 98.799), (119.065, 98.799), (119.065, 101.057), (98.182, 101.057), (98.182, 103.316), (75.607, 103.316), (75.607, 105.574), (53.031, 105.574), (53.031, 106.703), (31.585, 106.703), (31.585, 108.397), (11.266, 108.397), (11.266, 105.574), (0.0, 105.574), (0.0, 98.799), (3.388, 98.799), (14.68, 95.976), (29.36, 94.847), (47.985, 92.024), (69.439, 88.637), (91.459, 84.684), (116.303, 79.603), (141.641, 74.521), (166.485, 69.439), (188.496, 64.359), (212.211, 59.843), (229.799, 25.408), (230.928, 10.728), (239.962, 12.986), (281.179, 29.36), (309.41, 31.054), (349.498, 31.054), (375.471, 25.972), (405.395, 28.795), (438.708, 35.006), (434.191, 42.346)]

def face_xy(points,z=-40):
    pts=[App.Vector(x,y,z) for x,y in points]
    if pts[0].distanceToPoint(pts[-1])>1e-6: pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))
def face_xz(points,y=-300):
    pts=[App.Vector(x,y,z) for x,z in points]
    if pts[0].distanceToPoint(pts[-1])>1e-6: pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))

top_solid=face_xy(TOP,-40).extrude(App.Vector(0,0,180))
side_solid=face_xz(SIDE,-300).extrude(App.Vector(0,600,0))
hull=top_solid.common(side_solid)
obj=doc.addObject('PartDesign::Feature','MasterVisualHull')
obj.Label='FINAL MASTER silhouette-locked visual hull'
obj.Shape=hull
obj.addProperty('App::PropertyString','Source','Master').Source='Final Master top+side silhouettes, image-traced'
obj.addProperty('App::PropertyString','Status','Master').Status='Exterior reference envelope; do not alter visible silhouette'
obj.addProperty('App::PropertyLength','OverallLength','Master').OverallLength=450
obj.addProperty('App::PropertyLength','OverallWidth','Master').OverallWidth=482.07
obj.addProperty('App::PropertyLength','OverallHeight','Master').OverallHeight=108.97

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v13_VISUAL_HULL.FCStd'); doc.saveAs(fc)
Part.export([obj],os.path.join(CAD,'Hydrofoam_Final_Master_v13_VISUAL_HULL.step'))
Mesh.export([obj],os.path.join(CAD,'Hydrofoam_Final_Master_v13_VISUAL_HULL.stl'))
print('V13_VISUAL_HULL_SAVED',len(hull.Solids),'vol',hull.Volume)
