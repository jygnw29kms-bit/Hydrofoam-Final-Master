from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v333 (WIP)

![Hydrofoam v333: Original-Elevons aus dem Final-Master als separat bewegliche CAD-Baugruppen](renders/v333/master_elevon_articulation_iso.png)

**Neu:** Beide **originalen** Elevon-Meshes (`24 Elevon Left/Right`) und ihre orangefarbenen Trims wurden mit je einem schraeg verlaufenden, animierbaren Scharnier-Pivot verbunden. Blender-Keyframes zeigen neutral, +15 und -15 Grad; Originalkonturen nicht durch Rechtecke ersetzt. Die Achsen sind derzeit **geometrische Referenzen**, keine druckbaren Scharniere. [CAD-QA v333](docs/V333_MASTER_ELEVON_ARTICULATION_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v333')
