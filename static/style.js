// ===================== FIREBASE INIT =====================
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-analytics.js";

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

// ===================== OPENAI CHAT =====================
const chatForm = document.querySelector(".chat-input form");
const chatInput = document.querySelector(".chat-input input");
const chatContainer = document.querySelector(".chat-container");

async function sendMessage(message) {
  if (!message) return;
  appendMessage("student", message);
  chatInput.value = "";

  try {
    const response = await fetch("/ai_chat", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({ message })
    });
    const data = await response.json();
    appendMessage("ai", data.reply);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } catch(err) {
    appendMessage("ai", "Error connecting to AI.");
  }
}

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.classList.add("chat-message", sender);
  div.textContent = text;
  chatContainer.appendChild(div);
}

// ===================== EVENT LISTENERS =====================
chatForm?.addEventListener("submit", e => {
  e.preventDefault();
  sendMessage(chatInput.value);
});

// ===================== STICKY HEADER SHADOW =====================
const header = document.querySelector(".header");
window.addEventListener("scroll", () => {
  if(window.scrollY>10) header.style.boxShadow="0 6px 20px rgba(0,0,0,0.2)";
  else header.style.boxShadow="0 4px 10px rgba(0,0,0,0.1)";
});

// ===================== SIMPLE UI UPGRADES =====================
document.querySelectorAll(".card").forEach(card=>{
  card.addEventListener("mouseenter", ()=>card.style.transform="translateY(-5px)");
  card.addEventListener("mouseleave", ()=>card.style.transform="translateY(0)");
});

document.querySelectorAll("button").forEach(btn=>{
  btn.addEventListener("mouseenter", ()=>btn.style.opacity="0.9");
  btn.addEventListener("mouseleave", ()=>btn.style.opacity="1");
});

// ===================== SCROLL SMOOTH =====================
document.documentElement.style.scrollBehavior = "smooth";

// ===================== DUMMY FUNCTION FOR AI PLACEHOLDER =====================
async function dummyAI(message) {
  return `You said: ${message}. Here’s a method to solve it... (AI powered)`;
}

// ===================== MORE STYLING INTERACTIONS =====================
// Card gradients
document.querySelectorAll(".card").forEach(card=>{
  card.style.background = "linear-gradient(135deg,#f0f9ff,#e0f7fa)";
  card.style.transition = "0.4s";
});
// Button shadow animations
document.querySelectorAll(".button").forEach(btn=>{
  btn.style.boxShadow = "0 5px 15px rgba(0,123,255,0.3)";
  btn.addEventListener("mousedown", ()=>btn.style.boxShadow="0 2px 5px rgba(0,123,255,0.2)");
  btn.addEventListener("mouseup", ()=>btn.style.boxShadow="0 5px 15px rgba(0,123,255,0.3)");
});
// Table row hover animations
document.querySelectorAll("tr").forEach(tr=>{
  tr.addEventListener("mouseenter", ()=>tr.style.background="#d9f1ff");
  tr.addEventListener("mouseleave", ()=>tr.style.background="#fff");
});
