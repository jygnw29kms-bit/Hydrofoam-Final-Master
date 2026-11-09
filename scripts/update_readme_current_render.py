from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md'
t=p.read_text(encoding='utf-8')
start='<!-- CURRENT_CONSTRUCTION_RENDER_START -->'
end='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktions-Screenshot: v312 (WIP)

![Hydrofoam v312: echter Blender-Render mit Elektronikgehaeuse und Foil-Prototypen](renders/v312/electronics_pod_exploded_iso.png)

**Stand v312:** Das Elektronikgehaeuse und die Foils sind separate Prototypen, noch nicht eingepasst oder wasserdicht getestet. Keine Druck-, Wasser- oder Flugfreigabe. [QA-Bericht](docs/V312_WATERPROOF_POD_QA.json). Das Original-Final-Master-Bild oben bleibt unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->
'''
if start in t and end in t:
 a=t.index(start);b=t.index(end)+len(end);t=t[:a]+section+t[b:]
else:
 marker='## Aktueller technischer Modellstand: v305 (WIP)'
 assert marker in t
 t=t.replace(marker,section+'\n'+marker,1)
p.write_text(t,encoding='utf-8')
print('README_CURRENT_SCREENSHOT_SET_v312')
