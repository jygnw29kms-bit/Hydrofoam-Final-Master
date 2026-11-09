from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v331 (WIP)

![Hydrofoam v331 Blender Modell mit zehn Scharnierhuelsen und angeformten Bruecken](renders/v331/hinge_mount_bridges_iso.png)

**Bauabschnitt 01:** Zehn Scharnierhuelsen mit je einer per Boolean vereinigten Befestigungsbruecke modelliert. **10/10 resultierende Huelsen-Meshes topologisch geschlossen.** Die Bruecken sind noch nicht mit den Flossen/Ruderkoerpern vereint und nicht belastungs- oder bewegungsgeprueft. [QA v331](docs/V331_HINGE_MOUNT_BRIDGES_QA.json). [Bauabschnitte](docs/BUILD_SECTIONS_TO_FINAL.md).

Original-Final-Master-Bild unveraendert. LAND/WASSER/LUFT noch nicht abgenommen.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v331')
