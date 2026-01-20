/* ==================== FIREBASE & OPENAI INITIALIZATION ==================== */
// Import Firebase SDK (assumes script included in HTML)
const firebaseConfig = {
    apiKey: "AIzaSyApDMmuJhsTuzlfK0zxZZbl1VEjdPp4FM8",
    authDomain: "resonance-portal.firebaseapp.com",
    projectId: "resonance-portal",
    storageBucket: "resonance-portal.firebasestorage.app",
    messagingSenderId: "955977806009",
    appId: "1:955977806009:web:ceb858298b16475747ab68",
    measurementId: "G-Z599TEBV6R"
};

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);
const analytics = firebase.analytics();
const db = firebase.firestore();

/* ==================== OPENAI CONFIG ==================== */
const openaiApiKey = "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";

/* ==================== FIREBASE AUTH ==================== */
function firebaseLogin(email, password) {
    firebase.auth().signInWithEmailAndPassword(email, password)
    .then((userCredential) => {
        const user = userCredential.user;
        console.log("Logged in:", user.uid);
    })
    .catch((error) => { console.error("Login error:", error); });
}

function firebaseLogout() {
    firebase.auth().signOut()
    .then(() => { console.log("Logged out"); })
    .catch((error) => { console.error("Logout error:", error); });
}

/* ==================== CHAT FUNCTIONS ==================== */
async function sendMessage(message, sender = "student") {
    // Add to Firebase Firestore
    await db.collection("chats").add({
        message: message,
        sender: sender,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });

    // Display message
    displayMessage(message, sender);

    // If student, also call OpenAI
    if(sender === "student") {
        const reply = await getAIResponse(message);
        displayMessage(reply, "ai");

        // Store AI response
        await db.collection("chats").add({
            message: reply,
            sender: "ai",
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });
    }
}

function displayMessage(message, sender) {
    const chatHistory = document.getElementById("chat-history");
    const div = document.createElement("div");
    div.className = sender === "ai" ? "ai-message" : "student-message";
    div.textContent = message;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

/* ==================== OPENAI CALL ==================== */
async function getAIResponse(userMessage) {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${openaiApiKey}`
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: [{role: "user", content: userMessage}],
            temperature: 0.7
        })
    });

    const data = await response.json();
    return data.choices[0].message.content;
}

/* ==================== LOAD CHAT HISTORY ==================== */
function loadChat() {
    db.collection("chats").orderBy("timestamp", "asc").onSnapshot(snapshot => {
        const chatHistory = document.getElementById("chat-history");
        chatHistory.innerHTML = "";
        snapshot.forEach(doc => {
            const chat = doc.data();
            displayMessage(chat.message, chat.sender);
        });
    });
}

/* ==================== INITIALIZATION ==================== */
document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const messageInput = document.getElementById("message-input");

    sendBtn.addEventListener("click", () => {
        const msg = messageInput.value.trim();
        if(msg !== "") {
            sendMessage(msg);
            messageInput.value = "";
        }
    });

    messageInput.addEventListener("keypress", (e) => {
        if(e.key === "Enter") {
            sendBtn.click();
        }
    });

    // Load previous messages
    loadChat();
});
