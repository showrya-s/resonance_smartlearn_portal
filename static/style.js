// ------------------- Firebase Initialization -------------------
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore, doc, getDoc } from "firebase/firestore";

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
const analytics = getAnalytics(app);
const db = getFirestore(app);

// ------------------- Firebase Login -------------------
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // In Firebase, authenticate user (dummy example, replace with your auth)
    // Here we assume the user exists in Firestore collection "users"
    try {
      const docRef = doc(db, "users", email);
      const docSnap = await getDoc(docRef);

      if (!docSnap.exists()) {
        document.getElementById("error-msg").innerText = "User not found!";
        return;
      }

      const user = docSnap.data();

      // Simple password check (for demo, you can use Firebase Auth later)
      if (user.password !== password) {
        document.getElementById("error-msg").innerText = "Incorrect password!";
        return;
      }

      // Redirect based on role
      if (user.role === "student") {
        window.location.href = "/student_dashboard";
      } else if (user.role === "teacher") {
        window.location.href = "/teacher_dashboard";
      } else {
        document.getElementById("error-msg").innerText = "Unknown role!";
      }

    } catch (err) {
      document.getElementById("error-msg").innerText = "Login error!";
      console.error(err);
    }
  });
}

// ------------------- Chat Functionality Hook -------------------
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    // Display user message
    chatBox.innerHTML += `<div class="user-msg">You: ${message}</div>`;
    chatInput.value = "";

    // Placeholder for OpenAI call (server-side)
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await response.json();

      chatBox.innerHTML += `<div class="ai-msg">AI: ${data.reply}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
      chatBox.innerHTML += `<div class="ai-msg">AI: Error connecting to server.</div>`;
    }
  });
}

// ------------------- Optional UI Enhancements -------------------
window.addEventListener("scroll", () => {
  const header = document.querySelector(".header");
  if (header) {
    header.style.boxShadow = window.scrollY > 0 ? "0 4px 10px rgba(0,0,0,0.2)" : "none";
  }
});
