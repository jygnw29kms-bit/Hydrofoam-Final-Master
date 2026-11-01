import FreeCAD as App
import FreeCADGui as Gui
import os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
fc=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v01.FCStd')
out=os.path.join(ROOT,'renders')
os.makedirs(out,exist_ok=True)
doc=App.openDocument(fc)
Gui.activeDocument().activeView().setAnimationEnabled(False)
# colors + visibility
for o in doc.Objects:
    try:
        mat=getattr(o,'Material','')
        if mat=='REFERENCE':
            o.ViewObject.Visibility=False
        elif mat=='PETG':
            o.ViewObject.ShapeColor=(0.22,0.24,0.28)
        elif o.Name in ['Aileron_L','Aileron_R','Pitch_Surface','Rudder_L','Rudder_R','Hatch']:
            o.ViewObject.ShapeColor=(0.95,0.48,0.10)
        else:
            o.ViewObject.ShapeColor=(0.86,0.88,0.91)
    except Exception:
        pass
v=Gui.activeDocument().activeView()
v.setBackgroundColor if False else None
# perspective-ish axonometric
v.viewAxonometric(); v.fitAll(); v.saveImage(os.path.join(out,'assembled_iso.png'),1600,1000,'Current')
v.viewTop(); v.fitAll(); v.saveImage(os.path.join(out,'assembled_top.png'),1600,1000,'Current')
v.viewRight(); v.fitAll(); v.saveImage(os.path.join(out,'assembled_side.png'),1600,1000,'Current')
v.viewFront(); v.fitAll(); v.saveImage(os.path.join(out,'assembled_front.png'),1600,1000,'Current')
doc.save()
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
