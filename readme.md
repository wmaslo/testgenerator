# Testgenerator (Flask + SQLite + Docker)

Der Testgenerator ist ein webbasiertes Tool zur Verwaltung von Unterrichtsthemen, Fragen und kompletten Tests.  
Er läuft containerisiert (Docker) auf einer Synology NAS und verwendet SQLite als Datenbank.

## 🚀 Funktionen

- Themen anlegen, bearbeiten, löschen  
- Fragen pro Thema verwalten  
- Tests anlegen, bearbeiten, duplizieren, löschen  
- Fragen zu Tests hinzufügen (mit Reihenfolge)  
- Testvorschau mit druckoptimiertem Layout  
- Antwortfelder für Schüler  
- Punktesystem pro Frage  
- Notenschlüssel am Ende jedes Tests  

## 🗂 Projektstruktur

```
/testgenerator
├── app.py
├── docker-compose.yml
├── templates/
├── static/
├── data/
│   └── questions.db   (nicht versionieren!)
└── docs/
```

## 🛢 Datenbank

Die SQLite-Datenbank liegt unter:

```
data/questions.db
```

Tabellen:

- topics  
- questions  
- tests  
- test_questions  

Details siehe: `docs/database.md`.

## 🐳 Deployment (Docker / Synology NAS)

### Starten

```bash
docker compose up -d
```

### Stoppen

```bash
docker compose down
```

### Container neu starten

```bash
docker compose restart
```

## 🔄 Entwicklung

Der Ordner `/volume1/docker/testgenerator` wird 1:1 als `/app` in den Container gemountet.

- Änderungen an Templates → Browser aktualisieren  
- Änderungen an app.py → Container neu starten:

```bash
docker compose restart
```

## 🧰 Backup

- Code → Git  
- Datenbank → Synology Backups (Snapshots / Hyper Backup)

**Wichtig:**  
`data/questions.db` niemals in Git committen.

## 📝 Weiterführende Dokumentation

Die vollständige technische Dokumentation befindet sich im Ordner:

```
docs/
```