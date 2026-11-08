# Hydrofoam v309: Montage- und Bodenkontakt-Prüfplan (Offline-Vorbereitung)

Stand: 2026-11-08. **Nur vorbereitende Ingenieurarbeit im Repository; keine neue CAD-Geometrie, keine Druck- oder Betriebsfreigabe.** Jens-PC war beim Lauf offline. Einziger visueller Master bleibt `reference/FINAL_MASTER_ORIGINAL.jpeg`, SHA-256 `a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd`.

## Befund aus v308

Die vier approximierten, *vorzeichenlosen* Abstände zwischen Kufen- und Schwimmer-Oberflächen betragen 3,214 / 3,902 / 3,264 / 3,907 mm. Sie sagen weder aus, ob die Schrauben in tragendes Material greifen, noch ob die Teile kollidieren. Kein direktes Anziehen der Kufen gegen die dünne Hohlhülle freigeben.

## Konkrete CAD-Arbeit beim nächsten Online-Lauf

1. **Verbindlichen Ausgangsstand feststellen:** `git status --short`, `git log -1`, Master-SHA-256, Blender-Datei v307 und vier v307-Kufen-STLs prüfen. Nicht auf die ältere v306-Angabe zurückspringen.
2. **Exakte Kontaktanalyse:** In Blender oder mit robustem Mesh-Boolean die Kufen gegen die beiden Schwimmer-Hohlkörper schneiden; an jedem der acht M3-Bohrungszentren die vertikale Strahl-Schnittfolge durch Außen- und Innenwand ermitteln. Pro Bohrung Außenhaut-Z, Innenhaut-Z, Wanddicke, freier Abstand und Abstand zur Modultrennfuge als CSV/JSON exportieren. Nicht aus einem unsignierten Punktwolkenabstand auf Kollisionsfreiheit schließen.
3. **Lastpfad und Abdichtung:** Pro Schraubachse einen druckbaren, mit der tragenden Innenstruktur verbundenen Boss bzw. einen durchgängigen lokalen Verstärkungssteg vorsehen. M3-Gewindeeinsatz nur in genügend Material mit nachgewiesener Einsetztiefe; kein Durchbruch in den wasserdichten Schwimmer ohne separat abgedichtete Schraubhülse. Verbindung als eigene, im CAD abnehmbare Komponente modellieren.
4. **Kufenlage:** Neue Montagehöhe aus exakter Kontur ermitteln; Kufe darf nicht frei unter der Schwimmerhülle schweben. Falls Formausgleich erforderlich, formschlüssigen Sattel zwischen Schwimmer und Kufe konstruieren. Vorder- und Hinterkufe dürfen die gemeinsame Modulnaht nicht blockieren.
5. **Foil-Landstellung:** Alle Wasserfoil-/Mast-Unterkanten gegen die tatsächliche Kontakt-Bodenebene der montierten Kufen prüfen. Bodenfreiheit für Ebene und Unebenheit ausgeben. Ohne positiv geprüfte Schutz-/Einzieh-/Abnahme-Lösung keine Landfreigabe.
6. **Druck und QA:** Baugruppen als parametrische FreeCAD-Datei plus Blender-Assembly und STL ausgeben. Je Teil Watertightness, Normalkonsistenz, getrennte Komponenten, P2S-Bauraum, Schraublochdurchmesser, Wanddicken und Passung prüfen. PLA/PETG-Passung zunächst als Druckcoupon verifizieren; Druckschrumpfung und Belastung nicht aus CAD allein ableiten.
7. **Fototreue:** Nur reale CAD-Ansichten mit exakt gleichen Kameraparametern gegen v307 und das unveränderte Masterbild vergleichen. README-Hauptbilder ausschließlich bei belegter Formverbesserung aktualisieren.

## Verbindliche Mehrmoden-Prüfung

- **Land:** Eigenstart auf glattem Boden, Kurzrasen und tragfähigem Sand, Langsamfahrt-Lenkung, Bodenfreiheit, Kufenabrieb und Motorstrom separat messen. Gleiten auf PETG-Kufen ist auf Rasen/Sand nicht garantiert.
- **Wasser:** Statische Verdrängung, Dichtheit, Gleitfahrt und Foil-Übergang nachweisen; die Kufen dürfen den hydrodynamischen Ablauf nicht unzulässig verschlechtern.
- **Luft:** 3S-Schub, Abflugmasse, Schwerpunkt, Ruderwirksamkeit, Stabilität und Propellerfreiheit prüfen. Masse sämtlicher Montageelemente in der Bilanz führen.

## Freigabe

**Nicht freigegeben:** Kufenmontage, Foil-Landfahrt, Wasserbetrieb, Flug. Erst nach geometrischem Nachweis und separaten realen Versuchen entscheiden. Keine sichtbaren Zusatzräder oder andere vom Master abweichende Designmerkmale ohne expliziten Bildabgleich.
