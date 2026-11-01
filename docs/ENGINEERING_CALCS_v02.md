# ENGINEERING CALCS v02 – Final Master Hydrofoam

## Verbindliche Komponentenbasis
- Motor: SunnySky X2212 2450KV
- Akku: 3S LiPo, bevorzugt 2200 mAh; 1500–1800 mAh zulässig
- Propeller: APC 6x4
- ESC: 40 A
- Servos: JX PDI-1109MG oder gleichwertig, 4 Stück
- Servo-Versorgung: 6,0 V

## Herstellerdaten Antrieb
SunnySky X2212 2450KV, 3S, APC 6x4:
- Standschub: 880 g
- Strom: 28,5 A
- Eingangsleistung: 316 W
- Motor: 57 g
- max. Dauerstrom: 40 A
- max. Dauerleistung: 450 W
- empfohlener ESC: 40 A

## Gewichtsgrenzen
Schub/Gewicht mit 880 g Standschub:
- 550 g AUW: 1,60 : 1
- 600 g AUW: 1,47 : 1
- 625 g AUW: 1,41 : 1
- 650 g AUW: 1,35 : 1
- 700 g AUW: 1,26 : 1

Verbindliches Konstruktionsziel:
- Ziel-AUW: 600–625 g mit 3S 2200
- harte MTOW-Grenze: 650 g
- 700 g ist für Sand/Rasen-Reserve nicht akzeptabel

## Massenbudget bei 625 g Ziel-AUW
- 3S 2200 Akku: 190 g Zielwert
- Motor: 57 g
- ESC 40 A: 30 g Zielwert
- 4 Servos: 40 g
- RX: 10 g
- Prop/Spinner/Adapter: 12 g
- Kabel, Stecker, Gestänge, Schrauben: 31 g
- verbleibend für PLA/PETG-Airframe inkl. Kufen: ca. 255 g

Die CAD-Konstruktion muss daher auf maximal ca. 250–260 g gedruckte Struktur zielen.

## Flächenziel und Fluggeschwindigkeit
Final-Master-Außenform bleibt optisch unverändert; die tragende Center-Deck/Sponson-Geometrie wird so ausgelegt, dass mindestens 0,10 m² wirksame Tragfläche erreicht werden, Ziel 0,10–0,11 m².

Bei 625–650 g ergibt das ca. 57–65 g/dm² Flächenbelastung.

Abschätzung Stallgeschwindigkeit:
- 0,10 m² / 650 g / CLmax 1,0: ca. 10,2 m/s = 36,7 km/h
- 0,10 m² / 650 g / CLmax 1,2: ca. 9,3 m/s = 33,5 km/h
- 0,11 m² / 650 g / CLmax 1,2: ca. 8,9 m/s = 32,0 km/h

Konstruktionsziel: reale Start-/Abhebegeschwindigkeit etwa 32–36 km/h, abhängig von Profil, Anstellwinkel und Oberflächenqualität.

## Sand- und Rasenreserve
Bei 650 g AUW entspricht das Gewicht ca. 6,38 N; der statische Motorschub ca. 8,63 N.
Damit bleibt bereits im Stand ein Schubüberschuss von rund 2,25 N gegenüber dem Eigengewicht. Entscheidend für Bodenbetrieb sind deshalb geringe Reibung und kein Einsinken:
- breite, austauschbare PETG-Kufen
- große Aufstandsfläche
- abgerundete Anlaufkante
- keine hervorstehenden Schrauben/Scharnierteile unterhalb der Kufenebene
- Propeller ausreichend hoch über Boden

## Servodimensionierung
JX PDI-1109MG:
- 2,5 kg·cm bei 6,0 V
- 2,2 kg·cm bei 4,8 V
- 10 g
- Metallgetriebe

Konservative Hinge-Moment-Abschätzung bei 25 m/s:
- Aileron je Seite: ca. 0,78 kg·cm
- Pitch: ca. 1,41 kg·cm
- beide Rudder gemeinsam: ca. 1,56 kg·cm

Damit verbleiben bei 6 V Reserven von ca.:
- Aileron: Faktor 3,2
- Pitch: Faktor 1,8
- Rudder gemeinsam: Faktor 1,6

Verbindlich:
- 2 separate Aileron-Servos
- 1 Pitch-Servo
- 1 Rudder-Servo mit spielfreier symmetrischer Doppelanlenkung
- keine Mini-5-g-Servos im Final Master

## BEC
Da für PDI-1109MG kein belastbarer Stallstrom-Herstellerwert vorliegt, wird nicht knapp dimensioniert:
- 6 V BEC
- mindestens 5 A Dauer
- bevorzugt 8 A Peak/Reserve
- Brownout-Test mit allen 4 Servos gleichzeitig vor Erstflug

## Akku und Stromreserve
Bei 28,5 A Vollgas:
- 3S 2200: ca. 13 C
- 3S 1800: ca. 15,8 C
- 3S 1500: ca. 19 C

Bei 40 A Systemreserve:
- 2200: 18,2 C
- 1800: 22,2 C
- 1500: 26,7 C

Daher mindestens echter 30C-LiPo, bevorzugt 40C, keine Fantasie-C-Rating-Rolle mit Aufkleberpoesie.

## Flugzeit grob, 80 % nutzbare Kapazität
3S 2200:
- 12 A Mittelstrom: ca. 8,8 min
- 15 A: ca. 7,0 min
- 20 A: ca. 5,3 min
- 28,5 A Dauervollgas: ca. 3,7 min

## CAD-Konsequenzen für v02_MASTER_FORM
- Mockup bleibt sichtbarer Final Master und darf nicht verändert werden, um Komponenten bequemer unterzubringen.
- Motorachse/Brücke auf 6x4-Prop mit Boden- und Leitwerksfreigang dimensionieren.
- Akku längs verschiebbar, ca. 50 mm Trimmweg.
- Ziel-Strukturmasse <= 260 g PLA/PETG.
- tragende Fläche 0,10–0,11 m² innerhalb der Mockup-Kontur ausnutzen.
- Kufen breit und austauschbar für Rasen/Sand.
- Servoaufnahmen direkt an Lastpfade, PETG-Cradles, kurze Pushrods.
- Schwerpunkt erst nach tatsächlicher v02-Flächengeometrie neutralpunktbasiert berechnen; alter v01/v10-CG ist ungültig.
