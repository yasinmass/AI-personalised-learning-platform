# LearnPath - Project Overview & Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (Frontend)                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ HTML5 | CSS3 | JavaScript (Vanilla)                        │   │
│  │ - Authentication Pages (Login/Register)                    │   │
│  │ - Course Browsing & Selection                              │   │
│  │ - Assessment Quiz Interface                                │   │
│  │ - Learning Path Display                                    │   │
│  │ - Dashboard & Analytics                                    │   │
│  │ - Responsive Design (Mobile/Tablet/Desktop)                │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────────┐
│                    REST API (Backend)                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Django REST Framework                                       │  │
│  │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐               │  │
│  │ │ Auth   │ │ Course │ │ Assess │ │ Learn  │               │  │
│  │ │ Routes │ │ Routes │ │ Routes │ │ Routes │               │  │
│  │ └────────┘ └────────┘ └────────┘ └────────┘               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌──────────┐        ┌──────────┐
    │Database│          │OpenAI API│        │JWT Token│
    │(Postgre│          │  (GPT-4) │        │ Manager  │
    │SQL)    │          │          │        │          │
    └────────┘          └──────────┘        └──────────┘
```

## 🔄 User Journey Flow

```
START
  │
  ├─ Register/Login
  │   └─ JWT Token Generated
  │
  ├─ Browse Courses
  │   └─ Display Available Courses
  │
  ├─ Select Course & Start Assessment
  │   ├─ LLM Generates 10 MCQs (OpenAI)
  │   └─ User Takes Assessment
  │
  ├─ Submit Assessment & Get Results
  │   ├─ Score Calculated
  │   ├─ Skill Level Determined (Beginner/Intermediate/Advanced)
  │   └─ Display Results
  │
  ├─ Set Learning Duration & Generate Roadmap
  │   ├─ User Inputs Preferred Duration (weeks)
  │   ├─ LLM Generates Personalized Roadmap (OpenAI)
  │   └─ Roadmap Includes:
  │       ├─ Chapter Breakdown
  │       ├─ Topics & Learning Resources
  │       ├─ Time Estimates
  │       └─ YouTube/Documentation Links
  │
  ├─ Start Learning Path
  │   ├─ View Chapters in Sidebar
  │   ├─ Read Chapter Content & Resources
  │   ├─ Mark Chapter Complete
  │   └─ Track Time Spent
  │
  ├─ Take Chapter Tests
  │   ├─ LLM Generates 4 MCQs Per Chapter
  │   ├─ User Completes Test
  │   ├─ Score Calculated
  │   └─ Weak Areas Identified
  │
  ├─ Adaptive Learning Path Update
  │   ├─ System Analyzes Weak Areas
  │   ├─ Recommendations Generated
  │   └─ Roadmap Adjusted (Optional)
  │
  ├─ Monitor Progress on Dashboard
  │   ├─ View Overall Progress %
  │   ├─ Check Performance Metrics
  │   ├─ Review Weak Areas
  │   └─ See Learning Activity Feed
  │
  └─ Continue Learning...
```

## 📦 Component Architecture

### Frontend Components

```
┌─ App.js (Main Controller)
│  ├─ Authentication Module
│  │  ├─ Login Form Handler
│  │  ├─ Register Form Handler
│  │  └─ Token Management
│  │
│  ├─ Course Module
│  │  ├─ Course Display
│  │  └─ Enrollment Handler
│  │
│  ├─ Assessment Module
│  │  ├─ Question Display
│  │  ├─ Answer Collection
│  │  └─ Results Display
│  │
│  ├─ Learning Module
│  │  ├─ Chapter Navigation
│  │  ├─ Content Display
│  │  ├─ Resource Links
│  │  ├─ Progress Tracking
│  │  └─ Test Interface
│  │
│  ├─ Dashboard Module
│  │  ├─ Progress Visualization
│  │  ├─ Performance Metrics
│  │  ├─ Activity Feed
│  │  └─ Weak Areas Display
│  │
│  └─ UI Components
│     ├─ Navigation Bar
│     ├─ Modal Dialogs
│     ├─ Progress Bars
│     └─ Cards & Layouts
│
└─ API.js (API Client)
   ├─ APIClient Class
   ├─ Request/Response Handling
   └─ Error Management
```

### Backend Components

```
┌─ Django Project (config/)
│  ├─ settings.py (Configuration)
│  ├─ urls.py (Routing)
│  ├─ wsgi.py (Deployment)
│  └─ asgi.py (Async)
│
├─ Users App
│  ├─ Models: User, UserProfile
│  ├─ Serializers
│  ├─ Views: Register, Login, Profile
│  └─ URLs: /auth/*
│
├─ Courses App
│  ├─ Models: Course, UserCourse
│  ├─ Views: List, Enroll, Progress
│  ├─ Management Command: create_initial_data
│  └─ URLs: /courses/*
│
├─ Assessments App
│  ├─ Models: Assessment, Roadmap
│  ├─ LLMService: OpenAI Integration
│  │  ├─ generate_assessment_questions()
│  │  ├─ generate_roadmap()
│  │  ├─ generate_chapter_test()
│  │  └─ generate_adaptive_recommendations()
│  ├─ Views: Generate, Submit, Results
│  └─ URLs: /assessment/*
│
├─ Learning App
│  ├─ Models: ChapterProgress, ChapterTest, LearningActivity
│  ├─ Views:
│  │  ├─ get_roadmap_chapters()
│  │  ├─ track_chapter_progress()
│  │  ├─ generate_chapter_test()
│  │  ├─ submit_chapter_test()
│  │  └─ get_learning_dashboard()
│  └─ URLs: /learning/*
│
└─ Database (PostgreSQL)
   ├─ Users Table
   ├─ Courses Table
   ├─ UserCourses Table
   ├─ Assessments Table
   ├─ Roadmaps Table
   ├─ ChapterProgress Table
   ├─ ChapterTests Table
   └─ LearningActivity Table
```

## 🔌 Data Flow Diagram

```
USER ACTION
    │
    ├─ [Frontend] User Input → JavaScript Handler
    │
    ├─ [API Call] axios/fetch → REST Endpoint
    │
    ├─ [Backend] Django View → Process Request
    │
    ├─ [Models] Database Query
    │   │
    │   └─ [LLMService] (If needed)
    │       └─ OpenAI API Call → Generate Content
    │
    ├─ [Serializers] Format Response
    │
    ├─ [Response] JSON → Frontend
    │
    ├─ [Frontend] JavaScript → Update DOM
    │
    └─ [UI] User Sees Result
```

## 📊 Database Schema Relationship

```
┌──────────────┐
│   User       │
├──────────────┤
│ id (PK)      │
│ email        │
│ password     │
│ username     │
└──────┬───────┘
       │ 1:1
       ▼
┌──────────────────────┐
│  UserProfile         │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK)         │
│ learning_duration    │
└──────┬───────────────┘
       │ 1:M
       │
       ├─────────────┬─────────────┬──────────────┐
       │             │             │              │
       ▼             ▼             ▼              ▼
    ┌────────────────────────┐
    │   UserCourse           │
    ├────────────────────────┤
    │ user_id (FK) (PK)      │
    │ course_id (FK) (PK)    │
    │ status                 │
    │ progress_percentage    │
    └─────┬────────────────┬─┘
          │                │
          │                ├─────────────────────────┐
          ▼                ▼                         ▼
    ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐
    │   Course     │  │  Assessment    │  │  Roadmap         │
    ├──────────────┤  ├────────────────┤  ├──────────────────┤
    │ id (PK)      │  │ id (PK)        │  │ id (PK)          │
    │ title        │  │ user_id (FK)   │  │ user_id (FK)     │
    │ description  │  │ course_id (FK) │  │ course_id (FK)   │
    │ difficulty   │  │ score          │  │ assessment_id(FK)│
    │ duration     │  │ percentage     │  │ skill_level      │
    └──────────────┘  │ skill_level    │  │ duration_weeks   │
                      │ questions_data │  │ roadmap_data     │
                      └────────┬───────┘  └──────────────────┘
                               │                    │
                               │                    ▼
                               │          ┌──────────────────────┐
                               │          │  ChapterProgress     │
                               │          ├──────────────────────┤
                               │          │ roadmap_id (FK)      │
                               │          │ chapter_number       │
                               │          │ status               │
                               │          │ time_spent_minutes   │
                               │          └─────────┬────────────┘
                               │                    │
                               │                    ▼
                               │          ┌──────────────────────┐
                               │          │  ChapterTest         │
                               │          ├──────────────────────┤
                               │          │ chapter_progress(FK) │
                               │          │ score                │
                               │          │ percentage           │
                               │          │ questions_data       │
                               │          └──────────────────────┘
                               │
                               └─────────────────────┐
                                                     ▼
                                           ┌──────────────────────┐
                                           │  LearningActivity    │
                                           ├──────────────────────┤
                                           │ roadmap_id (FK)      │
                                           │ activity_type        │
                                           │ chapter_name         │
                                           │ duration_minutes     │
                                           └──────────────────────┘
```

## 🎯 Feature Matrix

| Feature | Frontend | Backend | Database | LLM |
|---------|----------|---------|----------|-----|
| User Auth | ✅ Forms | ✅ JWT | ✅ Users | ❌ |
| Courses | ✅ Display | ✅ API | ✅ Courses | ❌ |
| Assessment | ✅ Quiz UI | ✅ Scoring | ✅ Store | ✅ Generate |
| Roadmap | ✅ Display | ✅ Generate | ✅ Store | ✅ Generate |
| Learning | ✅ Interface | ✅ Track | ✅ Progress | ❌ |
| Tests | ✅ Quiz UI | ✅ Generate | ✅ Store | ✅ Generate |
| Dashboard | ✅ Display | ✅ Analytics | ✅ Query | ❌ |
| Adapt | ✅ Display | ✅ Recommend | ✅ Store | ✅ Recommend |

## 🔐 Authentication Flow

```
User Inputs Credentials
         │
         ▼
    Hash Password
         │
         ▼
    Query Database
         │
    ┌────┴────┐
    │          │
    ▼          ▼
  Match    No Match
    │          │
    ▼          ▼
Generate    Error
  JWT        401
  Token
    │
    ▼
Return Token
    │
    ▼
Store in localStorage
    │
    ▼
Include in API Headers
    │
    ▼
Backend Validates Token
```

## 🌐 API Request/Response Example

```
REQUEST:
POST /api/assessment/generate-questions
Headers: {
  "Content-Type": "application/json",
  "Authorization": "Bearer <JWT_TOKEN>"
}
Body: {
  "course_id": 1
}

PROCESSING:
1. Validate JWT Token
2. Check User Exists
3. Call LLMService.generate_assessment_questions()
4. OpenAI API Call → Generate 10 MCQs
5. Create Assessment Record in DB
6. Serialize Response

RESPONSE:
{
  "assessment_id": 123,
  "course_id": 1,
  "total_questions": 10,
  "questions": [
    {
      "question": "What is...",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correct_answer": "A",
      "difficulty": "easy",
      "explanation": "..."
    },
    ...
  ]
}
```

## 📈 Performance Considerations

```
Optimization Areas:
├─ Database
│  ├─ Indexing on frequently queried fields
│  ├─ Query optimization (select_related, prefetch_related)
│  └─ Connection pooling
│
├─ API
│  ├─ Response pagination
│  ├─ Caching strategies
│  └─ Rate limiting
│
├─ Frontend
│  ├─ Lazy loading
│  ├─ CSS/JS minification
│  └─ Image optimization
│
└─ Infrastructure
   ├─ CDN for static files
   ├─ Compression (gzip)
   └─ Database replication
```

## 🚀 Deployment Architecture (Production)

```
                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │App     │          │App     │          │App     │
    │Server  │          │Server  │          │Server  │
    │(Gunic) │          │(Gunic) │          │(Gunic) │
    └───┬────┘          └───┬────┘          └───┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    │                    ▼
    ┌────────────┐       ┌──────────┐      ┌───────────┐
    │PostgreSQL  │       │Redis     │      │OpenAI API │
    │Database    │       │Cache     │      │           │
    └────────────┘       └──────────┘      └───────────┘
         │                    │
         └────────────────────┴────────────────┐
                              │
                              ▼
                          ┌────────────┐
                          │   Backup   │
                          │  & Archive │
                          └────────────┘
```

---

**This architecture supports:**
- ✅ Scalability (horizontal scaling with load balancer)
- ✅ Reliability (database redundancy, caching)
- ✅ Security (JWT, environment variables, HTTPS)
- ✅ Performance (optimization at all levels)
- ✅ Maintainability (modular architecture)

**Ready for production deployment!** 🎯
