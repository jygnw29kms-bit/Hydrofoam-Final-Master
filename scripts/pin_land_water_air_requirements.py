from pathlib import Path
root=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
p=root/'README.md'
a=p.read_text(encoding='utf-8')
mark='## VERBINDLICH: LAND + WASSER + LUFT'
if mark not in a:
 new='''## VERBINDLICH: LAND + WASSER + LUFT

**Hydrofoam ist ein Dreimoden-Modell, kein reines Wasserfahrzeug.**
Es muss eigenstaendig auf Land (auch Kurzrasen/tragfaehiger Sand), auf Wasser mit Gleit-/Foilfahrt und in der Luft funktionieren. Die sichtbare Form des [unveraenderten Final Masters](reference/FINAL_MASTER_ORIGINAL.jpeg) bleibt dabei verbindlich.
Technische Einzelheiten, Risiken, Unterseitenkufen, Bodenkontakt, Foil-Bodenfreiheit und separate Abnahmetests: [LAND_WATER_AIR_REQUIREMENTS.md](docs/LAND_WATER_AIR_REQUIREMENTS.md).

**Status v306:** Diese Funktionen sind noch nicht nachgewiesen. Kein Final-Release.

'''
 idx=a.find('## Aktueller technischer Modellstand:')
 if idx<0:raise RuntimeError('README ANCHOR NOT FOUND')
 a=a[:idx]+new+a[idx:]
 p.write_text(a,encoding='utf-8',newline='\n')
print('README_THREE_MODE_PRESENT',mark in p.read_text(encoding='utf-8'))
