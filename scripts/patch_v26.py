from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v25_station_fit.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('v25_parts','v26_parts').replace('v25_STATION_FIT','v26_STATION_FIT2').replace('V25_IMAGE_MEASUREMENTS','V26_IMAGE_MEASUREMENTS').replace('V25_PART_AUDIT','V26_PART_AUDIT').replace('V25_SAVED','V26_SAVED').replace('Hydrofoam_Final_Master_v25','Hydrofoam_Final_Master_v26')
anchor="VSC=sc['vert']"
insert=anchor+"\n# second station-by-station correction pass\nsc26=json.load(open(os.path.join(DOCS,'V26_STATION_CORRECTIONS.json')))\nbody_w=[body_w[i]*sc26['body'][i] for i in range(31)]\nspy=[spy[i]*sc26['spy'][i] for i in range(31)]\nspw=[spw[i]*sc26['spw'][i] for i in range(31)]\nenv=[env[i]*sc26['env'][i] for i in range(31)]\nVSC=[VSC[i]*sc26['vert'][i] for i in range(31)]"
if anchor not in s: raise RuntimeError('anchor missing')
s=s.replace(anchor,insert)
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v26_station_fit2.py').write_text(s,encoding='utf-8')
print('PATCHED_V26')