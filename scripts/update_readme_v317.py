from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v317 (WIP)

![Hydrofoam v317, reale Blender-Baugruppe mit Querruder- und Seitenruder-Anlenkungen](renders/v317/ailerons_rudder_linkages_iso.png)

**Neu:** Zwei Querruder-Servos, Seitenruder-Servo, Gestange und Ruderhoerner als konstruktive Platzhalter. Die Mechanik ist noch nicht kinematisch oder auf Belastbarkeit freigegeben. [QA Ruderanlenkungen](docs/V317_CONTROL_LINKAGE_QA.json).

**Geometrieansichten v316:** [links](renders/v316/left_orthographic.png), [rechts](renders/v316/right_orthographic.png), [oben](renders/v316/top_orthographic.png), [unten](renders/v316/bottom_orthographic.png). Das originale Final-Master-Bild bleibt unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v317')
