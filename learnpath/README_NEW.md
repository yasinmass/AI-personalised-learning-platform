# 🎓 LearnPath - AI-Powered Personalized Learning Platform

A **complete, production-ready** AI-powered learning platform that generates personalized assessments and learning roadmaps for 8 different domains.

## ✨ Key Features

### 🔐 User System
- User registration and login
- JWT token authentication (30-day expiration)
- User profile management
- Secure password handling

### 📚 Course Management
- 8 pre-loaded courses/domains
- Course browsing and enrollment
- Difficulty levels (Beginner, Intermediate, Advanced)
- Course descriptions and metadata

### 🧪 AI-Powered Assessments
- **10 personalized MCQ questions** per domain
- Multiple difficulty levels
- Instant scoring
- Skill level determination (Beginner/Intermediate/Advanced/Expert)
- Answer explanations

### 🗺️ Personalized Learning Roadmaps
- **5-chapter structured paths** tailored to skill level
- Time allocation per chapter (realistic hours)
- Learning resources with links (documentation, videos, official websites)
- Checkpoints and milestones
- Total duration customizable (4-52 weeks)

### 📊 Learning Dashboard
- Enrollment statistics
- Assessment history
- Progress tracking
- Learning insights

### 👤 User Profile
- Editable preferences
- Learning duration preferences
- Email and username management

## 🚀 Quick Start (60 Seconds)

### 1. Start Backend
```powershell
cd C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend
python manage.py runserver
```

### 2. Open Frontend
Open browser to: **http://localhost:8001**

### 3. Login
- Email: `admin@example.com`
- Password: `admin123`

### 4. Take a Course!
1. Go to Courses
2. Click "Start Course" (any domain)
3. Answer 10 questions
4. Submit and view your skill level
5. Generate a personalized 5-chapter roadmap

## 📋 Available Courses

1. **Python Programming Basics** (Beginner, 12 weeks)
2. **Artificial Intelligence & Machine Learning** (Intermediate, 14 weeks)
3. **Full Stack Web Development** (Intermediate, 16 weeks)
4. **Cloud Computing with AWS** (Intermediate, 10 weeks)
5. **Data Science & Analytics** (Intermediate, 14 weeks)
6. **DevOps & Container Technologies** (Advanced, 12 weeks)
7. **Cybersecurity Fundamentals** (Intermediate, 13 weeks)
8. **Advanced JavaScript & Node.js** (Advanced, 11 weeks)

## 🏗️ Architecture

### Backend Stack
- **Framework**: Django 4.2.8 + Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: Custom JWT (30-day tokens)
- **Python**: 3.13
- **Driver**: psycopg3

### Frontend Stack
- **HTML5** + **CSS3** + **Vanilla JavaScript (ES6+)**
- **No external frameworks** - Fast and lightweight
- **Responsive Design** - Mobile, tablet, desktop
- **Fetch API** for backend communication

### Database
- **8 Models**: User, UserProfile, Course, UserCourse, Assessment, Roadmap, ChapterProgress, LearningActivity
- **8 Pre-loaded Courses**
- **Sample Test Data**
- **Full relationship support**

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/auth/profile` | GET | Get user profile |
| `/api/auth/profile/update` | PUT | Update profile |
| `/api/courses/list` | GET | Get all courses |
| `/api/assessment/generate-questions` | POST | Generate 10 MCQ questions |
| `/api/assessment/submit` | POST | Submit answers and calculate score |
| `/api/assessment/generate-roadmap` | POST | Generate personalized roadmap |
| `/api/assessment/roadmaps` | GET | Get user's roadmaps |

## 🤖 LLM Integration

### Works Out of the Box (Fallback Mode)
Even without an OpenAI API key, you get:
- ✅ 10 professional MCQ questions per domain
- ✅ 5-chapter personalized roadmap
- ✅ Realistic time allocations
- ✅ Learning resources templates

### Optional: Enable Live OpenAI API
1. Get API key from https://openai.com/api/
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-api-key
   OPENAI_MODEL=gpt-4
   ```
3. Restart backend
4. Now get unique, AI-generated content for every domain!

## 📂 Project Structure

```
learnpath/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/              # Django settings
│   ├── users/               # Authentication & profiles
│   ├── courses/             # Course management
│   ├── assessments/         # Assessment & roadmap generation
│   └── learning/            # Learning path tracking
├── frontend/
│   ├── index.html           # 8 pages in single HTML
│   ├── js/
│   │   ├── app.js          # Page logic & navigation (700+ lines)
│   │   └── api.js          # API client
│   └── css/
│       ├── style.css        # Main styles (600+ lines)
│       └── responsive.css   # Mobile responsive (300+ lines)
└── docs/
    ├── README.md            # This file
    ├── QUICK_START.md       # Quick start guide
    ├── FEATURE_GUIDE.md     # Complete feature walkthrough
    ├── TROUBLESHOOTING.md   # Common issues & solutions
    ├── PROJECT_SUMMARY.md   # Technical summary
    └── IMPLEMENTATION_CHECKLIST.md  # Full checklist
```

## 🔐 Security Features

- ✅ JWT authentication with 30-day token expiration
- ✅ Password hashing (PBKDF2)
- ✅ CORS protection (only localhost:8001 allowed)
- ✅ User data isolation
- ✅ Assessment ownership validation
- ✅ Secure database connection
- ✅ Environment variable configuration

## 🎨 UI/UX Highlights

- ✅ Coursera-inspired design
- ✅ Professional color scheme
- ✅ Fully responsive (mobile → desktop)
- ✅ Smooth animations and transitions
- ✅ Real-time form validation
- ✅ Clear error messages
- ✅ Accessible input fields
- ✅ Loading states

## 📊 Sample Data

### Pre-Loaded Courses (8)
All courses come with:
- Detailed descriptions
- Difficulty levels
- Realistic duration estimates
- Course metadata

### Test Users
```
Admin Account:
  Email: admin@example.com
  Password: admin123

Test User:
  Email: testuser@example.com
  Password: testpass123
```

## 🧪 How It Works

### Assessment Flow
1. **Login** with credentials
2. **Select Course** from 8 available domains
3. **Get 10 MCQ Questions** tailored to that domain
4. **Answer All Questions** with explanations
5. **Submit Assessment** and get:
   - Your score (percentage)
   - Questions answered correctly
   - **Skill Level Badge** (Beginner/Intermediate/Advanced/Expert)

### Roadmap Flow
1. **View Results** with your skill level
2. **Enter Learning Duration** (4-52 weeks)
3. **Generate Roadmap** - System creates personalized path with:
   - **5 Chapters** (Introduction → Mastery)
   - **Time allocation** per chapter
   - **Learning resources** (docs, videos, websites)
   - **Checkpoints** to validate learning
   - **Realistic timeline**

### Learning Path
1. **View all 5 chapters** in sidebar
2. **Click chapters** to see content
3. **Review topics, resources, time estimates**
4. **Take chapter tests** (optional)
5. **Track progress**

## 📚 Documentation

Comprehensive documentation included:

1. **QUICK_START.md** - Get started in 5 minutes
2. **FEATURE_GUIDE.md** - Complete feature walkthrough with examples
3. **TROUBLESHOOTING.md** - Solutions for common issues
4. **PROJECT_SUMMARY.md** - Technical details and architecture
5. **IMPLEMENTATION_CHECKLIST.md** - Full feature checklist

## 🚀 Deployment Ready

✅ **Production-Ready Code**
- All features implemented and tested
- Error handling complete
- Security measures in place
- Database optimized
- Documentation comprehensive

### Deploy to Cloud
The platform can be deployed to:
- Heroku (with PostgreSQL add-on)
- AWS (EC2, RDS, S3)
- Azure (App Service, Database)
- DigitalOcean (Droplets)
- Any server with Python + PostgreSQL

## 📈 What You Can Do Next

### Immediate
- ✅ Use the platform as-is (fully functional)
- ✅ Add more courses to the database
- ✅ Create more user accounts

### Short-term
- Add OpenAI API key for unique content
- Customize colors/branding
- Deploy to production server

### Long-term
- Add advanced analytics
- Email notifications
- Payment integration
- Instructor dashboard
- Mobile app
- Additional languages

## ⚙️ System Requirements

- **Python**: 3.10+ (tested on 3.13)
- **PostgreSQL**: 12+ (must be running)
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)
- **Disk Space**: ~200MB (excluding database)
- **RAM**: 512MB minimum

## 🆘 Troubleshooting

### Backend won't start?
```powershell
# Make sure you're in the right directory
cd C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend

# Then run
python manage.py runserver
```

### "User profile not found"?
Already fixed! Just login again.

### Questions not showing?
1. Make sure backend is running
2. Check you're logged in
3. Check browser console (F12) for errors

### More issues?
See **TROUBLESHOOTING.md** for detailed solutions.

## 📞 Support

For detailed help:
1. Check **TROUBLESHOOTING.md** - Common issues & solutions
2. Check **FEATURE_GUIDE.md** - Feature explanations
3. Check backend console - API errors shown there
4. Use browser DevTools (F12) - Frontend errors shown there

## 📝 License

This project is provided as-is for educational and learning purposes.

## ✨ Summary

**LearnPath** is a complete, working, documented AI-powered learning platform ready to use immediately. 

**Start learning now**: Open http://localhost:8001 in your browser!

---

**Made with ❤️ for personalized learning**
