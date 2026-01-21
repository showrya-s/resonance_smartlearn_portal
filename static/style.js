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

// ---------------- UTILITIES ----------------
function safeAppend(el, html) {
  el.insertAdjacentHTML("beforeend", html);
  el.scrollTop = el.scrollHeight;
}

function sanitize(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------- LOGIN ----------------
const loginForm = document.getElementById("login-form");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = loginForm.email.value.trim();
    const password = loginForm.password.value.trim();

    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }

    try {
      const userCred = await signInWithEmailAndPassword(auth, email, password);
      const snap = await getDoc(doc(db, "users", email));
      const role = snap.exists() ? snap.data().role : "student";

      await fetch("/set-session", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, role })
      });

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

if (chatForm && chatBox && chatInput) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const msg = chatInput.value.trim();
    if (!msg) return;

    safeAppend(chatBox, `<div class="user-msg">🧑 ${sanitize(msg)}</div>`);
    chatInput.value = "";

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      const reply = data.reply ? sanitize(data.reply) : "No reply.";
      safeAppend(chatBox, `<div class="ai-msg">🤖 ${reply}</div>`);
    } catch (err) {
      safeAppend(chatBox, `<div class="ai-msg">⚠️ Error: ${sanitize(err.message)}</div>`);
    }
  });

  // Enter to send (without Shift)
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Auto-scroll on new messages
  const observer = new MutationObserver(() => {
    chatBox.scrollTop = chatBox.scrollHeight;
  });
  observer.observe(chatBox, { childList: true });
}

// ---------------- TEACHER DASHBOARD: Filters & Sort ----------------
(function initTeacherFilters() {
  const classSelect = document.getElementById("class");
  const sectionSelect = document.getElementById("section");
  const perfSelect = document.getElementById("performance");
  const applyBtn = document.querySelector(".filters-panel .button");
  const rows = document.querySelectorAll(".students-table tbody tr");

  if (!classSelect || !sectionSelect || !perfSelect || !applyBtn || rows.length === 0) return;

  function matches(row, cls, sec, perf) {
    const rClass = row.children[2].textContent.trim();
    const rSection = row.children[3].textContent.trim();
    const rPerf = row.children[5].textContent.trim();
    const classOk = (cls === "All" || rClass === cls);
    const sectionOk = (sec === "All" || rSection === sec);
    const perfOk = (perf === "All" || rPerf === perf);
    return classOk && sectionOk && perfOk;
  }

  applyBtn.addEventListener("click", () => {
    const cls = classSelect.value;
    const sec = sectionSelect.value;
    const perf = perfSelect.value;
    rows.forEach(row => {
      row.style.display = matches(row, cls, sec, perf) ? "" : "none";
    });
  });

  // Sort by clicking headers
  const table = document.querySelector(".students-table table");
  if (!table) return;
  const headers = table.querySelectorAll("th");

  function sortTableByColumn(table, column, asc = true) {
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    const sortedRows = rows.sort((a, b) => {
      const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
      const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();

      const aNum = parseFloat(aColText.replace("%",""));
      const bNum = parseFloat(bColText.replace("%",""));
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return (aNum - bNum) * dirModifier;
      }
      return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    });

    while (tBody.firstChild) tBody.removeChild(tBody.firstChild);
    tBody.append(...sortedRows);
  }

  headers.forEach((header, index) => {
    header.style.cursor = "pointer";
    header.addEventListener("click", () => {
      const currentIsAscending = header.classList.contains("th-sort-asc");
      headers.forEach(h => h.classList.remove("th-sort-asc", "th-sort-desc"));
      header.classList.toggle("th-sort-asc", !currentIsAscending);
      header.classList.toggle("th-sort-desc", currentIsAscending);
      sortTableByColumn(table, index, !currentIsAscending);
    });
  });
})();

// ---------------- TEACHER DASHBOARD: Remarks Submit UX ----------------
(function initRemarksSubmit() {
  const remarkCards = document.querySelectorAll(".remarks-panel .card");
  remarkCards.forEach(card => {
    const btn = card.querySelector("button");
    const ta = card.querySelector("textarea");
    if (!btn || !ta) return;
    btn.addEventListener("click", async () => {
      const studentLine = card.querySelector("p")?.textContent || "";
      const studentName = studentLine.replace("Student:", "").trim();
      const remark = ta.value.trim();
      if (!remark) {
        alert("Please enter a remark before submitting.");
        return;
      }
      // Placeholder for backend submission if needed:
      // await fetch("/api/teacher/remark", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ studentName, remark }) });
      ta.value = "";
      btn.textContent = "Submitted";
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = "Submit";
        btn.disabled = false;
      }, 2000);
    });
  });
})();

// ---------------- PROFILE: Hover Effects ----------------
(function initProfileHover() {
  const cards = document.querySelectorAll(".performance-summary .card");
  cards.forEach(card => {
    card.addEventListener("mouseenter", () => card.classList.add("shadow-hover"));
    card.addEventListener("mouseleave", () => card.classList.remove("shadow-hover"));
  });
})();

// ---------------- ACCESSIBILITY: Focus Main ----------------
(function initFocusMain() {
  const main = document.querySelector("main");
  if (main) {
    main.setAttribute("tabindex", "-1");
    window.addEventListener("load", () => main.focus());
  }
})();
