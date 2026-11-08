# Hydrofoam v297 Zusatzpruefung: Trennflaechen und Volumenerhaltung

2026-11-08. Geprueft gegen die tatsaechlich vorhandene v296 Blender-Basis, nicht gegen angenommene Formen.

- Fuenf Schnittpaare, zehn STL: alle geschlossen und winding-consistent. Schnittflaechen-Bounding-Boxen paarweise innerhalb 0.01 mm gleich.
- Zentralrumpf: Quellvolumen 632177.29 mm3; Module zusammen 632173.56 mm3; Differenz -3.73 mm3.
- Schwimmer links/rechts: Quelle jeweils ca. 418947.17 mm3; Module zusammen 418946.70 mm3; Differenz -0.46 mm3.
- **FEHLER GEFUNDEN:** Haupttragflaeche links und rechts: Quellvolumen je 20324.01 mm3; exportierte Teilmodule zusammen je 60972.0 mm3. Das ist +200 % und NICHT freigabefaehig, obwohl alle Meshes watertight melden.
- Die Schnittstudie ist also nur fuer Rumpf und Schwimmer geometrisch volumengetreu. Wing-STLs unter print/v297_wing_modules/ sind als **NICHT DRUCKFREIGEGEBEN** zu behandeln. Volumendifferenz kann aus triangulierten selbstueberschneidenden Flaechen und/oder fehlerhafter urspruenglicher Fluegel-Netztopologie entstehen; Ursache vor Reparatur mit topologischer Analyse belegen.
- Fuer die Fototreue gibt es weiterhin keinen nachgewiesenen Master-Overlay-Abnahmewert. README-Hauptbilder deshalb nicht ersetzen.
- Druckverbindungen, Schalenstaerke, Leichtbau, Servos, Schwerpunkt, 3S-Antrieb und P2S-Slicer-3MF weiterhin offen.

Automatische Pruefdateien: scripts/audit_v297_seams.py, scripts/audit_v297_volume_blender.py, scripts/audit_v297_volume_compare.py; Daten in docs/V297_SEAM_VALIDATION.json, docs/V297_SOURCE_VOLUMES.json und docs/V297_VOLUME_CONSERVATION.json.
