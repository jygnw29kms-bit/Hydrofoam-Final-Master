from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v323 (WIP)

![Hydrofoam v323 Blender Gesamtmodell mit zwei separaten Leitwerks-Servo-Anlenkungen](renders/v323/twin_fin_rudder_layout_iso.png)

**Bauabschnitt 01:** Zwei symmetrische Seitenruder-Servo- und Gestange-Einbaustudien an den tatsaechlichen Leitwerksflossen. Der bisherige mittige Ruderservo-Entwurf wurde ausgeblendet. **Die Ruderflaechen sind noch nicht getrennt, Gelenke und Bewegungen noch nicht validiert.** [QA v323](docs/V323_TWIN_RUDDER_LAYOUT_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. **LAND / WASSER / LUFT** noch nicht funktionsgeprueft.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v323')
