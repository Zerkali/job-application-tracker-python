# Job Application Tracker

Eine datenbankgestützte Webanwendung zur Verwaltung von Bewerbungen. Portfolio-Projekt mit Python, SQLite und Streamlit.

## Funktionen
- Registrierung und Anmeldung mit gesalzenem PBKDF2-Passwort-Hash
- Bewerbungen erstellen, anzeigen, bearbeiten und löschen (CRUD)
- Suche und Statusfilter
- Dashboard mit Status- und Monatsstatistiken
- CSV-Export und benutzerspezifische Daten

## Technologien
Python 3.11+, SQLite (SQL), Streamlit, Pandas, Pytest

## Installation (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open http://localhost:8501 and register a local account. The database is created automatically.

## Architektur
`app.py` enthält die Benutzeroberfläche und `database.py` die Datenbank- und Authentifizierungslogik. Die Tabellen `users` und `applications` sind über `user_id` verbunden (1:n). SQL-Abfragen sind parametrisiert.

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Grenzen
Lokaler Portfolio-Prototyp, kein produktionsreifer öffentlicher Dienst. Für öffentliche Bereitstellung wären unter anderem HTTPS, Login-Rate-Limits und weitere Sicherheitsprüfungen erforderlich. Persönliche Daten und die lokale Datenbank nicht veröffentlichen.
