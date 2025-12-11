# Deployment & Betrieb (Synology NAS + Docker)

Dieses Dokument beschreibt Installation, Start, Stop und Aktualisieren des Testgenerators auf einer Synology NAS mit Docker / Container Manager.

---

## Voraussetzungen

- Synology NAS mit DSM 7  
- Container Manager (Docker) installiert  
- Projekt liegt unter:  
  `/volume1/docker/testgenerator`  
- Datei `docker-compose.yml` ist vorhanden  
- Python-App ist über Docker lauffähig

---

## Erstmaliges Deployment

1. Per SSH auf die NAS verbinden  
2. In den Projektordner wechseln:

```bash
cd /volume1/docker/testgenerator
```

3. Docker-Image bauen:

```bash
docker build -t testgenerator:latest .
```

4. Anwendung starten:

```bash
docker compose up -d
```

5. Browser öffnen:

    http://<NAS-IP>:8050

---

## Container stoppen

```bash
docker compose down
```

Dadurch wird der Container entfernt, jedoch **nicht** der Code oder die Datenbank.

---

## Container neu starten (z. B. nach Änderungen an `app.py`)

```bash
docker compose restart
```

Die App lädt neu, da der Quellcode per Volume eingehangen ist.

---

## Container komplett neu aufbauen  
(z. B. nach Änderungen an `requirements.txt` oder dem Dockerfile)

1. Container stoppen:

```bash
docker compose down
```

2. Image neu bauen:

```bash
docker build -t testgenerator:latest .
```

3. Neu starten:

```bash
docker compose up -d
```

---

## Logs ansehen

```bash
docker compose logs -f testgenerator
```

Mit Strg+C beenden.

---

## Datenbankpfad

Die SQLite-Datei befindet sich in:

    /volume1/docker/testgenerator/data/questions.db

Im Container erscheint sie durch Mounting unter:

    /app/data/questions.db

Kein externer Datenbankserver notwendig.

---

## Automatischer Start nach NAS-Neustart

In `docker-compose.yml`:

```
restart: unless-stopped
```

Bedeutet:

- Startet automatisch nach jedem Systemstart  
- Wird nur auf manuelles Stoppen hin deaktiviert

---

## Aktualisierung des Projekts (Git)

1. Zum Projekt wechseln:

```bash
cd /volume1/docker/testgenerator
```

2. Änderungen holen:

```bash
git pull
```

3. Wenn nur Code/HTML geändert wurden:

```bash
docker compose restart
```

4. Wenn auch Abhängigkeiten geändert wurden:

```bash
docker compose down
docker build -t testgenerator:latest .
docker compose up -d
```

---

## Backup & Restore

### Backup

- Code → GitHub  
- Datenbank → Synology Snapshot / Hyper Backup  

Manuelles Backup der DB:

```bash
cp /volume1/docker/testgenerator/data/questions.db /volume1/backup/
```

### Restore

1. Container stoppen  
2. Backup nach `data/questions.db` zurückkopieren  
3. Container starten

---

## Häufige Probleme & Lösungen

### Port 8050 belegt

In `docker-compose.yml` ändern:

```yaml
ports:
  - "8060:5000"
```

Dann:

```bash
docker compose up -d
```

---

### Änderungen an Templates werden nicht sichtbar

- Browser neu laden (Strg+F5)  
- Richtige Datei geändert?  
- Ggf. Container neu starten:

```bash
docker compose restart
```

---

### Fehler: `no such table`

Ursachen:

- falsche oder leere Datenbank  
- Volume-Mount fehlt  
- DB-Pfad falsch gesetzt  

Check:

- Existiert `data/questions.db`?  
- Stimmt `DB_PATH` in app.py?  
- Wird das Volume korrekt gemountet?

---

## Zusammenfassung (Cheat Sheet)

Start:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

Restart:

```bash
docker compose restart
```

Update:

```bash
git pull
docker compose restart
```

Rebuild:

```bash
docker compose down
docker build -t testgenerator:latest .
docker compose up -d
```

