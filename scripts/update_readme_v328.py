from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v328 (WIP)

![Hydrofoam v328 Blender Modell mit 10 Seitenruder-Scharnierhuelsen und zwei Achsen](renders/v328/twin_rudder_hinge_knuckles_iso.png)

**Bauabschnitt 01:** Je Leitwerksseite 5 wechselweise zugeordnete Scharnierhuelsen und ein Achsreferenz-Pin. 10/10 Huelsen haben geschlossene Mesh-Topologie. **Huelsen sind noch nicht tragend mit Flosse/Ruder verbunden, Achsen und Spiel nicht validiert.** [QA v328](docs/V328_RUDDER_HINGE_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v328')
