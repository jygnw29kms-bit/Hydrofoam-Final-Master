import requests,zipfile,io,os
u='https://cncloisirs.com/fichiers/Ressources.FichiersGRV/Dossier_DXF_HydroFoam.zip'
r=requests.get(u,timeout=30);print('HTTP',r.status_code,'BYTES',len(r.content),'TYPE',r.headers.get('Content-Type'))
if r.status_code!=200 or not zipfile.is_zipfile(io.BytesIO(r.content)):
 print('NOT A VALID ZIP',r.content[:120]);raise SystemExit(2)
p='reference/historical_hydrofoam/Dossier_DXF_HydroFoam.zip';os.makedirs(os.path.dirname(p),exist_ok=True);open(p,'wb').write(r.content)
with zipfile.ZipFile(p) as z:
 for i in z.infolist():print('ENTRY',i.filename,i.file_size)
