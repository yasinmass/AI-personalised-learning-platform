# Final Setup & Running Instructions

## ✅ Current Status
Your LearnPath platform is **fully configured and ready to use**.

---

## 🚀 How to Run Everything

### Step 1: Start the Backend Server

Open PowerShell and run:
```powershell
cd "C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend"
python manage.py runserver
```

You should see:
```
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
Django version 4.2.8, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Backend running on: http://localhost:8000**

### Step 2: Open Frontend in Browser

The frontend is already running (Python simple HTTP server on port 8001)

Open your browser and go to:
```
http://localhost:8001
```

You should see the **LearnPath login page**.

---

## 🔐 Login Credentials

### Option 1: Use Admin Account (Recommended for Testing)
```
Email: admin@example.com
Password: admin123
```

### Option 2: Create New Account
Click **"Register"** and create a new account with any email/password.

---

## 🎓 Complete Feature Flow

### 1. **Login**
- Enter email and password
- Click "Login"
- You'll be redirected to home page

### 2. **View Available Courses**
- Click **"Courses"** in navbar
- You'll see 8 available courses:
  1. Python Programming Basics
  2. Artificial Intelligence & Machine Learning
  3. Full Stack Web Development
  4. Cloud Computing with AWS
  5. Data Science & Analytics
  6. DevOps & Container Technologies
  7. Cybersecurity Fundamentals
  8. Advanced JavaScript & Node.js

### 3. **Take Assessment**
- Click **"Start Course"** on any domain
- You'll get **10 multiple-choice questions** specific to that domain
- Each question has 4 options (A, B, C, D)
- Read the explanation for each question

### 4. **Submit Assessment**
- Answer all 10 questions
- Click **"Submit Assessment"**
- System calculates:
  - Your score (how many correct)
  - Your percentage
  - Your skill level (Beginner/Intermediate/Advanced/Expert)

### 5. **Generate Personalized Roadmap**
- On results page, enter **learning duration** (4-52 weeks, default 12)
- Click **"Generate Your Roadmap"**
- System creates a personalized 5-chapter learning path

### 6. **View Learning Path**
- See all 5 chapters:
  - Chapter 1: Introduction & Fundamentals
  - Chapter 2: Core Principles
  - Chapter 3: Practical Application
  - Chapter 4: Advanced Topics
  - Chapter 5: Mastery & Specialization
- Each chapter shows:
  - Topics to learn
  - Duration (in hours)
  - Recommended resources (links)
  - Checkpoints and milestones

### 7. **Explore Other Features**
- **Dashboard** - View your learning statistics
- **Profile** - Update your learning preferences
- **Logout** - Exit the platform

---

## 🛠️ Backend Technical Details

### Technologies Used
- **Python 3.13**
- **Django 4.2.8** - Web framework
- **Django REST Framework 3.14.0** - API
- **PostgreSQL** - Database
- **psycopg3** - PostgreSQL driver
- **PyJWT** - JWT token handling

### Database
- **Host**: localhost
- **Port**: 5432
- **Database**: learnpath_db
- **User**: postgres
- **Password**: postgres

### Key Endpoints
All endpoints require `Authorization: Bearer {token}` header (except login/register)

```
Authentication:
  POST /api/auth/register
  POST /api/auth/login
  GET /api/auth/profile
  PUT /api/auth/profile/update

Courses:
  GET /api/courses/list

Assessment:
  POST /api/assessment/generate-questions
  POST /api/assessment/submit
  POST /api/assessment/generate-roadmap
  GET /api/assessment/roadmaps
```

---

## 📊 Frontend Technical Details

### Technologies Used
- **HTML5** - Markup
- **CSS3** - Styling (with responsive design)
- **Vanilla JavaScript (ES6+)** - No frameworks!
- **Fetch API** - API communication

### Pages (8 total)
1. **loginPage** - Login & register forms
2. **homePage** - Welcome screen
3. **coursesPage** - Browse 8 available courses
4. **assessmentPage** - Take MCQ assessment
5. **resultsPage** - View score and generate roadmap
6. **learningPage** - View personalized learning path
7. **dashboardPage** - View statistics
8. **profilePage** - Edit user preferences

### Design Features
- ✅ Responsive (mobile, tablet, desktop)
- ✅ Coursera-inspired design
- ✅ Dark-themed UI
- ✅ Smooth animations
- ✅ Real-time form validation
- ✅ Clear error messages

---

## 🤖 LLM (AI) Integration

### How It Works
The platform can generate unique content using OpenAI's GPT-4 API.

### Current Mode: Fallback (No API Key Needed)
If you don't have an OpenAI API key, the system uses pre-generated content:
- ✅ 10 professionally written MCQ questions per domain
- ✅ 5-chapter personalized learning roadmap
- ✅ Realistic time allocations and resources

### Enable Live OpenAI API (Optional)
If you want truly unique, AI-generated content:

1. Get an API key from https://openai.com/api/
2. Create/edit `.env` file in backend folder:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4
   JWT_SECRET=your-jwt-secret
   
   DB_NAME=learnpath_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```
3. Restart backend: `python manage.py runserver`
4. Now each assessment will generate unique questions!

---

## 📚 Sample Data

### Pre-Loaded Courses
```
1. Python Programming Basics
   - Difficulty: Beginner
   - Duration: 12 weeks

2. Artificial Intelligence & Machine Learning
   - Difficulty: Intermediate
   - Duration: 14 weeks

3. Full Stack Web Development
   - Difficulty: Intermediate
   - Duration: 16 weeks

4. Cloud Computing with AWS
   - Difficulty: Intermediate
   - Duration: 10 weeks

5. Data Science & Analytics
   - Difficulty: Intermediate
   - Duration: 14 weeks

6. DevOps & Container Technologies
   - Difficulty: Advanced
   - Duration: 12 weeks

7. Cybersecurity Fundamentals
   - Difficulty: Intermediate
   - Duration: 13 weeks

8. Advanced JavaScript & Node.js
   - Difficulty: Advanced
   - Duration: 11 weeks
```

### Test Users
```
Admin User:
  Email: admin@example.com
  Password: admin123

Or create your own by registering
```

---

## ⚠️ Important Notes

### Backend Server Must Be Running
- Frontend on port 8001 needs API on port 8000
- If you see "Failed to fetch" errors, restart backend
- Check console logs (terminal) for errors

### PostgreSQL Must Be Running
- Database must be accessible on localhost:5432
- If database connection fails, start PostgreSQL service

### CORS Configuration
- Frontend: http://localhost:8001
- Backend: http://localhost:8000
- These are already configured and working

---

## 🔍 Monitoring & Debugging

### Backend Logs
Watch the terminal running `python manage.py runserver`:
```
[03/Dec/2025 12:00:00] "POST /api/auth/login HTTP/1.1" 200 300
[03/Dec/2025 12:00:01] "GET /api/courses/list HTTP/1.1" 200 2500
[03/Dec/2025 12:00:02] "POST /api/assessment/generate-questions HTTP/1.1" 200 1800
```

Status codes:
- **200** = Success ✅
- **201** = Created ✅
- **400** = Bad request ⚠️
- **401** = Unauthorized ⚠️
- **404** = Not found ⚠️
- **500** = Server error ❌

### Frontend Debugging
1. Open browser DevTools: **F12**
2. Go to **Console** tab for errors
3. Go to **Network** tab to see API calls
4. Check **Application > Local Storage** for auth token

---

## 🆘 Troubleshooting

### "Failed to fetch" Error
- ✅ Check backend is running (`python manage.py runserver`)
- ✅ Check backend is on http://localhost:8000
- ✅ Check frontend is on http://localhost:8001

### "User profile not found"
- Already fixed! Just login again

### Questions not showing
- Make sure you're logged in
- Click "Start Course" again
- Check browser console (F12) for errors

### Roadmap not generating
- Make sure you submitted the assessment
- Enter a valid duration (4-52 weeks)
- Check browser console for errors

### Database errors
- Make sure PostgreSQL is running
- Check database credentials in .env file

---

## 📖 Additional Resources

### Files to Read
1. **FEATURE_GUIDE.md** - Complete feature walkthrough
2. **TROUBLESHOOTING.md** - Common issues and solutions
3. **PROJECT_SUMMARY.md** - Technical summary

### Django Admin Panel (Optional)
Access at: http://localhost:8000/admin
- Username: admin
- Password: admin123 (default admin, may need to set)

---

## ✅ You're All Set!

Your LearnPath platform is ready to use:

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend ready on http://localhost:8001
3. ✅ Database connected and data loaded
4. ✅ Sample courses and users created
5. ✅ All features working (assessment, roadmap, dashboard, profile)

**Start here**: Open http://localhost:8001 in your browser and login!

---

## 🎓 Next Steps

1. **Try the complete flow**:
   - Login → Courses → Start Course → Take Assessment → Generate Roadmap

2. **Explore features**:
   - Check Dashboard for statistics
   - Update Profile preferences
   - Try different courses

3. **Optional enhancements**:
   - Add OpenAI API key for unique content
   - Customize questions and roadmap
   - Add more courses to database
   - Deploy to production

---

**Enjoy learning! 🚀**

