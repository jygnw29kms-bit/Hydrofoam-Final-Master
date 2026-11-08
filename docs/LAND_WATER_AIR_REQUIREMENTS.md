# Hydrofoam: Land + Wasser + Luft (verbindliches Betriebsziel)

**Status 2026-11-08:** Verbindliche Produktanforderung und technische Integrationsplanung. Noch kein Nachweis der Betriebsfaehigkeit. Der originalgetreue Master bleibt unter [FINAL_MASTER_ORIGINAL.jpeg](../reference/FINAL_MASTER_ORIGINAL.jpeg) dauerhaft unveraendert.

## Verpflichtende Betriebsarten

1. **LAND:** Selbststaendiges Fahren/Anfahren auf trockenem festem Untergrund, kurz gemähtem Rasen und tragfaehigem Sand. Das Modell muss mit eigenem Antrieb vorwaerts rollen/gleiten, lenkbar, bodenstabil und vor Sand-/Schmutzeintrag geschuetzt sein. Rollwiderstand und Flaechenpressung getrennt untersuchen.
2. **WASSER:** Schwimmstabilitaet, verteilte Auftriebslast, kontrollierte Gleitfahrt, Foil-Auftrieb und wiederholbarer Uebergang zwischen Verdrängung, Gleiten und Foil-Fahrt. Wasserdichte Elektronik und verstaerkte Maste sind Pflicht.
3. **LUFT:** Flugfaehigkeit als Starrfluegler mit ausreichendem Schub, Fluggeschwindigkeit, Auftrieb, Steuerbarkeit und Strukturfestigkeit. Fliegender Propeller muss einen sicheren Abstand zu Wasser, Gras und Boden haben. Bodentrimm und hydrodynamischer Trimm duerfen Flugschwerpunkt nicht unguenstig verschieben.

**Keine** dieser Betriebsarten ist optional. Eine reine Wasserfahrzeug-Optimierung oder ein Foil-only-Modell waere ein Anforderungsfehler.

## Final-Master Form bleibt unveraendert

- Die zwei seitlichen, kantigen Schwimmer, Zentralrumpf, mittige vorgezogene Nase, Fluegel, Heckflossen und der hochliegende Heck-Pusherantrieb bleiben von aussen wie auf dem Masterbild.
- Im Original sind schwarze, unter den seitlichen Schwimmern anliegende Laengskufen zu sehen. Sie werden als **austauschbare Multi-Surface-Glide-Skids** ausgelegt: verschleissarm auf tragfaehigen Boden und Gras, hydrodynamisch kontrolliert im Wasser. Das bedeutet nicht, dass sie bereits auf Sand oder Rasen ausreichend funktionieren.
- **Land-Bodenkontakt** muss technisch unter dem bereits sichtbaren Kufenbereich gelöst werden; abnehmbare Bodengleitplatten/Rollen sind als zusaetzliche Technikmodule pruefbar, jedoch nicht automatisch genehmigte sichtbare Formveraenderungen. Jede sichtbare Bauform gegen das Foto-Master pruefen.
- Unterwasserfoils muessen so integriert werden, dass sie auf Land nicht in Boden/Rasen einschlagen: einziehbar, abnehmbar oder geschuetzt. Die technische Wahl ist offen, bis Foil-Geometrie, Gewicht und Belastungen geprueft sind.
- Ein hoher Pusherpropeller kann Grundvortrieb liefern, aber weder ausreichende Anfahrkraft auf Rasen/Sand noch sichere Bodenfreiheit oder die Flugleistung ohne Messung garantieren.

## Konstruktionsplan nach Baugruppe

| Baugruppe | Land | Wasser | Luft | CAD-Zustaendigkeit |
|---|---|---|---|---|
| Zwei Schwimmer | tragende Kufen, definierte Bodenfreiheit | Auftrieb, Chines, Spritzschutz | Formwiderstand und Masse minimieren | Blender Huelle + FreeCAD Kufensitze |
| Unterseitenkufen | PLA/PETG-Bodenkontaktplatten, moegliche Rollmodule | Gleit-/Wasserkontakt, Austausch | wenig Gewicht und Widerstand | FreeCAD |
| Unterwasser-Foils & Masten | Bodenfreiheit/Schutz oder eingefahren | Foil-Auftrieb, Nick-/Rollstabilitaet | eingefahren bzw. geringer Widerstand | FreeCAD |
| Zentralrumpf | Gewichtsverteilung, Akku sichern | abgedichtete Haube, Spritzwasser | Schwerpunkt, Tragwerksanschluss | Blender + FreeCAD |
| Propeller/Motor | Sand-/Gras-Abstand, Schub gegen Reibung | Spritzabstand, Schub fuer Wasserstart | ausreichende Schubreserve und Flugleistung | FreeCAD |
| Servos & Ruder | Bodenlenkbarkeit pruefen; Rudern nur im Luftstrom ggf. schwach | Ruderwirksamkeit, Foilsteuerung | Nick/Gier/Rollsteuerung | FreeCAD |
| Elektronik | Vibrationsschutz, Schmutz | Wasserdichtung, Entwaesserung | Kuehlung bei Fluglast | FreeCAD |

## Mess- und Abnahmekriterien

### Land
- [ ] Start auf glattem, trockenem Boden ohne Fremdanschieben; Testvideo und Startstrecke dokumentiert
- [ ] 10 m geradeaus sowie kontrollierter links/rechts Kurvenversuch bei niedriger Geschwindigkeit
- [ ] Kurzrasen, dann trockener, tragfaehiger Sand separat testen; keine voreilige Zusage ueber tiefen Sand
- [ ] Kufenverschleiss, Luftschraubenfreiheit, Akku- und Motorstrom dokumentiert
- [ ] Keine ungeschuetzte Foil-Spitze beruehrt den Boden

### Wasser
- [ ] Schwimmtest im Stillstand mit korrekter Wasserlinie, leerer und eingebauter Elektronik
- [ ] Dichtigkeit der Kabinen-/Elektronikbox separat nachweisen
- [ ] Gleitfahrt, Foil-Uebergang, Geradeausstabilitaet und Kurvenverhalten mit Messwerten dokumentiert
- [ ] Keine Foil-Ventilation / unkontrollierbare Nickschwingung bei Testgeschwindigkeit

### Luft
- [ ] Gesamt-Abfluggewicht auf echter Waage innerhalb der Projektgrenze
- [ ] Flugschwerpunkt und Längs-/Querstabilität mit Massenbilanz und Flugmodell bewertet
- [ ] Motor/Propeller auf 3S unter Last auf Strom, Temperatur, Schub, Leistungsreserve geprüft
- [ ] Aero-Kontrolle über alle Flugachsen, ausreichende Boden- und Flächensicherheit
- [ ] Erstflug nur nach freigegebenen Stand- und Rolltests im geeigneten Gelände

## Konkrete Folgearbeit ab v306

1. Unterseiten-Geometrie von beiden **kantigen Master-Schwimmern** auf ebenen, tragenden Kontakt, Bodenfreiheit und abriebfeste austauschbare PETG-Kufen analysieren.
2. Separate FreeCAD-Kufen-/Bodenmodulaufnahme mit verdeckten Verschraubungen und reproduzierbaren Schnittstellen konstruieren.
3. Konstruktive Landlenkung untersuchen: aerodynamische Steuerung allein bei niedriger Rollgeschwindigkeit möglicherweise unwirksam; Bodenkontakt-Lenkprinzip/Schubdifferenzierung nur nach Messung festlegen.
4. Foil-Aufnahmen inklusive freier Bodendurchfahrt und Land-Schutzstellung auslegen, ohne die Master-Huelle sichtbar zu aendern.
5. Gemeinsames Gewichts-/Schwerpunktbudget aller drei Modi in einer Bilanz zusammenfuehren; bei Konflikten zuerst Sicherheit, danach das bereits verbindliche Design und das Gewichtsbudget.
6. Zuletzt die drei Betriebsarten **getrennt** abnehmen, nie eine Wasserprobe als Nachweis von Land oder Flug werten.

**Freigaberegel:** `Final` erfordert bestandene Nachweise fuer Land, Wasser und Luft, dazu Fototreue und P2S-Modul-Druckbarkeit. v306 erfuellt das noch nicht.
