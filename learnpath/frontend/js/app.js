// Global variables
const API_BASE_URL = 'http://localhost:8000/api';
let currentUser = null;
let authToken = null;
let currentAssessmentId = null;
let currentRoadmapId = null;
let currentCourseId = null;
let assessmentAnswers = {};
let testAnswers = {};

// Initialize app on page load
document.addEventListener('DOMContentLoaded', function() {
    checkUserLoggedIn();
    setupEventListeners();
    loadCourses();
});

// Setup event listeners
function setupEventListeners() {
    // Authentication
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // Assessment
    document.getElementById('submitAssessment').addEventListener('click', submitAssessment);
    document.getElementById('generateRoadmap').addEventListener('click', generateRoadmap);
    
    // Chapter Test
    document.getElementById('submitTest').addEventListener('click', submitChapterTest);
    
    // Navigation
    document.getElementById('hamburger').addEventListener('click', toggleMobileMenu);
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
}

// Authentication Functions
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            errorDiv.textContent = '';
            goToPage('homePage');
            updateNavbar();
        } else {
            errorDiv.textContent = data.error || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error: ' + error.message;
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const firstName = document.getElementById('registerFirstName').value;
    const lastName = document.getElementById('registerLastName').value;
    const password = document.getElementById('registerPassword').value;
    const password2 = document.getElementById('registerPassword2').value;
    const errorDiv = document.getElementById('registerError');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email, 
                username, 
                first_name: firstName,
                last_name: lastName,
                password,
                password2
            })
        });

        const data = await response.json();

        if (response.ok) {
            errorDiv.textContent = '';
            alert('Registration successful! Please login.');
            switchTab('login-form');
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerUsername').value = '';
            document.getElementById('registerFirstName').value = '';
            document.getElementById('registerLastName').value = '';
            document.getElementById('registerPassword').value = '';
            document.getElementById('registerPassword2').value = '';
        } else {
            errorDiv.textContent = Object.values(data)[0] || 'Registration failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error: ' + error.message;
    }
}

function checkUserLoggedIn() {
    authToken = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (authToken && user) {
        currentUser = JSON.parse(user);
        goToPage('homePage');
        updateNavbar();
    } else {
        goToPage('loginPage');
        // Ensure navbar is hidden when not logged in
        updateNavbar();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    goToPage('loginPage');
    updateNavbar();
}

// Page Navigation
function goToPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    window.scrollTo(0, 0);
    
    // Load page-specific data
    if (pageId === 'profilePage') {
        loadProfile();
    } else if (pageId === 'dashboardPage') {
        loadDashboard();
    } else if (pageId === 'coursesPage') {
        loadCourses();
    }
}

function switchTab(formId) {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    document.getElementById(formId).classList.add('active');
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

function handleNavigation(e) {
    const href = e.target.getAttribute('href');
    if (href.startsWith('#')) {
        e.preventDefault();
        const pageId = href.substring(1) + 'Page';
        goToPage(pageId);
        document.getElementById('navLinks').classList.remove('active');
    }
}

function updateNavbar() {
    // Show navbar only when a user is logged in
    document.querySelectorAll('.navbar').forEach(nav => {
        nav.style.display = currentUser ? 'block' : 'none';
    });
}

// Course Functions
async function loadCourses() {
    try {
        const response = await fetch(`${API_BASE_URL}/courses/list`);
        const courses = await response.json();
        
        const container = document.getElementById('coursesContainer');
        container.innerHTML = '';
        
        courses.forEach(course => {
            const courseCard = createCourseCard(course);
            container.appendChild(courseCard);
        });
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

function createCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'course-card';
    
    const difficultyClass = `difficulty-${course.difficulty}`;
    
    card.innerHTML = `
        <div class="course-header">
            <h3>${course.title}</h3>
        </div>
        <div class="course-body">
            <span class="course-difficulty ${difficultyClass}">${course.difficulty.toUpperCase()}</span>
            <p class="course-description">${course.description.substring(0, 100)}...</p>
            <div class="course-meta">
                <span class="course-duration"><i class="fas fa-clock"></i> ${course.duration_weeks} weeks</span>
            </div>
            <div class="course-actions">
                <button class="btn btn-primary btn-small" onclick="startAssessment(${course.id})">Start Course</button>
            </div>
        </div>
    `;
    
    return card;
}

// Assessment Functions
async function startAssessment(courseId) {
    currentCourseId = courseId;
    
    try {
        // First check if user has already completed assessment for this course
        const checkResponse = await fetch(`${API_BASE_URL}/assessment/check-status?course_id=${courseId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const statusData = await checkResponse.json();
        
        // If assessment already completed, load the roadmap
        if (statusData.assessment_completed && statusData.roadmap_id) {
            currentAssessmentId = statusData.assessment_id;
            currentRoadmapId = statusData.roadmap_id;
            loadRoadmap(statusData.roadmap_id);
            return;
        }
        
        // Otherwise, generate new assessment questions
        generateAssessmentQuestions(courseId);
    } catch (error) {
        console.error('Error checking assessment status:', error);
        // Fallback: show assessment if check fails
        generateAssessmentQuestions(courseId);
    }
}

async function generateAssessmentQuestions(courseId) {
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/generate-questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ course_id: courseId })
        });

        const data = await response.json();
        
        if (response.ok) {
            currentAssessmentId = data.assessment_id;
            displayAssessmentQuestions(data.questions);
            goToPage('assessmentPage');
        } else {
            alert('Error generating questions: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayAssessmentQuestions(questions) {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    assessmentAnswers = {};
    
    questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        
        const optionsHtml = Object.keys(question.options).map(key => `
            <label class="option">
                <input type="radio" name="question-${index}" value="${key}" onchange="selectAnswer(${index}, '${key}')">
                <span>${key}. ${question.options[key]}</span>
            </label>
        `).join('');
        
        questionDiv.innerHTML = `
            <h4>Question ${index + 1}</h4>
            <p>${question.question}</p>
            ${optionsHtml}
        `;
        
        container.appendChild(questionDiv);
    });
    
    document.getElementById('questionNumber').textContent = `Questions 1 - ${questions.length}`;
    updateProgressBar(0, questions.length);
}

function selectAnswer(questionIndex, answer) {
    assessmentAnswers[questionIndex] = answer;
    updateProgressBar(Object.keys(assessmentAnswers).length, 
                     document.querySelectorAll('.question-item').length);
}

function updateProgressBar(completed, total) {
    const percentage = (completed / total) * 100;
    document.getElementById('progressFill').style.width = percentage + '%';
}

async function submitAssessment() {
    const totalQuestions = document.querySelectorAll('.question-item').length;
    
    if (Object.keys(assessmentAnswers).length < totalQuestions) {
        alert('Please answer all questions');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ 
                assessment_id: currentAssessmentId,
                answers: assessmentAnswers
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
            goToPage('resultsPage');
        } else {
            alert('Error submitting assessment: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayResults(assessment) {
    const percentage = Math.round(assessment.percentage);
    
    document.getElementById('scorePercentage').textContent = percentage + '%';
    document.getElementById('skillLevel').textContent = assessment.skill_level.toUpperCase();
    document.getElementById('scoreText').textContent = `${assessment.score} out of ${assessment.total_questions}`;
}

async function generateRoadmap() {
    const durationWeeks = parseInt(document.getElementById('durationWeeks').value);
    
    if (durationWeeks < 1) {
        alert('Please enter valid duration');
        return;
    }
    
    if (!currentAssessmentId) {
        alert('No assessment found. Please take the assessment first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/generate-roadmap`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ 
                assessment_id: currentAssessmentId,
                duration_weeks: durationWeeks
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            currentRoadmapId = data.id;
            displayLearningPath(data);
            goToPage('learningPage');
        } else {
            alert('Error generating roadmap: ' + (data.error || JSON.stringify(data)));
            console.error('Roadmap error:', data);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Roadmap fetch error:', error);
    }
}

// Learning Functions
async function loadRoadmap(roadmapId) {
    try {
        const response = await fetch(`${API_BASE_URL}/assessment/get-roadmap/${roadmapId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            currentRoadmapId = roadmapId;
            displayLearningPath(data);
            goToPage('learningPage');
        } else {
            console.error('Error loading roadmap:', data);
            alert('Error loading learning path');
        }
    } catch (error) {
        console.error('Error fetching roadmap:', error);
        alert('Error: ' + error.message);
    }
}

function displayLearningPath(roadmap) {
    const courseTitle = roadmap.course && roadmap.course.title ? roadmap.course.title : 'Unknown Course';
    document.getElementById('courseTitleLearning').textContent = courseTitle;
    document.getElementById('skillLevelLearning').textContent = 'Level: ' + roadmap.skill_level.toUpperCase();
    
    const roadmapData = roadmap.roadmap_data || {};
    
    // Handle both old format (chapters) and new format (modules)
    let items = [];
    if (roadmapData.modules) {
        // New format: convert modules to flat list of topics
        roadmapData.modules.forEach(module => {
            module.topics.forEach((topic, topicIndex) => {
                items.push({
                    module_number: module.module_number,
                    module_name: module.name,
                    topic_number: topic.topic_number,
                    name: topic.name,
                    explanation: topic.explanation,
                    duration_hours: topic.duration_hours,
                    youtube_videos: topic.youtube_videos || [],
                    documentation: topic.documentation || [],
                    official_docs: topic.official_docs,
                    tools: topic.tools || [],
                    summary: topic.summary,
                    assignments: topic.assignments || []
                });
            });
        });
    } else if (roadmapData.chapters) {
        // Old format: keep compatibility
        items = roadmapData.chapters.map((ch, idx) => ({
            module_number: ch.chapter_number,
            module_name: ch.title,
            topic_number: ch.chapter_number,
            name: ch.title,
            explanation: ch.topics ? ch.topics.join(', ') : '',
            duration_hours: ch.duration_hours,
            youtube_videos: ch.learning_resources ? ch.learning_resources.filter(r => r.type === 'youtube') : [],
            documentation: ch.learning_resources ? ch.learning_resources.filter(r => r.type === 'documentation') : [],
            official_docs: '#',
            tools: [],
            summary: ch.checkpoint || '',
            assignments: []
        }));
    }
    
    const chaptersList = document.getElementById('chaptersList');
    chaptersList.innerHTML = '';
    
    items.forEach((item, index) => {
        const chapterItem = document.createElement('div');
        chapterItem.className = 'chapter-item' + (index === 0 ? ' active' : '');
        chapterItem.innerHTML = `
            <div onclick="selectChapter(${roadmap.id}, ${index}, '${item.name.replace(/'/g, "\\'")}', '${item.module_name.replace(/'/g, "\\'")}')">
                <strong>${item.module_number}. ${item.name}</strong>
                <p style="font-size: 0.85rem; color: #666; margin: 0.25rem 0;">${item.module_name}</p>
                <div class="chapter-status">
                    <small>${item.duration_hours} hours</small>
                </div>
            </div>
        `;
        chaptersList.appendChild(chapterItem);
    });
    
    // Store items for later use
    window.currentRoadmapItems = items;
    
    if (items.length > 0) {
        selectChapter(roadmap.id, 0, items[0].name, items[0].module_name);
    }
}

function selectChapter(roadmapId, itemIndex, itemName, moduleName) {
    currentRoadmapId = roadmapId;
    
    // Update active chapter in sidebar
    document.querySelectorAll('.chapter-item').forEach((item, index) => {
        if (index === itemIndex) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Load and display chapter content
    loadChapterContent(roadmapId, itemIndex, itemName, moduleName);
}

async function loadChapterContent(roadmapId, itemIndex, itemName, moduleName) {
    try {
        // Get the stored items from displayLearningPath
        const items = window.currentRoadmapItems || [];
        const item = items[itemIndex];
        
        if (!item) return;
        
        const content = document.getElementById('chapterContent');
        
        // Build YouTube videos HTML
        const youtubeHtml = (item.youtube_videos || []).map(video => `
            <div class="resource-item">
                <div class="resource-icon">
                    <i class="fas fa-play-circle"></i>
                </div>
                <div class="resource-info">
                    <h4>${video.title || 'Video'}</h4>
                    <p class="resource-type">📺 Video - ${video.channel || 'Unknown Channel'}</p>
                    <p style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">${video.why || 'High-quality video tutorial'}</p>
                </div>
                <div class="resource-link">
                    ${video.url && video.url !== '#' ? `<a href="${video.url}" target="_blank" class="btn btn-sm">Watch</a>` : '<span class="btn btn-sm disabled">Coming Soon</span>'}
                </div>
            </div>
        `).join('');
        
        // Build Documentation HTML
        const docsHtml = (item.documentation || []).map(doc => `
            <div class="resource-item">
                <div class="resource-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <div class="resource-info">
                    <h4>${doc.title || 'Documentation'}</h4>
                    <p class="resource-type">📖 ${doc.type || 'Guide'}</p>
                </div>
                <div class="resource-link">
                    ${doc.url && doc.url !== '#' ? `<a href="${doc.url}" target="_blank" class="btn btn-sm">Read</a>` : '<span class="btn btn-sm disabled">Coming Soon</span>'}
                </div>
            </div>
        `).join('');
        
        // Build Tools HTML
        const toolsHtml = (item.tools || []).map(tool => `
            <div class="resource-item">
                <div class="resource-icon">
                    <i class="fas fa-wrench"></i>
                </div>
                <div class="resource-info">
                    <h4>${tool.name || 'Tool'}</h4>
                    <p class="resource-type">🛠 ${tool.purpose || 'Development Tool'}</p>
                </div>
                <div class="resource-link">
                    ${tool.url && tool.url !== '#' ? `<a href="${tool.url}" target="_blank" class="btn btn-sm">Visit</a>` : '<span class="btn btn-sm disabled">Coming Soon</span>'}
                </div>
            </div>
        `).join('');
        
        // Build Assignments HTML
        const assignmentsHtml = (item.assignments || []).map((assignment, idx) => `
            <div class="assignment-item">
                <span class="assignment-number">${idx + 1}</span>
                <p>${assignment}</p>
            </div>
        `).join('');
        
        content.innerHTML = `
            <div class="chapter-header">
                <div>
                    <p style="color: #0e5ba8; font-size: 0.9rem; margin: 0 0 0.5rem 0;"><strong>Module: ${moduleName}</strong></p>
                    <h2>${itemName}</h2>
                    <p style="color: #666; font-size: 0.95rem; margin-top: 0.5rem;">${item.explanation || ''}</p>
                </div>
                <div class="chapter-meta">
                    <span class="duration"><i class="fas fa-clock"></i> ${item.duration_hours} hours</span>
                </div>
            </div>
            
            <div class="chapter-section">
                <h3><i class="fas fa-lightbulb"></i> Summary</h3>
                <p style="line-height: 1.8; color: #333;">${item.summary || 'No summary available'}</p>
            </div>
            
            ${youtubeHtml ? `
            <div class="chapter-section">
                <h3><i class="fas fa-play-circle"></i> YouTube Videos</h3>
                <p style="color: #666; margin-bottom: 1rem; font-size: 0.9rem;">Learn from top-quality video tutorials</p>
                <div class="resources-grid">
                    ${youtubeHtml}
                </div>
            </div>
            ` : ''}
            
            ${docsHtml ? `
            <div class="chapter-section">
                <h3><i class="fas fa-book"></i> Documentation & Guides</h3>
                <p style="color: #666; margin-bottom: 1rem; font-size: 0.9rem;">Read official documentation and in-depth guides</p>
                <div class="resources-grid">
                    ${docsHtml}
                </div>
            </div>
            ` : ''}
            
            ${item.official_docs && item.official_docs !== '#' ? `
            <div class="chapter-section" style="background: #f0f7ff; border-left-color: #1f73b7;">
                <h3><i class="fas fa-globe"></i> Official Documentation</h3>
                <a href="${item.official_docs}" target="_blank" class="btn btn-primary" style="display: inline-block;">
                    <i class="fas fa-external-link-alt"></i> Visit Official Docs
                </a>
            </div>
            ` : ''}
            
            ${toolsHtml ? `
            <div class="chapter-section">
                <h3><i class="fas fa-wrench"></i> Tools & Software</h3>
                <p style="color: #666; margin-bottom: 1rem; font-size: 0.9rem;">Essential tools and software for this topic</p>
                <div class="resources-grid">
                    ${toolsHtml}
                </div>
            </div>
            ` : ''}
            
            ${assignmentsHtml ? `
            <div class="chapter-section">
                <h3><i class="fas fa-tasks"></i> Practice Assignments</h3>
                <p style="color: #666; margin-bottom: 1rem; font-size: 0.9rem;">Apply what you learned with these hands-on assignments</p>
                <div class="assignments-list">
                    ${assignmentsHtml}
                </div>
            </div>
            ` : ''}
            
            <div class="chapter-actions">
                <button class="btn btn-secondary" onclick="markChapterComplete(${roadmapId}, ${itemIndex})">
                    <i class="fas fa-check"></i> Mark Complete
                </button>
                <button class="btn btn-primary" onclick="startChapterTest(${roadmapId}, ${itemIndex})">
                    <i class="fas fa-pencil-alt"></i> Take Quiz
                </button>
            </div>
        `;
    } catch (error) {
        console.error('Error loading chapter:', error);
    }
}

function getResourceIcon(type) {
    switch (type) {
        case 'youtube': return 'play-circle';
        case 'documentation': return 'file-alt';
        case 'official_website': return 'globe';
        default: return 'link';
    }
}

function formatResourceType(type) {
    const typeMap = {
        'youtube': '📺 Video Tutorial',
        'documentation': '📖 Documentation',
        'official_website': '🌐 Official Website',
        'book': '📚 Book',
        'course': '🎓 Course',
        'article': '📰 Article'
    };
    return typeMap[type] || type;
}

function markChapterComplete(roadmapId, chapterNumber) {
    fetch(`${API_BASE_URL}/learning/track-progress`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            roadmap_id: roadmapId,
            chapter_number: chapterNumber,
            status: 'completed',
            time_spent_minutes: 60
        })
    }).then(response => response.json())
      .then(data => {
          alert('Chapter marked as complete!');
      })
      .catch(error => console.error('Error:', error));
}

async function startChapterTest(roadmapId, chapterNumber) {
    try {
        const response = await fetch(`${API_BASE_URL}/learning/chapter-test/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                roadmap_id: roadmapId,
                chapter_number: chapterNumber
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displayChapterTest(data.test_id, data.questions);
        } else {
            alert('Error generating test: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayChapterTest(testId, questions) {
    const container = document.getElementById('testQuestionsContainer');
    container.innerHTML = '';
    testAnswers = {};
    
    questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        
        const optionsHtml = Object.keys(question.options).map(key => `
            <label class="option">
                <input type="radio" name="test-question-${index}" value="${key}" onchange="selectTestAnswer(${index}, '${key}')">
                <span>${key}. ${question.options[key]}</span>
            </label>
        `).join('');
        
        questionDiv.innerHTML = `
            <h4>Question ${index + 1}</h4>
            <p>${question.question}</p>
            ${optionsHtml}
        `;
        
        container.appendChild(questionDiv);
    });
    
    document.getElementById('testModal').classList.add('active');
    document.getElementById('submitTest').onclick = () => submitChapterTest(testId);
}

function selectTestAnswer(questionIndex, answer) {
    testAnswers[questionIndex] = answer;
}

async function submitChapterTest(testId) {
    const totalQuestions = document.querySelectorAll('#testQuestionsContainer .question-item').length;
    
    if (Object.keys(testAnswers).length < totalQuestions) {
        alert('Please answer all questions');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/learning/chapter-test/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                test_id: testId,
                answers: testAnswers
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            alert(`Test submitted! Your score: ${data.percentage.toFixed(2)}%`);
            closeTestModal();
        } else {
            alert('Error submitting test: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function closeTestModal() {
    document.getElementById('testModal').classList.remove('active');
}

// Dashboard Functions
async function loadDashboard() {
    if (!currentRoadmapId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/learning/dashboard/${currentRoadmapId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();
        
        document.getElementById('progressPercent').textContent = 
            Math.round(data.progress.progress_percentage) + '%';
        document.getElementById('progressText').textContent = 
            `${data.progress.completed_chapters} / ${data.progress.total_chapters} Chapters`;
        
        document.getElementById('totalHours').textContent = 
            Math.round(data.time_tracking.total_hours) + ' hrs';
        
        document.getElementById('avgScore').textContent = 
            Math.round(data.performance.average_test_score) + '%';
        
        const weakAreasList = document.getElementById('weakAreasList');
        if (data.performance.weak_areas.length === 0) {
            weakAreasList.innerHTML = '<p>No weak areas identified!</p>';
        } else {
            weakAreasList.innerHTML = data.performance.weak_areas.map(area => `
                <div class="weak-area-item">
                    <p>${area.chapter}</p>
                    <span class="weak-area-score">${area.score.toFixed(2)}%</span>
                </div>
            `).join('');
        }
        
        const activityList = document.getElementById('activityList');
        activityList.innerHTML = data.recent_activity.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-book"></i>
                </div>
                <div class="activity-details">
                    <h4>${activity.activity_type.replace(/_/g, ' ')}</h4>
                    <p>${activity.chapter_name}</p>
                </div>
                <div class="activity-time">${new Date(activity.created_at).toLocaleDateString()}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Profile Functions
async function loadProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();
        
        document.getElementById('profileEmail').value = data.user.email;
        document.getElementById('profileUsername').value = data.user.username;
        document.getElementById('profileDuration').value = data.learning_duration_preference;
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateProfile() {
    const duration = document.getElementById('profileDuration').value;
    
    fetch(`${API_BASE_URL}/auth/profile/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            learning_duration_preference: parseInt(duration)
        })
    }).then(response => response.json())
      .then(data => {
          alert('Profile updated successfully!');
      })
      .catch(error => console.error('Error:', error));
}

// Modal close
window.onclick = function(event) {
    const modal = document.getElementById('testModal');
    if (event.target == modal) {
        modal.classList.remove('active');
    }
}
