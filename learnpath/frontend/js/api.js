// API Helper Functions
// This file contains utility functions for API calls

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('authToken');
    }

    setToken(token) {
        this.token = token;
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    async getProfile() {
        return this.request('/auth/profile');
    }

    async updateProfile(profileData) {
        return this.request('/auth/profile/update', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    // Course endpoints
    async getCourses() {
        return this.request('/courses/list');
    }

    async getCourse(courseId) {
        return this.request(`/courses/${courseId}`);
    }

    async enrollCourse(courseId) {
        return this.request(`/courses/${courseId}/enroll`, {
            method: 'POST'
        });
    }

    async getUserCourses() {
        return this.request('/courses/my-courses');
    }

    // Assessment endpoints
    async generateAssessmentQuestions(courseId) {
        return this.request('/assessment/generate-questions', {
            method: 'POST',
            body: JSON.stringify({ course_id: courseId })
        });
    }

    async submitAssessment(assessmentId, answers) {
        return this.request('/assessment/submit', {
            method: 'POST',
            body: JSON.stringify({
                assessment_id: assessmentId,
                answers: answers
            })
        });
    }

    async generateRoadmap(assessmentId, durationWeeks) {
        return this.request('/assessment/generate-roadmap', {
            method: 'POST',
            body: JSON.stringify({
                assessment_id: assessmentId,
                duration_weeks: durationWeeks
            })
        });
    }

    async getUserRoadmaps() {
        return this.request('/assessment/my-roadmaps');
    }

    // Learning endpoints
    async getChapters(roadmapId) {
        return this.request(`/learning/chapters/${roadmapId}`);
    }

    async trackProgress(roadmapId, chapterNumber, status, timeSpent) {
        return this.request('/learning/track-progress', {
            method: 'POST',
            body: JSON.stringify({
                roadmap_id: roadmapId,
                chapter_number: chapterNumber,
                status: status,
                time_spent_minutes: timeSpent
            })
        });
    }

    async generateChapterTest(roadmapId, chapterNumber) {
        return this.request('/learning/chapter-test/generate', {
            method: 'POST',
            body: JSON.stringify({
                roadmap_id: roadmapId,
                chapter_number: chapterNumber
            })
        });
    }

    async submitChapterTest(testId, answers) {
        return this.request('/learning/chapter-test/submit', {
            method: 'POST',
            body: JSON.stringify({
                test_id: testId,
                answers: answers
            })
        });
    }

    async getDashboard(roadmapId) {
        return this.request(`/learning/dashboard/${roadmapId}`);
    }
}

// Create global API client instance. Prefer `window.API_BASE_URL` (set by app.js)
// to avoid redeclaring globals when both scripts are loaded. Fall back to
// a sensible localhost host for development.
const _base = (typeof window !== 'undefined' && window.API_BASE_URL)
    ? window.API_BASE_URL
    : (function(){
        const host = (typeof window !== 'undefined') ? window.location.hostname : '127.0.0.1';
        const scheme = (typeof window !== 'undefined' && window.location.protocol) ? window.location.protocol : 'http:';
        const resolvedHost = (host === 'localhost' || host === '127.0.0.1') ? `${scheme}//127.0.0.1:8000` : (typeof window !== 'undefined' ? window.location.origin : `${scheme}//127.0.0.1:8000`);
        return `${resolvedHost}/api`;
    })();

const api = new APIClient(_base);
