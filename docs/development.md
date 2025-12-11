# Entwicklung & Erweiterung des Testgenerators

Dieses Dokument beschreibt den Entwicklungs-Workflow, den Umgang mit dem Code, das Arbeiten auf der NAS sowie die Struktur der Anwendung.

---

## Projektstruktur

Der relevante Projektordner auf der NAS lautet:

    /volume1/docker/testgenerator

Struktur:

    /app.py
    /templates/
    /static/
    /data/questions.db
    /docker-compose.yml
    /docs/

Alle Änderungen hier werden durch den Docker-Container direkt verwendet.

---

## Grundprinzipien der Entwicklung

- Der gesamte Code wird per Volume nach `/app` in den Container gemountet.  
- Änderungen an Python-Dateien benötigen oft einen Neustart des Containers.  
- Änderungen an Templates werden meist sofort übernommen (Browser-Reload).  
- Die Datenbank liegt lokal unter `data/questions.db` und wird nie in Git gespeichert.  

---

## Änderungen am Code

### Schritt 1: Auf die NAS einloggen

```bash
ssh <dein-nas-user>@<nas-ip>
```

### Schritt 2: In den Projektordner wechseln

```bash
cd /volume1/docker/testgenerator
```

### Schritt 3: Datei mit Editor öffnen

Beispiele:

```bash
micro app.py
nano templates/test_preview.html
vim static/styles.css
```

### Schritt 4: Container neu starten (nur bei Python-Änderungen)

```bash
docker compose restart
```

### Schritt 5: Browser aktualisieren

Strg+F5 (Cache umgehen).

---

## Änderungen an Templates

Templates liegen unter:

    templates/*.html

Flask lädt Templates im Debug-Modus automatisch neu.  
Wenn dennoch alte Version angezeigt werden:

1. Browser Strg+F5  
2. Ggf. Container restart:

```bash
docker compose restart
```

---

## Arbeiten mit Git

### Status prüfen

```bash
git status
```

### Änderungen hinzufügen

```bash
git add .
```

### Commit erstellen

```bash
git commit -m "Beschreibung der Änderung"
```

### Änderungen pushen

```bash
git push origin main
```

### Wichtig

Die Datei `data/questions.db` darf **niemals** committet werden.  
Daher sollte sie in der Datei `.gitignore` stehen.

---

## Arbeiten an der Datenbank

Der Pfad zur Datenbank (im Container):

    /app/data/questions.db

Auf dem Host:

    /volume1/docker/testgenerator/data/questions.db

### SQLite direkt öffnen:

```bash
sqlite3 data/questions.db
```

Verlassen der SQLite-Konsole:

```
.exit
```

### Beispiel: Alle Punkte auf 1 setzen

```sql
UPDATE questions SET points = 1;
```

---

## Neue Python-Abhängigkeiten hinzufügen

Wenn du z. B. ein neues Paket installierst (in `requirements.txt`):

1. Image neu bauen:

```bash
docker compose down
docker build -t testgenerator:latest .
docker compose up -d
```

---

## Debugging & Logging

Container-Logs:

```bash
docker compose logs -f testgenerator
```

Debug-Ausgaben in `app.py` erscheinen hier.

---

## Entwicklung neuer Features

### Prinzipieller Ablauf

1. Neues Feature planen  
2. Datenbank anpassen (falls nötig)  
3. Template erstellen oder erweitern  
4. Neue Route in `app.py` hinzufügen  
5. SQL-Abfragen mit SELECT/INSERT/UPDATE schreiben  
6. Feature testen  
7. Commit & Push  

### Empfehlung

Bei DB-Änderungen:
- Migrationsskript schreiben (z. B. `migrate_2025_01_add_column_xyz.py`)
- Immer dokumentieren, was geändert wurde

---

## Typische Probleme

### Änderungen werden nicht angezeigt

- Richtige Datei bearbeitet?  
- Browser-Cache löschen  
- Container neu starten  

### Python-Fehler im Log

- Logs prüfen  

```bash
docker compose logs -f testgenerator
```

### Datenbankfehler

- Falscher Pfad?  
- Falsche Datei?  
- Fehlt eine Tabelle?

```bash
sqlite3 data/questions.db ".tables"
```

---

## Zusammenfassung

- Entwicklung geschieht direkt im NAS-Projektordner  
- Templates sofort sichtbar, Python-Code nach Restart  
- Git ist die Wahrheit für den Code  
- SQLite ist die Wahrheit für die Daten  
- Docker sorgt dafür, dass das Projekt überall gleich läuft  

Dieses Dokument ermöglicht dir auch in einigen Jahren wieder einen schnellen Einstieg in die Weiterentwicklung.
