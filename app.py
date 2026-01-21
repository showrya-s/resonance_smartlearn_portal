import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from openai import OpenAI
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------- LOGIN REQUIRED DECORATOR ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES ----------------
@app.route("/login")
def login():
    return render_template("base.html", page="login", page_title="Login")

@app.route("/student_dashboard")
@login_required
def student_dashboard():
    student = {"class": "10", "section": "A", "roll": "1", "attendance": 95}
    performance = [
        ("Math", "Prodigy"),
        ("Science", "Prodigy"),
        ("English", "Average"),
        ("Social Science", "Average"),
        ("Language", "Prodigy"),
    ]
    remarks = {
        "teacher_remark": "Keep up the good work in Math and Science. Focus on English grammar.",
        "ai_remark": "Strong performance in Math and Science. Maintain practice for weak areas in English."
    }
    return render_template(
        "base.html",
        page="student_dashboard",
        page_title="Student Dashboard",
        student=student,
        performance=performance,
        remarks=remarks
    )

@app.route("/teacher_dashboard")
@login_required
def teacher_dashboard():
    return render_template("base.html", page="teacher_dashboard", page_title="Teacher Dashboard")

@app.route("/student_profile")
@login_required
def student_profile():
    return render_template("base.html", page="student_profile", page_title="Student Profile")

@app.route("/chat")
@login_required
def chat_page():
    return render_template("base.html", page="chat", page_title="AI Chat")

# ---------------- SESSION HANDLING ----------------
@app.route("/set-session", methods=["POST"])
def set_session():
    data = request.json or {}
    session["email"] = data.get("email")
    session["role"] = data.get("role", "student")
    return jsonify({"status": "ok"})

@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role", "student")
    if role == "teacher":
        return redirect(url_for("teacher_dashboard"))
    return redirect(url_for("student_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- AI CHAT API ----------------
@app.route("/api/chat", methods=["POST"])
@login_required
def ai_chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please ask a question."})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful academic tutor for school students. "
                        "Explain concepts clearly with steps, formulas, and examples. "
                        "Focus on teaching methods, not just answers."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=400
        )
        ai_reply = response.choices[0].message.content
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": "AI error occurred.", "error": str(e)}), 500

# ---------------- ROOT ----------------
@app.route("/")
def root():
    if session.get("email"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False)
