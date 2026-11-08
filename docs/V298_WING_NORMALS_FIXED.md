# Hydrofoam v298: Haupttragflaechen-Volumenfehler behoben

Datum 2026-11-08

## Nachweisliche Fehlerursache
Das Quellvolumen aus v296 war falsch, weil die Hauptfluegel gemischte/falsch gerichtete Facenormalen hatten. Das urspruenglich berechnete abs(signed volume) 20324.008 mm3 war KEIN physikalisch korrektes Volumen. Die Neuorientierung durch bmesh.ops.recalc_face_normals liefert konsistent 60972.002 mm3 fuer jeden Hauptfluegel. Der v297-Split selbst erzeugte bereits das richtige geometrische Volumen, wurde aber mit dem fehlerhaften Quellwert verglichen.

## Real ausgefuehrte Korrektur
- scripts/build_v298_correct_wing_normals.py: beiden Hauptfluegeln korrekte, konsistente Normalen zugewiesen und Blender+STL als v298 gespeichert.
- scripts/build_v298_wing_split.py: korrigierte Fluegel erneut in je zwei P2S-grosse Module geschnitten und Schnittstellen geschlossen.
- scripts/audit_v298_wings.py: Mesh- und Volumen-Pruefung erfolgreich.
- Volumensumme L: 60972.002291 mm3; Soll: 60972.001999 mm3, Fehler 0.000000479 %.
- Volumensumme R: 60972.002049 mm3; Soll: 60972.001999 mm3, Fehler 0.000000082 %.
- Alle 4 Fluegel-STLs watertight, winding-consistent und X/Y/Z jeweils unter 256 mm.

## Arbeitsdateien
- cad/Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.blend
- cad/Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.stl
- cad/Hydrofoam_v298_WING_SPLIT_STUDY.blend
- print/v298_wing_modules/*.stl
- docs/V298_WING_VOLUME_QA.json

## Nicht geloeste Aufgaben
- Es fehlen noch die konstruktiven Verbindungen der geteilten Bauteile (Passstifte, tragende Holme, Verklebung oder Verschraubungen), Leichtbauschalen, Antriebs-/Servoeinbauraeume und vollstaendiger Slicer-/P2S-Test.
- Die auf 256 mm bezogenen Achsgrenzen ersetzen keine reale Bauplattenpruefung mit Randabstaenden.
- Noch keine fotografische Final-Master-Uebereinstimmung nachgewiesen; README-Finalansichten bleiben deshalb unveraendert.
- Kein fertiger Drucksatz und keine Final-Freigabe.
