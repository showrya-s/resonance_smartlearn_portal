import os
from flask import Flask, render_template, request, redirect, session, jsonify
import openai

# ------------------ CONFIG ------------------
app = Flask(__name__)
app.secret_key = "resonance_secret_key"

# ------------------ OPENAI ------------------
# Your API key directly here for Render deployment
openai.api_key = "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"

# ------------------ DUMMY USERS ------------------
students = [
    {"id": 1, "username": "student1", "password": "stud123", "name": "Riya Sharma", "class": 10, "section": "A", "roll": 1, "attendance": 95},
    {"id": 2, "username": "student2", "password": "stud123", "name": "Arjun Mehta", "class": 10, "section": "B", "roll": 2, "attendance": 90}
]

teachers = [
    {"id": 1, "username": "teacher1", "password": "teach123", "name": "Ms. Ananya Sharma"},
    {"id": 2, "username": "teacher2", "password": "teach123", "name": "Mr. Rakesh Verma"}
]

# ------------------ LOGIN ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "student":
            user = next((s for s in students if s["username"] == username and s["password"] == password), None)
            if user:
                session["student_id"] = user["id"]
                return redirect("/student")
        else:
            user = next((t for t in teachers if t["username"] == username and t["password"] == password), None)
            if user:
                session["teacher_id"] = user["id"]
                return redirect("/teacher")

    return render_template("login.html")

# ------------------ STUDENT DASHBOARD ------------------
@app.route("/student")
def student_dashboard():
    student_id = session.get("student_id")
    if not student_id:
        return redirect("/")

    student = next((s for s in students if s["id"] == student_id), None)
    return render_template("student_dashboard.html", student=student)

# ------------------ STUDENT PROFILE ------------------
@app.route("/student_profile")
def student_profile():
    student_id = session.get("student_id")
    if not student_id:
        return redirect("/")

    student = next((s for s in students if s["id"] == student_id), None)
    return render_template("student_profile.html", student=student)

# ------------------ TEACHER DASHBOARD ------------------
@app.route("/teacher")
def teacher_dashboard():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect("/")

    return render_template("teacher_dashboard.html", students=students)

# ------------------ AI CHAT ------------------
@app.route("/chat")
def chat_page():
    student_id = session.get("student_id")
    if not student_id:
        return redirect("/")
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"response": "Please ask a question!"})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        answer = completion.choices[0].message.content.strip()
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"response": f"AI Error: {str(e)}"})

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
