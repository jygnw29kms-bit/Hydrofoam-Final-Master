from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')/'README.md'
text=p.read_text(encoding='utf8')
heading='## Aktueller technischer Modellstand: v305 (WIP)'
block='''## Aktueller technischer Modellstand: v305 (WIP)

**Blender-Gesamtbaugruppe, noch keine Final-/Flug- oder Druckfreigabe.**
Der Maßstab, das äußere Design und die lackierte Silhouette werden ausschließlich an [FINAL_MASTER_ORIGINAL.jpeg](reference/FINAL_MASTER_ORIGINAL.jpeg) gemessen.

![Hydrofoam v305, echtes Blender-Modell Isometrie](renders/v305/assembled_iso.png)

![Hydrofoam v305, Draufsicht](renders/v305/assembled_top.png)

![Hydrofoam v305, Cockpit geöffnet](renders/v305/exploded_cockpit.png)

[CAD-Schnittstudie, Leichtbau- und Mesh-Prüfbericht v305](docs/V305_MODEL_PROGRESS.md)

---
'''
if heading not in text:
 anchor='## Aktueller Konstruktionsstand'
 assert anchor in text
 text=text.replace(anchor,block+'\n## Historischer Vergleichsstand v288 (nicht Final)',1)
 p.write_text(text,encoding='utf8',newline='\n')
print('README_V305_WIP_LINKED',heading in p.read_text(encoding='utf8'))
