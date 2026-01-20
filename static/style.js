// ------------------ FIREBASE ------------------
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

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

// ------------------ AI CHAT ------------------
document.addEventListener("DOMContentLoaded", () => {
    const input = document.querySelector(".chat-input input");
    const button = document.querySelector(".chat-input button");
    const chatHistory = document.querySelector(".chat-history");

    if (input && button && chatHistory) {
        button.addEventListener("click", async () => {
            const prompt = input.value.trim();
            if (!prompt) return;
            appendMessage(prompt, "student-message");
            input.value = "";

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt })
                });
                const data = await response.json();
                appendMessage(data.response, "ai-message");
            } catch (err) {
                appendMessage("Error connecting to AI.", "ai-message");
            }
        });
    }

    function appendMessage(text, cls) {
        const div = document.createElement("div");
        div.classList.add("message", cls);
        div.textContent = text;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
