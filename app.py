from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "questions.db")

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

if __name__ == "__main__":
    app.run(debug=True)
