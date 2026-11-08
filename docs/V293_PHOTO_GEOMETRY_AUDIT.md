# Hydrofoam v293: fotobasierter Form-Neuaufbau

Datum: 2026-11-08

## Verbindlicher Master
Das vom Nutzer hochgeladene einzige Referenzbild „Futuristischer RC-Hydrofoil mit Detailansichten.png“ zeigt die 3/4-Ansicht, Draufsicht, Seitenansicht und vier technische Detailausschnitte. Es ersetzt alle älteren approximativen Forminterpretationen. Die Bilddatei liegt derzeit als Original im Chat-Anhang; auf dem PC sind nur ältere Bildmasken vorhanden.

## Geometrieverbesserung gegenüber v292
- Mittelrumpfnase beginnt bei X=-225 mm und liegt sichtbar vor den äußeren Schwimmerspitzen bei X=-164 mm (zuvor umgekehrt).
- Beide Schwimmer neu loft-basiert mit eigenständiger Gleitunterseite und schwarzen, abnehmbar zu konstruierenden PETG-Kufen.
- Geänderte geschwungene Tragflächen, hintere Außenflügel, orange Streifen, Elevons.
- Aufrechte, nach hinten geschwungene Seitenleitwerke mit orangenen Spitzen und dunklen Einsätzen.
- Dunkle Kanzel in eigenen Loftstationen und Pusher-Motorbrücke mit Querholm.
- 42 Mesh-Objekte in der Blender-Datei.

## Konkrete Dateien
- cad/Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.blend
- cad/Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.stl
- scripts/build_v293_photo_geometry.py
- scripts/render_v293.py
- renders/v293/{assembled_iso,assembled_top,assembled_side,assembled_front}.png
- print/v293_individual_meshes/ (42 separat exportierte STLs)

## Prüfstand
- Aggregat-STL: 2535 Eckpunkte, 4920 Dreiecke, Geometrieausdehnung X 445 mm / Y 474 mm / Z 168.9 mm.
- Aggregat-STL is_watertight=False. Sie fasst überlappende Volumenkörper und Dekorteile zusammen und ist nicht als einteiliger Druck freigegeben.
- Einzelteile: 42/42 separat exportierte Mesh-STLs sind laut trimesh is_watertight=True.
- Damit ist ausdrücklich noch NICHT nachgewiesen: kollisionsfreie Baugruppen, passgenaue Steck- und Schraubverbindungen, Druckorientierung, Masse, aerodynamische und hydrodynamische Funktion, sichere Elektronik- und Motorbefestigung.
- Höhe Z beinhaltet Propeller/Motor; die bildbasierte Höhenfestlegung ist noch nicht kalibriert.
- Geometrie ist weiterhin sichtbar grob; Abnahme der Bildtreue aus Front-/Seiten-/Top-/ISO-Overlay fehlt.

## Reihenfolge für nächste Iterationen
1. Fotogerechte Verjüngung und S-förmige Übergänge von Nasen-/Cockpitdeck zur Tragfläche.
2. Flügel-/Schwimmeranschlüsse ohne harte Überschneidungen modellieren.
3. Heckansicht, Heckflossenprofil und angetriebene Propeller-Naben-Geometrie verfeinern.
4. Mechanische Baugruppen mit Verschraubungen, Passflächen und Bauraum für vorhandene Motor-/Servo-/Akku-Hardware.
5. P2S-bettgerechte Modulschnitte und Druckprofile für PLA/PETG, Gewichts- und Belastungsrechnung.
6. Bilder direkt gegen das Nutzer-Masterbild prüfen und nur nach echter Deckung die Final-Freigabe setzen.
