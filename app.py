import os
from flask import Flask, render_template, request, redirect, session, jsonify
import firebase_admin
from firebase_admin import credentials, auth, firestore
import openai
from datetime import datetime

# ------------------ CONFIG ------------------
# Your OpenAI API key (already set in Render environment variables)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize Firebase Admin
cred = credentials.Certificate("firebase-admin.json")  # Place your downloaded Firebase Admin JSON here
firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore client

# Flask setup
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# ------------------ HELPERS ------------------

def get_user(uid):
    """Fetch user info from Firestore"""
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

def get_performance(uid):
    """Fetch student performance"""
    perf_doc = db.collection("performance").document(uid).get()
    if perf_doc.exists:
        return perf_doc.to_dict()
    return {}

def ai_response(message, student_name="Student"):
    """Call OpenAI API to respond dynamically"""
    try:
        prompt = f"""
        You are an educational AI assistant for a student named {student_name}.
        Answer their questions concisely and explain formulas and methods clearly.
        Student asks: {message}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful AI tutor."},
                      {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=400
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"AI Error: {str(e)}"

# ------------------ ROUTES ------------------

# ---- LOGIN ----
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")  # 'student' or 'teacher'

        try:
            user = auth.get_user_by_email(email)
            session["uid"] = user.uid
            session["role"] = role
            return redirect(f"/{role}_dashboard")
        except:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# ---- STUDENT DASHBOARD ----
@app.route("/student_dashboard")
def student_dashboard():
    uid = session.get("uid")
    if not uid or session.get("role") != "student":
        return redirect("/")

    user = get_user(uid)
    performance = get_performance(uid)
    return render_template("student_dashboard.html", user=user, performance=performance)

# ---- TEACHER DASHBOARD ----
@app.route("/teacher_dashboard")
def teacher_dashboard():
    uid = session.get("uid")
    if not uid or session.get("role") != "teacher":
        return redirect("/")

    # List all students
    students = [doc.to_dict() for doc in db.collection("users").where("role", "==", "student").stream()]
    return render_template("teacher_dashboard.html", teacher=get_user(uid), students=students)

# ---- STUDENT PROFILE ----
@app.route("/student_profile/<student_uid>")
def student_profile(student_uid):
    uid = session.get("uid")
    if not uid or session.get("role") != "teacher":
        return redirect("/")

    student = get_user(student_uid)
    performance = get_performance(student_uid)
    return render_template("student_profile.html", student=student, performance=performance)

# ---- CHAT ----
@app.route("/chat", methods=["GET", "POST"])
def chat():
    uid = session.get("uid")
    if not uid:
        return redirect("/")

    user = get_user(uid)

    if request.method == "POST":
        message = request.form.get("message")
        response = ai_response(message, student_name=user.get("name", "Student"))

        # Save chat in Firestore
        db.collection("chats").document(uid).collection("messages").add({
            "role": "student",
            "message": message,
            "timestamp": datetime.utcnow()
        })
        db.collection("chats").document(uid).collection("messages").add({
            "role": "ai",
            "message": response,
            "timestamp": datetime.utcnow()
        })

        return jsonify({"response": response})

    # GET → render chat page
    # Fetch previous chat messages
    messages = []
    chat_docs = db.collection("chats").document(uid).collection("messages").order_by("timestamp").stream()
    for msg in chat_docs:
        messages.append(msg.to_dict())

    return render_template("chat.html", user=user, messages=messages)

# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
