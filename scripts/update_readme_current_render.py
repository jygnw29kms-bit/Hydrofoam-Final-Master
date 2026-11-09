from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8')
a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v314 (WIP)

**Gesamtmodell v313 (Blender):**

![Hydrofoam Gesamtmodell mit Foil- und Elektronikprototypen](renders/v313/continuous_gasket_pod_iso.png)

**Neue Detailkonstruktion v314, Elektronikgehaeuse:**

![Blender Detailaufnahme Elektronikgehaeuse v314](renders/v314/lid_groove_detail.png)

Die Dichtungsnut wurde per Boolean an der Deckelunterseite modelliert, ist in dieser Oberseitenansicht aber nicht sichtbar. Keine nachgewiesene Kompression oder Wasserdichtigkeit, keine mechanische Einpassung ins Flugmodell. [QA v314](docs/V314_LID_GROOVE_QA.json). Der originale Final-Master bleibt unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t
t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_v314')
