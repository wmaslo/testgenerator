import csv
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "questions.db")
TXT_PATH = os.path.join(os.path.dirname(__file__), "Fragenkatalog.txt")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_topic(conn, name):
    cur = conn.execute("SELECT id FROM topics WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row["id"]

    cur = conn.execute(
        "INSERT INTO topics (name, description) VALUES (?, ?)",
        (name, "")
    )
    return cur.lastrowid

def import_questions():
    conn = get_db_connection()

    # Deine Datei verwendet Semikolon
    with open(TXT_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')

        count = 0
        for row in reader:
            # Format: ID;Frage;Thema;Punkte
            if len(row) < 4:
                print("Überspringe defekte Zeile:", row)
                continue

            _id = row[0].strip()
            question_text = row[1].strip().strip('"')
            topic_name = row[2].strip().strip('"')
            points_raw = row[3].strip()

            # Punkte prüfen
            try:
                points = float(points_raw)
            except:
                points = 1.0

            if not question_text or not topic_name:
                print("Überspringe unvollständige Zeile:", row)
                continue

            # Topic sicherstellen
            topic_id = ensure_topic(conn, topic_name)

            # Frage einfügen
            conn.execute(
                """
                INSERT INTO questions (text, topic_id, difficulty, points, solution)
                VALUES (?, ?, ?, ?, ?)
                """,
                (question_text, topic_id, 1, points, "")
            )

            count += 1

        conn.commit()
        conn.close()

        print(f"{count} Fragen erfolgreich importiert.")

if __name__ == "__main__":
    import_questions()
