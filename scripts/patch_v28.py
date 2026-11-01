from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v27_side_image_fit.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('v27_parts','v28_parts').replace('v27_SIDE_IMAGE_FIT','v28_CONVERGENCE').replace('V27_IMAGE_MEASUREMENTS','V28_IMAGE_MEASUREMENTS').replace('V27_PART_AUDIT','V28_PART_AUDIT').replace('V27_SAVED','V28_SAVED').replace('Hydrofoam_Final_Master_v27','Hydrofoam_Final_Master_v28')
anchor="VSC=sc['vert']"
insert=anchor+"\n# another local convergence pass against current best overlay\nsc28=json.load(open(os.path.join(DOCS,'V28_STATION_CORRECTIONS.json')))\nbody_w=[body_w[i]*sc28['body'][i] for i in range(31)]\nspy=[spy[i]*sc28['spy'][i] for i in range(31)]\nspw=[spw[i]*sc28['spw'][i] for i in range(31)]\nenv=[env[i]*sc28['env'][i] for i in range(31)]\nVSC=[VSC[i]*sc28['vert'][i] for i in range(31)]"
if anchor not in s: raise RuntimeError('anchor missing')
s=s.replace(anchor,insert)
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v28_convergence.py').write_text(s,encoding='utf-8')
print('PATCHED_V28')