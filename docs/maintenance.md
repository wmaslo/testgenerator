# Wartung & Fehlerbehebung des Testgenerators

Dieses Dokument beschreibt typische Wartungsaufgaben, Backups, Fehlerdiagnose und Wiederherstellungsstrategien für den langfristigen Betrieb des Testgenerators.

---

## Regelmäßige Wartungsaufgaben

### 1. Code aktuell halten (Git)

```bash
cd /volume1/docker/testgenerator
git pull
```

### 2. Datenbank sichern

Die Datei:

    /volume1/docker/testgenerator/data/questions.db

sollte durch Synology Snapshot Replication oder Hyper Backup gesichert werden.

Manuelles Backup:

```bash
cp data/questions.db /volume1/backup/
```

### 3. Container prüfen

```bash
docker ps
```

### 4. Logs ansehen

```bash
docker compose logs -f testgenerator
```

---

## Typische Probleme & Lösungen

---

### 🔧 Problem: Änderungen in Templates werden nicht angezeigt

Mögliche Ursachen:

- Browser-Cache
- falsches Template bearbeitet
- Browser lädt Druck-Cache

Lösungen:

1. Komplett neu laden (Strg+F5)  
2. Cache löschen  
3. Container neu starten:

```bash
docker compose restart
```

---

### 🔧 Problem: Änderungen in `app.py` werden nicht übernommen

Grund:

- Python-Code wird erst nach Neustart neu geladen.

Lösung:

```bash
docker compose restart
```

---

### 🔧 Problem: Fehler `no such table`

Das ist der häufigste SQLite-Fehler.

Mögliche Ursachen:

1. Falsche Datenbankdatei verwendet  
2. DB wurde versehentlich neu angelegt  
3. Volume-Mount wurde verändert  
4. Tabellen fehlen in der DB  

Diagnose:

```bash
sqlite3 data/questions.db ".tables"
```

Wenn Tabellen fehlen → falsche Datei oder nicht gemountet.

---

### 🔧 Problem: Port 8050 ist belegt

Lösung: in `docker-compose.yml` Port ändern:

```yaml
ports:
  - "8060:5000"
```

Dann neu starten:

```bash
docker compose up -d
```

---

### 🔧 Problem: Container startet nicht

Diagnose:

```bash
docker compose logs testgenerator
```

Typische Ursachen:

- Syntaxfehler in `app.py`  
- fehlende Python-Library  
- falscher DB-Pfad  

---

### 🔧 Problem: SQLite ist „locked“

Passiert selten, meist durch fehlerhafte Editor-Sessions.

Lösung:

1. Container neu starten  
2. Wenn Blockade bestehen bleibt → Kopie anfertigen, Original überschreiben.

---

## Datenbank prüfen & reparieren

### Tabellen anzeigen

```bash
sqlite3 data/questions.db ".tables"
```

### Schema einer Tabelle anzeigen

```bash
sqlite3 data/questions.db ".schema questions"
```

### Konsistenz prüfen

```sql
PRAGMA integrity_check;
```

---

## Wiederherstellung nach Fehlern

### Schritt 1: Container stoppen

```bash
docker compose down
```

### Schritt 2: Backup zurückspielen

```bash
cp /volume1/backup/questions.db data/questions.db
```

### Schritt 3: Container starten

```bash
docker compose up -d
```

### Schritt 4: Funktion prüfen

Browser öffnen:  
    http://<NAS-IP>:8050

---

## Migrationen (DB-Änderungen)

Wenn eine neue Spalte benötigt wird:

1. kleines Python- oder SQL-Migrationsskript schreiben  
2. im Container ausführen:

```bash
docker exec -it testgenerator python migrate_xyz.py
```

Beispiel:

```sql
ALTER TABLE questions ADD COLUMN tags TEXT;
```

### Wichtig:

Migrationen **immer dokumentieren** und **im Repo speichern**, damit du in 5 Jahren weißt, was du geändert hast.

---

## Backup-Strategie

Empfohlen:

- **Täglich Snapshot-Replication** (NAS intern)
- **Wöchentlich Hyper Backup** (extern)
- **Optional: manuelle Kopie der SQLite-Datei**

SQLite ist extrem stabil und leicht zu sichern.

---

## Container-Aufräumarbeiten

Nicht zwingend nötig, aber gelegentlich sinnvoll:

### Ungenutzte Images löschen

```bash
docker image prune
```

### Ungenutzte Container löschen

```bash
docker container prune
```

(Vorsicht: löscht alle gestoppten Container.)

---

## Cheat Sheet

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

Logs:

```bash
docker compose logs -f testgenerator
```

Backup:

```bash
cp data/questions.db /volume1/backup/
```

DB prüfen:

```bash
sqlite3 data/questions.db ".tables"
```

---

## Fazit

Mit den Werkzeugen:

- Docker  
- SQLite  
- Git  
- Synology-Backups  

ist der Testgenerator extrem wartungsarm und über viele Jahre stabil nutzbar.  
Dieses Dokument hilft dir, auch nach langer Zeit wieder in die Wartung einzusteigen.
