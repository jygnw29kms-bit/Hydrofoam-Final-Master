from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v23_profile_corrected.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('v23_parts','v24_parts').replace('v23_PROFILE_CORRECTED','v24_SECOND_PASS').replace('V23_IMAGE_MEASUREMENTS','V24_IMAGE_MEASUREMENTS').replace('V23_PART_AUDIT','V24_PART_AUDIT').replace('V23_SAVED','V24_SAVED').replace('Hydrofoam_Final_Master_v23','Hydrofoam_Final_Master_v24')
anchor="env=[v*corr['tail_envelope_scale'] for v in env]\nVS=corr['vertical_scale']"
insert=anchor+"\n# second measured convergence pass\ncorr24=json.load(open(os.path.join(DOCS,'V24_PROFILE_CORRECTIONS.json')))\nbody_w=[v*corr24['body_width_scale'] for v in body_w]\nspy=[v*corr24['sponson_y_scale'] for v in spy]\nspw=[v*corr24['sponson_width_scale'] for v in spw]\nenv=[v*corr24['tail_envelope_scale'] for v in env]"
if anchor not in s: raise RuntimeError('anchor not found')
s=s.replace(anchor,insert)
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v24_second_pass.py').write_text(s,encoding='utf-8')
print('PATCHED_V24')