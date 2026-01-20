// ------------------ Firebase Initialization ------------------
// Make sure you included Firebase scripts in your HTML before this
const firebaseConfig = {
  apiKey: "AIzaSyApDMmuJhsTuzlfK0zxZZbl1VEjdPp4FM8",
  authDomain: "resonance-portal.firebaseapp.com",
  projectId: "resonance-portal",
  storageBucket: "resonance-portal.firebasestorage.app",
  messagingSenderId: "955977806009",
  appId: "1:955977806009:web:ceb858298b16475747ab68",
  measurementId: "G-Z599TEBV6R"
};

const app = firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// ------------------ Login Form ------------------
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = loginForm["email"].value;
    const password = loginForm["password"].value;

    // Firebase login
    firebase.auth().signInWithEmailAndPassword(email, password)
      .then(async (cred) => {
        const uid = cred.user.uid;

        // Get role from Firestore
        const doc = await db.collection("users").doc(uid).get();
        if (!doc.exists) {
          alert("User data not found!");
          return;
        }
        const role = doc.data().role;

        // Redirect based on role
        if (role === "student") {
          window.location.href = "student_dashboard.html";
        } else if (role === "teacher") {
          window.location.href = "teacher_dashboard.html";
        } else {
          alert("Unknown role!");
        }
      })
      .catch((err) => {
        alert(err.message);
      });
  });
}

// ------------------ Logout Function ------------------
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    firebase.auth().signOut().then(() => {
      window.location.href = "login.html";
    });
  });
}

// ------------------ Auto Redirect if Logged In ------------------
firebase.auth().onAuthStateChanged(async (user) => {
  if (user) {
    const doc = await db.collection("users").doc(user.uid).get();
    if (!doc.exists) return;
    const role = doc.data().role;
    if (role === "student") {
      if (!window.location.href.includes("student_dashboard.html"))
        window.location.href = "student_dashboard.html";
    } else if (role === "teacher") {
      if (!window.location.href.includes("teacher_dashboard.html"))
        window.location.href = "teacher_dashboard.html";
    }
  }
});
