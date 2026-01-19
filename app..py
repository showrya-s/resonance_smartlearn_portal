from flask import Flask, render_template, request, redirect, session
import sqlite3
import openai

app = Flask(__name__)
app.secret_key = "resonance_secret_key"

# ------------------ OPENAI SETUP ------------------
openai.api_key = "YOUR_OPENAI_API_KEY"  # <- Replace with your key

# ------------------ DATABASE CONNECTION ------------------
def get_db():
    return sqlite3.connect("database.db")

# ------------------ INIT DB ------------------
@app.route("/init_db")
def init_db():
    db = get_db()
    cur = db.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT,
        class INTEGER,
        section TEXT,
        roll INTEGER,
        attendance INTEGER,
        photo TEXT
    );

    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS marks (
        student_id INTEGER,
        subject TEXT,
        exam_type TEXT,
        marks INTEGER
    );

    CREATE TABLE IF NOT EXISTS remarks (
        student_id INTEGER,
        teacher_remark TEXT,
        ai_remark TEXT
    );

    CREATE TABLE IF NOT EXISTS performance (
        student_id INTEGER,
        subject TEXT,
        level TEXT
    );
    """)
    db.commit()
    return "Database initialized!"

# ------------------ LOGIN ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        db = get_db()
        cur = db.cursor()

        if role == "student":
            cur.execute("SELECT * FROM students WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()
            if user:
                session["student_id"] = user[0]
                return redirect("/student")
        else:
            cur.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()
            if user:
                session["teacher"] = True
                return redirect("/teacher")

    return render_template("login.html")

# ------------------ STUDENT DASHBOARD ------------------
@app.route("/student")
def student_dashboard():
    student_id = session.get("student_id")
    if not student_id:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT name, class, section, attendance FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()

    cur.execute("SELECT subject, level FROM performance WHERE student_id=?", (student_id,))
    performance = cur.fetchall()

    cur.execute("SELECT teacher_remark, ai_remark FROM remarks WHERE student_id=?", (student_id,))
    remarks = cur.fetchone()

    return render_template(
        "student_dashboard.html",
        student=student,
        performance=performance,
        remarks=remarks
    )

# ------------------ TEACHER DASHBOARD ------------------
@app.route("/teacher")
def teacher_dashboard():
    if not session.get("teacher"):
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, class, section FROM students")
    students = cur.fetchall()

    return render_template("teacher_dashboard.html", students=students)

# ------------------ STUDENT PROFILE ------------------
@app.route("/student_profile/<int:student_id>")
def student_profile(student_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT name, class, section, roll, attendance FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()

    cur.execute("SELECT subject, exam_type, marks FROM marks WHERE student_id=?", (student_id,))
    marks = cur.fetchall()

    cur.execute("SELECT subject, level FROM performance WHERE student_id=?", (student_id,))
    performance = cur.fetchall()

    cur.execute("SELECT teacher_remark, ai_remark FROM remarks WHERE student_id=?", (student_id,))
    remarks = cur.fetchone()

    return render_template(
        "student_profile.html",
        student=student,
        marks=marks,
        performance=performance,
        remarks=remarks
    )

# ------------------ AI LOGIC ------------------
def ai_analysis(marks):
    if not marks:
        return "No marks available for analysis."

    avg = sum(marks) / len(marks)

    if avg >= 85:
        return "Excellent performance. Prodigy level. Increase difficulty."
    elif avg >= 60:
        return "Good performance. Maintain practice and improve weak areas."
    else:
        return "Needs improvement. Focus on basics with lower difficulty."

# ------------------ UPDATE PERFORMANCE ------------------
def update_performance(student_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT subject, marks FROM marks WHERE student_id=?", (student_id,))
    subject_marks = cur.fetchall()

    marks_list = []
    for subject, mark in subject_marks:
        marks_list.append(mark)
        if mark >= 85:
            level = "Prodigy"
        elif mark >= 60:
            level = "Average"
        else:
            level = "Improver"

        # insert or update performance
        cur.execute("""
            INSERT INTO performance(student_id, subject, level)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject) DO UPDATE SET level=excluded.level
        """, (student_id, subject, level))

    db.commit()
    ai_remark = ai_analysis(marks_list)

    cur.execute("SELECT * FROM remarks WHERE student_id=?", (student_id,))
    if cur.fetchone():
        cur.execute("UPDATE remarks SET ai_remark=? WHERE student_id=?", (ai_remark, student_id))
    else:
        cur.execute("INSERT INTO remarks(student_id, ai_remark) VALUES (?, ?)", (student_id, ai_remark))
    db.commit()

# ------------------ AI HOMEWORK CHAT ------------------
@app.route("/chat", methods=["GET", "POST"])
def chat():
    response_text = ""
    student_id = session.get("student_id")
    if not student_id:
        return redirect("/")

    if request.method == "POST":
        question = request.form["question"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT subject, level FROM performance WHERE student_id=?", (student_id,))
        performance = cur.fetchall()
        perf_context = "\n".join([f"{sub}: {lvl}" for sub, lvl in performance]) or "No performance data yet."

        prompt = f"You are a helpful AI tutor. Student performance:\n{perf_context}\n\nStudent asks: {question}\nExplain thoroughly with formulas, steps, and methods. Do not give shortcuts."

        res = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        response_text = res['choices'][0]['message']['content']

    return render_template("chat.html", response=response_text)

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True)
