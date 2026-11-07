# Bildbasierter Neuaufbau Hydrofoam, Arbeitsstand 2026-11-07

## Bildquellen im lokalen Projekt
- reference/final_master_top_mask_exact.png (Original-Silhouette aus dem Mockup)
- reference/final_master_side_mask_exact.png
- reference/final_master_top_mask_v4.png, reference/final_master_side_mask_v4.png

Die vollfarbige Originaldatei 'futuristischer_rc_hydrofoil_mit_detailansichten.png' wurde auf Jens' PC unter den bekannten Projektordnern nicht gefunden. Die Masken enthalten keine Oberflaechendetails, Materialkanten, Farbaufteilung oder raeumliche Tiefeninformation.

## Erstellte bildgetriebene 3D-Varianten
- v289: Vorlagenmaske v4 als direkte Deckkontur; fehlerhafter Streifen am Bildrand
- v290: Originalmasken-Aussenkontur mit Breitenwarp; lokale Selbstueberlappung und Loecher im Deck
- v291: Originalmasken-Aussenkontur ohne Breitenwarp; wesentlich bessere geschlossene Draufsicht, aber Seitenansicht nicht korrekt rekonstruiert

### Binäre Silhouettenvergleiche (Top/Side IoU)
- v288 Altstand: 0.520 / 0.616
- v289 Bildspur: 0.559 / 0.474
- v290 Breitenwarp: 0.362 / 0.478
- v291 ohne Breitenwarp: 0.570 / 0.476

Die Bildrekonstruktion ist nur eine Geometrieexploration und darf nicht als Final-Master-Modell freigegeben werden.
Die nachgezeichnete Draufsicht allein reicht nicht aus, um eine korrekte dreidimensionale Oberflaeche zu rekonstruieren.

## Noch erforderlich
1. Vollfarbige Originalbilddatei mit allen Ansichten als verbindliche Modellierungsreferenz im Repo speichern.
2. Sichtbare Elemente einzeln aus den Bildern konstruieren: schmale Zentralnase, zwei Aussenschwimmer, verbindende Tragflaeche, Kanzel, Antrieb, Heckleitwerk, Farb- und Panelkanten.
3. Front-, Top-, Side- und Iso-Ansichten bildgenau uebereinanderlegen und visuell pruefen.
4. Erst bei dokumentierter optischer Deckung als Final Master deklarieren.
