# Final-Master Geometrieabgleich v286 (2026-11-07)

Referenz: gemessene Unterseiten-Sollwerte aus scripts/analyze_bottom_v284.py (15 Vergleichsstationen, mm).
Modell: v284 -> v285 -> v286, jeweils aus den STL-Querschnitten mit demselben Z-Nullpunkt ausgewertet.

| Version | mittlere absolute Unterseitenabweichung |
|---|---:|
| v284 | 12.89 mm |
| v285 | 6.58 mm |
| v286 | 4.72 mm |

v286 ist ein geometrischer Zwischenstand, NICHT die finale Freigabe.
Oberkontur bewusst nicht direkt bearbeitet. Unterseitenkorrektur blendet ueber 27 mm aus.
Offen: Bug-/Frontstation bei -180.1 mm (22.5 mm), hintere Stationen 180.1 und 202.6 mm, visuelle Overlay-Freigabe, geschlossene/wasserdichte Einzelteile und Druckvalidierung.

Dateien:
- cad/Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.blend
- cad/Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.stl
- renders/v286/assembled_*.png
- scripts/build_v286_master_lower_fit.py
- scripts/compare_bottom_v286.py
