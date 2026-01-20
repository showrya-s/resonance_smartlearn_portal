from flask import Flask, render_template

app = Flask(__name__)

# ------------------ ROUTES ------------------

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/teacher_dashboard")
def teacher_dashboard():
    return render_template("teacher_dashboard.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/student_profile")
def student_profile():
    return render_template("student_profile.html")

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
