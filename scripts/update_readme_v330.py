from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v330 (WIP)

![Hydrofoam v330 Blender Modell mit symmetrisch rekonstruierten Leitwerksausschnitten](renders/v330/symmetric_twin_fin_cut_iso.png)

**Bauabschnitt 01:** Die fehlerhafte linke Flosse wurde aus dem topologisch sauberen rechten Ausschnitt gespiegelt neu aufgebaut. Beide Flossen: **0 nicht-manifold Kanten**. Beide rechteckigen Seitenruder-Prototypen: **keine BVH-Dreiecksueberschneidung mit festen Flossen bei -25 bis +25 Grad (5-Grad-Schritte)**; bei +/-30 Grad bestehen Kollisionen. Scharnierhuelsen/Gestaenge und reale Spaltmasse noch nicht geprueft. [QA v330](docs/V330_MIRRORED_FIN_REBUILD_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v330')
