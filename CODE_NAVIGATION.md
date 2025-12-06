# Code Navigation Map - AI Personalized Learning Platform

## 📍 Complete File Index with Feature Mapping

### BACKEND CORE

#### Django Configuration
```
backend/config/settings.py
├─ Lines 1-20: Base configuration
├─ Lines 20-40: SECRET_KEY, DEBUG, ALLOWED_HOSTS
├─ Lines 40-70: INSTALLED_APPS (users, courses, assessments, learning)
├─ Lines 70-120: MIDDLEWARE stack
├─ Lines 120-150: TEMPLATES config
├─ Lines 150-175: DATABASE PostgreSQL config
├─ Lines 175-200: AUTH & PASSWORD validation
├─ Lines 200-220: STATIC/MEDIA files
├─ Lines 220-250: REST_FRAMEWORK (JWT, pagination)
└─ Lines 250-280: CORS, OpenAI config

backend/config/urls.py
├─ Lines 1-14: Root URL configuration
└─ API route prefixes: /api/auth/, /api/courses/, /api/assessment/, /api/learning/

backend/config/asgi.py
└─ ASGI application for deployment

backend/config/wsgi.py
└─ WSGI application for GuniCorn
```

#### User Management
```
backend/users/
├─ models.py
│  └─ UserProfile (lines 5-17): Stores learning preferences & hours
│
├─ views.py (6 functions)
│  ├─ register() [POST]: User registration with validation
│  ├─ login() [POST]: JWT token generation
│  ├─ get_profile() [GET]: Retrieve user profile
│  └─ update_profile() [PUT]: Update learning preferences
│
├─ serializers.py
│  ├─ UserSerializer: Basic user serialization
│  ├─ UserProfileSerializer: Full profile with nested user
│  ├─ RegisterSerializer: Validation + auto-create UserProfile
│  └─ LoginSerializer: Email/password parsing
│
├─ urls.py: Routes (/register, /login, /profile, /profile/update)
│
├─ authentication.py: CustomJWTAuthentication class
│  └─ Token validation, user attachment to request
│
├─ admin.py: Django admin registration
└─ apps.py: App configuration
```

#### Course Management
```
backend/courses/
├─ models.py
│  ├─ Course (lines 3-13): Course metadata + difficulty levels
│  │  └─ Fields: title, description, difficulty, icon_url, duration_weeks
│  │
│  └─ UserCourse (lines 16-30): Enrollment tracking
│     └─ Fields: user, course, status, progress_percentage, dates
│
├─ views.py (5 functions)
│  ├─ list_courses() [GET]: All courses, public access
│  ├─ get_course() [GET]: Single course details
│  ├─ enroll_course() [POST]: Create UserCourse enrollment
│  ├─ get_user_courses() [GET]: User's enrolled courses
│  └─ Unique constraint: (user, course) on UserCourse
│
├─ serializers.py
│  ├─ CourseSerializer: Course data serialization
│  └─ UserCourseSerializer: Enrollment data + nested course
│
├─ urls.py: Routes (/list, /<id>, /<id>/enroll, /my-courses)
├─ admin.py: Register models
└─ apps.py: App config
```

#### Assessments & AI Integration
```
backend/assessments/
├─ models.py
│  ├─ Assessment (lines 4-17)
│  │  ├─ Fields: user, course, score, percentage, questions_data (JSON)
│  │  ├─ skill_level: Calculated from percentage
│  │  └─ calculate_skill_level() method (lines 20-25)
│  │
│  └─ Roadmap (lines 28-44)
│     ├─ Fields: user, course, assessment (OneToOne), roadmap_data (JSON)
│     ├─ Stores chapters, resources, time estimates
│     └─ duration_weeks: User's learning pace preference
│
├─ llm_service.py (442 lines)
│  ├─ LLMService class initialization (lines 1-30)
│  │  ├─ OpenAI API key setup
│  │  ├─ RoadmapGenerator integration
│  │  └─ DynamicResourceFetcher setup
│  │
│  ├─ generate_assessment_questions() (lines 32-60)
│  │  ├─ Prompt engineering for 10 MCQs
│  │  ├─ OpenAI API call
│  │  └─ Fallback: _get_fallback_questions()
│  │
│  ├─ generate_roadmap() (lines 62-110)
│  │  ├─ Logic: Check USE_DYNAMIC_RESOURCES flag
│  │  ├─ Priority: Dynamic (if enabled) → Static → DB fallback
│  │  ├─ RoadmapGenerator.generate_roadmap() call
│  │  └─ DynamicResourceFetcher.get_complete_roadmap() call
│  │
│  ├─ generate_chapter_test() (lines 112-150+)
│  │  └─ Generates 4 MCQ per chapter
│  │
│  └─ Helper methods:
│     ├─ _get_fallback_questions()
│     ├─ _get_fallback_roadmap()
│     ├─ _generate_dynamic_roadmap()
│     ├─ _fallback_to_static_roadmap()
│     └─ _convert_dynamic_to_roadmap()
│
├─ roadmap_generator.py
│  └─ RoadmapGenerator: Static roadmap generation (predefined for courses)
│
├─ dynamic_resource_fetcher.py
│  └─ DynamicResourceFetcher: Real-time YouTube/Google search integration
│     ├─ get_complete_roadmap()
│     ├─ fetch_youtube_videos()
│     ├─ fetch_documentation()
│     ├─ _db_fallback_roadmap()
│     └─ Supports Serper API + YouTube API + Ollama
│
├─ views.py (150+ lines)
│  ├─ generate_assessment_questions() [POST] (lines 12-41)
│  │  └─ Creates Assessment record + calls LLMService
│  │
│  ├─ submit_assessment() [POST] (lines 43-90)
│  │  ├─ Calculates score from answers
│  │  ├─ Updates UserCourse status to 'in_progress'
│  │  └─ Returns score + skill_level
│  │
│  ├─ generate_roadmap() [POST] (lines 92-130)
│  │  ├─ Checks for existing roadmap
│  │  ├─ Calls LLMService.generate_roadmap()
│  │  └─ Creates Roadmap record
│  │
│  ├─ check_assessment_status() [GET] (lines 132-160)
│  │  └─ Returns assessment_completed, skill_level
│  │
│  └─ get_roadmap_detail() [GET] + get_user_roadmaps() [GET]
│
├─ serializers.py
│  ├─ AssessmentSerializer: Basic assessment data
│  ├─ AssessmentDetailSerializer: Includes questions_data
│  └─ RoadmapSerializer: Roadmap + nested course data
│
├─ urls.py: Routes + DynamicResourceViewSet
├─ admin.py: Register Assessment, Roadmap
└─ apps.py: App config
```

#### Learning & Progress Tracking
```
backend/learning/
├─ models.py
│  ├─ ChapterProgress (lines 3-26)
│  │  ├─ Fields: user, roadmap, chapter_name, chapter_number, status
│  │  ├─ time_spent_minutes: Cumulative time tracking
│  │  ├─ Status choices: not_started, in_progress, completed
│  │  └─ Unique: (roadmap, chapter_number)
│  │
│  ├─ ChapterTest (lines 29-49)
│  │  ├─ Fields: user, roadmap, chapter_progress, score, percentage
│  │  ├─ total_questions: Fixed at 4
│  │  └─ questions_data: JSON with test MCQs
│  │
│  └─ LearningActivity (lines 52-75)
│     ├─ Activity types: chapter_viewed, test_taken, resource_accessed, time_logged
│     ├─ Complete audit trail of user learning
│     └─ Stores duration_minutes, details (JSON)
│
├─ views.py (239 lines)
│  ├─ get_roadmap_chapters() [GET] (lines 17-32)
│  │  └─ Returns all chapters with progress status
│  │
│  ├─ track_chapter_progress() [POST] (lines 34-72)
│  │  ├─ Creates/updates ChapterProgress
│  │  ├─ Logs LearningActivity
│  │  └─ Tracks time spent
│  │
│  ├─ generate_chapter_test() [POST] (lines 74-110)
│  │  ├─ Calls LLMService.generate_chapter_test()
│  │  └─ Creates ChapterTest record
│  │
│  ├─ submit_chapter_test() [POST] (lines 112-160)
│  │  ├─ Calculates score
│  │  ├─ Identifies weak areas (low scoring topics)
│  │  └─ Updates progress percentage
│  │
│  ├─ get_learning_dashboard() [GET] (lines 162-239)
│  │  ├─ Overall progress percentage
│  │  ├─ Performance metrics by chapter
│  │  ├─ Weak areas identification
│  │  ├─ Learning activity feed
│  │  └─ Time spent analytics
│  │
│  └─ Helper methods:
│     ├─ _calculate_overall_progress()
│     ├─ _get_weak_areas()
│     └─ _get_activity_feed()
│
├─ serializers.py
│  ├─ ChapterProgressSerializer: Chapter progress data
│  ├─ ChapterTestDetailSerializer: Test + questions
│  └─ LearningActivitySerializer: Activity logging
│
├─ urls.py: Routes (/chapters/<id>, /track-progress, etc.)
├─ admin.py: Register models
└─ apps.py: App config
```

---

### FRONTEND

#### HTML Structure
```
frontend/index.html (298 lines)
├─ Head section (lines 1-10)
│  ├─ Meta tags (charset, viewport)
│  ├─ CSS imports (style.css, responsive.css, Font Awesome)
│  └─ Title: "LearnPath - AI Personalized Learning Platform"
│
├─ Navigation bar (lines 12-26)
│  ├─ Brand: "LearnPath" with icon
│  ├─ Nav links: Home, Courses, Dashboard, Profile, Logout
│  └─ Hamburger menu (responsive)
│
├─ Main container with pages (lines 28+)
│  ├─ loginPage (lines 30-70)
│  │  ├─ Tabs: Login & Register
│  │  ├─ Login form: email, password
│  │  ├─ Register form: email, username, name, password
│  │  └─ Error message placeholders
│  │
│  ├─ homePage (lines 72-95)
│  │  ├─ Hero section with CTA button
│  │  └─ Feature overview cards
│  │
│  ├─ coursesPage (lines 97-125)
│  │  ├─ Course cards grid
│  │  ├─ Difficulty badges
│  │  └─ "Enroll" & "Start Assessment" buttons
│  │
│  ├─ assessmentPage (lines 127-160)
│  │  ├─ Quiz question display
│  │  ├─ Multiple choice options (A, B, C, D)
│  │  ├─ Progress bar (1/10, 2/10, etc.)
│  │  ├─ Score display (after submission)
│  │  └─ Skill level badge
│  │
│  ├─ durationPage (lines 162-180)
│  │  ├─ Input: weeks for learning duration
│  │  └─ "Generate Roadmap" button
│  │
│  ├─ roadmapPage (lines 182-220)
│  │  ├─ Roadmap overview
│  │  ├─ Chapter sidebar (clickable)
│  │  ├─ Chapter resources (videos, docs, tutorials)
│  │  ├─ Time estimates per chapter
│  │  └─ "Start Learning" button per chapter
│  │
│  ├─ learningPage (lines 222-260)
│  │  ├─ Chapter content display
│  │  ├─ Resource links (clickable)
│  │  ├─ Mark complete checkbox
│  │  ├─ Time tracker
│  │  ├─ "Take Chapter Test" button
│  │  └─ Progress percentage
│  │
│  ├─ chapterTestPage (lines 262-280)
│  │  ├─ 4 test questions display
│  │  ├─ Multiple choice options
│  │  └─ Submit test button
│  │
│  └─ dashboardPage (lines 282-298)
│     ├─ Overall progress bar
│     ├─ Performance chart by chapter
│     ├─ Weak areas list
│     ├─ Learning activity feed
│     └─ Total time spent
└─ Script imports: app.js, api.js
```

#### Main Application Logic
```
frontend/js/app.js
├─ Global variables:
│  ├─ API_BASE_URL = "http://127.0.0.1:8000"
│  ├─ currentUser: {}
│  ├─ currentCourse: {}
│  ├─ currentAssessment: {}
│  ├─ currentRoadmap: {}
│  └─ currentChapter: {}
│
├─ Page navigation functions:
│  ├─ goToPage(pageName): Show/hide pages
│  ├─ switchTab(formId): Show/hide form tabs
│  └─ displayPage(pageId): Set active page
│
├─ Authentication functions:
│  ├─ login(event): [Form submission]
│  │  └─ Calls api.login() → saves token → redirects to home
│  │
│  ├─ register(event): [Form submission]
│  │  └─ Calls api.register() → auto-login → redirects to home
│  │
│  └─ logout(): Clear token → go to login page
│
├─ Course functions:
│  ├─ loadCourses(): [On page init]
│  │  ├─ Calls api.getCourses()
│  │  └─ Renders course cards
│  │
│  ├─ selectCourse(courseId): [On course click]
│  │  ├─ Stores currentCourse
│  │  └─ Navigates to assessment page
│  │
│  ├─ enrollCourse(courseId): [On enroll button]
│  │  └─ Calls api.enrollCourse()
│  │
│  └─ getUserCourses(): [Dashboard view]
│     └─ Calls api.getUserCourses()
│
├─ Assessment functions:
│  ├─ startAssessment(): [On "Start Assessment"]
│  │  ├─ Calls api.generateAssessmentQuestions()
│  │  ├─ Stores assessment ID & questions
│  │  └─ Displays first question
│  │
│  ├─ displayQuestion(index): [Question display]
│  │  ├─ Shows question text & options
│  │  └─ Highlights selected option
│  │
│  ├─ selectAnswer(optionKey): [On option click]
│  │  ├─ Stores answer in userAnswers{}
│  │  └─ Enables next button
│  │
│  ├─ nextQuestion(): [On next button]
│  │  └─ Increments question index or ends quiz
│  │
│  └─ submitAssessment(): [On submit]
│     ├─ Calls api.submitAssessment()
│     ├─ Displays score & skill_level
│     └─ Shows "Generate Roadmap" button
│
├─ Roadmap functions:
│  ├─ setDuration(): [On duration input]
│  │  ├─ Stores duration_weeks
│  │  └─ Enables "Generate Roadmap" button
│  │
│  ├─ generateRoadmap(): [On generate button]
│  │  ├─ Calls api.generateRoadmap()
│  │  ├─ Parses chapters from response
│  │  └─ Displays roadmap page
│  │
│  ├─ displayRoadmap(roadmapData): [Roadmap rendering]
│  │  ├─ Renders chapter sidebar
│  │  ├─ Shows resources for each chapter
│  │  └─ Sets click handlers
│  │
│  └─ selectChapter(chapterNumber): [On chapter click]
│     ├─ Loads chapter content
│     └─ Navigates to learning page
│
├─ Learning functions:
│  ├─ startLearning(chapterNumber): [On "Start Learning"]
│  │  ├─ Displays chapter resources
│  │  ├─ Starts time tracker
│  │  └─ Enables "Mark Complete"
│  │
│  ├─ markChapterComplete(): [On complete checkbox]
│  │  ├─ Calls api.trackProgress() with status='completed'
│  │  └─ Updates progress percentage
│  │
│  ├─ takeChapterTest(): [On "Take Test"]
│  │  ├─ Calls api.generateChapterTest()
│  │  └─ Displays test page
│  │
│  ├─ displayTestQuestion(index): [Test question display]
│  │  ├─ Shows question & options
│  │  └─ Tracks answers
│  │
│  ├─ submitChapterTest(): [On submit test]
│  │  ├─ Calls api.submitChapterTest()
│  │  ├─ Shows test score
│  │  ├─ Identifies weak areas
│  │  └─ Option to retry or continue
│  │
│  └─ loadDashboard(): [Dashboard view]
│     ├─ Calls api.getLearningDashboard()
│     ├─ Renders progress chart
│     ├─ Shows weak areas
│     └─ Displays activity feed
│
├─ Utility functions:
│  ├─ formatTime(minutes): Convert minutes to "1h 30m" format
│  ├─ calculateProgress(): Overall % from chapters
│  ├─ updateProgressBar(): DOM update
│  └─ showNotification(message, type): Alert/success message
│
├─ Event listeners (on page load):
│  ├─ Login form submit
│  ├─ Register form submit
│  ├─ Course card clicks
│  ├─ Option selection (radio buttons)
│  ├─ Navigation clicks
│  └─ Hamburger menu toggle
│
└─ Initialization:
   ├─ Check for saved token on page load
   ├─ Redirect to login if not authenticated
   └─ Load user profile & courses if authenticated
```

#### API Client Class
```
frontend/js/api.js (167 lines)
├─ APIClient class
│  ├─ Constructor (lines 3-7)
│  │  ├─ baseURL: API server address
│  │  └─ token: Retrieved from localStorage
│  │
│  ├─ setToken(token): Store JWT for future requests
│  │
│  ├─ getHeaders(): Returns headers with Authorization
│  │  ├─ Content-Type: application/json
│  │  └─ Authorization: Bearer <token> (if authenticated)
│  │
│  ├─ request(endpoint, options): Generic fetch wrapper
│  │  ├─ Constructs full URL
│  │  ├─ Adds headers
│  │  ├─ Makes fetch call
│  │  ├─ Parses JSON response
│  │  └─ Error handling
│  │
│  └─ API methods:
│     ├─ Auth:
│     │  ├─ register(userData)
│     │  ├─ login(email, password)
│     │  ├─ getProfile()
│     │  └─ updateProfile(profileData)
│     │
│     ├─ Courses:
│     │  ├─ getCourses()
│     │  ├─ getCourse(courseId)
│     │  ├─ enrollCourse(courseId)
│     │  └─ getUserCourses()
│     │
│     ├─ Assessments:
│     │  ├─ generateAssessmentQuestions(courseId)
│     │  ├─ submitAssessment(assessmentId, answers)
│     │  ├─ generateRoadmap(assessmentId, durationWeeks)
│     │  ├─ checkAssessmentStatus(courseId)
│     │  ├─ getRoadmapDetail(roadmapId)
│     │  └─ getUserRoadmaps()
│     │
│     ├─ Learning:
│     │  ├─ getChapters(roadmapId)
│     │  ├─ trackProgress(roadmapId, chapterNumber, status, timeSpent)
│     │  ├─ generateChapterTest(roadmapId, chapterNumber)
│     │  ├─ submitChapterTest(testId, answers)
│     │  └─ getLearningDashboard(roadmapId)
│     │
│     └─ Resources (optional):
│        ├─ getDynamicResources(course)
│        └─ getCachedResources(courseId)
│
└─ Usage:
   const api = new APIClient('http://127.0.0.1:8000/api');
   const courses = await api.getCourses();
   api.setToken(token);
   const profile = await api.getProfile();
```

#### Styling
```
frontend/css/style.css
├─ Root variables: --primary, --secondary, --danger, --success
├─ Navbar styling (60+ lines)
│  └─ Brand logo, nav links, animations
├─ Page containers (hidden by default, .active shows)
├─ Form styling (100+ lines)
│  ├─ Input fields, labels, error messages
│  ├─ Buttons: primary, secondary, danger
│  └─ Form groups, validation feedback
├─ Course cards (80+ lines)
│  ├─ Grid layout, hover effects
│  ├─ Difficulty badges with colors
│  └─ Enroll button styling
├─ Assessment/Test quiz (100+ lines)
│  ├─ Question display
│  ├─ Multiple choice options (radio buttons)
│  ├─ Progress bar
│  └─ Score display
├─ Roadmap display (80+ lines)
│  ├─ Chapter sidebar
│  ├─ Resource links
│  └─ Chapter content area
├─ Learning page (60+ lines)
│  ├─ Chapter header
│  ├─ Resource embeds (videos)
│  ├─ Time tracker
│  └─ Progress bar
├─ Dashboard (100+ lines)
│  ├─ Progress chart
│  ├─ Weak areas display
│  ├─ Activity feed styling
│  └─ Performance metrics
└─ Animations & transitions

frontend/css/responsive.css
├─ Mobile breakpoints: max-width 768px, 480px
├─ Hamburger menu toggle
├─ Responsive grid (courses, chapters)
├─ Font scaling for mobile
├─ Touch-friendly button sizes
├─ Stack layout for forms
├─ Hide desktop elements on mobile
└─ Adjust navbar for small screens
```

---

## 🔗 API Call Flow Diagram

```
Frontend (app.js)
  ↓ User action (click, form submit)
  ↓
APIClient.method() in api.js
  ↓ fetch() with JWT header
  ↓
Django URL Router (config/urls.py)
  ↓ Match URL pattern
  ↓
View Function (views.py)
  ↓ Authentication check (@permission_classes)
  ↓
Serializer validation
  ↓
Model operations (save, filter, etc.)
  ↓
Optional: LLMService calls (llm_service.py)
  ├─ OpenAI API call
  ├─ Parse response
  └─ Store in database
  ↓
Return Response() object
  ↓ JSON response
  ↓
Frontend receives data
  ↓ Update DOM (app.js)
  ↓ Display to user
```

---

## 📊 Key Decision Points in Code

### Where to add new course types?
- **File**: `backend/courses/models.py`
- **Action**: Add to Course model, or create CourseCategory table
- **Frontend**: Update `loadCourses()` to filter by type

### Where to modify assessment scoring?
- **File**: `backend/assessments/models.py::Assessment.calculate_skill_level()`
- **Lines**: 20-25
- **Current logic**: < 33% = beginner, < 67% = intermediate, > 67% = advanced

### Where to change roadmap generation?
- **Files**:
  - Static: `backend/assessments/roadmap_generator.py`
  - Dynamic: `backend/assessments/dynamic_resource_fetcher.py`
  - Controller: `backend/assessments/llm_service.py::generate_roadmap()`

### Where to customize chapter test questions?
- **File**: `backend/assessments/llm_service.py::generate_chapter_test()`
- **Current logic**: 4 MCQ generated per chapter
- **Change**: Adjust prompt or number of questions

### Where to track custom learning metrics?
- **File**: `backend/learning/models.py::LearningActivity`
- **Action**: Add new ACTIVITY_TYPES
- **Frontend logging**: Call `api.trackActivity()` from app.js

---

## 🔐 Authentication Flow

```
1. User submits login form (app.js::login())
2. POST /api/auth/login with email, password
3. Backend authenticates user (users/views.py::login())
4. Generate JWT token with 30-day expiration
5. Return token to frontend
6. Frontend stores token in localStorage
7. APIClient adds token to every request header
8. Backend verifies token (users/authentication.py)
9. If valid, attach user to request object
10. View can now access request.user
```

---

## 📈 Data Flow Examples

### Creating Assessment & Roadmap
```
1. Student enrolls in course
2. Frontend calls api.generateAssessmentQuestions(courseId)
3. Backend creates Assessment record, calls LLMService
4. OpenAI generates 10 MCQs, stored in questions_data (JSON)
5. Frontend displays questions
6. Student answers, frontend calls api.submitAssessment(assessmentId, answers)
7. Backend calculates score, sets skill_level
8. Frontend shows score & requests roadmap generation
9. Student inputs duration_weeks
10. Frontend calls api.generateRoadmap(assessmentId, durationWeeks)
11. Backend generates Roadmap record with chapters, resources
12. Frontend displays roadmap with chapters
```

### Learning & Progress Tracking
```
1. Student clicks chapter
2. Frontend displays resources (videos, docs)
3. Student marks chapter complete
4. Frontend calls api.trackProgress(roadmapId, chapterNumber, 'completed', timeSpent)
5. Backend updates ChapterProgress status
6. Backend logs LearningActivity
7. Backend recalculates overall progress %
8. Frontend calls api.getLearningDashboard()
9. Backend queries all ChapterProgress, ChapterTest, LearningActivity
10. Calculates weak areas, performance metrics
11. Frontend displays dashboard with charts
```

---

**Last Updated**: December 5, 2025  
**Version**: 1.0  
**Ready for modifications**
