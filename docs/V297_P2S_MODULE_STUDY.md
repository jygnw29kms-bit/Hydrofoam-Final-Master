# Hydrofoam v297 - P2S Modul-Schnittstudie (2026-11-08)

## Eingang
Unveraenderte Form-Basis: v296, Commit 90f5ba8. Foto-Master ist verbindliche Aussenform. Keine neuen Laengen, Formen oder Texturen erfunden.

## Konstruktion
Die fuenf nach X zu grossen Bauteile wurden geometrisch entlang ebenen Trennflaechen geteilt, an der Schnittflaeche geschlossen und als eigenstaendige STL-Dateien exportiert:
- Zentralrumpf bei X=-15 mm in zwei Module
- Schwimmer links/rechts bei X=-10 mm in je zwei Module
- Haupttragflaechen links/rechts bei X=-10 mm in je zwei Module

Gesamt: 10 Module aus 5 urspruenglich ueberlangen Mesh-Objekten. Bearbeitbare Blender-Schnittstudien und automatisiert reproduzierbare Skripte im Repo.

## Gepruefte Maximal-Abmessungen (mm, X x Y x Z)
|Modul|X|Y|Z|
|---|---:|---:|---:|
|Zentralrumpf vorne|209.85|86.60|47.20|
|Zentralrumpf hinten|217.15|78.76|33.64|
|Schwimmer links/rechts vorne, je|153.89|59.50|41.84|
|Schwimmer links/rechts hinten, je|179.63|59.45|41.31|
|Haupttragflaeche links/rechts vorne, je|155.00|95.40|3.96|
|Haupttragflaeche links/rechts hinten, je|180.00|189.44|6.40|

Die Einzelmeshes passen in einer achsparallelen Orientierung innerhalb der P2S-Grenze von 256 mm pro Achse; reale Slicer-Bauplattenauslastung, Raender, Support und brim sind NICHT abgenommen.

## Qualitaetspruefung
- 10/10 Module: watertight=true, winding consistent=true nach Trimesh-Exportpruefung.
- Schnittflaechen wurden durch bmesh bisect + holes_fill geschlossen.
- Front/Rear-Verwechslungsfehler im ersten Export wurde erkannt, korrigiert und erneut exportiert.
- Grundform des urspruenglichen v296-Modells bleibt erhalten, die nicht geteilten Bauteile unveraendert.

## Offene, zwingend notwendige Arbeit
1. Druckmodul-Verbindungen: Passstifte, Aufnahmebohrungen, Klebe-/Schraubflaechen; Festigkeits- und Toleranzpruefung.
2. Fluegel-/Rumpf-Fairings bislang ueberlappend und nicht solide vereint.
3. Massen, Wandstaerken und Materialverbrauch der tatsaechlich ausgehoehlten Druckteile; aktuell geschlossene Volumina sind keine fertigen Leichtbau-Schalen.
4. Druckorientierung, Stuetzelemente und exportierbare Bambu-P2S 3MF Projekte.
5. Foto-Overlay: Vorderansicht, Draufsicht, Seitenansicht; noch keine photogetreue Abnahme.
6. Echte Mechanik, RC-Komponenten, Servoeinbau, Antrieb, Ruderhoerner, Akku, Schwerpunkt und Lastfaelle.

Kein Final-Status. v297 ist eine belastbare geometrische Schnittstudie, kein sofort druckfertiger Gesamtsatz.
