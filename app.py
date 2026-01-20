import os
from flask import Flask, render_template, request, jsonify, session, redirect
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "resonance_super_secret"

# OpenAI client (REAL)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chat-page")
def chat_page():
    if "user" not in session:
        return redirect("/")
    return render_template("chat.html")

@app.route("/set-session", methods=["POST"])
def set_session():
    data = request.json
    session["user"] = data.get("email")
    session["role"] = data.get("role")
    return jsonify({"status": "ok"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Not logged in"}), 401

    data = request.json
    message = data.get("message")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful educational AI tutor."},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"AI Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

