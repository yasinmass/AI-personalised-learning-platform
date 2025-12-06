# AI-Personalized Learning Platform - Complete Project Analysis

## 📋 Project Overview

**LearnPath** is an AI-powered personalized learning platform that adapts educational content to individual learner skill levels. It combines Django REST backend with vanilla JavaScript frontend, PostgreSQL database, and OpenAI integration for intelligent content generation.

---

## 🏗️ Architecture

### High-Level Architecture
```
Frontend (HTML/CSS/JS)
        ↓ HTTP/REST
Django REST API Backend
        ↓
PostgreSQL Database
+ OpenAI API Integration
+ Dynamic Resource Fetcher
+ LLM Service
```

### Tech Stack
- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Database**: PostgreSQL
- **Authentication**: JWT (Custom implementation)
- **AI Integration**: OpenAI API (GPT-4), Ollama (fallback)
- **External APIs**: Serper (Google Search), YouTube Data API
- **Build Tool**: GuniCorn (production server)

---

## 📦 Project Structure

```
learnpath/
├── backend/                    # Django project root
│   ├── config/                # Django settings & URL routing
│   ├── users/                 # Authentication & profiles
│   ├── courses/               # Course management
│   ├── assessments/           # Assessments & roadmaps
│   ├── learning/              # Learning progress tracking
│   ├── manage.py
│   ├── requirements.txt
│   └── [migrations & media folders]
└── frontend/                  # Client-side code
    ├── index.html            # Main HTML
    ├── css/
    │   ├── style.css        # Primary styles
    │   └── responsive.css   # Mobile responsive
    └── js/
        ├── app.js           # Main application logic
        └── api.js           # API client
```

---

## 🗄️ Database Schema

### 1. **Users Module** (`users/`)
#### `UserProfile` Model
```python
- user: OneToOneField(User)              # Django auth user
- learning_duration_preference: Integer  # Duration in weeks
- total_learning_hours: Integer          # Cumulative hours
- created_at, updated_at: DateTime
```

### 2. **Courses Module** (`courses/`)
#### `Course` Model
```python
- title: CharField
- description: TextField
- difficulty: Choice (beginner/intermediate/advanced)
- icon_url: URLField
- duration_weeks: Integer
- created_at, updated_at: DateTime
```

#### `UserCourse` Model (Enrollment Tracking)
```python
- user: ForeignKey(UserProfile)
- course: ForeignKey(Course)
- status: Choice (enrolled/in_progress/completed/paused)
- enrollment_date, completion_date: DateTime
- progress_percentage: Integer
- UNIQUE: (user, course)
```

### 3. **Assessments Module** (`assessments/`)
#### `Assessment` Model (Initial Skill Assessment)
```python
- user: ForeignKey(UserProfile)
- course: ForeignKey(Course)
- score: Integer                         # 0-10
- total_questions: Integer              # Fixed at 10
- percentage: Float                     # Score percentage
- questions_data: JSONField             # MCQ questions & answers
- skill_level: Choice               # beginner/intermediate/advanced
- created_at: DateTime
```

#### `Roadmap` Model (Personalized Learning Path)
```python
- user: ForeignKey(UserProfile)
- course: ForeignKey(Course)
- assessment: OneToOneField(Assessment) # Links to skill assessment
- skill_level: CharField                # Copied from assessment
- duration_weeks: Integer               # Preferred learning duration
- roadmap_data: JSONField               # Chapters, resources, times
- created_at, updated_at: DateTime
```

**Roadmap Data Structure**:
```json
{
  "chapters": [
    {
      "number": 1,
      "title": "Chapter Title",
      "topics": ["Topic 1", "Topic 2"],
      "duration": 7,
      "resources": {
        "videos": ["url1", "url2"],
        "documentation": ["url1"],
        "tutorials": ["url1"]
      }
    }
  ]
}
```

### 4. **Learning Module** (`learning/`)
#### `ChapterProgress` Model
```python
- user: ForeignKey(UserProfile)
- roadmap: ForeignKey(Roadmap)
- chapter_name: CharField
- chapter_number: Integer
- status: Choice (not_started/in_progress/completed)
- time_spent_minutes: Integer
- last_accessed, completion_date: DateTime
- UNIQUE: (roadmap, chapter_number)
```

#### `ChapterTest` Model
```python
- user: ForeignKey(UserProfile)
- roadmap: ForeignKey(Roadmap)
- chapter_progress: ForeignKey(ChapterProgress)
- chapter_name: CharField
- score: Integer                  # 0-4 (4 questions)
- total_questions: Integer        # Fixed at 4
- percentage: Float
- questions_data: JSONField       # Test MCQs
- created_at: DateTime
```

#### `LearningActivity` Model (Audit Trail)
```python
- user: ForeignKey(UserProfile)
- roadmap: ForeignKey(Roadmap)
- activity_type: Choice (chapter_viewed/test_taken/resource_accessed/time_logged)
- chapter_name: CharField
- duration_minutes: Integer
- details: JSONField
- created_at: DateTime
```

---

## 🔌 API Endpoints

### Authentication (`/api/auth/`)
```
POST   /register              # User registration
POST   /login                 # User login (returns JWT)
GET    /profile               # Get user profile (authenticated)
PUT    /profile/update        # Update profile preferences
```

**Login Response**:
```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John"
  }
}
```

### Courses (`/api/courses/`)
```
GET    /list                  # All available courses
GET    /<course_id>           # Course details
POST   /<course_id>/enroll    # Enroll in course (authenticated)
GET    /my-courses            # User's enrolled courses (authenticated)
```

**Course Object**:
```json
{
  "id": 1,
  "title": "Python Basics",
  "description": "Learn Python fundamentals",
  "difficulty": "beginner",
  "icon_url": "https://...",
  "duration_weeks": 12
}
```

### Assessments (`/api/assessment/`)
```
POST   /generate-questions        # Generate 10 MCQ questions
POST   /submit                    # Submit answers, calculate score
POST   /generate-roadmap          # Create personalized roadmap
GET    /check-status              # Check if assessment done
GET    /get-roadmap/<roadmap_id> # Roadmap details
GET    /my-roadmaps              # User's roadmaps (authenticated)
```

**Generate Questions Request**:
```json
{
  "course_id": 1
}
```

**Assessment Response**:
```json
{
  "assessment_id": 123,
  "questions": [
    {
      "question": "What is Python?",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "difficulty": "easy"
    }
  ],
  "total_questions": 10
}
```

**Submit Assessment Request**:
```json
{
  "assessment_id": 123,
  "answers": {
    "0": "A",
    "1": "B",
    "2": "C"
  }
}
```

**Assessment Result**:
```json
{
  "score": 7,
  "total_questions": 10,
  "percentage": 70.0,
  "skill_level": "intermediate"
}
```

### Learning (`/api/learning/`)
```
GET    /chapters/<roadmap_id>              # Get all chapters
POST   /track-progress                     # Update chapter progress
POST   /chapter-test/generate              # Generate 4-question test
POST   /chapter-test/submit                # Submit test answers
GET    /dashboard/<roadmap_id>             # Learning dashboard
```

**Track Progress Request**:
```json
{
  "roadmap_id": 5,
  "chapter_number": 1,
  "status": "completed",
  "time_spent_minutes": 45
}
```

---

## 🧠 Core Business Logic

### 1. User Registration Flow
```
User fills register form
  ↓
POST /api/auth/register
  ↓
Create Django User + UserProfile
  ↓
Return user object
```

### 2. Course Selection & Assessment Flow
```
User views courses (GET /api/courses/list)
  ↓
User enrolls (POST /api/courses/<id>/enroll)
  ↓
Frontend requests questions (POST /api/assessment/generate-questions)
  ↓
LLMService.generate_assessment_questions() 
  → OpenAI API generates 10 MCQs
  ↓
Assessment record created with questions
  ↓
User takes test, submits answers
  ↓
Score calculated, skill_level determined (0-33%: beginner, etc.)
```

### 3. Roadmap Generation Flow
```
Assessment completed with skill_level
  ↓
POST /api/assessment/generate-roadmap with duration_weeks
  ↓
LLMService.generate_roadmap() called with:
  - course_title
  - course_description
  - skill_level (from assessment)
  - duration_weeks (user preference)
  ↓
If USE_DYNAMIC_RESOURCES=true:
  - DynamicResourceFetcher gets real resources
  - Converts to roadmap format
Else (default):
  - RoadmapGenerator creates static roadmap
  ↓
Roadmap saved with chapters, resources, times
  ↓
Frontend displays roadmap with sidebar chapters
```

### 4. Learning Progress Tracking
```
User views chapter
  ↓
ChapterProgress created/updated with status
  ↓
Time spent tracked
  ↓
LearningActivity logged
  ↓
User takes chapter test
  ↓
ChapterTest created with 4 auto-generated MCQs
  ↓
Answers submitted, score calculated
  ↓
Dashboard updated with progress %
```

---

## 🔐 Authentication System

### JWT Implementation
- **Location**: `users/authentication.py` (Custom JWT Authentication)
- **Secret**: `JWT_SECRET` from settings
- **Expiration**: 30 days
- **Header**: `Authorization: Bearer <token>`
- **Token Payload**:
  ```python
  {
    "user_id": 1,
    "email": "user@example.com",
    "exp": <unix_timestamp>,
    "iat": <unix_timestamp>
  }
  ```

### Permission Classes
- `AllowAny`: Registration, login, course list
- `IsAuthenticated`: Profile, enrollment, assessments, learning

---

## 🤖 AI Integration

### LLMService (`assessments/llm_service.py`)

**Key Methods**:

1. **generate_assessment_questions()**
   - Prompt: Requests 10 MCQ on course topic
   - Returns: JSON with questions, options, correct answers
   - Fallback: `_get_fallback_questions()` returns static questions

2. **generate_roadmap()**
   - Input: course title, skill level, duration weeks
   - Logic:
     - If `USE_DYNAMIC_RESOURCES=false` (default): Use RoadmapGenerator
     - If `USE_DYNAMIC_RESOURCES=true`: Use DynamicResourceFetcher
   - Returns: Roadmap data with chapters, resources, time estimates

3. **generate_chapter_test()**
   - Generates 4 MCQ for specific chapter
   - Called when user completes chapter

### Dynamic Resource Fetching (`assessments/dynamic_resource_fetcher.py`)
- Fetches real YouTube videos via YouTube API
- Fetches documentation via Serper (Google Search)
- Uses Ollama for local LLM (if available)
- Database fallback for missing resources

### Static Roadmap Generator (`assessments/roadmap_generator.py`)
- Pre-defined roadmaps for common courses
- Skill-level specific content
- Predictable, reliable (no API calls)

---

## 🎨 Frontend Architecture

### Main Files

**`index.html`** (298 lines)
- Single-page application (SPA) with multiple page containers
- Login/Register forms (tab-based)
- Home page hero section
- Course browsing interface
- Assessment quiz interface
- Roadmap display with sidebar chapters
- Learning dashboard
- Navigation bar with responsive hamburger menu

**`js/app.js`** (Main Controller)
- Page navigation logic
- Form submission handlers
- API calls coordination
- DOM manipulation
- Local storage (token management)
- Event listeners

**`js/api.js`** (API Client Class)
- `APIClient` class with methods for all endpoints
- Header management with JWT token
- Error handling
- Methods:
  - Auth: `register()`, `login()`, `getProfile()`, `updateProfile()`
  - Courses: `getCourses()`, `enrollCourse()`, `getUserCourses()`
  - Assessment: `generateAssessmentQuestions()`, `submitAssessment()`, `generateRoadmap()`
  - Learning: `getChapters()`, `trackProgress()`, `generateChapterTest()`, `submitChapterTest()`

**`css/style.css`** (Primary Styling)
- Color scheme: Professional education theme
- Components: Navigation, cards, forms, buttons
- Animations and transitions

**`css/responsive.css`** (Mobile Design)
- Media queries for tablet/mobile
- Hamburger menu for small screens
- Responsive typography
- Flexible layouts

### Page Components (SPA)
1. **Login Page** - Registration/Login forms
2. **Home Page** - Hero section, feature overview
3. **Courses Page** - Course cards, enrollment button
4. **Assessment Page** - Quiz interface, question display
5. **Roadmap Page** - Roadmap overview, chapter selection
6. **Learning Page** - Chapter content, progress tracker
7. **Dashboard Page** - Analytics, performance metrics

---

## 🔄 User Journey

```
1. USER REGISTRATION/LOGIN
   └─ Navigate to /
   └─ Fill register form or login
   └─ POST /api/auth/register or login
   └─ Get JWT token
   └─ Redirect to home page

2. COURSE SELECTION
   └─ View available courses (GET /api/courses/list)
   └─ Click course
   └─ View course details
   └─ Click "Start Assessment"

3. SKILL ASSESSMENT
   └─ POST /api/assessment/generate-questions
   └─ Answer 10 MCQ questions
   └─ POST /api/assessment/submit
   └─ Receive score & skill_level
   └─ View results

4. ROADMAP GENERATION
   └─ Input duration preference (weeks)
   └─ POST /api/assessment/generate-roadmap
   └─ Receive personalized roadmap
   └─ View chapters in sidebar

5. LEARNING PATH
   └─ Start learning chapter 1
   └─ View chapter resources (YouTube, docs)
   └─ Mark chapter complete (POST /api/learning/track-progress)
   └─ LearningActivity logged
   └─ Progress % updated

6. CHAPTER TEST
   └─ Finish chapter
   └─ Click "Take Test"
   └─ POST /api/learning/chapter-test/generate
   └─ Answer 4 MCQ
   └─ POST /api/learning/chapter-test/submit
   └─ View score & weak areas

7. DASHBOARD
   └─ View overall progress
   └─ Check performance metrics
   └─ See learning activity history
   └─ Adjust roadmap if needed
```

---

## 🛠️ Key Utilities

### Settings (`config/settings.py`)
- Django core config
- Database: PostgreSQL
- REST Framework: JWT authentication, pagination
- CORS: Allows localhost:3000, localhost:8000, localhost:8001
- OpenAI: API key from env

### Serializers
- **Users**: `UserProfileSerializer`, `RegisterSerializer`, `LoginSerializer`
- **Courses**: `CourseSerializer`, `UserCourseSerializer`
- **Assessments**: `AssessmentSerializer`, `RoadmapSerializer`
- **Learning**: `ChapterProgressSerializer`, `ChapterTestDetailSerializer`, `LearningActivitySerializer`

### Authentication (`users/authentication.py`)
- Custom JWT authentication class
- Decodes token from Authorization header
- Validates token expiration
- Attaches user to request object

---

## 📊 Data Relationships

```
User (Django Auth)
  ↓ OneToOne
UserProfile
  ├─ Many Enrolled Courses (UserCourse)
  ├─ Many Assessments
  ├─ Many Roadmaps
  ├─ Many ChapterProgress
  ├─ Many ChapterTests
  └─ Many LearningActivities
    
Course
  ├─ Many Assessments (initial skill checks)
  ├─ Many Roadmaps
  └─ Many UserCourse (enrollments)

Assessment
  ├─ One Roadmap (relationship)
  └─ Questions stored in JSONField

Roadmap
  ├─ One Assessment
  ├─ Many ChapterProgress
  ├─ Many ChapterTests
  └─ Many LearningActivities

ChapterProgress
  ├─ One Roadmap
  └─ Many ChapterTests

ChapterTest
  └─ One ChapterProgress
```

---

## 🔑 Key Configuration

### Environment Variables (`.env`)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=learnpath_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

JWT_SECRET=your-jwt-secret

SERPER_API_KEY=optional
YOUTUBE_API_KEY=optional
OLLAMA_URL=http://localhost:11434
USE_DYNAMIC_RESOURCES=false
```

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
```

---

## 📝 Dependencies

### Backend (`requirements.txt`)
```
Django==4.2.8
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
python-decouple==3.8
PyJWT==2.10.1
openai==1.3.8
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

## 🚀 API Flow Summary

### Request Flow
```
Frontend (JavaScript)
  ↓ Fetch API call
APIClient.method() (api.js)
  ↓ HTTP request with JWT header
Django URL Router (config/urls.py)
  ↓ Route matching
View Function (views.py)
  ↓ Authentication check
Business Logic (serializers, models)
  ↓ LLM calls if needed
Response JSON
  ↓ Return to frontend
Frontend handles response
```

---

## ✅ Implementation Checklist

### Core Features ✓
- [x] User authentication (JWT)
- [x] Course management
- [x] Initial assessment (10 MCQ)
- [x] AI roadmap generation
- [x] Chapter tracking
- [x] Chapter tests (4 MCQ each)
- [x] Learning activity audit
- [x] Dashboard/progress tracking
- [x] Responsive frontend

### Integration Points
- [x] OpenAI API for question/roadmap generation
- [x] PostgreSQL database
- [x] JWT authentication
- [x] CORS for frontend-backend communication
- [ ] Dynamic resource fetching (optional, fallback available)

---

## 🔗 Important File Locations

| File | Purpose |
|------|---------|
| `backend/config/settings.py` | Django settings, database, API config |
| `backend/config/urls.py` | URL routing |
| `backend/users/models.py` | User, UserProfile models |
| `backend/courses/models.py` | Course, UserCourse models |
| `backend/assessments/models.py` | Assessment, Roadmap models |
| `backend/learning/models.py` | ChapterProgress, ChapterTest, LearningActivity |
| `backend/assessments/llm_service.py` | OpenAI integration, roadmap generation |
| `frontend/index.html` | Main HTML single-page app |
| `frontend/js/app.js` | Frontend logic, page routing |
| `frontend/js/api.js` | API client class |

---

## 📌 Key Concepts

### Skill Level Determination
- **Score < 33%**: Beginner (fundamentals focus)
- **Score 33-67%**: Intermediate (building on basics)
- **Score > 67%**: Advanced (optimization & deep topics)

### Roadmap Generation Logic
1. Based on skill level from assessment
2. Personalized duration (user preference in weeks)
3. Includes chapters, topics, resources
4. Resource types: Videos, Documentation, Official websites

### Progress Tracking
- Chapter status: not_started → in_progress → completed
- Time spent tracked per chapter
- Tests provide score & identify weak areas
- LearningActivity provides complete audit trail

---

## 🎯 Next Steps for Development

1. **Testing**: Write unit/integration tests
2. **Documentation**: Add API documentation (Swagger/OpenAPI)
3. **Enhancement**: Add more course content
4. **Optimization**: Implement caching for roadmaps
5. **Monitoring**: Add logging and error tracking
6. **Deployment**: Set up CI/CD pipeline

---

**Document Version**: 1.0  
**Last Updated**: December 5, 2025  
**Project Status**: Complete & Ready for Modifications
