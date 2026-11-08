# Hydrofoam v308 | Landkufen-Montage: geometrischer Abstandstest

Status: Prüfstand, **keine Final-, Druck- oder Fahrfreigabe**. Original-Final-Master und v307-CAD unverändert.

## Reproduzierbarer Ist-Befund

`python scripts/audit_v308_skid_interface.py` vergleicht die vier echten v307-Kufen-STLs mit den vier v306-Schwimmersegmenten. Es nutzt 12.000 deterministisch gesampelte Oberflächenpunkte pro Segment und einen KD-Baum für einen **ungefähren, vorzeichenlosen** Abstandstest. Die kleinsten gefundenen Abstände sind links vorne 3,214 mm, links hinten 3,902 mm, rechts vorne 3,264 mm, rechts hinten 3,907 mm. Diese Werte sind **kein exakter Mindestabstand**, keine Kollisionsprüfung und kein Nachweis für Schraubeneingriff.

**Konsequenz:** Die Kufen sind nicht als direkt anschraubbare Teile freizugeben. Vor der Konstruktion von Befestigungsbossen müssen die lokale Schwimmerunterseite, Schraubenachsen, vorhandene Wandstärke und Platz für dichtbare Einlegeteile über exakte Schnitte und Volumenüberschneidungen vermessen werden. Die Montage darf die Hohlkammer nicht unkontrolliert öffnen.

## Konstruktive Freigabesperren

1. Lastpfad Kufe -> Schraube -> Einleger/Boss -> Schwimmerstruktur dimensionieren und geometrisch herstellen.
2. Foil-Tiefpunkt in Landstellung gegen Bodenebene inklusive Federweg/Unebenheit nachweisen; ohne Schutzstellung keine Bodenfahrt.
3. Bodenlenkung, Traktion und Anfahren auf Kurzrasen und Sand real prüfen; eine glatte Kufe allein belegt dies nicht.
4. Wasserabdichtung, Flugmasse, Schwerpunkt, Schub und Steuerbarkeit getrennt abnehmen.

Maschinenlesbarer Befund: `docs/V308_SKID_INTERFACE_SCREEN.json`. Die README-Masterbilder bleiben unverändert, da kein Fototreue-Fortschritt nachgewiesen ist.
