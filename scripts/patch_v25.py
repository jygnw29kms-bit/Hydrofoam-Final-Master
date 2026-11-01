from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v22_image_fit.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('v22_parts','v25_parts').replace('v22_IMAGE_FIT','v25_STATION_FIT').replace('V22_IMAGE_MEASUREMENTS','V25_IMAGE_MEASUREMENTS').replace('V22_PART_AUDIT','V25_PART_AUDIT').replace('V22_SAVED','V25_SAVED').replace('Hydrofoam_Final_Master_v22','Hydrofoam_Final_Master_v25')
anchor="body_w=[max(8,min(115,v)) for v in body_w]; spy=[max(115,min(155,v)) for v in spy]; spw=[max(12,min(68,v)) for v in spw]"
insert=anchor+"\n# station-by-station correction from best measured candidate\nsc=json.load(open(os.path.join(DOCS,'V25_STATION_CORRECTIONS.json')))\nbody_w=[body_w[i]*sc['body'][i] for i in range(31)]\nspy=[spy[i]*sc['spy'][i] for i in range(31)]\nspw=[spw[i]*sc['spw'][i] for i in range(31)]\nenv=[env[i]*sc['env'][i] for i in range(31)]\nVSC=sc['vert']"
s=s.replace(anchor,insert)
# per-station vertical correction
s=s.replace("h=8 + 39*math.sin(math.pi*min(max(x/365.0,0),1))**0.78", "h=(8 + 39*math.sin(math.pi*min(max(x/365.0,0),1))**0.78)*VSC[i]")
s=s.replace("h=max(7,38*max(.28,taper)**.55); sec.append", "h=max(7,38*max(.28,taper)**.55)*VSC[i]; sec.append")
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v25_station_fit.py').write_text(s,encoding='utf-8')
print('PATCHED_V25')