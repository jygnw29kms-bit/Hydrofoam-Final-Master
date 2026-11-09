from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v324 (WIP)

![Hydrofoam v324 echtes Blender-Modell mit zwei separaten Seitenruderflaechen und Scharnierreferenzen](renders/v324/movable_rudder_surfaces_iso.png)

**Bauabschnitt 01:** Zwei getrennte Seitenruder-Meshes (je 18 x 3,2 x 66 Modell-Einheiten) und zwei Scharnierachsen-Referenzen an den Zwillingsleitwerken. **Die starren Flossen ueberlappen diese WIP-Ruder noch; es sind noch keine ausgeschnittenen, bewegungsgeprueften Scharnierbaugruppen.** [QA v324](docs/V324_MOVABLE_RUDDER_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v324')
