# Hydrofoam RC-Hydrofoil | FreeCAD + Blender Engineering Workflow

> **Status:** Konstruktions-Workflow, keine Final- oder Flugfreigabe. **Designautorität:** ausschließlich das originale, vom Nutzer hochgeladene Final-Master-Mockup. **Repository:** `Hydrofoam-Final-Master`; Entwicklungsbranch `wip/master-image-reconstruction`.

## 0. Verbindliche Designregeln

Das Originalbild zeigt: weiße/orange Außenform, längere mittige Rumpfnase, zwei nach hinten versetzte seitliche Schwimmer, geschwungene Haupttragflächen mit organischen Übergängen, dunkle Kanzel, Pusher-Motor hinter der Kanzel und zwei äußere Heckleitwerke. Die unsichtbare Unterseite sowie Unterwasser-Foils dürfen **technisch ergänzt**, aber nicht als bildlich belegt ausgegeben werden. Jede neue Formvariante erhält einen Vorher/Nachher-Vergleich mit Top-, Seiten-, Front- und isometrischer Ansicht; keine AI-generierten Illustrationen als Nachweis einer CAD-Konstruktion.

**Funktionsziel:** (1) Wasserverdrängungs-/Gleitfahrt, (2) Foil-Fahrt mit Auftrieb durch im Wasser befindliche Foils, (3) Freiflug. Diese drei Betriebszustände müssen separat in Stabilität, Antrieb, Regelung und Schwerpunkt nachgewiesen werden. Ein im Wasser gut tragendes Foil ist nicht automatisch für das Fliegen geeignet und kann großen Luftwiderstand verursachen.

## 1. Verbindliche Daten und offene Variablen

| Parameter | Aktueller Projektstatus | Bedeutung |
|---|---|---|
| Abfluggewicht | Ziel 600–625 g, harte bisherige Grenze 650 g laut Repository-README | Nicht ohne Massenbilanz auf 800 g ändern |
| Maßliche Ausgangsform | Bildrekonstruktion; jüngstes Blender-Formmodell v298, v299 Fugenprüfung | Endmaße bis zur Master-Skalierung **nicht freigegeben** |
| Beispielhülle v293 | ca. 445 × 474 × 169 mm inkl. Modell-Anbauten | Technischer Zwischenstand, **kein** Master-Nennmaß |
| Drucker | Bambu Lab P2S, 256 × 256 × 256 mm, 0,4-mm-Düse | Druckreserve und Platzierungsprüfung vorsehen |
| Material | Ausschließlich PLA und PETG | PLA für leichte strukturierte Schalen, PETG für nasse, stoßbeanspruchte und austauschbare Teile; tatsächliche Eigenschaften testen |
| Antrieb | Historische README-Basis: SunnySky X2212 2450KV, 3S, 40-A-ESC, APC 6×4 | Nur Planungsstand. Motorstrom, Propellerfreigabe und Leistungsbedarf messen |
| RC | Historische README-Basis: vier JX PDI-1109MG-Klasse-Servos | Wirkliche Abmessungen, Rudermomente und Stromaufnahme vermessen |
| Foil-Typ | **Offen**: T-Foil, V-Foil oder mehrere Foils | Nicht anhand einer einzelnen Designansicht festlegen |
| Akku | Historische Basis: 3S 2200 mAh | Abmessungen, tatsächliche Masse und Schwerpunkt prüfen |

**Wichtig:** Ein einzelnes perspektivisches Masterbild erlaubt **keine** sicheren absoluten Maße. Der CAD-Maßstab wird nur aus einem separat beschlossenen Referenzmaß festgelegt. Keine Annahme wie „Rumpf 500 mm“ als bestätigte Nutzervorgabe behandeln.

## Phase 1: FreeCAD | Hydrodynamik und belastbare Mechanik

### 1.1 Projekt-Masterdatei und globale Parameter

1. Neues FreeCAD-Dokument `cad/freecad/Hydrofoam_Master_Parameters.FCStd` erstellen; Einheiten **mm, kg, s, Grad** festlegen.
2. Arbeitsbereich **Spreadsheet** öffnen: neues Spreadsheet erstellen und als **`Params`** benennen. Spalten: `Gruppe`, `Alias`, `Wert`, `Einheit`, `Freigabe/Quelle`.
3. Jede Wertzelle über Rechtsklick → **Eigenschaften** mit einem Alias versehen. Präfixe `HF_` (Hydrofoil), `STR_` (Strut), `BOX_` (Elektronikbox), `MTR_` (Motor), `JNT_` (Verbindung), `HULL_` (Rumpf).
4. Im Expression-Editor eines Skizzenmaßes oder einer Feature-Eigenschaft `<<Params>>.HF_Chord` einsetzen, wenn das Tabellenlabel `Params` lautet. Die konkrete Funktion entspricht der FreeCAD-Spreadsheet-/Expressions-Dokumentation.
5. Designvariablen wie `HF_AoA` und `HF_Incidence` nicht mit Ruderanstellwinkeln verwechseln: `AoA` beschreibt den tatsächlich angeströmten Winkel, `Incidence` die mechanische Einbaulage. Für Belastung zusätzlich separate Betriebswinkel untersuchen.

**Tabellenvorlage**, Anfangswerte nur als ausdrücklich zu validierende Testparameter:

| Alias | Testwert | Definition |
|---|---:|---|
| `HF_Chord` | 55 mm | Profilsehne des Unterwasserfoils |
| `HF_Span` | 180 mm | Summe der wirksamen Spannweiten je Foil-Element |
| `HF_Profile` | NACA 0012 | Erste symmetrische Vergleichsgeometrie, kein freigegebenes Optimum |
| `HF_Incidence` | 2° | Mechanischer Test-Anstellwinkel |
| `HF_Submerge` | 45 mm | Foil-Tiefe unter Referenz-Wasserlinie im Versuchsfall |
| `STR_Thickness` | 5 mm | Anfangsdicke des Masts, statisch zu prüfen |
| `BOX_Wall` | 2.4 mm | Startwert für 0,4-mm-Düse; nicht als Dichtigkeitsgarantie |
| `BOX_SealCord` | 2.0 mm | Beispiel-O-Ring-Schnurstärke, genauen Ring noch wählen |
| `BOX_SealCompression` | 0.20 | Zielkompression im Muster, abhängig vom O-Ring-Werkstoff |
| `MTR_Tilt` | 0° | Einstellbarer Schubvektorwinkel |
| `JNT_Clearance` | 0.25 mm | Startwert für einseitiges FDM-Passspiel, per Testcoupon prüfen |

Es gelten beispielsweise `FoilArea = HF_Chord × HF_Span` für eine rechteckige Abschätzung und `BOX_GrooveDepth = BOX_SealCord × (1 - BOX_SealCompression)` **nur als Vorentwurf**. Nutabmessungen und Füllgrad sind mit dem tatsächlichen O-Ring-Datenblatt festzulegen; die freie Nutbreite wird nicht allein aus dem Kompressionswert bestimmt.

**Dokumentgrenze:** FreeCAD-Spreadsheets sind parameterbasierte Referenzen, keine globalen, automatisch in jeder externen FCStd-Datei verfügbaren Variablen. Für mehrere Dateien gemeinsame Parameter über explizite Links/Referenzen, oder aus einer zentralen Parameterquelle reproduzierbar erzeugen.

### 1.2 Hydrofoil-Profil in Part Design

1. Neues Dokument `Foil_Front.FCStd`, einen **Body** `Foil_Front` anlegen und eine Skizze auf der lokalen XY-Ebene erzeugen.
2. NACA-Koordinaten generieren oder importieren. Die Koordinaten sind normiert auf die Sehne `x/c`, `y/c`. Bei einem vierstelligen symmetrischen NACA-00xx-Profil definiert `xx` die maximale relative Dicke. Eine offene/geschlossene Hinterkante muss bewusst festgelegt werden.
3. Koordinaten im Sketcher als B-Spline/Segmentkontur abbilden; Skizze schließen. Die Endpunkte am Hinterrand auf Druck- und Festigkeitstauglichkeit prüfen. Für eine definierte Foil-Spannweite **Pad** verwenden; für Verjüngung und Verdrehung mehrere Skizzen mit **Additive Loft** verbinden.
4. Für variable Inzidenz Winkel nicht willkürlich am Profil ändern: einen separaten **Datum Plane** auf die Lage der Foil-Wurzel legen und dessen Drehung über `<<Params>>.HF_Incidence` führen.
5. In `Foil_Strut.FCStd` eigene Bodies für linke/rechte Masten verwenden: Skizze einer strömungsgünstigen, symmetrischen Profilkontur → Pad oder Additive Loft. Übergänge über Additive Pipe/Loft mit Querschnitten ausrunden, Fillets **nach** dem Grundkörper.
6. Mast/Foil-Knoten mit Durchsteck-Holm, metallischem Verbindungselement oder formschlüssiger Lasche **als separaten Lastpfad** auslegen. Keine reine 1–2-mm-PLA-Haut als Foil-Krafteinleitung verwenden.
7. Trenne hydrodynamische Oberfläche und mechanische Einbauflächen: Scharnier, Schrauben, Sitz- und Dichtflächen werden in FreeCAD bemaßt. Ein **Lagepunkt** und ein lokales Foil-Koordinatensystem markieren die Schnittstelle zum Blender-Rumpf.

**Hydrodynamische Vorbemessung** pro Betriebspunkt: `L = 0.5 × ρ_water × V² × S × CL`; `D = 0.5 × ρ_water × V² × S × CD`. Für Süßwasser als erste Näherung `ρ_water ≈ 1000 kg/m³`. Beispiel **nur zur Größenordnung**: Für 0,65 kg Gewicht, `S = 0.0099 m²` und `CL = 0.4` folgt `V = sqrt(2 m g / (ρ S CL)) ≈ 1.80 m/s`. Das ist keine Abhebegarantie, denn reale Foils benötigen ausreichende Eintauchtiefe und Stabilität; Ventilation, Kavitation, Reynolds-Zahl, Rumpfwiderstand, Strut-Widerstand und Lastverteilung sind zu prüfen.

Für Flug gilt die analoge Gleichung mit **Luftdichte** und den tatsächlichen lufttragenden Flächen; die Wasserfoils allein liefern keine brauchbare Flugauslegung. Tragflächenbelastung, Fluggeschwindigkeit und Motorreserve separat berechnen.

### 1.3 Wassergeschützte Elektronikbox: reproduzierbarer Part-Design-Bauablauf

1. In `Electronics_Enclosure.FCStd` den Body `BOX_Base` anlegen. Skizze auf XY-Ebene: Außenkontur mit abgerundeten Ecken. Maße über `BOX_InnerLength`, `BOX_InnerWidth`, `BOX_Wall` führen.
2. Mit **Pad** zur Boxhöhe extrudieren.
3. Auf der Oberseite eine neue, innen umlaufend zurückgesetzte Skizze erzeugen. Über **Pocket** bis zur benötigten Innentiefe ausschneiden. Der geschlossene Boden bleibt mit separatem Parameter `BOX_Floor` bestehen.
4. Umlaufenden, ebenen **Dichtflansch** um die Öffnung vorsehen. Vier bis acht Schraubdome in belastbaren Zonen mit Pad oder separaten Skizzen erzeugen. Schraubpositionen so legen, dass der Flansch zwischen ihnen nicht unzulässig aufbiegt.
5. Für eine rechteckige geschlossene Dichtschnur eine Skizze mit zwei ineinander liegenden abgerundeten Rechtecken auf dem Flansch erzeugen. **Pocket** mit parametrisierter Nuttiefe anwenden. Alternativ bei rotationssymmetrischer Ringnut eine Skizze für den Nutquerschnitt erstellen und **Groove (subtractive revolution)** um eine definierte Achse verwenden. **Groove ist für eine rechteckige umlaufende Flanschdichtung nicht der Standardweg.**
6. Deckel `BOX_Lid` als **eigenen Body** mit Pad und ggf. innerer Zentrierlippe anlegen. Die Lippe darf die Dichtung nicht unkontrolliert quetschen. Montageanschläge für definierte Kompression vorsehen.
7. Durchgangsbohrungen im Deckel mit **Hole** bzw. Pocket erzeugen; Grundkörper bei Bedarf mit Gehäusegewinden, Messing-Gewindeeinsätzen oder separaten Muttern auslegen.
8. Kabel nicht durch „ein Loch mit Silikon“ führen. Eine zugentlastete, geeignete Kabelverschraubung oder einen separat gedichteten Steckverbinder mit passenden Freiräumen bemaßen.
9. Unterseite der Box über vier elastisch entkoppelte Befestigungspunkte an einem **FreeCAD-definierten** Rumpfträger montieren, Wasserlinie berücksichtigen.
10. Dichtigkeitsprüfung mit Dummy-Elektronik, Druck-/Unterdruck- oder Spritzwasserprüfung und Temperaturwechsel durchführen. Ein geometrisch geschlossener Körper ist **nicht** automatisch wasserdicht; keine IP-Einstufung ohne standardkonformen Test vergeben.

### 1.4 Motorhalterung, Mastaufnahme und tragende Flügelmodule

1. `Motor_Mount.FCStd`: neues Body `MTR_Bracket`; am Master-Propellerzentrum ein Datum Point + Datum Axis anlegen. Befestigungslochkreis **aus dem realen Motor-Datenblatt** übernehmen.
2. Skizze für Motorplatte, **Pad**, Bohrungen mit Hole; lasttragende Seitenstege als separate Skizzen/Pad bzw. Additive Loft aufbauen. Große Übergangsradii und definierte Wandungen verwenden.
3. Drehmoment, Motorschub, Schlaglasten und Propellerschwingungen als eigenständige Lastfälle prüfen. Propellerkreis gegen Haube, Flügel und Leitwerke auf Abstand testen; Sicherheitsabstand auch für Blattdurchbiegung und Vibration berücksichtigen.
4. `Foil_Receiver.FCStd`: Mastwurzel als geradlinigen Einsatz mit durchgehendem strukturellem Anschluss konstruieren, dessen Kraft in den verstärkten Rumpf/Holm eingeleitet wird. Unterwasserseitige Schrauben und Spalten abdichten; austauschbare Masten vorsehen.
5. Die aktuellen Trennflächen sind dokumentiert: Zentralrumpf **2079.55 mm²**, Schwimmer je **1927.83 mm²**, Hauptflügel je **236.51 mm²**. Am Flügelschnitt ist die verfügbare Profilhöhe nur **3.93 mm**. Dort **keine normalen Rundstifte oder Gewindeschrauben in die Haut pressen**; flache, längs überlappende Holm-/Laschensysteme, angepasste Schnittposition oder größere innere Lastpfade auslegen.
6. Für alle Verbindungen aufeinander abgestimmte Passflächen, Testcoupons und Montage-Reihenfolge definieren; mechanische Festigkeit bei Nässe und Aufprall separat testen.

## Phase 2: Blender | Mastergetreue Außenform und ultraleichter Oberwasserrumpf

### 2.1 Koordinatenvertrag FreeCAD ↔ Blender

- Gemeinsames System **X = Längsrichtung (Bug negativ), Y = rechts positiv, Z = nach oben positiv**, Ursprung an einer **fest dokumentierten Referenz** im Zentralrumpf; alle Modelle in Millimetern auslegen.
- Blender-Einheiten: `Unit System = Metric`, `Unit Scale = 0.001`, `Length = Millimeters`. Alternativ Scale=1 mit expliziter `mm↔m`-Export-Transformation verwenden, aber **nicht beide Methoden mischen**.
- Für jeden mechanischen Fixpunkt Namen und Lage dokumentieren, z. B. `MTR_AXIS`, `CG_TARGET`, `FOIL_FRONT_ROOT_L/R`, `FOIL_REAR_ROOT`, `BOX_MOUNT_01..04`, `WING_SPAR_L/R`, `WATERLINE_REF`.
- Aus FreeCAD **STEP AP242** (wenn im verwendeten FreeCAD verfügbar) für präzise B-Rep-Mechanik exportieren, **STL oder OBJ als triangulierte, unverbindliche Referenz in Blender**. Blender importiert STEP nicht nativ als parametrische B-Rep-Geometrie. STEP nicht durch zufällige Mesh-Konvertierung als neue mechanische Datenquelle ersetzen.
- Export als `mechanical_interfaces.step`, `mechanical_interfaces.stl`, `interfaces.json` mit Punktkoordinaten, Einheiten, Matrix, Dateiversion und Prüfsumme. Das JSON ist der verbindliche Übergabevertrag. Bei einer Änderung mechanischer Fixpunkte müssen Blender-Referenzen neu geladen und geprüft werden.

### 2.2 Außenhaut nur nach Final Master

1. Master-Bild in Blender als Referenzebene laden. Unterschiedliche Ansichten nur dann orthografisch ausrichten, wenn sie tatsächlich orthografisch sind; perspektivische Verzerrungen nicht als exakte Maßdaten verwenden.
2. Zuerst folgende Silhouetten erfassen: verlängerte Zentralnase, zwei nach hinten versetzte Schwimmer, geschwungene Flügelkontur, Cockpithaubenform, zwei Heckflossen, Propellermittelpunkt.
3. Kontrollpunkte nur so setzen, dass sie die sichtbare Masterkontur nachbilden. Die bekannte Geometrie-Version v298 ist eine **Ausgangsbasis**, kein freigegebenes Vorbild.
4. Rumpfsegmente mit wenigen sauber verteilten Quads modellieren; **Mirror** für links/rechts, **Subdivision Surface** für weiche Krümmung. Rand-Loops für definierte Stoßkanten, Deckel und Aufnahmen hinzufügen.
5. Flügel-Rumpf-Übergänge mit gemeinsamem kontrollierten Randverlauf verbinden oder über in FreeCAD verbindlich definierte Baugruppenschnittstellen trennen. Unkontrolliert ineinanderlaufende, geschlossene Meshes sind keine konstruktiven Übergänge.
6. Die Ober- und Unterseite der freien Außenhaut aus einem gemeinsamen, zusammenhängenden Volumen erzeugen. Große Flächen zuerst in Silhouette und Flächenkrümmung abnehmen; die orange Lackierung darf Konturfehler nicht verdecken.

### 2.3 Leichtbau und Solidify

1. Außenhaut als **referenzgetreues Quads-Mesh** erstellen; Freeze/Apply nur nach Sicherung einer nichtdestruktiven Version.
2. **Solidify** für definierte Schalenstärke einsetzen und gleichmäßigen Offset prüfen. Startpunkt z. B. 0.8–1.2 mm bei 0,4-mm-Düse, jedoch abhängig von Druckstrategie, Schichtorientierung, Spannweite und Lastpfad. **Kein** pauschaler Nachweis ausreichender Festigkeit.
3. Belastete Einbaubereiche, Motorrahmen, Mastwurzeln, Steckflächen und Hohlraumecken mit FreeCAD-definierten Rippen bzw. Holmen verstärken.
4. Mit **Weighted Normals**, sauberer Topologie und gezielten Bevels Schatten und Übergänge verbessern, ohne reale Druckwandungen ungewollt auszudünnen.
5. **Solidify nach Subdivision** testen, Reihenfolge der Modifier dokumentieren. Enge konkave Bereiche können Selbstüberschneidungen verursachen; den Mesh-Validator auf modifizierter **Export-Geometrie** ausführen, nicht nur auf dem unveränderten Edit-Mesh.
6. Innenseitige Drainage, Wartungsdeckel, Montageöffnungen und Dichtungssitze getrennt planen; kein eingeschlossenes Wasser oder ungeprüfte Leckpfade.
7. Tragende Flügel nicht allein als 3,93-mm-hohe geschlossene Vollkörper belassen. Die Lastabtragung zwischen Rumpf, Flügel und Foil über Holz-/CFK-/Metallholm **nur nach Materialentscheidung und expliziter Konstruktionsfreigabe** lösen; eine neue Fremdmaterialkomponente nicht als vorhandene Ausstattung ausgeben.

### 2.4 Blender-QA

- Jedes Exportmesh auf **watertight/manifold, konsistente Normalen, Selbstüberschneidungen, Nullflächen, lose Komponenten, Minimalwandstärken** prüfen.
- Ein gemeinsamer Export aus **überlappenden Einzelteilen** kann technisch problematisch sein, auch wenn alle Teile einzeln watertight sind.
- Vergleichsmessungen gegen den Master für Top, Side, Front, Hero mit gleicher Kamera/Skalierung; Kantenüberlagerung und Abweichungen protokollieren.
- Nach dem Teilen: `Volume(parts) ≈ Volume(source)` unter einer expliziten numerischen Toleranz. Der v297-Flügelfehler beruhte auf falsch ausgerichteten Flächennormalen, wurde in v298 korrigiert. Volumenprüfungen immer mit **konsistent orientiertem, gültigem Ausgangsmesh** durchführen.

## Phase 3: Integration, P2S-Druck und GitHub

### 3.1 Repository-Struktur

```text
Hydrofoam-Final-Master/
├── README.md                         # Projektziel, freigegebener Stand, Statusbilder
├── docs/
│   ├── WORKFLOW_FREECAD_BLENDER.md   # Dieses Dokument
│   ├── design/                        # Masterbild, Referenz- und Messprotokoll
│   ├── calculations/                  # Hydrodynamik, Aerodynamik, Schwerpunkt, Lasten
│   ├── qa/                            # Mesh-, Fit-, Dichtigkeits- und Belastungsreports
│   ├── construction-images/           # Verlauf und bestätigter current/Stand
│   └── assembly/                      # Stückliste, Explosionszeichnung, Montagefolge
├── cad/
│   ├── freecad/                       # .FCStd parametrisierte mechanische Originale
│   ├── blender/                       # .blend organische Außenhaut
│   └── exchange/                      # .step, STL-Referenzen, interfaces.json
├── print/
│   ├── prototypes/                    # unfertige, getrennte STL
│   ├── validated/                     # geprüfte Baugruppen-STL und 3MF
│   └── profiles/                       # versionierte P2S-Slicer-Konfiguration
├── scripts/                           # Generatoren, Prüfungen, Exporter
└── releases/                          # unveränderliche, explizit freigegebene Pakete
```

**Migration:** Bestehende Verzeichnisse `cad/`, `print/`, `renders/` und `docs/` bleiben erhalten. Keine historische Datei automatisch umbenennen oder verschieben; die neue Struktur gilt zunächst für neu erstellte Artefakte.

### 3.2 Dateiformate und eindeutige Verantwortlichkeit

| Format | Autorität | Zweck |
|---|---|---|
| `.FCStd` | FreeCAD | Maße, Foil-/Strut-Geometrie, Montagepunkte, Dichtsitze, Motor- und Elektronikboxen |
| `.blend` | Blender | referenzgetreue, editierbare Außenhaut, Oberflächenverlauf, Render- und Meshkontrolle |
| `.step` | FreeCAD-B-Rep | neutrales CAD-Austauschformat, mechanische Referenzen |
| `.stl` | Export aus FreeCAD/Blender | reine Dreiecksnetze, **keine** Parameter oder Einheitenmetadaten als universelle Garantie |
| `.3mf` | Slicer-Projekt | Platzierung, Materialzuweisung, Druckprofil und Produktionsfreigabe |
| `.json` | Git | Parameter, Schnittstellen, Tests, Status, Referenz-Hashes |
| `.png` | echtes CAD-Rendering | nachvollziehbare Ansichten und Master-Vergleiche |

### 3.3 Versionsregeln, Konfliktschutz und Commit-Checkliste

1. Jeder Arbeitsschritt beginnt mit `git status --short`, `git branch --show-current`, `git log -1 --oneline`.
2. Am Branch `wip/master-image-reconstruction` arbeiten. `main` enthält nur nachweislich abgenommene Stände.
3. Für jede Iteration: eindeutiger Versionsname, Quellskript, native Dateien, Exportdateien, vier echte CAD-Renderings, QA-Report.
4. Keine simultane Bearbeitung derselben binären `.FCStd` oder `.blend`. Änderungen an Parametern vorher abstimmen; native Binärdateien sind nicht sinnvoll zeilenweise mergebar.
5. Große generierte Dateien nicht wahllos ins Git aufnehmen. Gefragte freigegebene Artefakte versionieren; unnötige Cache-/Backup-Dateien per `.gitignore` ausnehmen. Bei hohem Datenvolumen Git LFS erwägen, aber keinen Repo-Umbau ohne separate Prüfung.
6. `README.md`-Masterbilder nur bei belegter **Verbesserung gegenüber dem Originalbild** erneuern. Bildgenerierungen, bloße Render-Presets oder ungeprüfte WIP-Silhouetten sind kein Grund, `current/` zu überschreiben.
7. Bei Export Fehlercode, Testberichte und Prüfsummen speichern. Keine stillschweigende erfolgreiche Final-Freigabe.

### 3.4 Fertigungs- und Abnahmekette

1. **Design:** Silhouettenvergleich gegen Original-Master für jede Ansichtsrichtung bestanden.
2. **CAD:** FreeCAD-Dimensionen und mechanische Interfaces eindeutig, Blender-Außenhaut deckungsgleich, keine ungeklärten Schnittstellen.
3. **Mesh:** Einzelteile watertight, normalkonsistent, ohne Selbstüberschneidungen; volumen- und schnittflächentreue Segmentierung.
4. **P2S:** Positionierung im tatsächlichen **256 × 256 × 256 mm** Bauraum mit nötigen Randabständen, Stützen, Brim und Druckrichtung. `<256` pro Achse **allein** genügt nicht.
5. **Leichtbau:** vollständige Stückliste mit tatsächlich gewogenen PLA-/PETG-Teilen, Schrauben, Klebstoff, Foils, RC, Akku. Schwerpunkt und Masse mit der Maximalgrenze vergleichen.
6. **Struktur:** Modulverbinder, Motorrahmen, Struts und Foils auf statische Lasten, Schwingung, Stoß und Dauerbelastung prüfen. Die Unterwasser-Foil-Momente nicht an eine ungestützte Rumpfhaut übertragen.
7. **Wasser:** abgedichtete Elektronikbox mit Wasserprobe, statischer Schwimm-/Trimmlage und schrittweiser langsamer Wasserfahrt testen; anschließend kontrollierte Foil-Fahrten.
8. **Flug:** eigenständige Luftfahrt-Aerodynamik-, Steuerbarkeits-, Leistungs- und Sicherheitsprüfung; Erstflug nur in geeignetem Umfeld mit ausreichend Sicherheitsabstand.
9. **Release:** Erst nach bestandenen Tests ein `releases/vX.Y/manifest.json` mit freigegebenen STLs/3MF, Material, Profil, Montageanleitung, Prüfbericht und `sha256`-Hashes erzeugen.

## Aktueller Entwicklungsstand (Dokumentationsbasis)

Zuletzt im Gespräch belegte Form-/Schnittrevisionen: v296 organische Flügelübergänge; v297 zehn Hauptmodule im P2S-Achsbauraum; v298 korrigierte Hauptflügel-Normalen und bestandenes Volumen-Audit; v299 vermessene Trennflächen. Unter `print/v300_joiner_prototypes` wurden als **Versuch** sechs Rumpf-/Schwimmer-Stifte mit Bohrungen konstruiert; noch kein belastbarer Festigkeitsnachweis. **Kein fertiger flugtauglicher oder wasserdichter RC-Hydrofoil, kein freigegebenes Final-Modell.**

## Dokumentationsquellen

- [FreeCAD Spreadsheet Workbench](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Spreadsheet_Workbench.md)
- [FreeCAD Expressions](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Expressions.md)
- [Bambu Lab P2S: Build Volume 256 × 256 × 256 mm](https://blog.bambulab.com/the-icon-redefined-meet-the-p2s-a-completely-reengineered-version-of-the-ultra-productive-p1-series/)
