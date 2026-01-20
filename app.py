import os
from flask import Flask, render_template, request, redirect, session, url_for
from openai import OpenAI

# -----------------------------
# FLASK SETUP
# -----------------------------
app = Flask(__name__)
app.secret_key = "resonance_secret_key"

# -----------------------------
# OPENAI CLIENT (REAL AI)
# -----------------------------
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# -----------------------------
# DEMO USERS (NO DATABASE)
# -----------------------------
STUDENTS = {
    "student1": {
        "password": "stud123",
        "name": "Aarav Patel",
        "class": "9",
        "section": "A",
        "attendance": 92
    }
}

TEACHERS = {
    "teacher1": {
        "password": "teach123",
        "name": "Ms. Ananya Sharma"
    }
}

# -----------------------------
# STUDENT PERFORMANCE LEVELS
# -----------------------------
STUDENT_LEVELS = {
    "student1": "Average"  # Improver / Average / Prodigy
}

# -----------------------------
# CHAT MEMORY (SESSION BASED)
# -----------------------------
CHAT_MEMORY = {}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def detect_subject(message):
    msg = message.lower()

    if any(w in msg for w in ["math", "algebra", "geometry", "equation", "pythagoras"]):
        return "Mathematics"
    if any(w in msg for w in ["physics", "force", "motion", "velocity"]):
        return "Physics"
    if any(w in msg for w in ["chemistry", "reaction", "acid", "base"]):
        return "Chemistry"
    if any(w in msg for w in ["biology", "cell", "photosynthesis", "plant"]):
        return "Biology"

    return "General"


def difficulty_instruction(level):
    if level == "Improver":
        return "Use very simple language, basic examples, and slow explanations."
    if level == "Prodigy":
        return "Use deeper reasoning and slightly challenging explanations."
    return "Explain clearly with examples and standard difficulty."


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if role == "student":
            user = STUDENTS.get(username)
            if user and user["password"] == password:
                session.clear()
                session["role"] = "student"
                session["username"] = username
                return redirect(url_for("student_dashboard"))

        if role == "teacher":
            user = TEACHERS.get(username)
            if user and user["password"] == password:
                session.clear()
                session["role"] = "teacher"
                session["username"] = username
                return redirect(url_for("teacher_dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# -----------------------------
# STUDENT DASHBOARD
# -----------------------------
@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    student = STUDENTS.get(session["username"])

    performance = {
        "Maths": "Average",
        "Science": "Prodigy",
        "English": "Average",
        "Biology": "Improver"
    }

    return render_template(
        "student_dashboard.html",
        student=student,
        performance=performance
    )


# -----------------------------
# STUDENT PROFILE
# -----------------------------
@app.route("/profile")
def student_profile():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    student = STUDENTS.get(session["username"])

    marks = {
        "Maths": 68,
        "Science": 91,
        "English": 74,
        "Biology": 55
    }

    ai_remark = (
        "Strong conceptual understanding in Science. "
        "Biology fundamentals need reinforcement. "
        "Maths accuracy will improve with regular practice."
    )

    teacher_remark = (
        "Disciplined student. Should participate more actively in class."
    )

    return render_template(
        "student_profile.html",
        student=student,
        marks=marks,
        ai_remark=ai_remark,
        teacher_remark=teacher_remark
    )


# -----------------------------
# AI CHAT (REAL OPENAI)
# -----------------------------
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    username = session.get("username")
    ai_response = None

    if username not in CHAT_MEMORY:
        CHAT_MEMORY[username] = []

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()

        if user_message:
            subject = detect_subject(user_message)
            level = STUDENT_LEVELS.get(username, "Average")
            difficulty_note = difficulty_instruction(level)

            system_prompt = (
                f"You are an AI tutor for school students (Classes 6–10).\n"
                f"Subject: {subject}\n"
                f"Student level: {level}\n"
                f"{difficulty_note}\n"
                f"Explain concepts step by step.\n"
                f"Focus on methods and reasoning.\n"
                f"Never give shortcuts or final exam answers."
            )

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(CHAT_MEMORY[username][-6:])
            messages.append({"role": "user", "content": user_message})

            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.35,
                    max_tokens=450
                )

                ai_response = completion.choices[0].message.content

                CHAT_MEMORY[username].append(
                    {"role": "user", "content": user_message}
                )
                CHAT_MEMORY[username].append(
                    {"role": "assistant", "content": ai_response}
                )

            except Exception:
                ai_response = (
                    "The AI tutor is temporarily unavailable. "
                    "Please try again shortly."
                )

    return render_template("chat.html", ai_response=ai_response)


# -----------------------------
# TEACHER DASHBOARD
# -----------------------------
@app.route("/teacher")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect(url_for("login"))

    return render_template(
        "teacher_dashboard.html",
        students=STUDENTS,
        levels=STUDENT_LEVELS
    )


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
