# Hydrofoam v309: acht reale CAD-Dichtungsprototypen

**Nur WIP. Keine Wasser-, Land-, Flug- oder Druckfreigabe.** Ausgangspunkt: bestehende v308-Schwimmerkonturkufen, unverändertes Original-Final-Master-Bild.

Blender 4.5 wurde auf Jens-PC ausgeführt. Die echte v308-Blender-Baugruppe wurde geladen und um acht separate ringförmige Dichtungsprototypen an den bestehenden M3-Achsen ergänzt. Je Ring: Außendurchmesser 10 mm, Innendurchmesser 3,3 mm, Dicke 0,5 mm; Z-Position aus BVH-Strahlschnitt an der echten v306-Schwimmerunterseite bestimmt. Acht STL-Dateien und neue `.blend`-Baugruppe erzeugt.

`python scripts/audit_v309_gaskets.py`: **8/8 wasserdichte, konsistent orientierte Einzelmeshes**, alle innerhalb des P2S-Bauraums. Gesamtvolumen 279,5 mm³. Keine Slicer-Masse und keine Materialfreigabe: elastische Dichtungen benötigen geeignetes flexibles Material, PLA/PETG allein sind keine verlässliche komprimierbare Dichtung.

**Kritische Einschränkung:** Die Ringe sind zunächst planar, nicht der lokalen Schwimmerkontur angepasst; Kompression, Kontakt, Verschraubung, Wandstärken, Insert-Bosse und Leckage sind nicht nachgewiesen. Die Kufenbohrungen bleiben experimentell. Diese Geometrie dient zur räumlichen Positionierung und ersetzt keine belastbare Schraubverbindung. Wasserfoils und Landlenkung sind weiterhin offen.

Dateien: `cad/Hydrofoam_Final_Master_v309_GASKET_WIP.blend`, `print/v309_mounting_gasket_prototypes/*.stl`, `scripts/build_v309_mounting_gasket_prototypes.py`, `scripts/audit_v309_gaskets.py`, `docs/V309_GASKET_QA.json`.

README-Masterbilder bleiben unverändert, da keine gemessene Verbesserung der Fototreue vorliegt.
