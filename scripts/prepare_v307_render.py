from pathlib import Path
r=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
src=(r/'scripts'/'render_v306_workbench.py').read_text(encoding='utf-8')
src=src.replace('Hydrofoam_Final_Master_v306_FACETED_MASTER_FLOATS.blend','Hydrofoam_Final_Master_v307_LAND_SKID_PROTOTYPES.blend').replace("'v306'","'v307'").replace('"v306"','"v307"')
(r/'scripts'/'render_v307_workbench.py').write_text(src,encoding='utf-8')
print('render script generated',len(src))
