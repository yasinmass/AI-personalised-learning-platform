# 🗺️ Visual Architecture & Data Flow Maps

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (Browser)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  HTML5 (index.html)     │ CSS3 (responsive)   │ JavaScript (ES6+)  │   │
│  │  - 9 Pages              │ - Adaptive design   │ - app.js (routing) │   │
│  │  - SPA structure        │ - Mobile-first      │ - api.js (client)  │   │
│  │  - Form inputs          │ - Hamburger menu    │ - Event handlers   │   │
│  │  - Dynamic rendering    │ - Touch-friendly    │ - Local storage    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────┬─────────────────────────────────────┘
                                         │ HTTP/REST (JSON)
                                         │ JWT Token in Header
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API LAYER (Django REST Framework)                      │
│  ┌───────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │  Auth     │  │ Courses  │  │ Assessments │  │  Learning    │           │
│  │  (4 URLs) │  │ (4 URLs) │  │  (6 URLs)   │  │  (5 URLs)    │           │
│  └─────┬─────┘  └────┬─────┘  └──────┬──────┘  └──────┬───────┘           │
│        │             │               │               │                   │
│  ┌─────▼─────┐  ┌────▼─────┐  ┌─────▼──────────┐  ┌──▼──────────┐       │
│  │ JWT Token │  │  Models  │  │ LLM Service    │  │  Progress   │       │
│  │ Generate  │  │  Serialize│  │ OpenAI GPT-4   │  │  Tracking   │       │
│  └───────────┘  └──────────┘  │ (Fallback)     │  └─────────────┘       │
│                                └────────────────┘                        │
└────────────────────────────────────────┬─────────────────────────────────────┘
                                         │ Django ORM
                                         │ SQL Queries
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (PostgreSQL)                              │
│  ┌────────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────────┐          │
│  │  Users     │ │  Courses   │ │ Assessments │ │  Learning    │          │
│  ├────────────┤ ├────────────┤ ├─────────────┤ ├──────────────┤          │
│  │ User       │ │ Course     │ │ Assessment  │ │ ChapterProg. │          │
│  │ UserProfile│ │ UserCourse │ │ Roadmap     │ │ ChapterTest  │          │
│  │            │ │            │ │             │ │ LearningAct. │          │
│  └────────────┘ └────────────┘ └─────────────┘ └──────────────┘          │
│                                                                            │
│                         ↕️ Relationships                                   │
│                    (Foreign Keys, OneToOne)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ API Calls
                                         ▼
                          ┌──────────────────────────┐
                          │  External Services      │
                          ├──────────────────────────┤
                          │ OpenAI API (GPT-4)      │
                          │ Serper (Google Search)  │
                          │ YouTube API (optional)  │
                          │ Ollama (local LLM opt.) │
                          └──────────────────────────┘
```

---

## Data Flow: User Registration & Login

```
┌─────────────────────────────────────────────────────────────────────────┐
│ REGISTRATION FLOW                                                        │
└─────────────────────────────────────────────────────────────────────────┘

User fills registration form
    ↓
Frontend (app.js): api.register(email, username, password)
    ↓
POST /api/auth/register
    ↓
Backend (users/views.py::register)
    ├─ Validate data (RegisterSerializer)
    ├─ Check email unique
    ├─ Create Django User
    ├─ Create UserProfile (OneToOne)
    └─ Return user object
    ↓
Frontend receives response
    ├─ Store user info
    └─ Redirect to login/home
    ↓
✅ Registration Complete

───────────────────────────────────────────────────────────────────────────

LOGIN FLOW

User enters email & password
    ↓
Frontend (app.js): api.login(email, password)
    ↓
POST /api/auth/login
    ↓
Backend (users/views.py::login)
    ├─ Find User by email
    ├─ Authenticate password
    ├─ Generate JWT payload
    │  {
    │    "user_id": 1,
    │    "email": "user@example.com",
    │    "exp": <timestamp+30days>,
    │    "iat": <timestamp>
    │  }
    ├─ Encode token (JWT_SECRET)
    └─ Return token + user info
    ↓
Frontend receives token
    ├─ localStorage.setItem('authToken', token)
    ├─ api.setToken(token)
    └─ Redirect to home page
    ↓
✅ Login Complete
```

---

## Data Flow: Course Assessment & Roadmap Generation

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSESSMENT FLOW                                                          │
└─────────────────────────────────────────────────────────────────────────┘

User views course → Click "Start Assessment"
    ↓
Frontend: api.generateAssessmentQuestions(courseId)
    ↓
POST /api/assessment/generate-questions
    ↓
Backend (assessments/views.py)
    ├─ Get Course
    ├─ Get UserProfile
    ├─ Call LLMService.generate_assessment_questions()
    │  ├─ Create prompt with course title
    │  ├─ Call OpenAI GPT-4 API
    │  ├─ Receive 10 MCQ in JSON format
    │  └─ Return questions array
    ├─ Create Assessment record
    │  └─ Save questions_data (JSON)
    └─ Return assessment_id + questions
    ↓
Frontend displays 10 questions one by one
    ├─ User selects option (A/B/C/D)
    ├─ Click Next
    └─ Move to next question
    ↓
User completes all 10 → Click "Submit"
    ↓
Frontend: api.submitAssessment(assessmentId, {0: "A", 1: "B", ...})
    ↓
POST /api/assessment/submit
    ↓
Backend (assessments/views.py)
    ├─ Get Assessment
    ├─ Get questions from questions_data
    ├─ Calculate score
    │  (Count correct answers: 7/10 = 70%)
    ├─ Calculate skill_level
    │  (70% → "intermediate")
    ├─ Update Assessment record
    │  ├─ score: 7
    │  ├─ percentage: 70.0
    │  └─ skill_level: "intermediate"
    ├─ Update UserCourse status → "in_progress"
    └─ Return score + skill_level
    ↓
Frontend shows results
    ├─ Score: 7/10 (70%)
    ├─ Skill Level: Intermediate
    └─ "Generate Roadmap" button
    ↓
✅ Assessment Complete

───────────────────────────────────────────────────────────────────────────

ROADMAP GENERATION FLOW

User selects duration (12 weeks) → Click "Generate Roadmap"
    ↓
Frontend: api.generateRoadmap(assessmentId, 12)
    ↓
POST /api/assessment/generate-roadmap
    ↓
Backend (assessments/views.py)
    ├─ Get Assessment (has skill_level="intermediate")
    ├─ Get Course
    ├─ Call LLMService.generate_roadmap()
    │  (skill_level, course_title, duration_weeks)
    │
    ├─ LLMService logic:
    │  ├─ If USE_DYNAMIC_RESOURCES = false (default)
    │  │  ├─ Call RoadmapGenerator.generate_roadmap()
    │  │  │  └─ Return static roadmap (predefined)
    │  │  └─ If fails: use DB fallback
    │  │
    │  └─ If USE_DYNAMIC_RESOURCES = true
    │     ├─ Call DynamicResourceFetcher.get_complete_roadmap()
    │     │  ├─ Fetch YouTube videos (YouTube API)
    │     │  ├─ Fetch docs (Serper API)
    │     │  └─ Format resources
    │     └─ If fails: fallback to static
    │
    ├─ Generate roadmap structure:
    │  {
    │    "chapters": [
    │      {
    │        "number": 1,
    │        "title": "Chapter 1",
    │        "topics": [...],
    │        "duration": 7,
    │        "resources": {
    │          "videos": [...],
    │          "documentation": [...],
    │          "tutorials": [...]
    │        }
    │      }
    │    ]
    │  }
    │
    ├─ Create Roadmap record
    │  ├─ user: UserProfile
    │  ├─ course: Course
    │  ├─ assessment: Assessment (OneToOne link)
    │  ├─ skill_level: "intermediate"
    │  ├─ duration_weeks: 12
    │  └─ roadmap_data: {...} (JSON)
    │
    └─ Return roadmap object
    ↓
Frontend displays roadmap
    ├─ Chapter sidebar
    ├─ Resources for each chapter
    ├─ Time estimates
    └─ "Start Learning" buttons
    ↓
✅ Roadmap Generated
```

---

## Data Flow: Learning & Chapter Tests

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LEARNING FLOW                                                            │
└─────────────────────────────────────────────────────────────────────────┘

User clicks chapter → Click "Start Learning"
    ↓
Frontend displays chapter
    ├─ Chapter title & description
    ├─ Resources (videos, docs)
    ├─ Time tracker
    └─ "Mark Complete" button
    ↓
User reads/watches → Check "Mark Complete"
    ↓
Frontend: api.trackProgress(roadmapId, chapterNumber, "completed", timeSpent)
    ↓
POST /api/learning/track-progress
    ↓
Backend (learning/views.py)
    ├─ Get Roadmap
    ├─ Get/Create ChapterProgress
    │  ├─ Set status: "completed"
    │  ├─ Add time_spent_minutes
    │  └─ Set completion_date
    ├─ Create LearningActivity
    │  ├─ activity_type: "time_logged"
    │  ├─ duration_minutes: (timeSpent)
    │  └─ details: {...}
    ├─ Calculate overall progress %
    └─ Return updated progress
    ↓
Frontend updates dashboard
    ├─ Progress bar moves
    └─ Show "Take Test" button
    ↓
✅ Chapter Marked Complete

───────────────────────────────────────────────────────────────────────────

CHAPTER TEST FLOW

User clicks "Take Chapter Test"
    ↓
Frontend: api.generateChapterTest(roadmapId, chapterNumber)
    ↓
POST /api/learning/chapter-test/generate
    ↓
Backend (learning/views.py)
    ├─ Get Roadmap
    ├─ Get Chapter info
    ├─ Call LLMService.generate_chapter_test()
    │  ├─ Create prompt (chapter_name, course_title)
    │  ├─ Call OpenAI API
    │  └─ Generate 4 MCQ questions
    ├─ Create ChapterTest record
    │  ├─ questions_data: {...}
    │  └─ total_questions: 4
    └─ Return test_id + questions
    ↓
Frontend displays 4 test questions
    ├─ User selects options
    └─ Click "Submit Test"
    ↓
Frontend: api.submitChapterTest(testId, {0: "A", 1: "B", 2: "C", 3: "D"})
    ↓
POST /api/learning/chapter-test/submit
    ↓
Backend (learning/views.py)
    ├─ Get ChapterTest
    ├─ Calculate score (3/4 = 75%)
    ├─ Identify weak areas
    │  ├─ Questions scored < 50% are weak
    │  ├─ Map to topics
    │  └─ Store for recommendations
    ├─ Update ChapterTest
    │  ├─ score: 3
    │  └─ percentage: 75.0
    ├─ Create LearningActivity
    │  └─ activity_type: "test_taken"
    ├─ Recalculate overall progress
    └─ Return test results + weak areas
    ↓
Frontend shows test results
    ├─ Score: 3/4 (75%)
    ├─ Weak areas highlighted
    └─ "Continue Learning" or "Retry" button
    ↓
✅ Chapter Test Complete

───────────────────────────────────────────────────────────────────────────

DASHBOARD FLOW

User clicks "Dashboard"
    ↓
Frontend: api.getLearningDashboard(roadmapId)
    ↓
GET /api/learning/dashboard/<roadmap_id>
    ↓
Backend (learning/views.py)
    ├─ Calculate overall progress
    │  ├─ Total chapters: 10
    │  ├─ Completed chapters: 7
    │  └─ Overall %: 70%
    ├─ Calculate performance by chapter
    │  ├─ Chapter 1: 80% (test score)
    │  ├─ Chapter 2: 60% (test score)
    │  └─ Chapter 3: 70% (test score)
    ├─ Identify weak areas
    │  ├─ Topics with score < 60%
    │  └─ List for focused learning
    ├─ Get learning activity history
    │  ├─ Last 20 activities
    │  ├─ Sorted by date (newest first)
    │  └─ Activity types: chapter_viewed, test_taken, etc.
    ├─ Calculate total time spent
    │  ├─ Sum all time_spent_minutes
    │  └─ Format as hours:minutes
    └─ Return complete dashboard data
    ↓
Frontend displays dashboard
    ├─ Progress bar (70%)
    ├─ Performance chart
    ├─ Weak areas table
    ├─ Activity feed
    └─ Time statistics
    ↓
✅ Dashboard Displayed
```

---

## Database Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RELATIONAL MODEL                                 │
└─────────────────────────────────────────────────────────────────────────┘

Django User Model (built-in)
    │
    │ OneToOne (on_delete=CASCADE)
    │
    ▼
UserProfile
├── learning_duration_preference
├── total_learning_hours
└── created_at, updated_at

UserProfile (1) ────────── Many ────────── UserCourse
                                           │
                                           │ ForeignKey to UserProfile
                                           │ ForeignKey to Course
                                           │ Many
                                           │
                                           ▼
                                         Course
                                         ├── title
                                         ├── description
                                         ├── difficulty
                                         └── duration_weeks

UserProfile (1) ────────── Many ────────── Assessment
                                           │
                                           │ ForeignKey: user, course
                                           │ questions_data (JSON)
                                           │ score, percentage, skill_level
                                           │ OneToOne to Roadmap
                                           │
                                           ▼
                                         Roadmap
                                         ├── ForeignKey: user, course
                                         ├── OneToOne: Assessment (link back)
                                         ├── skill_level
                                         ├── duration_weeks
                                         └── roadmap_data (JSON: chapters, resources)
                                             │
                                             │ Chapters in JSON
                                             │
                                             └─ Chapter Info:
                                                ├── number
                                                ├── title
                                                ├── topics
                                                ├── duration
                                                └── resources (videos, docs)

Roadmap (1) ────────── Many ────────── ChapterProgress
                                       │
                                       │ ForeignKey: user, roadmap
                                       │ chapter_name, chapter_number
                                       │ status, time_spent_minutes
                                       │ UNIQUE: (roadmap, chapter_number)
                                       │
                                       ▼
                                     ChapterTest
                                     ├── ForeignKey: user, roadmap
                                     ├── ForeignKey: chapter_progress
                                     ├── questions_data (JSON)
                                     ├── score, percentage
                                     └── total_questions: 4

Roadmap (1) ────────── Many ────────── LearningActivity
                                       │
                                       │ ForeignKey: user, roadmap
                                       │ activity_type (chapter_viewed, test_taken, etc.)
                                       │ duration_minutes
                                       │ details (JSON)
                                       │ created_at
                                       │
                                       └─ Audit Trail

────────────────────────────────────────────────────────────────────────────

SUMMARY OF RELATIONSHIPS

User (1) → UserProfile (1)
  ├─ (1) → Many: UserCourse → Course
  ├─ (1) → Many: Assessment
  │         └─ (1) ← → (1): Roadmap
  │                    ├─ (1) → Many: ChapterProgress
  │                    │          ├─ (1) → Many: ChapterTest
  │                    │          └─ Related ChapterTests
  │                    └─ (1) → Many: LearningActivity
  ├─ (1) → Many: ChapterProgress
  ├─ (1) → Many: ChapterTest
  └─ (1) → Many: LearningActivity
```

---

## API Call Sequence Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL USER SESSION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

TIME  FRONTEND             API ENDPOINT              BACKEND             DB
────────────────────────────────────────────────────────────────────────────

0:00  Register Form
      ├─ POST /api/auth/register → (email, password)
      │                           └─ Validate, Create User → Save User
      │                           ← Return token + user_id
      └─ Save token

0:30  Homepage
      └─ Browse courses
          ├─ GET /api/courses/list
          │                        └─ Query Course
          │                           ← Return all courses
          └─ Display course cards

1:00  Select Course
      └─ Enroll
          ├─ POST /api/courses/<id>/enroll
          │                              └─ Create UserCourse
          │                                 ← Return enrollment
          └─ Start Assessment button

1:30  Start Assessment
      └─ POST /api/assessment/generate-questions
         │                                       └─ Call LLMService
         │                                          ├─ OpenAI API
         │                                          └─ Create Assessment → Save questions
         │                                          ← Return questions
         └─ Display 10 questions

2:00  Answer Questions
      └─ User selects options (no API calls)

3:00  Submit Assessment
      └─ POST /api/assessment/submit
         │                           └─ Calculate score
         │                              ├─ Update Assessment
         │                              └─ Calculate skill_level
         │                           ← Return score, skill_level
         └─ Show results

3:30  Input Duration
      └─ User enters 12 weeks

4:00  Generate Roadmap
      └─ POST /api/assessment/generate-roadmap
         │                                       └─ Call LLMService
         │                                          ├─ OpenAI API (roadmap)
         │                                          ├─ Create Roadmap
         │                                          └─ Save roadmap_data
         │                                       ← Return roadmap
         └─ Display roadmap with chapters

4:30  Select Chapter
      └─ Start Learning
          ├─ Display chapter resources
          └─ Start time tracker

5:00  Learning
      └─ User reads/watches (no API calls)

6:00  Mark Complete
      └─ POST /api/learning/track-progress
         │                                  └─ Update ChapterProgress
         │                                     ├─ Create LearningActivity
         │                                     └─ Recalculate progress %
         │                                  ← Return updated progress
         └─ Show "Take Test" button

6:30  Take Chapter Test
      └─ POST /api/learning/chapter-test/generate
         │                                         └─ Call LLMService
         │                                            ├─ OpenAI API
         │                                            ├─ Create ChapterTest
         │                                            └─ Save questions
         │                                         ← Return test questions
         └─ Display 4 questions

7:00  Answer Test
      └─ User selects options (no API calls)

7:30  Submit Test
      └─ POST /api/learning/chapter-test/submit
         │                                       └─ Calculate score
         │                                          ├─ Update ChapterTest
         │                                          ├─ Identify weak areas
         │                                          ├─ Create LearningActivity
         │                                          └─ Recalculate progress %
         │                                       ← Return score, weak areas
         └─ Show test results

8:00  View Dashboard
      └─ GET /api/learning/dashboard/<roadmap_id>
         │                                          └─ Calculate overall %
         │                                             ├─ Get performance by chapter
         │                                             ├─ Get weak areas
         │                                             ├─ Get activity history
         │                                             └─ Calculate time spent
         │                                          ← Return dashboard data
         └─ Display analytics

────────────────────────────────────────────────────────────────────────────
Total Requests: ~12 API calls for typical learning session
Total Time: ~8 hours of actual learning time
```

---

## Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       JWT AUTHENTICATION FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

LOGIN REQUEST:

User inputs email & password
    ↓
Frontend POST /api/auth/login
    ↓
Backend (users/views.py::login)
    ├─ Find User by email
    ├─ Authenticate password (Django auth)
    ├─ If valid:
    │  ├─ Create JWT Payload:
    │  │  {
    │  │    "user_id": 1,
    │  │    "email": "user@example.com",
    │  │    "exp": <30 days from now>,
    │  │    "iat": <now>
    │  │  }
    │  ├─ Encode with SECRET_KEY (settings.py)
    │  └─ Return token
    └─ Return error if invalid
    ↓
Frontend stores token in localStorage
    └─ localStorage.setItem('authToken', token)

─────────────────────────────────────────────────────────────────────────

AUTHENTICATED REQUEST:

User makes any authenticated request
    ↓
Frontend adds Authorization header
    ├─ Authorization: Bearer <token>
    └─ POST /api/courses/my-courses
    ↓
Backend receives request
    ├─ Django middleware
    ├─ URL routing
    ├─ @permission_classes([IsAuthenticated]) decorator
    ├─ CustomJWTAuthentication (users/authentication.py)
    │  ├─ Extract token from header
    │  ├─ Decode token with SECRET_KEY
    │  ├─ Verify expiration
    │  ├─ Get user_id from payload
    │  ├─ Fetch User from database
    │  └─ Attach to request.user
    ├─ Check permission (allowed)
    ├─ View executes (can access request.user)
    └─ Return response
    ↓
Frontend receives authenticated response
    └─ Use returned data (courses, etc.)

─────────────────────────────────────────────────────────────────────────

TOKEN EXPIRATION:

30 days pass
    ↓
User makes request with old token
    ↓
Backend tries to authenticate
    ├─ Decode token
    ├─ Check expiration date (exp < now)
    ├─ Token is expired → Authentication fails
    └─ Return 401 Unauthorized
    ↓
Frontend catches 401 error
    ├─ Clear localStorage
    ├─ Redirect to login
    └─ User must login again
    ↓
User logs in again → New token generated

─────────────────────────────────────────────────────────────────────────

TOKEN PAYLOAD STRUCTURE:

{
  "user_id": 1,                              ← User ID from database
  "email": "user@example.com",               ← User email
  "exp": 1733616000,                         ← Expiration timestamp
  "iat": 1701168000,                         ← Issued at timestamp
}

JWT Format: header.payload.signature

Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20ifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

---

## AI Integration Points

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI/LLM INTEGRATION POINTS                             │
└─────────────────────────────────────────────────────────────────────────┘

1. ASSESSMENT QUESTION GENERATION
   
   Flow:
   POST /api/assessment/generate-questions
   ↓
   LLMService.generate_assessment_questions(course_title, description)
   ├─ Create prompt with course info
   ├─ Call OpenAI API
   │  {
   │    model: "gpt-4",
   │    messages: [
   │      {role: "system", content: "You are an educator..."},
   │      {role: "user", content: prompt}
   │    ]
   │  }
   ├─ Receive response with 10 MCQ JSON
   ├─ Parse response
   └─ Return questions array
   ↓
   Result saved: Assessment.questions_data (JSON)
   
   Fallback: _get_fallback_questions() if API fails

─────────────────────────────────────────────────────────────────────────

2. ROADMAP GENERATION

   Flow:
   POST /api/assessment/generate-roadmap
   ↓
   LLMService.generate_roadmap()
   ├─ Check: USE_DYNAMIC_RESOURCES setting
   │
   ├─ If false (default):
   │  └─ RoadmapGenerator.generate_roadmap()
   │     ├─ Static roadmap from predefined library
   │     └─ Return roadmap data
   │
   ├─ If true:
   │  └─ DynamicResourceFetcher.get_complete_roadmap()
   │     ├─ OpenAI: Generate chapter outline
   │     ├─ Serper API: Search for tutorials
   │     ├─ YouTube API: Fetch video URLs
   │     └─ Combine resources with outline
   │
   └─ Fallback chain: Dynamic → Static → DB → Hardcoded
   ↓
   Result saved: Roadmap.roadmap_data (JSON)
   
   Structure:
   {
     "chapters": [
       {
         "number": 1,
         "title": "Chapter 1",
         "topics": ["Topic 1", "Topic 2"],
         "duration": 7,
         "resources": {
           "videos": ["https://youtube.com/..."],
           "documentation": ["https://docs.python.org/..."],
           "tutorials": ["https://w3schools.com/..."]
         }
       }
     ]
   }

─────────────────────────────────────────────────────────────────────────

3. CHAPTER TEST GENERATION

   Flow:
   POST /api/learning/chapter-test/generate
   ↓
   LLMService.generate_chapter_test(course_title, chapter_name)
   ├─ Create prompt for chapter-specific MCQ
   ├─ Call OpenAI API
   ├─ Generate 4 questions (chapter test)
   └─ Return questions array
   ↓
   Result saved: ChapterTest.questions_data (JSON)
   
   Fallback: _get_fallback_chapter_test()

─────────────────────────────────────────────────────────────────────────

API CONFIGURATION (settings.py):

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4'  # Can be 'gpt-3.5-turbo'

LLMService initialization:
├─ Loads OpenAI API key from settings
├─ Sets model to GPT-4
└─ Initializes fallback systems

─────────────────────────────────────────────────────────────────────────

FALLBACK MECHANISM:

API Call → Parse Response → Error? 
                             ↓
                         Fallback 1: Static Library
                                     ↓ Fails?
                         Fallback 2: Database Cache
                                     ↓ Fails?
                         Fallback 3: Hardcoded Default
```

---

**These diagrams provide visual representations of:**
- System architecture
- Data flows
- API interactions
- Database relationships
- Authentication process
- AI integration points

**Use these when explaining or understanding:**
- How the system works
- Where data goes
- What happens during key operations
- Integration points
