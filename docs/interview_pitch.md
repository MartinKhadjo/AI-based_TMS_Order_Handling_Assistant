# Interview Pitch

## 30 Sekunden

Ich habe zur Vorbereitung einen kleinen AI-native TMS-Prototypen gebaut. Ziel war es, Fahrzeuglogistik, Datenmodellierung, Backend/API, Frontend und AI-Workflows praktisch zu verbinden. Das System verwaltet Kunden, Fahrzeuge und Transportaufträge und kann aus einer unstrukturierten Kundenanfrage einen strukturierten Auftrag als menschlich prüfbaren Draft erzeugen.

## 3 Minuten Demo

1. Dashboard zeigen: Orders, offene Aufträge, Fahrzeuge, AI-created Orders.
2. Order Queue zeigen: Route, Kunde, Fahrzeug, Status, Priorität, Tracking.
3. AI Order Assistant öffnen: Freitext-Kundenanfrage extrahieren.
4. JSON-Draft erklären: AI schlägt vor, Backend validiert, Mensch bestätigt.
5. Draft bestätigen: Kunde/Fahrzeug/Transportauftrag werden angelegt.
6. Tool Calling zeigen: `Welche Fahrzeuge sind noch nicht disponiert?`
7. Backend-Architektur erklären: Django Models, DRF API, Services, PostgreSQL.

## Kernbotschaft

Das Projekt zeigt, dass AI nicht als oberflächlicher Chatbot ergänzt wird, sondern in Datenmodell, Validierung, Workflows und UI eingebettet ist. Die KI erzeugt Vorschläge, aber persistente Änderungen laufen über Backend-Regeln und menschliche Kontrolle.

## Brücke zur bisherigen Erfahrung

Bei PEM habe ich AI-gestützte Tools und produktionsnahe Workflows umgesetzt. Dieses Demo-Projekt überträgt dieselben Engineering-Prinzipien auf die Fahrzeuglogistik: unstrukturierte Information wird strukturiert, validiert und in produktive Arbeitsabläufe überführt.

## Gute technische Aussagen im Gespräch

- Das System trennt AI-Extraktion und persistente Datenänderung bewusst.
- Der Mock-AI-Modus macht die Demo reproduzierbar und key-frei.
- Das Datenmodell ist klein, aber domänennah: Customer, Vehicle, TransportOrder, TrackingEvent, Carrier, Invoice, AIExtractionLog.
- Tool Calling ist als Service gekapselt und kann später auf MCP erweitert werden.
- Der Prototyp ist nicht als fertiges TMS gemeint, sondern als präzise technische Demonstration.
