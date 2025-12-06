# Quick Reference Guide - AI Personalized Learning Platform

## 🔍 Finding Code by Feature

### User Authentication
- **Register endpoint**: `backend/users/views.py::register()`
- **Login endpoint**: `backend/users/views.py::login()`
- **JWT implementation**: `backend/users/authentication.py`
- **Models**: `backend/users/models.py::UserProfile`
- **Serializers**: `backend/users/serializers.py`

### Course Management
- **List courses**: `backend/courses/views.py::list_courses()`
- **Enroll in course**: `backend/courses/views.py::enroll_course()`
- **Models**: `backend/courses/models.py::Course`, `UserCourse`
- **URLs**: `backend/courses/urls.py`

### Assessment & Skill Level
- **Generate questions**: `backend/assessments/views.py::generate_assessment_questions()`
- **Submit answers**: `backend/assessments/views.py::submit_assessment()`
- **Calculate skill level**: `backend/assessments/models.py::Assessment.calculate_skill_level()`
- **LLM service**: `backend/assessments/llm_service.py::LLMService`

### Roadmap Generation
- **Generate roadmap**: `backend/assessments/views.py::generate_roadmap()`
- **LLM generation**: `backend/assessments/llm_service.py::generate_roadmap()`
- **Static generator**: `backend/assessments/roadmap_generator.py::RoadmapGenerator`
- **Dynamic resources**: `backend/assessments/dynamic_resource_fetcher.py::DynamicResourceFetcher`

### Learning Progress
- **Track chapter progress**: `backend/learning/views.py::track_chapter_progress()`
- **Generate chapter test**: `backend/learning/views.py::generate_chapter_test()`
- **Submit chapter test**: `backend/learning/views.py::submit_chapter_test()`
- **Models**: `backend/learning/models.py::ChapterProgress`, `ChapterTest`, `LearningActivity`

### Frontend
- **Main app**: `frontend/js/app.js` (Page logic, routing, DOM updates)
- **API client**: `frontend/js/api.js` (APIClient class, all API calls)
- **HTML structure**: `frontend/index.html` (Single-page app structure)
- **Styles**: `frontend/css/style.css` and `responsive.css`

---

## 🔗 Database Model Relationships

### User-Centric View
```
User ← UserProfile (OneToOne)
  ├─ UserCourse (Many) → Course
  ├─ Assessment (Many) → Course
  ├─ Roadmap (Many) → Course, Assessment (OneToOne)
  ├─ ChapterProgress (Many) → Roadmap
  ├─ ChapterTest (Many) → Roadmap, ChapterProgress
  └─ LearningActivity (Many) → Roadmap
```

### To find all user data:
```python
user = User.objects.get(id=user_id)
profile = user.profile  # UserProfile
courses = profile.enrolled_courses.all()  # UserCourse
assessments = profile.assessments.all()  # Assessment
roadmaps = profile.roadmaps.all()  # Roadmap
```

---

## 🔑 Common API Calls

### Backend to Frontend (APIClient methods in `api.js`)

**Authentication**
```javascript
const api = new APIClient('http://127.0.0.1:8000/api');
const response = await api.register({email, username, password});
const response = await api.login(email, password);
api.setToken(token);  // Save token after login
const profile = await api.getProfile();
```

**Courses**
```javascript
const courses = await api.getCourses();  // GET /courses/list
await api.enrollCourse(courseId);        // POST /courses/<id>/enroll
const myCourses = await api.getUserCourses();  // GET /courses/my-courses
```

**Assessment**
```javascript
const assessment = await api.generateAssessmentQuestions(courseId);
const result = await api.submitAssessment(assessmentId, answers);
const roadmap = await api.generateRoadmap(assessmentId, durationWeeks);
const roadmaps = await api.getUserRoadmaps();
```

**Learning**
```javascript
const chapters = await api.getChapters(roadmapId);
await api.trackProgress(roadmapId, chapterNumber, status, timeSpent);
const test = await api.generateChapterTest(roadmapId, chapterNumber);
const testResult = await api.submitChapterTest(testId, answers);
```

---

## 📝 Data Structures

### Assessment Questions (JSON in DB)
```json
{
  "questions": [
    {
      "question": "What is Python?",
      "options": {
        "A": "A programming language",
        "B": "A snake",
        "C": "A type of car",
        "D": "A dance move"
      },
      "correct_answer": "A",
      "difficulty": "easy",
      "explanation": "Python is a programming language."
    }
  ]
}
```

### Roadmap Data (JSON in DB)
```json
{
  "chapters": [
    {
      "number": 1,
      "title": "Introduction to Python",
      "topics": ["Variables", "Data Types", "Print Statements"],
      "duration": 7,
      "resources": {
        "videos": ["https://youtube.com/..."],
        "documentation": ["https://python.org/..."],
        "tutorials": ["https://w3schools.com/..."]
      }
    }
  ],
  "duration_weeks": 12,
  "difficulty": "beginner"
}
```

### ChapterTest Questions (JSON in DB)
```json
{
  "questions": [
    {
      "question": "What is a variable?",
      "options": {
        "A": "A named container for data",
        "B": "A function",
        "C": "A loop",
        "D": "A class"
      },
      "correct_answer": "A"
    }
  ]
}
```

---

## 🔄 Common Modification Patterns

### Adding a New Course
```python
# In Django shell or management command
from courses.models import Course

Course.objects.create(
    title="Advanced Python",
    description="Learn advanced Python concepts",
    difficulty="advanced",
    duration_weeks=10
)
```

### Manually Setting Skill Level
```python
from assessments.models import Assessment

assessment = Assessment.objects.get(id=123)
assessment.percentage = 75.0
assessment.calculate_skill_level()  # Sets to 'intermediate'
assessment.save()
```

### Creating a User Programmatically
```python
from django.contrib.auth.models import User
from users.models import UserProfile

user = User.objects.create_user(
    username="john_doe",
    email="john@example.com",
    password="securepass123"
)
profile = UserProfile.objects.create(
    user=user,
    learning_duration_preference=12
)
```

### Querying User's Learning Progress
```python
from users.models import UserProfile
from learning.models import ChapterProgress, LearningActivity

user_profile = UserProfile.objects.get(user__email="user@example.com")
chapters = ChapterProgress.objects.filter(user=user_profile)
activities = LearningActivity.objects.filter(user=user_profile).order_by('-created_at')
```

---

## 🧪 Testing Endpoints with cURL

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123",
    "password2": "securepass123"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

### List Courses
```bash
curl http://127.0.0.1:8000/api/courses/list
```

### Generate Assessment Questions
```bash
curl -X POST http://127.0.0.1:8000/api/assessment/generate-questions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": 1}'
```

### Submit Assessment
```bash
curl -X POST http://127.0.0.1:8000/api/assessment/submit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": 123,
    "answers": {
      "0": "A",
      "1": "B",
      "2": "C",
      "3": "D",
      "4": "A"
    }
  }'
```

---

## 🔧 Configuration Changes

### Change OpenAI Model
**File**: `backend/config/settings.py` (line ~150)
```python
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4')
# Change default to 'gpt-3.5-turbo' or other model
```

### Change Database
**File**: `backend/config/settings.py` (lines 64-73)
```python
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='learnpath_db'),
        # ... other settings
    }
}
```

### Add CORS Origin
**File**: `backend/config/settings.py` (lines 168-176)
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Add your URL here
    # ... existing origins
]
```

### Enable Dynamic Resources
**File**: `.env`
```
USE_DYNAMIC_RESOURCES=true
SERPER_API_KEY=your_serper_key
YOUTUBE_API_KEY=your_youtube_key
```

---

## 📊 Database Queries (Django ORM)

### Get user with all related data
```python
from django.db.models import Prefetch
from users.models import UserProfile
from assessments.models import Roadmap

user_profile = UserProfile.objects.prefetch_related(
    'enrolled_courses',
    'assessments',
    Prefetch('roadmaps', Roadmap.objects.select_related('assessment'))
).get(user__email='user@example.com')
```

### Find assessments by skill level
```python
from assessments.models import Assessment

beginners = Assessment.objects.filter(skill_level='beginner')
intermediates = Assessment.objects.filter(skill_level='intermediate')
advanced = Assessment.objects.filter(skill_level='advanced')
```

### Get user's learning activity for past 7 days
```python
from datetime import timedelta
from django.utils import timezone
from learning.models import LearningActivity

seven_days_ago = timezone.now() - timedelta(days=7)
recent_activity = LearningActivity.objects.filter(
    user__user__email='user@example.com',
    created_at__gte=seven_days_ago
).order_by('-created_at')
```

### Calculate user progress percentage
```python
from django.db.models import Count, Q

user_profile = UserProfile.objects.get(id=1)
roadmap = user_profile.roadmaps.first()

total_chapters = roadmap.roadmap_data.get('chapters', []).__len__()
completed = roadmap.chapters.filter(status='completed').count()
progress_percent = (completed / total_chapters * 100) if total_chapters > 0 else 0
```

---

## 🐛 Common Issues & Solutions

### Issue: Assessment score not calculating correctly
**Solution**: Check `submit_assessment()` in `backend/assessments/views.py`
- Verify `answers` parameter format: `{"0": "A", "1": "B", ...}`
- Ensure `questions_data` is stored correctly during generation
- Check `calculate_skill_level()` logic in Assessment model

### Issue: JWT token not working
**Solution**: Check authentication in request
- Token must be in `Authorization: Bearer <token>` header
- Verify JWT_SECRET matches in settings
- Check token expiration (30 days from creation)

### Issue: Roadmap not generating
**Solution**: Check LLM service
- Verify OpenAI API key is set in `.env`
- Check `USE_DYNAMIC_RESOURCES` setting
- Verify course title is not empty
- Check fallback methods if API fails

### Issue: CORS errors on frontend
**Solution**: Check CORS settings
- Verify frontend URL is in `CORS_ALLOWED_ORIGINS`
- Check `CORS_ALLOW_CREDENTIALS = True`
- Ensure frontend sends correct headers

---

## 📈 Performance Tips

1. **Optimize DB queries**: Use `select_related()` and `prefetch_related()`
2. **Cache roadmaps**: Don't regenerate if exists for same assessment
3. **Paginate results**: Use DRF pagination for large datasets
4. **Lazy load chapters**: Load chapter content on demand, not all at once
5. **Cache OpenAI responses**: Store generated questions in DB, don't regenerate

---

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Change `SECRET_KEY` to random string
- [ ] Set up proper database credentials
- [ ] Configure OpenAI API key securely
- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Set up HTTPS
- [ ] Configure CORS for production frontend
- [ ] Set up logging and monitoring
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Use GuniCorn for serving: `gunicorn config.wsgi`

---

## 📚 File Index with Line Numbers

| File | Total Lines | Key Sections |
|------|------------|--------------|
| settings.py | ~200 | Database (63), REST (146), CORS (167) |
| users/models.py | ~18 | UserProfile |
| courses/models.py | ~38 | Course, UserCourse |
| assessments/models.py | ~57 | Assessment, Roadmap |
| learning/models.py | ~87 | ChapterProgress, ChapterTest, LearningActivity |
| assessments/views.py | 204 | All assessment endpoints |
| learning/views.py | 239 | All learning endpoints |
| assessments/llm_service.py | 442 | LLM integration |
| frontend/index.html | 298 | Main SPA |

---

**This guide assumes you're modifying existing code in the actual project.**  
**Always reference the PROJECT_ANALYSIS.md for detailed information.**
