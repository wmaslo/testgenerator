# Datenbankschema des Testgenerators

Der Testgenerator verwendet eine SQLite-Datenbank unter:

`data/questions.db`

Diese Datei wird per Docker-Volume direkt vom Host eingebunden und ist dadurch vollständig durch Synology-Snapshots und Hyper Backup geschützt.

---

## Tabellenübersicht

Die Datenbank besteht aus vier Haupttabellen:

1. `topics`  
2. `questions`  
3. `tests`  
4. `test_questions`

Diese Tabellen bilden die Struktur ab: Themen, Fragen, Tests und deren Zuordnungen.

---

## Tabelle: topics

Repräsentiert ein Unterrichtsthema.

Spalten:

- id — INTEGER, PRIMARY KEY AUTOINCREMENT  
- name — TEXT, Pflichtfeld  
- description — TEXT, optional  

Beziehungen:

- Ein Topic kann beliebig viele Questions enthalten.  
- Beim Löschen eines Topics kümmert sich die App darum, alle zugehörigen Fragen und Testverknüpfungen zu löschen.

---

## Tabelle: questions

Repräsentiert eine einzelne Frage.

Spalten:

- id — INTEGER, PRIMARY KEY AUTOINCREMENT  
- text — TEXT, Pflichtfeld  
- topic_id — INTEGER, verweist auf `topics.id`  
- difficulty — INTEGER, optional (Schwierigkeitsgrad)  
- points — NUMERIC, Punkte pro Frage  
- solution — TEXT, optional (Musterlösung / Korrekturhinweis)  
- updated_at — optional, von der App gesetzt  

Beziehungen:

- Jede Frage gehört genau zu einem Topic.  
- Eine Frage kann in mehreren Tests referenziert werden.  
- Wird eine Frage gelöscht, werden auch die Einträge in `test_questions` entfernt.

---

## Tabelle: tests

Repräsentiert einen Test (Schularbeit).

Spalten:

- id — INTEGER, PRIMARY KEY AUTOINCREMENT  
- name — TEXT, Pflichtfeld  
- date — TEXT, optional  
- notes — TEXT, optional (Beschreibung, Klasse etc.)

Beziehungen:

- Ein Test besteht aus mehreren Fragen (über `test_questions`).

---

## Tabelle: test_questions

Diese Tabelle verknüpft Fragen mit Tests.

Spalten:

- id — INTEGER, PRIMARY KEY AUTOINCREMENT  
- test_id — INTEGER, verweist auf `tests.id`  
- question_id — INTEGER, verweist auf `questions.id`  
- position — INTEGER (Reihenfolge der Frage im Test)  
- points_override — NUMERIC, optional (Punkte im Test abweichend von der Frage)

Beziehungen:

- Ein Test kann viele Fragen haben.  
- Eine Frage kann in mehreren Tests vorkommen.  
- Die Sortierung erfolgt über die Spalte `position`.

---

## Typische SQL-Abfragen

### Alle Fragen zu einem Thema:

```sql
SELECT id, text
FROM questions
WHERE topic_id = ?
ORDER BY id;
```

### Alle Fragen eines Tests nach Reihenfolge:

```sql
SELECT
    q.id,
    q.text,
    q.points,
    t.name AS topic_name,
    tq.position
FROM test_questions tq
JOIN questions q ON q.id = tq.question_id
JOIN topics t ON q.topic_id = t.id
WHERE tq.test_id = ?
ORDER BY tq.position;
```

### Alle Punkte auf 1 setzen:

```sql
UPDATE questions SET points = 1;
```

---

## Datenbankpfad in der Anwendung

In `app.py` wird der Pfad so gesetzt:

```python
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(BASE_DIR, "data", "questions.db")
)
```

Das bedeutet:

- Containerpfad: `/app/data/questions.db`  
- Hostpfad: `/volume1/docker/testgenerator/data/questions.db`

---

## Backup der Datenbank

SQLite ist extrem portabel. Ein Backup besteht aus genau **einer Datei**:

`data/questions.db`

Backup-Strategien:

- NAS-Snapshot (empfohlen)  
- Hyper Backup  
- Manuelles Kopieren:  
  `cp data/questions.db /volume1/backup/`

Wiederherstellung:

- Container stoppen  
- Datei zurückkopieren  
- Container starten

---

## Zusammenfassung

- SQLite ist perfekt für diese Anwendung.  
- Keine externe DB, kein Server, einfache Datei.  
- Tabellen sind klar strukturiert und gut erweiterbar.  
- Backups sind trivial und zuverlässig.  
- DB-Pfad ist hart stabil: `data/questions.db`  

Damit ist die Datenhaltung extrem robust und zukunftssicher.
