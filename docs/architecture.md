# Architektur des Testgenerators

## Übersicht

Der Testgenerator besteht aus folgenden Komponenten:

- **Flask Web-App** (Python)
- **SQLite-Datenbank**
- **HTML-Templates (Jinja2)**
- **Docker-Container**, betrieben auf einer Synology NAS (DSM)
- **docker-compose.yml** für Start/Stop/Deployment

Die Anwendung ist vollständig containerisiert und benötigt keine zusätzlichen Dienste wie PostgreSQL oder Redis.

---

## Gesamtstruktur

```
/testgenerator
├── app.py                 # Hauptapplikation
├── templates/             # HTML-Templates (Jinja2)
├── static/                # CSS-Dateien (Layout, Print-Styles)
├── data/questions.db      # SQLite-Datenbank
├── docker-compose.yml     # Start-, Mount- und Netzwerk-Konfiguration
└── docs/                  # Dokumentation
```

---

## Container-Architektur

Der Container wird aus dem lokalen Projektordner `/volume1/docker/testgenerator` gestartet und mountet diesen Ordner vollständig nach `/app` im Container.

Dies bedeutet:

- Änderungen am Code sind **ohne Neubau des Images** sichtbar.
- Die Datenbank `data/questions.db` wird **direkt vom Host gelesen**.
- Die Ordnerstruktur im Container entspricht exakt dem Host.

### Dienst: testgenerator

- **Image:** testgenerator:latest  
- **Portmapping:** Host-Port 8050 → Container-Port 5000  
- **Working Directory:** `/app`
- **DB-Datei:** `/app/data/questions.db`
- **Restart Policy:** `unless-stopped` (startet automatisch nach NAS-Reboot)
- **Volumes:**  
  `/volume1/docker/testgenerator:/app`

---

## Datenfluss in der Anwendung

1. Ein Benutzer ruft im Browser `http://NAS-IP:8050` auf.  
2. Flask verarbeitet die Route und greift über SQLite auf `data/questions.db` zu.  
3. Die Ergebnisse werden als Jinja2-Templates gerendert.  
4. Die Druckvorschau baut Tests dynamisch aus:
   - Test-Metadaten
   - Fragenliste
   - Punkte pro Frage
   - Themenzuordnung
   - Notenschlüssel
5. HTML wird dem Browser ausgeliefert.

---

## Gründe für SQLite

SQLite ist ideal für dieses Projekt, weil:

- es nur eine einzelne Datei benötigt
- es sehr schnell ist
- keine externe Datenbankverwaltung nötig ist
- Backups extrem einfach funktionieren (NAS-Snapshots reichen)
- es lokal, im Container und auf jeder Plattform ohne Anpassung funktioniert

---

## Gründe für Docker

Docker sorgt dafür, dass:

- die Python-Umgebung immer identisch bleibt  
- keine System-Pakete auf der NAS installiert werden müssen  
- das Deployment mit einem einzigen Befehl möglich ist  
- die App unabhängig von DSM-Versionen läuft  
- der gesamte Code gekapselt bleibt  

---

## Zusammenfassung

Diese Architektur macht den Testgenerator:

- **einfach wartbar**
- **leicht erweiterbar**
- **portabel**
- **NAS-freundlich**
- **sehr langlebig**, weil keine externen Dienste oder Abhängigkeiten benötigt werden
