from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v22_image_fit.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("v22_parts","v23_parts").replace("v22_IMAGE_FIT","v23_PROFILE_CORRECTED").replace("V22_IMAGE_MEASUREMENTS","V23_IMAGE_MEASUREMENTS").replace("V22_PART_AUDIT","V23_PART_AUDIT").replace("V22_SAVED","V23_SAVED").replace("Hydrofoam_Final_Master_v22","Hydrofoam_Final_Master_v23")
anchor="body_w=[max(8,min(115,v)) for v in body_w]; spy=[max(115,min(155,v)) for v in spy]; spw=[max(12,min(68,v)) for v in spw]"
repl=anchor+"\n# Apply measured v22->master profile correction factors.\ncorr=json.load(open(os.path.join(DOCS,'V23_PROFILE_CORRECTIONS.json')))\nbody_w=[v*corr['body_width_scale'] for v in body_w]\nspy=[v*corr['sponson_y_scale'] for v in spy]\nspw=[v*corr['sponson_width_scale'] for v in spw]\nenv=[v*corr['tail_envelope_scale'] for v in env]\nVS=corr['vertical_scale']"
s=s.replace(anchor,repl)
s=s.replace("h=8 + 39*math.sin", "h=(8 + 39*math.sin").replace("**0.78\n z=31+h*.18", "**0.78)*VS\n z=31+h*.18")
s=s.replace("h=max(7,38*max(.28,taper)**.55); sec.append", "h=max(7,38*max(.28,taper)**.55)*VS; sec.append")
# scale canopy z-height around local baseline while preserving planform
s=s.replace("can=[(58,0,51,8,5),(78,0,58,29,13),(106,0,67,52,23),(138,0,73,67,31),(171,0,72,65,29),(203,0,65,46,21),(228,0,56,16,8)]", "can=[(58,0,51,8,5*VS),(78,0,58,29,13*VS),(106,0,67,52,23*VS),(138,0,73,67,31*VS),(171,0,72,65,29*VS),(203,0,65,46,21*VS),(228,0,56,16,8*VS)]")
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v23_profile_corrected.py').write_text(s,encoding='utf-8')
print('PATCHED_V23')