from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md'
t=p.read_text(encoding='utf-8')
a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktueller Konstruktions-Screenshot: v313 (WIP)

![Hydrofoam v313: Blender-Modell mit separatem Elektronikgehaeuse und Foil-Prototypen](renders/v313/continuous_gasket_pod_iso.png)

**Stand v313:** Elektronikgehaeuse mit neuem geschlossenen Dichtungs-Kurvenpfad (im Gesamtbild nicht sichtbar). Noch keine gefraeste Dichtungsnut, keine nachgewiesene Dichtungskompression, keine wasserdichte Abnahme. Foil-Prototypen und Gehaeuse sind nicht in den Rumpf eingepasst. [QA-Bericht](docs/V313_GASKET_LOOP_QA.json). Original-Final-Master unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t
t=t[:t.index(a)]+section+t[t.index(b)+len(b):]
p.write_text(t,encoding='utf-8');print('README_UPDATED_v313')
