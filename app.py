import os
from flask import Flask, render_template, request, redirect, session
import openai

# ------------------ OPENAI SETUP ------------------
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ------------------ FLASK SETUP ------------------
app = Flask(__name__)
app.secret_key = "resonance_secret_key"

# ------------------ FAKE DATA LAYER (IN-MEMORY) ------------------

students = {
    "student1": {
        "password": "stud123",
        "name": "Aarav Mehta",
        "class": 9,
        "section": "A",
        "roll": 12,
        "attendance": 92,
        "photo": "logo.png",
        "marks": {
            "Maths": 55,
            "Science": 78,
            "English": 81,
            "Social Science": 60,
            "Language": 74,
            "Physics": 58,
            "Chemistry": 65,
            "Biology": 88
        }
    }
}

teachers = {
    "teacher1": {
        "password": "teach123",
        "name": "Ms. Ananya Sharma"
    }
}

# ------------------ AI LOGIC ------------------

def performance_level(score):
    if score >= 85:
        return "🟢 Prodigy"
    elif score >= 60:
        return "🟡 Average"
    else:
        return "🔴 Improver"

def generate_ai_remark(subject, score):
    prompt = f"""
    A student scored {score}/100 in {subject}.
    Explain their performance and suggest improvement methods.
    Avoid shortcuts.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return "AI service unavailable. Try again later."

# ------------------ ROUTES ------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "student" and username in students:
            if students[username]["password"] == password:
                session["user"] = username
                session["role"] = "student"
                return redirect("/student-dashboard")

        if role == "teacher" and username in teachers:
            if teachers[username]["password"] == password:
                session["user"] = username
                session["role"] = "teacher"
                return redirect("/teacher-dashboard")

    return render_template("login.html")

@app.route("/student-dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return redirect("/")

    student = students[session["user"]]
    performance = {
        subject: performance_level(score)
        for subject, score in student["marks"].items()
    }

    return render_template(
        "student_dashboard.html",
        student=student,
        performance=performance
    )

@app.route("/teacher-dashboard")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect("/")

    return render_template(
        "teacher_dashboard.html",
        students=students
    )

@app.route("/student/<username>")
def student_profile(username):
    if session.get("role") != "teacher":
        return redirect("/")

    student = students[username]
    ai_remarks = {
        subject: generate_ai_remark(subject, score)
        for subject, score in student["marks"].items()
    }

    return render_template(
        "student_profile.html",
        student=student,
        ai_remarks=ai_remarks,
        performance=student["marks"]
    )

@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    question = request.form["question"]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except:
        return "AI service unavailable."

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)
