# Hydrofoam v299: vermessene Modul-Trennflaechen

Stand: 2026-11-08. Grundlage: v297 Rumpf/Schwimmer, v298 korrigierte Hauptfluegel. Keine neue Form erdacht.

Die reale STL-Schnittgeometrie wurde anhand der auf X=-15 bzw. X=-10 mm liegenden Dreiecke analysiert. Front/Rear-Flachen sind paarweise flaechenidentisch (Differenz <0.000001 mm2).

| Schnitt | Flaeche mm2 | Y-Breite mm | Z-Hoehe mm |
|---|---:|---:|---:|
| Zentralrumpf | 2079.55 | 78.76 | 33.64 |
| Schwimmer links | 1927.83 | 59.45 | 41.31 |
| Schwimmer rechts | 1927.83 | 59.45 | 41.31 |
| Hauptfluegel links | 236.51 | 78.84 | 3.93 |
| Hauptfluegel rechts | 236.51 | 78.84 | 3.93 |

**Konstruktive Folgerung:** Die Fluegel besitzen an der Trennung nur knapp 3.93 mm Profilhoehe. Runde Stifte, Schrauben oder Holmaufnahmen mit Wandstaerken duerfen hier NICHT ohne weitere konstruktive Untersuchung eingesetzt werden. Die Fluegel brauchen ein gezielt dimensioniertes flaches Holm-/Laschenkonzept oder eine andere Trennposition, mit Lastfallrechnung und Flaechenvergleich gegen den Original-Master.

Rumpf und Schwimmer haben deutlich groessere Trennflaechen. Dennoch sind deren aktuelle STL-Schnittkappen volle Scheiben und keine belastbar ausgelegten Verbindungsflaechen. Fuer PETG/PLA muessen Druckrichtung, Laminat-Anisotropie, Passung, Abdichtung, Wasserlast und Antriebs-/Landebelastung nachgewiesen werden.

**Pruefgrenze:** Die Flachenidentitaet zeigt Registrierbarkeit, nicht mechanische Tragfaehigkeit oder Fertigungsfreigabe. Es wurden in diesem Durchlauf keine mechanischen Verbinder eingebaut, weil die Material- und Lastpfade noch nicht ausgelegt sind. Keine Aenderung an README-Hauptbildern; kein Final-Status.

Automatisch reproduzierbar: scripts/audit_v299_joint_sections.py, Rohwerte: docs/V299_JOINT_SECTIONS.json.
