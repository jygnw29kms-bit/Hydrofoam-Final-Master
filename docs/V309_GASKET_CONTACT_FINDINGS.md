# v309 Dichtungsauflage: geometrischer Gegencheck

Die acht nominell ebenen M3-Ringdichtungen wurden auf Jens-PC gegen die **tatsächlichen v306-Schwimmer-STL** geprüft. Pro Ring wurden 64 vertikale Dreiecksstrahlen über den Ringbereich (Radien 2,2/3,0/4,0/4,8 mm) ausgewertet.

| Position je Schwimmer | Oberflächen-Z-Spannweite |
|---|---:|
| vorne, Schraube 1 | 2,123 mm |
| vorne, Schraube 2 | 0,276 mm |
| hinten, Schraube 1 | 0,538 mm |
| hinten, Schraube 2 | 2,329 mm |

Links/rechts spiegelbildlich. Die größten Abweichungen sind gegenüber einer nominellen Dichtungsdicke von 0,5 mm erheblich. **Die ebenen Ringe dürfen nicht als wasserdichte Endkonstruktion behandelt werden.** Die Messung beweist weder tatsächliche Kompression noch Leckfreiheit, sie zeigt aber die notwendige Konturanpassung. Nächster CAD-Schritt: konturangepasste Dichtflächen samt tragfähigen verschlossenen Insert-Bossen und Verschraubungs-/Druckprüfung; Materialfreigabe separat.

Quelle: `docs/V309_GASKET_CONTACT_QA.json`, reproduzierbar mit `python scripts/audit_v309_gasket_contact.py`. Final-Master-Bild und README-Bilder unverändert. Land/Wasser/Luft nicht freigegeben.
