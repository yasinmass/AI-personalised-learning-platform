const API_BASE_URL = "http://127.0.0.1:8000";   // Django backend

// ---------- LOGIN ----------
async function login(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            alert("Invalid login details");
            return;
        }

        const data = await response.json();
        localStorage.setItem("token", data.token);
        window.location.href = "dashboard.html";
    } catch (error) {
        alert("Failed to connect to server");
    }
}

// ---------- LOAD COURSES ----------
async function loadCourses() {
    try {
        const token = localStorage.getItem("token");

        const response = await fetch(`${API_BASE_URL}/api/courses/list/`, {
            headers: { "Authorization": `Token ${token}` }
        });

        const courses = await response.json();

        const list = document.getElementById("course-list");
        list.innerHTML = "";

        courses.forEach(c => {
            list.innerHTML += `<li>${c.title}</li>`;
        });

    } catch (error) {
        alert("Could not load courses");
    }
}

// ---------- GENERATE QUESTIONS ----------
async function generateQuestions() {
    try {
        const token = localStorage.getItem("token");

        const response = await fetch(`${API_BASE_URL}/api/assessment/generate-questions`, {
            method: "POST",
            headers: {
                "Authorization": `Token ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });

        const data = await response.json();
        console.log("Questions:", data);

        alert("Questions generated. Check console.");

    } catch (error) {
        alert("Failed to generate questions");
    }
}
