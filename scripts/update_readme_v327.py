from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v327 (WIP)

![Hydrofoam v327 Blender Gesamtmodell mit reparierter linker Leitwerks-Topologie](renders/v327/repaired_twin_fins_iso.png)

**Bauabschnitt 01:** Der Boolean-Ausschnitt v325 erzeugte 14 offene Kanten links. Die v327-Lochverschlussoperation beseitigt alle 14 offenen Kanten im Mesh. **Die Reparatur ist nur topologisch, die reale Form und Ruderausschlag-Freigaengigkeit muessen noch geprueft werden.** [QA v327](docs/V327_LEFT_FIN_REPAIR_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v327')
