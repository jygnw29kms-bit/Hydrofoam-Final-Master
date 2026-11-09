from pathlib import Path
p=Path(__file__).resolve().parent.parent/'README.md';t=p.read_text(encoding='utf-8')
a='<!-- CURRENT_CONSTRUCTION_RENDER_START -->';b='<!-- CURRENT_CONSTRUCTION_RENDER_END -->'
section='''<!-- CURRENT_CONSTRUCTION_RENDER_START -->
## Aktuelle CAD-Ansichten: v316 (WIP)

**Linke Seitenansicht**

![Hydrofoam v316 linke Seitenansicht](renders/v316/left_orthographic.png)

**Rechte Seitenansicht**

![Hydrofoam v316 rechte Seitenansicht](renders/v316/right_orthographic.png)

**Draufsicht und Unterseite**

![Hydrofoam v316 Draufsicht](renders/v316/top_orthographic.png)

![Hydrofoam v316 Unterseite](renders/v316/bottom_orthographic.png)

**Aktuelle Dichtungsnut-Konstruktion v314**

![Elektronikgehaeuse v314](renders/v314/lid_groove_detail.png)

Die sechs orthografischen Ansichten sind echte Blender-Renderings der bestehenden Geometrie. Keine finale Wasser-, Land- oder Flugfreigabe. Abnehmbare Foils und Elektronikgehaeuse sind in den Silhouettenansichten ausgeblendet. [Ansichtsbericht](docs/V316_ORTHOGRAPHIC_VIEWS_QA.json). Original-Final-Master unveraendert.

<!-- CURRENT_CONSTRUCTION_RENDER_END -->'''
assert a in t and b in t
t=t[:t.index(a)]+section+t[t.index(b)+len(b):];p.write_text(t,encoding='utf-8');print('README_v316')
