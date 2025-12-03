# LearnPath - Complete Feature Guide

## ✅ System Status

Your AI-powered personalized learning platform is now **fully functional**! Here's what's working:

---

## 🚀 Quick Start

### 1. **Login/Register**
- **URL**: `http://localhost:8001`
- **Admin Credentials**:
  - Email: `admin@example.com`
  - Password: `admin123`
- **Or Register** a new account with any email

### 2. **Available Courses** (8 domains)
1. Python Programming Basics
2. Artificial Intelligence & Machine Learning
3. Full Stack Web Development
4. Cloud Computing with AWS
5. Data Science & Analytics
6. DevOps & Container Technologies
7. Cybersecurity Fundamentals
8. Advanced JavaScript & Node.js

---

## 📚 Complete Feature Flow

### **Feature 1: Take Assessment & Get MCQ Questions**
1. Go to **Courses** page
2. Click **"Start Course"** on any domain
3. System generates **10 personalized MCQ questions** based on the domain
4. Answer all questions and click **"Submit Assessment"**
5. Your skill level is calculated: **Beginner | Intermediate | Advanced | Expert**

### **Feature 2: Generate Personalized Roadmap**
1. After submitting assessment, you're shown your **results page**
2. Enter **learning duration** (4-52 weeks, default 12)
3. Click **"Generate Your Roadmap"**
4. System creates a **customized learning path** with:
   - 5 chapters tailored to your skill level
   - Time allocation per chapter
   - Learning resources (documentation, videos, official websites)
   - Checkpoints and milestones
   - **Total duration**: Your weeks × 8 hours/week

### **Feature 3: Learning Path & Chapter Content**
1. View generated **roadmap on Learning page**
2. **5 chapters** structured progressively:
   - Chapter 1: Introduction & Fundamentals
   - Chapter 2: Core Principles
   - Chapter 3: Practical Application
   - Chapter 4: Advanced Topics
   - Chapter 5: Mastery & Specialization
3. Click each chapter to view:
   - Topics to cover
   - Duration (hours)
   - Learning resources with links
   - Checkpoints/milestones
4. Take **chapter tests** for each section

### **Feature 4: User Profile**
1. Go to **Profile** page
2. View your:
   - Email address
   - Username
   - Learning duration preference
3. Update your learning duration preference
4. Saved preferences used for future roadmaps

### **Feature 5: Dashboard**
1. View your **learning overview**:
   - Total courses enrolled
   - Total assessments taken
   - Courses in progress
   - Courses completed
2. Track your **learning statistics**

---

## 🔧 Backend API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile/update` - Update profile

### Courses
- `GET /api/courses/list` - Get all courses
- `POST /api/courses/enroll` - Enroll in course
- `GET /api/courses/{id}` - Get course details

### Assessments
- `POST /api/assessment/generate-questions` - Generate 10 MCQ questions
- `POST /api/assessment/submit` - Submit answers & calculate score
- `POST /api/assessment/generate-roadmap` - Generate learning roadmap
- `GET /api/assessment/roadmaps` - Get user's roadmaps

### Learning
- `GET /api/learning/chapters` - Get course chapters
- `POST /api/learning/chapter-test` - Submit chapter test
- `GET /api/learning/progress` - Get learning progress

---

## 💾 Database

**PostgreSQL** with 8 models:
- `User` - Django built-in auth
- `UserProfile` - Custom user preferences
- `Course` - Learning domains (8 pre-loaded)
- `UserCourse` - Course enrollments
- `Assessment` - Assessment records with questions & scores
- `Roadmap` - Personalized learning paths
- `ChapterProgress` - Chapter completion tracking
- `LearningActivity` - Learning activity logs

---

## 🤖 LLM Integration

### Current Setup
- **OpenAI API** (optional) - If you add an API key in `.env`
- **Fallback Mode** (active) - Comprehensive pre-generated content

### What the LLM Does
1. **Generates Assessment Questions** - 10 domain-specific MCQ questions
2. **Creates Roadmaps** - Personalized 5-chapter learning paths based on skill level
3. **Generates Chapter Tests** - Quick validation questions
4. **Adaptive Recommendations** - Suggests improvements based on weak areas

### Fallback Questions (No API Key Needed)
- 10 professionally written questions per domain
- Covers fundamentals, benefits, prerequisites, application, challenges, mastery
- Difficulty levels: Easy, Medium, Hard

### Fallback Roadmap (No API Key Needed)
- 5 comprehensive chapters
- Realistic time allocation (weeks × 8 hours)
- Learning resources templates
- Structured progression from basics to mastery

---

## 🎨 Frontend Features

### Pages
1. **Login/Register** - User authentication
2. **Home** - Welcome and quick links
3. **Courses** - Browse 8 available domains
4. **Assessment** - Take MCQ test
5. **Results** - View score and roadmap options
6. **Learning Path** - View roadmap and take chapter tests
7. **Dashboard** - Learning statistics
8. **Profile** - User preferences

### Responsive Design
- ✅ Desktop optimized
- ✅ Tablet friendly
- ✅ Mobile responsive (hamburger menu)
- ✅ Accessible forms and inputs
- ✅ Real-time error messages

---

## 📊 Sample Data Pre-Loaded

### 8 Courses with Descriptions
```
1. Python Programming Basics (Beginner, 12 weeks)
2. Artificial Intelligence & Machine Learning (Intermediate, 14 weeks)
3. Full Stack Web Development (Intermediate, 16 weeks)
4. Cloud Computing with AWS (Intermediate, 10 weeks)
5. Data Science & Analytics (Intermediate, 14 weeks)
6. DevOps & Container Technologies (Advanced, 12 weeks)
7. Cybersecurity Fundamentals (Intermediate, 13 weeks)
8. Advanced JavaScript & Node.js (Advanced, 11 weeks)
```

### Test Users
```
Admin Account:
- Email: admin@example.com
- Password: admin123

Test User:
- Email: testuser@example.com
- Password: testpass123
```

---

## 🚀 How to Use

### Step 1: Start the Backend
```powershell
cd C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend
python manage.py runserver
```
Backend runs on: `http://localhost:8000`

### Step 2: Frontend Already Running
Open browser to: `http://localhost:8001`

### Step 3: Login & Test
1. Login with `admin@example.com / admin123`
2. Go to **Courses**
3. Click **"Start Course"** (any domain)
4. Answer 10 questions
5. Submit assessment
6. Set learning duration (e.g., 12 weeks)
7. Click **"Generate Your Roadmap"**
8. View your personalized 5-chapter learning path!

---

## 🔐 Security Features

✅ JWT token authentication  
✅ Password hashing (Django)  
✅ CORS protection (port 8001 only)  
✅ User profile isolation  
✅ Assessment ownership validation  

---

## 📈 Next Steps (Optional Enhancements)

### To Enable Live OpenAI Integration
1. Get API key from https://openai.com/api/
2. Add to `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4
   ```
3. Restart backend
4. Now LLM will generate unique questions/roadmaps per domain

### To Add More Domains
1. Add courses in Django admin or via:
   ```
   python manage.py shell
   >>> from courses.models import Course
   >>> Course.objects.create(title="Your Domain", description="...", difficulty="beginner", duration_weeks=12)
   ```

### To Customize Questions/Roadmaps
1. Edit `backend/assessments/llm_service.py`
2. Modify fallback content or add custom prompts
3. Restart backend

---

## ✨ You're All Set!

Your complete AI-powered personalized learning platform is ready to use. Start learning by picking a domain and getting your personalized roadmap today! 🎓

For issues or questions, check backend logs:
- Django dev server shows request logs
- Use browser DevTools (F12) Network tab to debug API calls

