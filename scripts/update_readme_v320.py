from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v320 (WIP)

![Hydrofoam v320 echtes Blender-Gesamtmodell mit drei gebohrten Ruderhorn-Prototypen](renders/v320/control_horn_bores_iso.png)

**Neu v320:** Drei Ruderhorn-Prototypen mit per Boolean erzeugten 2,2-mm-Durchgangsbohrungen. Die Anlenkungen sind nicht kinematisch, strukturell oder auf Wasserdichtigkeit abgenommen. [QA v320](docs/V320_LINKAGE_PIN_HOLES_QA.json).

**Seitenansichten v316:** [links](renders/v316/left_orthographic.png), [rechts](renders/v316/right_orthographic.png). Original-Final-Master unveraendert. **LAND + WASSER + LUFT** noch nicht nachgewiesen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v320')
