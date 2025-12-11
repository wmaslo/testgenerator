from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.environ.get(
    "DB_PATH",  # wenn gesetzt, diesen Pfad nehmen
    os.path.join(BASE_DIR, "data", "questions.db")  # sonst Standard
)

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # erlaubt Zugriff per Spaltennamen
    return conn


@app.route("/")
def index():
    """Startseite: zeigt alle Themen."""
    conn = get_db_connection()
    topics = conn.execute(
        "SELECT id, name, description FROM topics ORDER BY name"
    ).fetchall()
    conn.close()
    return render_template("index.html", topics=topics)


@app.route("/topic/<int:topic_id>")
def topic_questions(topic_id):
    """Zeigt alle Fragen zu einem bestimmten Thema."""
    conn = get_db_connection()

    topic = conn.execute(
        "SELECT id, name, description FROM topics WHERE id = ?",
        (topic_id,),
    ).fetchone()

    questions = conn.execute(
        """
        SELECT q.id, q.text, q.difficulty, q.points
        FROM questions q
        WHERE q.topic_id = ?
        ORDER BY q.id
        """,
        (topic_id,),
    ).fetchall()

    conn.close()

    return render_template("questions.html", topic=topic, questions=questions)


@app.route("/question/new", methods=["GET", "POST"])
def new_question():
    conn = get_db_connection()

    # 1. Wenn das Formular abgeschickt wurde -> speichern
    if request.method == "POST":
        text = request.form["text"].strip()
        topic_id = request.form["topic_id"]
        difficulty = request.form.get("difficulty", 1)
        points = request.form.get("points", 1.0)
        solution = request.form["solution"].strip()

        if text and topic_id:
            conn.execute(
                """
                INSERT INTO questions (text, topic_id, difficulty, points, solution)
                VALUES (?, ?, ?, ?, ?)
                """,
                (text, topic_id, difficulty, points, solution),
            )
            conn.commit()
            conn.close()
            # Nach dem Speichern: Zur Themenliste zurück
            return redirect(url_for("index"))

    # 2. Bei GET: Formular anzeigen, Themen brauchen wir für Dropdown
    topics = conn.execute(
        "SELECT id, name FROM topics ORDER BY name"
    ).fetchall()
    conn.close()

    return render_template("new_question.html", topics=topics)

@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    conn = get_db_connection()

    # Daten der Frage laden
    question = conn.execute(
        "SELECT * FROM questions WHERE id = ?",
        (question_id,)
    ).fetchone()

    if question is None:
        conn.close()
        return "Frage nicht gefunden", 404

    # POST: Änderungen speichern
    if request.method == "POST":
        text = request.form["text"].strip()
        topic_id = request.form["topic_id"]
        difficulty = request.form.get("difficulty", 1)
        points = request.form.get("points", 1.0)
        solution = request.form["solution"].strip()

        conn.execute(
            """
            UPDATE questions
            SET text = ?, topic_id = ?, difficulty = ?, points = ?, solution = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (text, topic_id, difficulty, points, solution, question_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("topic_questions", topic_id=topic_id))

    # GET: Themenliste laden für Dropdown
    topics = conn.execute(
        "SELECT id, name FROM topics ORDER BY name"
    ).fetchall()

    conn.close()

    return render_template("edit_question.html", question=question, topics=topics)

@app.route("/question/<int:question_id>/delete", methods=["POST"])
def delete_question(question_id):
    conn = get_db_connection()

    # Thema merken, um danach zurück navigieren zu können
    question = conn.execute(
        "SELECT id, topic_id FROM questions WHERE id = ?",
        (question_id,)
    ).fetchone()

    if question is None:
        conn.close()
        return "Frage nicht gefunden", 404

    # Hier später evtl. prüfen, ob die Frage in test_questions verwendet wird
    conn.execute(
        "DELETE FROM questions WHERE id = ?",
        (question_id,)
    )
    conn.commit()
    topic_id = question["topic_id"]
    conn.close()

    return redirect(url_for("topic_questions", topic_id=topic_id))

@app.route("/tests")
def list_tests():
    """Liste aller Tests."""
    conn = get_db_connection()
    tests = conn.execute(
        "SELECT id, name, date, notes FROM tests ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()
    return render_template("tests.html", tests=tests)


@app.route("/tests/new", methods=["GET", "POST"])
def new_test():
    """Neuen Test anlegen."""
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"].strip()
        date = request.form.get("date", "").strip()
        notes = request.form.get("notes", "").strip()

        if name:
            conn.execute(
                "INSERT INTO tests (name, date, notes) VALUES (?, ?, ?)",
                (name, date, notes),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("list_tests"))

    conn.close()
    return render_template("new_test.html")

@app.route("/tests/<int:test_id>/questions", methods=["GET", "POST"])
def edit_test_questions(test_id):
    conn = get_db_connection()

    # Test laden
    test = conn.execute(
        "SELECT id, name, date, notes FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if test is None:
        conn.close()
        return "Test nicht gefunden", 404

    if request.method == "POST":
        # Liste der ausgewählten Fragen (als Strings)
        selected_ids = request.form.getlist("question_ids")
        # In Integers umwandeln
        selected_ids = [int(qid) for qid in selected_ids]

        # Alte Zuordnungen löschen
        conn.execute(
            "DELETE FROM test_questions WHERE test_id = ?",
            (test_id,)
        )

        # Neue Zuordnungen einfügen, Position = Reihenfolge der Auswahl
        position = 1
        for qid in selected_ids:
            conn.execute(
                """
                INSERT INTO test_questions (test_id, question_id, position)
                VALUES (?, ?, ?)
                """,
                (test_id, qid, position)
            )
            position += 1

        conn.commit()
        conn.close()
        # Zur Testliste zurück – oder wieder auf diese Seite -->
        return redirect(url_for("list_tests"))

    # GET: alle Fragen + markieren, welche schon im Test sind
    questions = conn.execute(
        """
        SELECT
            q.id,
            q.text,
            q.difficulty,
            q.points,
            t.name AS topic_name,
            CASE WHEN tq.test_id IS NULL THEN 0 ELSE 1 END AS is_selected
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        LEFT JOIN test_questions tq
            ON tq.test_id = ? AND tq.question_id = q.id
        ORDER BY t.name, q.id
        """,
        (test_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "test_questions.html",
        test=test,
        questions=questions
    )

@app.route("/tests/<int:test_id>/preview")
def test_preview(test_id):
    conn = get_db_connection()

    # Test laden
    test = conn.execute(
        "SELECT id, name, date, notes FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if test is None:
        conn.close()
        return "Test nicht gefunden", 404

    # Fragen zum Test in der richtigen Reihenfolge laden
    questions = conn.execute(
        """
        SELECT
            q.id,
            q.text,
            q.points,
            t.name AS topic_name,
            tq.position
        FROM test_questions tq
        JOIN questions q ON q.id = tq.question_id
        JOIN topics t ON t.id = q.topic_id
        WHERE tq.test_id = ?
        ORDER BY tq.position
        """,
        (test_id,)
    ).fetchall()

    conn.close()

    return render_template("test_preview.html", test=test, questions=questions)

@app.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
def edit_test(test_id):
    conn = get_db_connection()

    test = conn.execute(
        "SELECT id, name, date, notes FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if test is None:
        conn.close()
        return "Test nicht gefunden", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        date = request.form.get("date", "").strip()
        notes = request.form.get("notes", "").strip()

        if name:
            conn.execute(
                """
                UPDATE tests
                SET name = ?, date = ?, notes = ?
                WHERE id = ?
                """,
                (name, date, notes, test_id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("list_tests"))

    conn.close()
    return render_template("edit_test.html", test=test)

@app.route("/topic/new", methods=["GET", "POST"])
def new_topic():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()

        if name:
            conn.execute(
                "INSERT INTO topics (name, description) VALUES (?, ?)",
                (name, description),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    conn.close()
    return render_template("new_topic.html")

@app.route("/topic/<int:topic_id>/edit", methods=["GET", "POST"])
def edit_topic(topic_id):
    conn = get_db_connection()

    # Thema laden
    topic = conn.execute(
        "SELECT id, name, description FROM topics WHERE id = ?",
        (topic_id,)
    ).fetchone()

    if topic is None:
        conn.close()
        return "Thema nicht gefunden", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()

        if name:
            conn.execute(
                """
                UPDATE topics
                SET name = ?, description = ?
                WHERE id = ?
                """,
                (name, description, topic_id)
            )
            conn.commit()
            conn.close()
            # Nach dem Bearbeiten z.B. zurück zur Themenliste
            return redirect(url_for("index"))

    conn.close()
    return render_template("edit_topic.html", topic=topic)

@app.route("/tests/<int:test_id>/duplicate", methods=["POST"])
def duplicate_test(test_id):
    conn = get_db_connection()

    # Original-Test laden
    original = conn.execute(
        "SELECT id, name, date, notes FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if original is None:
        conn.close()
        return "Test nicht gefunden", 404

    # Neuen Namen erzeugen, z.B. "Alter Name (Kopie)"
    new_name = f"{original['name']} (Kopie)"
    new_date = original["date"]      # kannst du auch auf "" setzen, wenn du willst
    new_notes = original["notes"]

    # Neuen Test eintragen
    cursor = conn.execute(
        "INSERT INTO tests (name, date, notes) VALUES (?, ?, ?)",
        (new_name, new_date, new_notes)
    )
    new_test_id = cursor.lastrowid

    # Zugehörige Fragen übernehmen (Positionen beibehalten)
    conn.execute(
        """
        INSERT INTO test_questions (test_id, question_id, position)
        SELECT ?, question_id, position
        FROM test_questions
        WHERE test_id = ?
        """,
        (new_test_id, test_id)
    )

    conn.commit()
    conn.close()

    # Entweder zurück zur Übersicht...
    return redirect(url_for("list_tests"))
    # ...oder direkt in den neuen Test:
    # return redirect(url_for("edit_test", test_id=new_test_id))

@app.route("/tests/<int:test_id>/delete", methods=["POST"])
def delete_test(test_id):
    conn = get_db_connection()

    # Test existiert?
    test = conn.execute(
        "SELECT id FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if test is None:
        conn.close()
        return "Test nicht gefunden", 404

    # Zugeordnete Fragen löschen
    conn.execute(
        "DELETE FROM test_questions WHERE test_id = ?",
        (test_id,)
    )

    # Selbst den Test löschen
    conn.execute(
        "DELETE FROM tests WHERE id = ?",
        (test_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("list_tests"))

@app.route("/topic/<int:topic_id>/catalog")
def topic_catalog(topic_id):
    conn = get_db_connection()

    # Thema laden
    topic = conn.execute(
        "SELECT id, name, description FROM topics WHERE id = ?",
        (topic_id,)
    ).fetchone()

    if topic is None:
        conn.close()
        return "Thema nicht gefunden", 404

    # Alle Fragen zu diesem Thema laden
    questions = conn.execute(
        """
        SELECT id, text
        FROM questions
        WHERE topic_id = ?
        ORDER BY id
        """,
        (topic_id,)
    ).fetchall()

    conn.close()

    return render_template("topic_catalog.html", topic=topic, questions=questions)

@app.route("/topic/<int:topic_id>/delete", methods=["POST"])
def delete_topic(topic_id):
    conn = get_db_connection()

    # Thema laden
    topic = conn.execute(
        "SELECT id, name FROM topics WHERE id = ?",
        (topic_id,)
    ).fetchone()

    if topic is None:
        conn.close()
        return "Thema nicht gefunden", 404

    # Test-Zuordnungen für Fragen dieses Themas löschen
    conn.execute(
        """
        DELETE FROM test_questions
        WHERE question_id IN (
            SELECT id FROM questions WHERE topic_id = ?
        )
        """,
        (topic_id,)
    )

    # Fragen des Themas löschen
    conn.execute(
        "DELETE FROM questions WHERE topic_id = ?",
        (topic_id,)
    )

    # Thema löschen
    conn.execute(
        "DELETE FROM topics WHERE id = ?",
        (topic_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
