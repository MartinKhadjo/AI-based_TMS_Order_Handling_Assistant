# LogiSense Demo Lite - AI-native TMS Order Handling Assistant

Ein kleiner, aber professioneller Interview-Prototyp fuer ein AI-native Transport Management System in der Fahrzeuglogistik.

Copyright (c) 2026 Martin Khadjavian. All rights reserved.  
Website: [martinkhadjavian.com](https://martinkhadjavian.com)

Der Prototyp verbindet:

- Django + Django REST Framework Backend
- PostgreSQL per Docker Compose, SQLite fuer schnelle lokale Entwicklung
- Svelte + TypeScript Frontend
- deterministischen Mock-AI-Workflow fuer Freitext-Extraktion
- Tool-Calling-Demo fuer operative Datenbankfragen
- ausfuehrliche Dokumentation mit Mermaid- und PlantUML-Diagrammen

## Schnellstart ohne Docker

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

In einem zweiten Terminal:

```powershell
cd frontend
npm install
npm run dev
```

Danach:

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000/api/>
- Django Admin: <http://localhost:8000/admin/>

## Schnellstart mit Docker

```powershell
docker compose up --build
```

Docker startet PostgreSQL, Backend und Frontend. Der Backend-Container fuehrt Migrationen aus und legt Demo-Daten an.

## Demo Flow

1. Dashboard oeffnen
2. AI Order Assistant nutzen
3. Beispiel-Freitext extrahieren
4. Draft pruefen und bestaetigen
5. Order Queue aktualisieren
6. Tool-Calling-Frage stellen: `Welche Fahrzeuge sind noch nicht disponiert?`

## Dokumentation

Die zentrale technische Anleitung liegt hier:

- [docs/manual.md](docs/manual.md)
- [docs/generated/LogiSense_Demo_Lite_Manual.pdf](docs/generated/LogiSense_Demo_Lite_Manual.pdf)
- [docs/implementation_learning_manual.md](docs/implementation_learning_manual.md)
- [docs/generated/LogiSense_Demo_Lite_Implementation_Learning_Manual.pdf](docs/generated/LogiSense_Demo_Lite_Implementation_Learning_Manual.pdf)
- [docs/generated/diagrams/](docs/generated/diagrams/)
- [docs/architecture.md](docs/architecture.md)
- [docs/interview_pitch.md](docs/interview_pitch.md)
- [docs/plantuml/](docs/plantuml/)

## Copyright

See [NOTICE.md](NOTICE.md).

## Tests

```powershell
cd backend
pytest
```

```powershell
cd frontend
npm run build
```
