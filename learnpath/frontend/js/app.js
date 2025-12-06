// Determine API base dynamically: prefer local dev server when developing,
// otherwise use same origin + /api so it works when served from a proxy.
const _API_HOST = (function(){
    const host = (typeof window !== 'undefined') ? window.location.hostname : '127.0.0.1';
    if (host === 'localhost' || host === '127.0.0.1') {
        return 'http://127.0.0.1:8000';
    }
    return (typeof window !== 'undefined') ? window.location.origin : 'http://127.0.0.1:8000';
})();
const API_BASE_URL = `${_API_HOST}/api`;
// Expose for other scripts (api.js) to reuse without redeclaring globals
if (typeof window !== 'undefined') window.API_BASE_URL = API_BASE_URL;

// ========== PAGE NAVIGATION ==========
function goToPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    
    // Track current page for session persistence
    if (localStorage.getItem("authToken")) {
        localStorage.setItem("currentPage", pageId);
    }
}

// Ensure courses are loaded whenever the user navigates to the courses page
// This covers cases where the page is switched via navigation without a full reload.
const _oldGoToPage = goToPage;
goToPage = function(pageId) {
    _oldGoToPage(pageId);
    try {
        if (pageId === 'coursesPage') {
            // Load courses each time the user visits the courses page
            loadCourses();
        }
    } catch (e) {
        console.warn('Failed to auto-load courses on navigation:', e);
    }
};

function switchTab(formId) {
    // Hide all forms
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    // Show selected form
    document.getElementById(formId).classList.add('active');
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// ========== LOGIN & REGISTER ==========
async function login(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    const errorMsg = document.getElementById("loginError");

    try {
        console.log("Attempting login with email:", email);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        console.log("Login response:", data);

        if (!response.ok) {
            errorMsg.textContent = data.error || "Invalid login details";
            return;
        }

        // Store token and user info
        localStorage.setItem("authToken", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        console.log("Login successful, token stored");
        
        // Clear form
        document.getElementById("login-form").reset();
        errorMsg.textContent = "";
        
        // Show navbar when logged in
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.classList.add('visible');
        
        // Redirect to home page after small delay
        setTimeout(() => {
            goToPage('homePage');
        }, 500);
        
    } catch (error) {
        console.error("Login error:", error);
        errorMsg.textContent = "Failed to connect to server: " + error.message;
    }
}

async function register(event) {
    event.preventDefault();

    const email = document.getElementById("registerEmail").value;
    const username = document.getElementById("registerUsername").value;
    const firstName = document.getElementById("registerFirstName").value;
    const lastName = document.getElementById("registerLastName").value;
    const password = document.getElementById("registerPassword").value;
    const password2 = document.getElementById("registerPassword2").value;
    const errorMsg = document.getElementById("registerError");

    if (password !== password2) {
        errorMsg.textContent = "Passwords don't match";
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email,
                username,
                first_name: firstName,
                last_name: lastName,
                password,
                password2
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            errorMsg.textContent = data.error || "Registration failed";
            return;
        }

        errorMsg.textContent = "";
        alert("Registration successful! Please login.");
        
        // Clear form and switch to login
        document.getElementById("register-form").reset();
        switchTab('login-form');
        
    } catch (error) {
        console.error("Register error:", error);
        errorMsg.textContent = "Failed to register: " + error.message;
    }
}

function logout() {
    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
    
    // Hide navbar when logged out
    const navbar = document.querySelector('.navbar');
    if (navbar) navbar.classList.remove('visible');
    
    goToPage('loginPage');
}

// ========== COURSES ==========
async function loadCourses() {
    try {
        const token = localStorage.getItem("authToken");
        const headers = { "Content-Type": "application/json" };
        
        // Add token if available (courses endpoint is AllowAny, but we include it if available)
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/courses/list`, {
            headers: headers
        });

        if (!response.ok) {
            console.error("Failed to load courses, status:", response.status);
            return;
        }

        const courses = await response.json();
        console.log("Courses loaded:", courses);

        const list = document.getElementById("coursesContainer");
        
        if (!list) {
            console.warn("Course list container not found");
            return;
        }

        list.innerHTML = "";
        if (!Array.isArray(courses) || courses.length === 0) {
            list.innerHTML = `<p class="no-courses">No courses available right now.</p>`;
            console.warn('No courses returned from API');
            return;
        }
        courses.forEach(course => {
            const courseCard = document.createElement("div");
            courseCard.className = "course-card";
            courseCard.innerHTML = `
                <div class="course-header">
                    <h3>${course.title}</h3>
                </div>
                <div class="course-body">
                    <p>${course.description}</p>
                    <p><strong>Difficulty:</strong> <span class="badge badge-${course.difficulty}">${course.difficulty.charAt(0).toUpperCase() + course.difficulty.slice(1)}</span></p>
                    <p><strong>Duration:</strong> ${course.duration_weeks} weeks</p>
                    <button onclick="selectCourse(${course.id})" class="btn btn-primary">
                        Start Assessment
                    </button>
                </div>
            `;
            list.appendChild(courseCard);
        });

    } catch (error) {
        console.error("Could not load courses:", error);
        alert("Failed to load courses");
    }
}

async function selectCourse(courseId) {
    const token = localStorage.getItem("authToken");
    
    // Check if assessment already completed for this course
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/check-status?course_id=${courseId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        const status = await response.json();
        console.log("Assessment status:", status);
        
        if (status.assessment_completed && status.roadmap_id) {
            // Assessment already completed, show results and roadmap option
            console.log("Assessment already completed, loading previous results");
            localStorage.setItem("selectedCourseId", courseId);
            localStorage.setItem("assessmentId", status.assessment_id);
            localStorage.setItem("roadmapId", status.roadmap_id);
            localStorage.setItem("assessmentCompleted", "true");
            
            // Fetch previous roadmap data to display results
            goToPage('resultsPage');
            loadPreviousResults(status.roadmap_id);
            return;
        }
    } catch (error) {
        console.warn("Could not check assessment status, starting fresh:", error);
    }
    
    // Start fresh assessment
    localStorage.setItem("selectedCourseId", courseId);
    localStorage.setItem("assessmentCompleted", "false");
    localStorage.removeItem("userAnswers");
    localStorage.removeItem("assessmentId");
    
    goToPage('assessmentPage');
    startAssessment();
}

// ========== ASSESSMENT ==========
async function startAssessment() {
    const courseId = localStorage.getItem("selectedCourseId");
    const token = localStorage.getItem("authToken");

    try {
        console.log("Starting assessment for course:", courseId);
        
        const response = await fetch(`${API_BASE_URL}/assessment/generate-questions`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ course_id: courseId })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Assessment response:", data);
        console.log("Total questions received:", data.questions ? data.questions.length : 0);
        
        if (!data.questions || data.questions.length === 0) {
            alert("No questions generated. Please try again.");
            return;
        }

        // Store assessment data
        localStorage.setItem("assessmentId", data.assessment_id);
        localStorage.setItem("assessmentQuestions", JSON.stringify(data.questions));
        console.log("Questions stored in localStorage");
        
        // Display first question
        displayQuestion(0);

    } catch (error) {
        console.error("Failed to generate questions:", error);
        alert("Failed to start assessment: " + error.message);
    }
}

function displayQuestion(index) {
    const questions = JSON.parse(localStorage.getItem("assessmentQuestions"));
    if (!questions || questions.length === 0) {
        console.error("No questions loaded");
        return;
    }

    const question = questions[index];
    if (!question) {
        console.error("Question not found at index:", index);
        return;
    }
    
    const container = document.getElementById("questionsContainer");
    if (!container) {
        console.error("Questions container not found");
        return;
    }

    console.log(`Displaying question ${index + 1} of ${questions.length}:`, question);

    // Update progress bar
    const progressFill = document.getElementById("progressFill");
    const questionNumber = document.getElementById("questionNumber");
    if (progressFill) {
        const progressPercent = ((index + 1) / questions.length) * 100;
        progressFill.style.width = progressPercent + "%";
    }
    if (questionNumber) {
        questionNumber.textContent = `Question ${index + 1} of ${questions.length}`;
    }

    const options = question.options;
    if (!options) {
        console.error("No options found for question:", question);
        return;
    }

    let optionsHtml = "";
    
    for (let option in options) {
        optionsHtml += `
            <div class="option">
                <label style="display: flex; align-items: center; cursor: pointer; width: 100%; margin: 0;">
                    <input type="radio" name="answer" value="${option}" onchange="selectAnswer('${index}', '${option}')">
                    <span>${option}: ${options[option]}</span>
                </label>
            </div>
        `;
    }

    container.innerHTML = `
        <div class="question-item">
            <h4>${question.question}</h4>
            <div class="options">
                ${optionsHtml}
            </div>
            <div class="assessment-actions">
                ${index > 0 ? `<button onclick="previousQuestion()" class="btn btn-secondary">Previous</button>` : ""}
                ${index < questions.length - 1 ? `<button onclick="nextQuestion()" class="btn btn-primary">Next</button>` : ""}
                ${index === questions.length - 1 ? `<button onclick="submitAssessment()" class="btn btn-primary">Submit Assessment</button>` : ""}
            </div>
        </div>
    `;
}

let userAnswers = {};

function selectAnswer(index, answer) {
    userAnswers[index] = answer;
    console.log("Answer recorded:", index, answer);
}

function nextQuestion() {
    const questionNumber = document.getElementById("questionNumber");
    if (questionNumber && questionNumber.textContent) {
        const text = questionNumber.textContent;
        const match = text.match(/Question (\d+) of/);
        if (match) {
            const currentIndex = parseInt(match[1]) - 1;
            displayQuestion(currentIndex + 1);
        }
    }
}

function previousQuestion() {
    const questionNumber = document.getElementById("questionNumber");
    if (questionNumber && questionNumber.textContent) {
        const text = questionNumber.textContent;
        const match = text.match(/Question (\d+) of/);
        if (match) {
            const currentIndex = parseInt(match[1]) - 1;
            displayQuestion(currentIndex - 1);
        }
    }
}

async function submitAssessment() {
    const assessmentId = localStorage.getItem("assessmentId");
    const token = localStorage.getItem("authToken");

    // Store user answers in localStorage for persistence
    localStorage.setItem("userAnswers", JSON.stringify(userAnswers));
    console.log("User answers saved:", userAnswers);

    try {
        const response = await fetch(`${API_BASE_URL}/assessment/submit`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                assessment_id: assessmentId,
                answers: userAnswers
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Assessment result:", data);

        // Store results comprehensively
        localStorage.setItem("assessmentScore", data.score);
        localStorage.setItem("assessmentTotal", data.total_questions);
        localStorage.setItem("assessmentPercentage", data.percentage);
        localStorage.setItem("skillLevel", data.skill_level);
        localStorage.setItem("assessmentCompleted", "true");
        localStorage.setItem("assessmentSubmittedAt", new Date().toISOString());

        console.log("Assessment completed - Score:", data.score, "Percentage:", data.percentage, "Skill Level:", data.skill_level);

        // Show results
        goToPage('resultsPage');
        displayResults(data);

        // Automatically generate and show the LLM-based roadmap for this assessment
        // using the LLM-generated skill level. This avoids requiring the user to
        // click the "Generate Roadmap" button.
        try {
            const skill = data.skill_level || localStorage.getItem('skillLevel');
            // Slight delay so results UI is visible before heavy LLM call
            setTimeout(() => {
                generateRoadmap(skill);
            }, 250);
        } catch (e) {
            console.warn('Auto-generate roadmap failed to start:', e);
        }

    } catch (error) {
        console.error("Failed to submit assessment:", error);
        alert("Failed to submit assessment: " + error.message);
    }
}

function displayResults(data) {
    // Ensure data is stored in localStorage for persistence
    if (data.score !== undefined) {
        localStorage.setItem("assessmentScore", data.score);
    }
    if (data.total_questions !== undefined) {
        localStorage.setItem("assessmentTotal", data.total_questions);
    }
    if (data.percentage !== undefined) {
        localStorage.setItem("assessmentPercentage", data.percentage);
    }
    if (data.skill_level !== undefined) {
        localStorage.setItem("skillLevel", data.skill_level);
    }
    
    // Update score circle
    const scorePercentage = document.getElementById("scorePercentage");
    if (scorePercentage) {
        const percentValue = data.percentage !== undefined ? data.percentage : localStorage.getItem("assessmentPercentage");
        scorePercentage.textContent = Math.round(percentValue) + "%";
        console.log("Updated score percentage:", scorePercentage.textContent);
    }

    // Update skill level
    const skillLevelElement = document.getElementById("skillLevel");
    if (skillLevelElement) {
        const skillVal = data.skill_level || localStorage.getItem("skillLevel");
        skillLevelElement.textContent = `Skill Level: ${skillVal}`;
        console.log("Updated skill level:", skillLevelElement.textContent);
    }

    // Update score text
    const scoreText = document.getElementById("scoreText");
    if (scoreText) {
        const score = data.score !== undefined ? data.score : localStorage.getItem("assessmentScore");
        const total = data.total_questions !== undefined ? data.total_questions : localStorage.getItem("assessmentTotal");
        scoreText.textContent = `Score: ${score}/${total}`;
        console.log("Updated score text:", scoreText.textContent);
    }

    // Attach event listener to roadmap button
    const generateRoadmapBtn = document.getElementById("generateRoadmap");
    if (generateRoadmapBtn) {
        const skillLevel = data.skill_level || localStorage.getItem("skillLevel");
        generateRoadmapBtn.onclick = function() {
            generateRoadmap(skillLevel);
        };
    }

    console.log("Results displayed successfully");
}

function restoreResults() {
    // Restore assessment results from localStorage
    const score = localStorage.getItem("assessmentScore");
    const total = localStorage.getItem("assessmentTotal");
    const percentage = localStorage.getItem("assessmentPercentage");
    const skillLevel = localStorage.getItem("skillLevel");
    
    if (score && total && percentage && skillLevel) {
        const data = {
            score: parseInt(score),
            total_questions: parseInt(total),
            percentage: parseFloat(percentage),
            skill_level: skillLevel
        };
        displayResults(data);
        console.log("Assessment results restored from localStorage");
    }
}

async function generateRoadmap(skillLevel) {
    const assessmentId = localStorage.getItem("assessmentId");
    const token = localStorage.getItem("authToken");
    const roadmapId = localStorage.getItem("roadmapId");
    
    // Check if roadmap already exists for this assessment
    if (roadmapId && localStorage.getItem("roadmapData")) {
        console.log("Roadmap already generated for this assessment, loading existing roadmap");
        const roadmapData = JSON.parse(localStorage.getItem("roadmapData"));
        goToPage('learningPage');
        displayRoadmap(roadmapData);
        return;
    }

    const durationWeeks = document.getElementById("durationWeeks") ? 
                          parseInt(document.getElementById("durationWeeks").value) : 12;
    
    // Get user answers for personalization
    const userAnswers = JSON.parse(localStorage.getItem("userAnswers") || "{}");
    console.log("User answers for roadmap:", userAnswers);

    try {
        console.log("Generating roadmap with skill_level:", skillLevel, "duration:", durationWeeks);
        
        const response = await fetch(`${API_BASE_URL}/assessment/generate-roadmap`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                assessment_id: assessmentId,
                duration_weeks: durationWeeks,
                skill_level: skillLevel,
                user_answers: userAnswers
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Roadmap generated:", data);

        // Store roadmap with completion metadata (store full API response for robust restore)
        localStorage.setItem("roadmapId", data.id);
        localStorage.setItem("roadmapData", JSON.stringify(data));
        localStorage.setItem("roadmapGeneratedAt", new Date().toISOString());
        localStorage.setItem("roadmapAssessmentId", assessmentId);
        
        console.log("Roadmap stored in localStorage");

        // Show roadmap
        goToPage('learningPage');
        displayRoadmap(data);

    } catch (error) {
        console.error("Failed to generate roadmap:", error);
        alert("Failed to generate roadmap: " + error.message);
    }
}

async function loadPreviousResults(roadmapId) {
    const token = localStorage.getItem("authToken");
    
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/get-roadmap/${roadmapId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error(`Failed to load roadmap: ${response.status}`);
        }

        const roadmapData = await response.json();
        console.log("Previous roadmap loaded:", roadmapData);

        // Restore previous results
        const scorePercentage = document.getElementById("scorePercentage");
        if (scorePercentage && roadmapData.assessment) {
            scorePercentage.textContent = Math.round(roadmapData.assessment.percentage) + "%";
        }

        const skillLevelElement = document.getElementById("skillLevel");
        if (skillLevelElement) {
            skillLevelElement.textContent = `Skill Level: ${roadmapData.skill_level}`;
        }

        const scoreText = document.getElementById("scoreText");
        if (scoreText && roadmapData.assessment) {
            scoreText.textContent = `Score: ${roadmapData.assessment.score}/${roadmapData.assessment.total_questions}`;
        }

        // Attach event listener to roadmap button
        const generateRoadmapBtn = document.getElementById("generateRoadmap");
        if (generateRoadmapBtn) {
            generateRoadmapBtn.textContent = "View Your Roadmap";
            generateRoadmapBtn.onclick = function() {
                goToPage('learningPage');
                displayRoadmap(roadmapData);
            };
        }

    } catch (error) {
        console.error("Failed to load previous results:", error);
    }
}

function displayRoadmap(roadmapData) {
    console.debug('displayRoadmap called with:', roadmapData);

    // Extract roadmap object and chapters from multiple possible shapes
    let roadmap = null;
    if (!roadmapData) roadmap = null;
    else if (roadmapData.roadmap_data) roadmap = roadmapData.roadmap_data;
    else if (roadmapData.roadmap) roadmap = roadmapData.roadmap;
    else roadmap = roadmapData; // might already be the roadmap_data object

    let chapters = [];
    // If roadmap is a JSON string (some APIs may return stringified JSON), try to parse
    if (typeof roadmap === 'string') {
        try {
            roadmap = JSON.parse(roadmap);
        } catch (e) {
            console.warn('Failed to parse roadmap string:', e);
        }
    }
    if (roadmap && Array.isArray(roadmap.chapters)) chapters = roadmap.chapters;

    // Build an aggregated list of all topics across available shapes
    // (chapters, related_topics, learning_resources, modules, or course.videos)
    (function buildCourseTopicsEarly() {
        // collect resources from roadmap and chapters
        const allResources = [];
        if (Array.isArray(roadmap.learning_resources)) roadmap.learning_resources.forEach(r => allResources.push(r));
        if (Array.isArray(roadmap.related_topics)) roadmap.related_topics.forEach(rt => allResources.push({ title: rt }));
        if (Array.isArray(roadmap.modules)) roadmap.modules.forEach(m => {
            if (m && m.learning_resources && Array.isArray(m.learning_resources)) m.learning_resources.forEach(r => allResources.push(r));
        });
        if (roadmapData && roadmapData.course && Array.isArray(roadmapData.course.videos)) roadmapData.course.videos.forEach(v => allResources.push(v));

        function findResourceForTopicGlobal(topic) {
            if (!topic) return null;
            const tLow = topic.toLowerCase();
            for (let r of allResources) {
                try {
                    if ((r.source && (r.source === 'admin' || r.source === 'course_admin')) && r.url) return r;
                } catch (e) {}
            }
            for (let r of allResources) {
                try {
                    const title = (r.title || '').toLowerCase();
                    const summary = (r.summary || r.description || '').toLowerCase();
                    if ((title && title.includes(tLow)) || (summary && summary.includes(tLow))) return r;
                } catch (e) {}
            }
            for (let r of allResources) {
                if (r && r.url) return r;
            }
            return null;
        }

        const topicSet = new Set();
        // gather from chapters if present
        if (Array.isArray(chapters) && chapters.length > 0) {
            chapters.forEach(ch => {
                const tlist = Array.isArray(ch.topics) ? ch.topics : (ch.topics ? [ch.topics] : []);
                tlist.forEach(t => {
                    const tstr = (typeof t === 'string') ? t : (t.title || t.name || JSON.stringify(t));
                    if (tstr) topicSet.add(tstr);
                });
            });
        }
        // gather related_topics
        if (Array.isArray(roadmap.related_topics)) roadmap.related_topics.forEach(rt => { if (rt) topicSet.add(rt); });
        // gather module titles and module topics
        if (Array.isArray(roadmap.modules)) roadmap.modules.forEach(m => {
            if (typeof m === 'string') topicSet.add(m);
            if (m && typeof m === 'object') {
                const mname = m.title || m.name; if (mname) topicSet.add(mname);
                const tlist = Array.isArray(m.topics) ? m.topics : (m.topics ? [m.topics] : []);
                tlist.forEach(t => { const tstr = (typeof t === 'string') ? t : (t.title || t.name || JSON.stringify(t)); if (tstr) topicSet.add(tstr); });
            }
        });
        // gather from course.videos titles
        if (roadmapData && roadmapData.course && Array.isArray(roadmapData.course.videos)) roadmapData.course.videos.forEach(v => { if (v && (v.topic || v.title)) topicSet.add(v.topic || v.title); });

        const topicsArr = Array.from(topicSet);
        let topicsContainer = document.getElementById('courseTopicsContainer');
        if (!topicsContainer) {
            topicsContainer = document.createElement('div');
            topicsContainer.id = 'courseTopicsContainer';
            topicsContainer.className = 'course-topics-summary';
            // insert before chaptersList if present, otherwise prepend to chapterContent parent
            const insertBeforeEl = document.getElementById('chaptersList') || document.getElementById('chapterContent');
            if (insertBeforeEl && insertBeforeEl.parentNode) insertBeforeEl.parentNode.insertBefore(topicsContainer, insertBeforeEl);
            else if (chapterContent && chapterContent.parentNode) chapterContent.parentNode.insertBefore(topicsContainer, chapterContent);
        }

        if (topicsArr.length === 0) {
            // If no chapters, try to synthesize a chapter from available data.
            // Priority: use existing learning_resources, then course.videos, else generate a fallback 1-chapter roadmap with 5 topics and curated resources so the page is never empty.
            if (roadmap && Array.isArray(roadmap.learning_resources) && roadmap.learning_resources.length > 0) {
            const itemsHtml = topicsArr.map(t => {
                const res = findResourceForTopicGlobal(t);
                if (res && res.url) {
                    return `<li class="course-topic-item"><span class="topic-name">${t}</span> <a class="btn btn-primary btn-sm" href="${res.url}" target="_blank">Watch</a></li>`;
                }
                return `<li class="course-topic-item"><span class="topic-name">${t}</span> <button class="btn btn-secondary btn-sm" disabled>No video yet</button></li>`;
            } else if (roadmapData && roadmapData.course && Array.isArray(roadmapData.course.videos) && roadmapData.course.videos.length > 0) {
            topicsContainer.innerHTML = `<div class="course-topics-heading"><strong>Course Topics:</strong></div><ul class="course-topics-list">${itemsHtml}</ul>`;
        }
    })();

    // Populate course and skill level if available
    const courseTitleEl = document.getElementById('courseTitleLearning');
    const skillLevelEl = document.getElementById('skillLevelLearning');
    if (courseTitleEl) {
        const courseTitle = roadmapData && roadmapData.course ? roadmapData.course.title : (roadmap.course_title || 'Your Course');
        courseTitleEl.textContent = courseTitle;
    }
    if (skillLevelEl) {
        const skill = roadmapData && roadmapData.skill_level ? roadmapData.skill_level : (roadmap && roadmap.skill_level ? roadmap.skill_level : localStorage.getItem('skillLevel') || 'Unknown');
        skillLevelEl.textContent = `Skill Level: ${skill}`;
            } else {
                // No resources from server — synthesize a fallback roadmap with 5 topics and curated resources
                const courseTitle = (roadmapData && roadmapData.course && roadmapData.course.title) || (roadmap && roadmap.title) || 'Course';
                const skill = (roadmapData && roadmapData.skill_level) || (roadmap && roadmap.skill_level) || localStorage.getItem('skillLevel') || 'intermediate';
                const fallback = synthesizeFallbackRoadmap(courseTitle, skill);
                chapters = fallback.chapters;
                // store fallback into local roadmap variable so UI and localStorage behave consistently
                roadmap = fallback;
            }
    }

        // Synthesize fallback generator: creates 1 chapter with 5 topics tailored to course title keywords
        function synthesizeFallbackRoadmap(courseTitle, skillLevel) {
            // Normalize title for keyword checks
            const titleLower = (courseTitle || '').toLowerCase();
            let topics = [];

            if (titleLower.includes('javascript') || titleLower.includes('node')) {
                topics = [
                    'Modern JavaScript (ES6+)',
                    'Asynchronous Patterns (Promises & async/await)',
                    'Node.js Basics & Modules',
                    'Building REST APIs with Express',
                    'Authentication & Security Fundamentals'
                ];
            } else if (titleLower.includes('artificial') || titleLower.includes('machine')) {
                topics = [
                    'Supervised Learning Basics',
                    'Neural Networks & Deep Learning Intro',
                    'Data Preprocessing & Feature Engineering',
                    'Model Evaluation & Validation',
                    'Deployment of ML Models'
                ];
            } else if (titleLower.includes('data') || titleLower.includes('analytics')) {
                topics = [
                    'Data Wrangling with Python',
                    'Exploratory Data Analysis',
                    'Statistical Foundations',
                    'Machine Learning Introduction',
                    'Data Visualization & Storytelling'
                ];
            } else {
                // Generic full-stack topics
                topics = [
                    'Programming Fundamentals',
                    'HTTP & RESTful APIs',
                    'Frontend Basics',
                    'Databases & Persistence',
                    'Testing & Deployment'
                ];
            }

            // Map each topic to curated resources (at least one YouTube + one documentation link)
            const topicObjects = topics.map((t, i) => {
                // select resources from a small curated list by topic keywords
                const lower = t.toLowerCase();
                const resources = [];
                if (lower.includes('javascript') || lower.includes('node') || lower.includes('express') || lower.includes('frontend') ) {
                    resources.push({ type: 'youtube', title: `${t} - Tutorial`, url: 'https://www.youtube.com/watch?v=upDLs1sn7g4' });
                    resources.push({ type: 'documentation', title: 'MDN Web Docs', url: 'https://developer.mozilla.org/' });
                } else if (lower.includes('supervised') || lower.includes('neural') || lower.includes('model')) {
                    resources.push({ type: 'youtube', title: `${t} - Crash Course`, url: 'https://www.youtube.com/watch?v=aircAruvnKk' });
                    resources.push({ type: 'documentation', title: 'scikit-learn documentation', url: 'https://scikit-learn.org/stable/documentation.html' });
                } else if (lower.includes('data') || lower.includes('visualization') || lower.includes('analysis')) {
                    resources.push({ type: 'youtube', title: `${t} - Tutorial`, url: 'https://www.youtube.com/watch?v=r-uOLxNrNk8' });
                    resources.push({ type: 'documentation', title: 'Pandas Documentation', url: 'https://pandas.pydata.org/docs/' });
                } else if (lower.includes('testing') || lower.includes('deployment') || lower.includes('ci')) {
                    resources.push({ type: 'youtube', title: `${t} - Guide`, url: 'https://www.youtube.com/watch?v=R8_veQiYBjI' });
                    resources.push({ type: 'documentation', title: '12 Factor App', url: 'https://12factor.net/' });
                } else {
                    // generic
                    resources.push({ type: 'youtube', title: `${t} - Overview`, url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' });
                    resources.push({ type: 'documentation', title: 'Wikipedia Overview', url: 'https://en.wikipedia.org/' });
                }

                // ensure at least two resources
                if (resources.length < 2) resources.push({ type: 'documentation', title: 'MDN', url: 'https://developer.mozilla.org/' });

                const tools = [];
                if (lower.includes('javascript') || lower.includes('frontend')) {
                    tools.push({ tool_name: 'Vite', description: 'Fast frontend tooling', official_url: 'https://vitejs.dev/' });
                } else if (lower.includes('node') || lower.includes('express')) {
                    tools.push({ tool_name: 'Postman', description: 'API client for testing endpoints', official_url: 'https://www.postman.com/' });
                } else if (lower.includes('neural') || lower.includes('model') || lower.includes('supervised')) {
                    tools.push({ tool_name: 'scikit-learn', description: 'Machine learning library for Python', official_url: 'https://scikit-learn.org/' });
                } else if (lower.includes('data') || lower.includes('analysis')) {
                    tools.push({ tool_name: 'Pandas', description: 'Data analysis library for Python', official_url: 'https://pandas.pydata.org/' });
                } else {
                    tools.push({ tool_name: 'GitHub', description: 'Source control and CI integration', official_url: 'https://github.com/' });
                }

                const miniProjects = [
                    { project_title: `${t} - Hands-on Exercise`, description: `Practical mini-project to apply ${t}.` }
                ];

                return {
                    topic_number: i + 1,
                    topic_title: t,
                    learning_resources: resources,
                    tools: tools,
                    mini_projects: miniProjects
                };
            });

            return {
                title: courseTitle,
                skill_level: skillLevel,
                chapters: [
                    {
                        chapter_number: 1,
                        title: `${courseTitle} - Recommended Roadmap`,
                        topics: topicObjects
                    }
                ]
            };
        }

    // Sidebar chapters list and main content containers
    const chaptersList = document.getElementById('chaptersList');
    const chapterContent = document.getElementById('chapterContent');
    if (!chaptersList || !chapterContent) return;

    chaptersList.innerHTML = '';
    chapterContent.innerHTML = '';

    // Build an aggregated list of all topics across chapters and show them
    // as a quick-access 'Course Topics' area above the chapters list.
    (function buildCourseTopics() {
        // Collect all learning resources from all chapters to match admin videos
        const allResources = [];
        chapters.forEach(ch => {
            const res = Array.isArray(ch.learning_resources) ? ch.learning_resources : (ch.learning_resources ? [ch.learning_resources] : []);
            res.forEach(r => allResources.push(r));
            // also include course-level resources if present on chapter object
            if (Array.isArray(ch.resources)) ch.resources.forEach(r => allResources.push(r));
        });

        // Helper used to find an appropriate resource for a topic
        function findResourceForTopicGlobal(topic) {
            if (!topic) return null;
            const tLow = topic.toLowerCase();
            // Prefer explicit admin-sourced resources
            for (let r of allResources) {
                try {
                    if ((r.source && (r.source === 'admin' || r.source === 'course_admin')) && r.url) return r;
                } catch (e) {}
            }
            // Match by title/description
            for (let r of allResources) {
                try {
                    const title = (r.title || '').toLowerCase();
                    const summary = (r.summary || r.description || '').toLowerCase();
                    if ((title && title.includes(tLow)) || (summary && summary.includes(tLow))) return r;
                } catch (e) {}
            }
            // Fallback: first resource with a url
            for (let r of allResources) {
                if (r && r.url) return r;
            }
            return null;
        }

        // Gather unique topics
        const topicSet = new Set();
        chapters.forEach(ch => {
            const tlist = Array.isArray(ch.topics) ? ch.topics : (ch.topics ? [ch.topics] : []);
            tlist.forEach(t => {
                const tstr = (typeof t === 'string') ? t : (t.title || t.name || JSON.stringify(t));
                if (tstr) topicSet.add(tstr);
            });
        });

        const topicsArr = Array.from(topicSet);
        // Ensure there's a container above chaptersList to show these topics
        let topicsContainer = document.getElementById('courseTopicsContainer');
        if (!topicsContainer) {
            topicsContainer = document.createElement('div');
            topicsContainer.id = 'courseTopicsContainer';
            topicsContainer.className = 'course-topics-summary';
            chaptersList.parentNode.insertBefore(topicsContainer, chaptersList);
        }

        // Build HTML
        if (topicsArr.length === 0) {
            topicsContainer.innerHTML = '<div class="course-topics-heading"><strong>Course Topics:</strong> <span>No topics available</span></div>';
        } else {
            const itemsHtml = topicsArr.map(t => {
                const res = findResourceForTopicGlobal(t);
                if (res && res.url) {
                    return `<li class="course-topic-item"><span class="topic-name">${t}</span> <a class="btn btn-primary btn-sm" href="${res.url}" target="_blank">Watch</a></li>`;
                }
                return `<li class="course-topic-item"><span class="topic-name">${t}</span> <button class="btn btn-secondary btn-sm" disabled>No video yet</button></li>`;
            }).join('');
            topicsContainer.innerHTML = `<div class="course-topics-heading"><strong>Course Topics:</strong></div><ul class="course-topics-list">${itemsHtml}</ul>`;
        }
    })();

    if (chapters.length === 0) {
        // If no chapters but there are learning_resources at top level, synthesize a single chapter
        if (roadmap && Array.isArray(roadmap.learning_resources) && roadmap.learning_resources.length > 0) {
            chapters = [{
                chapter_number: 1,
                title: roadmap.title || (roadmapData.course && roadmapData.course.title) || 'Resources',
                topics: roadmap.related_topics || [],
                learning_resources: roadmap.learning_resources
            }];
        } else if (roadmapData && roadmapData.course && Array.isArray(roadmapData.course.videos) && roadmapData.course.videos.length > 0) {
            // Synthesize a chapter from admin-provided course videos
            const vids = roadmapData.course.videos.map(v => ({
                type: (v.url && (v.url.includes('youtube.com') || v.url.includes('youtu.be'))) ? 'youtube' : 'video',
                title: v.title || v.name || 'Video',
                url: v.url,
                description: v.description || '',
                channel: v.channel || '' ,
            }));
            chapters = [{
                chapter_number: 1,
                title: `${(roadmapData.course && roadmapData.course.title) || 'Course'}: Video Tutorials`,
                topics: [],
                learning_resources: vids
            }];
        } else {
            chaptersList.innerHTML = '<p>No chapters available</p>';
            chapterContent.innerHTML = '<p>No content available</p>';
            return;
        }
    }

    // Helper to render a chapter into the main content area
    function renderChapter(chapter, index) {
        const title = chapter.title || `Chapter ${index + 1}`;
        const duration = chapter.duration_hours || chapter.duration || chapter.estimated_hours || 'Unknown';
        const topics = Array.isArray(chapter.topics) ? chapter.topics : (chapter.topics ? [chapter.topics] : []);
        const resources = Array.isArray(chapter.learning_resources) ? chapter.learning_resources : (chapter.resources && chapter.resources.items ? chapter.resources.items : []);

        // Build resource cards (prefer YouTube/video cards)
        let resourcesHtml = '';
        if (resources.length > 0) {
            // Create grid of cards
            resourcesHtml = '<div class="resource-cards">' + resources.map(r => {
                const title = r.title || r.name || r.video_title || 'Video';
                const url = r.url || r.link || r.video_url || '';
                const desc = r.description || r.summary || '';
                const type = (r.type || '').toLowerCase();
                if (type === 'youtube' || url.includes('youtube.com') || url.includes('youtu.be')) {
                    return `
                        <div class="video-card">
                            <div class="video-thumb">▶</div>
                            <div class="video-body">
                                <h4>${title}</h4>
                                <p class="video-meta">Video${r.channel ? ' - ' + r.channel : ''}</p>
                                <p class="video-desc">${desc}</p>
                                ${url ? `<a class="btn btn-primary" href="${url}" target="_blank">Watch</a>` : ''}
                            </div>
                        </div>
                    `;
                }
                // generic resource
                if (url) {
                    return `
                        <div class="resource-card">
                            <h4>${title}</h4>
                            <p>${desc}</p>
                            <a href="${url}" target="_blank">Open</a>
                        </div>
                    `;
                }
                return `<div class="resource-card"><h4>${title}</h4><p>${desc}</p></div>`;
            }).join('') + '</div>';
        } else if (chapter.resources && chapter.resources.documentation && chapter.resources.documentation.length) {
            resourcesHtml = '<ul>' + chapter.resources.documentation.map(d => `<li><a href="${d}" target="_blank">Documentation</a></li>`).join('') + '</ul>';
        } else {
            resourcesHtml = '<p>No resources available for this chapter.</p>';
        }

        // Helper: find admin resource matching a topic (by source flag or url/title match)
        function findResourceForTopic(topic, resources) {
            if (!topic) return null;
            const tLow = topic.toLowerCase();
            // Prefer explicit admin-sourced resources
            for (let r of resources) {
                try {
                    if ((r.source && r.source === 'admin') || (r.source && r.source === 'course_admin')) {
                        // if resource has a url, return it
                        if (r.url) return r;
                    }
                } catch (e) {}
            }
            // Next, try to match by title or topic substring
            for (let r of resources) {
                try {
                    const title = (r.title || '').toLowerCase();
                    const summary = (r.summary || r.description || '').toLowerCase();
                    if ((title && title.includes(tLow)) || (summary && summary.includes(tLow))) return r;
                } catch (e) {}
            }
            // Finally, return first resource that has a url (best-effort)
            for (let r of resources) {
                if (r.url) return r;
            }
            return null;
        }

        // Build topics HTML: always show topics with a button. If no admin URL exists, show disabled placeholder.
        let topicsHtml = '';
        if (topics.length > 0) {
            topicsHtml = '<ul>' + topics.map(t => {
                const res = findResourceForTopic(t, resources) || null;
                if (res && res.url) {
                    return `<li><span class="topic-name">${t}</span> <a class="btn btn-primary btn-sm" href="${res.url}" target="_blank">Watch</a></li>`;
                }
                // No resource yet - show disabled button / placeholder link that can be filled by admin later
                return `<li><span class="topic-name">${t}</span> <button class="btn btn-secondary btn-sm" disabled>No video yet</button></li>`;
            }).join('') + '</ul>';
        } else {
            topicsHtml = '<p>No topics listed for this chapter.</p>';
        }

        chapterContent.innerHTML = `
            <div class="chapter-main">
                <h2>${title}</h2>
                <p><strong>Estimated duration:</strong> ${duration} hours</p>
                <div class="chapter-topics"><strong>Topics:</strong>
                    ${topicsHtml}
                </div>
                <div class="chapter-resources"><strong>Resources:</strong>
                    ${resourcesHtml}
                </div>
                ${roadmap && roadmap.summary ? `<div class="roadmap-summary"><strong>Summary:</strong><p>${roadmap.summary}</p></div>` : ''}
                ${Array.isArray(chapter.tools) && chapter.tools.length ? `
                    <div class="chapter-tools"><strong>Tools:</strong>
                        <ul>${chapter.tools.map(tool => `<li><a href="${tool.get('url') || '#'}" target="_blank">${tool.title || tool.name || tool}</a> - ${tool.description || ''}</li>`).join('')}</ul>
                    </div>
                ` : ''}
                ${Array.isArray(chapter.projects) && chapter.projects.length ? `
                    <div class="chapter-projects"><strong>Projects:</strong>
                        <ul>${chapter.projects.map(p => `<li><a href="${p.get('url') || '#'}" target="_blank">${p.title || p.name || p}</a> - ${p.description || ''}</li>`).join('')}</ul>
                    </div>
                ` : ''}
            </div>
        `;

        // Mark active chapter in sidebar
        document.querySelectorAll('#chaptersList .chapter-entry').forEach(el => el.classList.remove('active'));
        const activeEl = document.querySelector(`#chaptersList .chapter-entry[data-index='${index}']`);
        if (activeEl) activeEl.classList.add('active');
    }

    // Build sidebar entries
    chapters.forEach((chapter, idx) => {
        const entry = document.createElement('div');
        entry.className = 'chapter-entry';
        entry.setAttribute('data-index', idx);
        entry.innerHTML = `<strong>Chapter ${chapter.chapter_number || idx + 1}:</strong> <div class="chapter-title">${chapter.title || `Chapter ${idx + 1}`}</div>`;
        entry.onclick = () => renderChapter(chapter, idx);
        chaptersList.appendChild(entry);
    });

    // Render first chapter by default
    renderChapter(chapters[0], 0);
}

function startLearning(chapterIndex) {
    localStorage.setItem("currentChapterIndex", chapterIndex);
    // Open learning page and show the selected chapter
    const chaptersList = document.getElementById('chaptersList');
    if (chaptersList) {
        goToPage('learningPage');
        // trigger click on the sidebar entry if present
        const entry = document.querySelector(`#chaptersList .chapter-entry[data-index='${chapterIndex}']`);
        if (entry) {
            entry.click();
        }
    } else {
        // fallback: go to dashboard
        goToPage('dashboardPage');
    }
}

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem("authToken");
    const navbar = document.querySelector('.navbar');

    // Determine whether to restore session state or show public courses.
    const assessmentCompleted = localStorage.getItem("assessmentCompleted");
    const roadmapId = localStorage.getItem("roadmapId");
    const currentPage = localStorage.getItem("currentPage");

    if (token) {
        // User is logged in, show navbar
        if (navbar) navbar.classList.add('visible');

        // If assessment completed, restore results regardless of roadmap presence
        if (assessmentCompleted === "true") {
            console.log("Restoring to results page from saved state");
            goToPage('resultsPage');
            restoreResults();
            if (roadmapId) loadPreviousResults(roadmapId);
        } else if (currentPage && currentPage !== 'loginPage') {
            console.log("Restoring to previous page:", currentPage);
            goToPage(currentPage);
            if (currentPage === 'coursesPage') {
                loadCourses();
            } else if (currentPage === 'resultsPage') {
                restoreResults();
            } else if (currentPage === 'learningPage') {
                const roadmapData = JSON.parse(localStorage.getItem('roadmapData') || 'null');
                if (roadmapData) {
                    goToPage('learningPage');
                    displayRoadmap(roadmapData);
                } else {
                    loadCourses();
                }
            }
        } else {
            goToPage('homePage');
            loadCourses();
        }

    } else {
        // Not logged in: show public home page with course list (AllowAny API)
        if (navbar) navbar.classList.remove('visible');

        if (assessmentCompleted === "true") {
            // If the user had completed an assessment previously on this browser,
            // restore results view even when not logged in (useful for demos).
            console.log("Restoring results page for anonymous user");
            goToPage('resultsPage');
            restoreResults();
            if (roadmapId) loadPreviousResults(roadmapId);
        } else {
            goToPage('homePage');
            loadCourses();
        }
    }

    // Attach form submit events
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }
});
