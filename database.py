import sqlite3


DB_PATH = "questions.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS topics (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS questions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        text        TEXT NOT NULL,
        topic_id    INTEGER NOT NULL,
        difficulty  INTEGER DEFAULT 1,
        points      REAL DEFAULT 1.0,
        solution    TEXT,
        is_active   INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT DEFAULT (datetime('now')),
        updated_at  TEXT,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );

    CREATE TABLE IF NOT EXISTS tests (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        date        TEXT,
        notes       TEXT
    );

    CREATE TABLE IF NOT EXISTS test_questions (
        test_id         INTEGER NOT NULL,
        question_id     INTEGER NOT NULL,
        position        INTEGER NOT NULL,
        points_override REAL,
        PRIMARY KEY (test_id, question_id),
        FOREIGN KEY (test_id) REFERENCES tests(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    );
    """)

    conn.commit()
    conn.close()


def seed_demo_data():
    """Ein paar Beispielthemen und -fragen zum Testen einfügen."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Themen anlegen
    topics = [
        ("Elektrik", "Elektrische Grundlagen, CAN-Bus, Sensorik"),
        ("Hydraulik", "Hydraulische Systeme, Druck, Ventile"),
        ("Motor", "Verbrennungsmotoren, Kennlinien, Komponenten"),
    ]

    for name, desc in topics:
        c.execute(
            "INSERT OR IGNORE INTO topics (name, description) VALUES (?, ?)",
            (name, desc),
        )

    # Themen-IDs holen
    c.execute("SELECT id, name FROM topics")
    topic_ids = {name: id_ for (id_, name) in c.fetchall()}

    # Beispiel-Fragen
    questions = [
        (
            "Erklären Sie den grundsätzlichen Aufbau eines CAN-Bus-Systems.",
            "Elektrik",
            2,
            3.0,
            "Knoten/Steuergeräte, Busleitung, Terminierung, Nachrichtenaustausch, Priorität über Identifier.",
        ),
        (
            "Was versteht man unter hydraulischem Druck und wie wird er erzeugt?",
            "Hydraulik",
            1,
            2.0,
            "Druck = Kraft/Fläche, Erzeugung z.B. durch Pumpe in einem geschlossenen System.",
        ),
        (
            "Nennen Sie mindestens drei Aufgaben des Motoröls im Verbrennungsmotor.",
            "Motor",
            1,
            2.0,
            "Schmierung, Kühlung, Korrosionsschutz, Reinigung (Schmutzpartikel binden), Abdichtung.",
        ),
    ]

    for text, topic_name, diff, points, solution in questions:
        topic_id = topic_ids[topic_name]
        c.execute(
            """
            INSERT INTO questions (text, topic_id, difficulty, points, solution)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, topic_id, diff, points, solution),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Initialisiere Datenbank …")
    init_db()
    print("Füge Demodaten ein …")
    seed_demo_data()
    print("Fertig. Die Datei 'questions.db' wurde erstellt.")
