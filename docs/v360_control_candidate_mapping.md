# v360: Tatsächliche Steuermechanik-Bestandsaufnahme (Jens-PC)

Quelle: Blender 4.5.10 LTS, geöffnetes `cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend` am 2026-11-12. Das lokale Inventar enthält 138 Mesh-Objekte und wurde als `docs/v360_control_candidate_inventory_local.json` auf Jens-PC erzeugt. Es wurde kein Originalbild und keine README geändert.

## Bereits vorhandene echte Blender-Meshes (nicht mit Funktionsabnahme verwechseln)

- `24 Elevon Left`, `24 Elevon Right` und zugehörige orange Trim-Meshes existieren.
- `V333_Left_SWEPT_HINGE_AXIS_REFERENCE` und `V333_Right_SWEPT_HINGE_AXIS_REFERENCE` existieren; es handelt sich dem Namen nach um Referenzachsen, nicht um abgenommene druckbare Scharniere.
- `LEFT_AILERON_HINGE_AXIS_REFERENCE`, `RIGHT_AILERON_HINGE_AXIS_REFERENCE`, zugehörige `*_HORN_PLACEHOLDER`, `*_SERVO_PLACEHOLDER`, `*_PUSHROD_WIP` existieren.
- `RUDDER_HINGE_REFERENCE`, `RUDDER_HORN_12P5MM_PROTOTYPE`, `RUDDER_PUSHROD_WIP`, `RUDDER_SERVO_PLACEHOLDER` existieren.
- Jeweils links/rechts `V324_*_MOVABLE_RUDDER_WIP` sowie `V328_*_FIXED_FIN_HINGE_SLEEVE_{0,2,4}`, `V328_*_MOVING_RUDDER_HINGE_SLEEVE_{1,3}` und `V328_*_HINGE_PIN_REFERENCE` existieren. Die V328-Buchsen sind als einzelne Meshes angelegt, nicht als physisch getestete Baugruppe.

## Konstruktive Konsequenz

Die v359-Prüfung mit normierten Namen lieferte fehlende Komponenten; das darf nicht als Aussage interpretiert werden, dass überhaupt keine Kandidatengeometrie vorhanden sei. Die Bestandsaufnahme belegt allerdings weder tragende Scharnierverbindungen noch korrekte Servoeinbaumaße, Befestigung, Kollisionfreiheit oder Stellweg. Als nächster Konstruktionsschritt sind die existierenden Meshes räumlich und topologisch den fünf geforderten Steuerflächen zuzuordnen, fehlende feste/moving Bauteile zu konstruieren und eine tatsächlich animierte Kollisionsprüfung durchzuführen. Kein WIP darf als Final gelten.

**Abnahme:** Fototreue NICHT belegt; vollständige Rudermechanik NICHT belegt; LAND/WASSER/LUFT NICHT freigegeben.
