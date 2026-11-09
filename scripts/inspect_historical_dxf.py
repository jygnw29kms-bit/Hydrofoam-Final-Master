import zipfile,collections,os
p='reference/historical_hydrofoam/Dossier_DXF_HydroFoam.zip'
with zipfile.ZipFile(p) as z:z.extract('hydrofoam_mm.dxf','reference/historical_hydrofoam')
try:import ezdxf
except Exception as e:print('NO EZDXF',e);raise
f=ezdxf.readfile('reference/historical_hydrofoam/hydrofoam_mm.dxf');m=f.modelspace()
print('VERSION',f.dxfversion,'UNITS',f.header.get('$INSUNITS'),'COUNT',len(m))
print('TYPES',collections.Counter(x.dxftype() for x in m));print('LAYERS',collections.Counter(x.dxf.layer for x in m))
for x in list(m)[:12]:print('ENTITY',x.dxftype(),x.dxf.layer,str(x.dxf.all_existing_dxf_attribs())[:220])
