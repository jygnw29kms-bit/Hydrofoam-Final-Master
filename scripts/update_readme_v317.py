from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';s=p.read_text(encoding='utf-8');a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->';assert a in s and b in s
v='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktionsstand v317: Aileron- und Rudder-Anlenkungen (WIP)

![Echter Blender-Screenshot v317 mit symmetrischen Aileron-Servoplatzhaltern und Rudder-Anlenkung](renders/v317/ailerons_rudder_linkages_iso.png)

Zwei getrennte Aileron-Servos und eine Rudder-Anlenkung sind als **Positionierungs- und Kinematik-Prototyp** in der echten CAD-Baugruppe angelegt. Scharnierachsen, Hebelwege, Kollisionsfreiheit und Servodrehmoment sind **noch nicht validiert**. Keine Freigabe fuer Land/Wasser/Luft oder Wasserdichtigkeit. [Pruefbericht](docs/V317_CONTROL_LINKAGE_QA.json).

**Orthografische Vergleichsansichten v316:** [links](renders/v316/left_orthographic.png) | [rechts](renders/v316/right_orthographic.png) | [oben](renders/v316/top_orthographic.png) | [unten](renders/v316/bottom_orthographic.png). Das unveraenderte Original-Final-Master-Bild bleibt oben.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
s=s[:s.index(a)]+v+s[s.index(b)+len(b):];p.write_text(s,encoding='utf-8');print('README v317 updated')
