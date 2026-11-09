# v313: Gemeinsame Auslegungsrechnung LAND / WASSER / LUFT (Arbeitsblatt)

Status: **Entwurf, keine Bau- oder Flugfreigabe**. 2026-11-09. Gilt ausschließlich für den Branch `wip/master-image-reconstruction`. Das Referenzbild `reference/FINAL_MASTER_ORIGINAL.jpeg` bleibt unverändert.

## Messgrößen vor dem nächsten CAD-Entscheid
Alle Werte am **montierten Modell** bzw. aus nachvollziehbaren CAD-Massen ermitteln; keine geschätzten Werte als Nachweis eintragen.

| Symbol | Einheit | Ermittlung |
|---|---|---|
| m | kg | Flugfertiges Modell mit Akku, Kufen, Foils und Mechanik wie tatsächlich betrieben |
| S | m² | Tragflächen-Projektionsfläche (aerodynamisch wirksam) |
| CLmax | 1 | Profil-/Konfigurationsnachweis, nicht aus Foto ableiten |
| rho_air | kg/m³ | Umgebungsbedingungen |
| T(v) | N | Gemessener Propellerschub über Fahrtgeschwindigkeit, 3S-Betrieb |
| x_CG, y_CG, z_CG | mm | Bauteilmassen und Schwerpunktlagen im einheitlichen CAD-Koordinatensystem |
| A_foil | m² | Wirksame Foil-Fläche, vollständig eingetaucht |
| CL_foil(v,alpha) | 1 | Validiertes Foil-Modell mit Ventilations-/Kavitationsgrenzen |
| V_displaced | m³ | Eintauchvolumen beider Schwimmer bei gemessener Wasserlinie |
| mu_eff | 1 | Effektiver Kufen-Reibbeiwert getrennt für festen Boden, Kurzrasen und tragfähigen Sand |
| F_sand/grass | N | Gemessener zusätzlicher Eindring-/Pflugwiderstand |
| h_min | mm | Minimaler Bodenabstand sämtlicher Foils/Masten/Propeller bei Nick- und Rollbewegung |

## Vorläufige Rechen-Gates (kein Ersatz für Messungen)
- **Land-Anfahren:** `T(0) > mu_eff * m * g + F_sand/grass` mit Sicherheitsreserve; bei Rasen und Sand **separat** messen. Pusher-Luftstrahl allein belegt keine Lenkbarkeit im Stand.
- **Wasser-Stillstand:** `rho_water * g * V_displaced >= m * g` bei zulässiger Wasserlinie, plus Reserve für Krängung, Wellen und Spritzwasser. Dichtigkeitsprüfung getrennt.
- **Foil-Heben:** `0.5 * rho_water * v² * A_foil * CL_foil >= m * g - F_buoyancy(v)`; für Stabilität zusätzlich Nickmoment und Rollmoment um den Schwerpunkt bilanzieren. Foils dürfen in Landkonfiguration nicht exponiert sein.
- **Flug-Stallgrenze:** `V_stall = sqrt(2 * m * g / (rho_air * S * CLmax))`; ohne belastbares `CLmax` keine belastbare Mindestgeschwindigkeit. Schubreserve über den relevanten Geschwindigkeitsbereich und aerodynamische Stabilität sind separat zu belegen.
- **Schwerpunkt:** `r_CG = sum(m_i * r_i) / sum(m_i)`; Konfigurationen Land/Wasser/Luft einzeln berechnen, einschließlich Mechanikstellung und Wasseraufnahme.
- **Struktur:** Kufenbefestigung nicht nur auf Scherung der M3-Schrauben auslegen. Lochleibung, PETG-Kriechen, Schraubenvorspannung, Ausreißen, Dichtung und lokale Schwimmerwandstärke prüfen.
- **Land-Foil-Freigang:** `h_min > 0` genügt nicht; Einfedern/Verwindung, Sand-/Grasbuckel, Verschleiß und Anstellwinkeländerungen als Toleranzkette addieren. Mindestreserve erst nach Vermessung festlegen.

## Nächster produktiver CAD-Lauf auf Jens-PC
1. SHA256 des Originalbilds gegen `a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd` prüfen; Datei niemals überschreiben.
2. Regressionstests v310/v311 und Gate v312 ausführen; Rohdaten der acht Kufenpunkte sichern. Fehlerhafte Messungen **nicht** in CAD übernehmen.
3. Reale Schnittgeometrie und Wandstärken beider kantigen Schwimmer erfassen; darauf abgestimmte, demontierbare, abgedichtete PETG-Kufenaufnahme als parametrische FreeCAD-Baugruppe erzeugen.
4. Foil-Landstellung im selben Koordinatensystem modellieren; Kollisions- und Freigangprüfung in extremer Nick-/Rollstellung.
5. Baugruppenmasse und Schwerpunkt für alle drei Konfigurationen exportieren; STL auf Wasserdichtheit/Manifoldness und P2S-Bauraum prüfen.
6. CAD-Ansichten gegen Masterbild vergleichen und QA-Protokoll mit Rohwerten, Skriptversion, Git-Commit und offenen Punkten ablegen. README-Masteransichten nur bei **belegter** Verbesserung ändern.

**Sperre:** Kein `Final` und keine Behauptung von Land-, Wasser- oder Flugtauglichkeit ohne getrennte reale Abnahme gemäß `docs/LAND_WATER_AIR_REQUIREMENTS.md`.
