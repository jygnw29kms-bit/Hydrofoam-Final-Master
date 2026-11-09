from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand: v319 (WIP)

![Hydrofoam v319 Blender-Modell mit Rudergestaengen und optimiertem Seitenruder-Horn-Prototyp](renders/v319/rudder_horn_optimized_iso.png)

**Neu:** Seitenruderhorn-Prototyp angepasst. Rechnerischer idealisierter Ausschlag 27,31 Grad bei 10-mm-Servohebel, 12,5-mm-effektivem Ruderhorn und +/-35 Grad Servoweg. **Noch keine reale Kinematik- oder Kollisionsfreigabe.** [QA v319](docs/V319_RUDDER_HORN_OPTIMIZATION_QA.json).

**Geometrieansichten v316:** [links](renders/v316/left_orthographic.png), [rechts](renders/v316/right_orthographic.png), [oben](renders/v316/top_orthographic.png), [unten](renders/v316/bottom_orthographic.png). Das originale Final-Master-Bild bleibt unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t;t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_UPDATED_v319')
