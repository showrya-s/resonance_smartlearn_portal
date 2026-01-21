// ---------------- FIREBASE ----------------
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyApDMmuJhsTuzlfK0zxZZbl1VEjdPp4FM8",
  authDomain: "resonance-portal.firebaseapp.com",
  projectId: "resonance-portal",
  storageBucket: "resonance-portal.firebasestorage.app",
  messagingSenderId: "955977806009",
  appId: "1:955977806009:web:ceb858298b16475747ab68",
  measurementId: "G-Z599TEBV6R"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// ---------------- LOGIN ----------------
const loginForm = document.getElementById("login-form");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = loginForm.email.value;
    const password = loginForm.password.value;

    try {
      const userCred = await signInWithEmailAndPassword(auth, email, password);
      const snap = await getDoc(doc(db, "users", email));
      const role = snap.exists() ? snap.data().role : "student";

      await fetch("/set-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, role })
      });

      // Redirect based on role
      window.location.href = "/dashboard";
    } catch (err) {
      alert("Login failed: " + err.message);
    }
  });
}

// ---------------- CHAT ----------------
const chatForm = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");

if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const msg = chatInput.value.trim();
    if (!msg) return;

    chatBox.innerHTML += `<div class="user-msg">🧑 ${msg}</div>`;
    chatInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      chatBox.innerHTML += `<div class="ai-msg">🤖 ${data.reply}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
      chatBox.innerHTML += `<div class="ai-msg">⚠️ Error: ${err.message}</div>`;
    }
  });
}
