import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from openai import OpenAI

# ------------------ FLASK SETUP ------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")  # set in Render ENV

# ------------------ OPENAI SETUP ------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment variables")

client = OpenAI(api_key=api_key)

# ------------------ ROUTES ------------------

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/teacher_dashboard")
def teacher_dashboard():
    return render_template("teacher_dashboard.html")

@app.route("/student_profile")
def student_profile():
    return render_template("student_profile.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

# ------------------ SESSION HANDLING ------------------

@app.route("/set-session", methods=["POST"])
def set_session():
    data = request.json
    session["email"] = data.get("email")
    session["role"] = data.get("role", "student")
    return jsonify({"status": "ok"})

@app.route("/dashboard")
def dashboard():
    role = session.get("role", "student")
    if role == "teacher":
        return redirect(url_for("teacher_dashboard"))
    return redirect(url_for("student_dashboard"))

# ------------------ AI CHAT API ------------------

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    data = request.json
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
                        "Do not give shortcuts or answers directly. Teach methods."
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
        return jsonify({
            "reply": "🤖 AI Error. Check API key or billing.",
            "error": str(e)
        }), 500

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=False)  # disable debug in production
