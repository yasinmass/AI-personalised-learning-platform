# Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Issue 1: Backend Server Won't Start
```
Error: "can't open file 'manage.py'"
```
**Solution**: Make sure you're in the correct directory
```powershell
cd C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend
python manage.py runserver
```

### Issue 2: "ModuleNotFoundError: No module named 'rest_framework'"
```
Error occurs when running manage.py
```
**Solution**: Virtual environment not activated. The backend should auto-use the venv.

### Issue 3: Login Shows "User profile not found"
```
Error when trying to start assessment after login
```
**Solution**: User's UserProfile wasn't created. Already fixed in code, but if you see this:
```powershell
python manage.py shell
>>> from users.models import UserProfile
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(email='your-email@example.com')
>>> UserProfile.objects.create(user=user)
```

### Issue 4: Assessment Shows "undefined" Error
```
Error: "Error generating questions: undefined"
```
**Solution**: Token not being sent. Already fixed. Refresh browser and login again.

### Issue 5: Roadmap Not Generating
```
Button doesn't work after submitting assessment
```
**Solutions**:
1. Make sure you submitted the assessment (got results page)
2. Enter a valid duration (4-52 weeks)
3. Click button again
4. Check browser DevTools Console (F12) for errors

### Issue 6: Assessment Questions Not Showing
```
Empty assessment page after clicking "Start Course"
```
**Solutions**:
1. Make sure you're logged in
2. Make sure the course exists in database
3. Check browser console for errors
4. Try refreshing the page

### Issue 7: Profile Page Shows No Data
```
Input fields are empty on Profile page
```
**Solution**: The loadProfile() function is now called automatically when navigating to Profile. Already fixed.

### Issue 8: CORS Error
```
Error: "Access to fetch... blocked by CORS policy"
```
**Solution**: CORS is already configured for localhost:8001. If you see this:
1. Make sure frontend is on http://localhost:8001 (not 127.0.0.1:8001)
2. Backend must be running on http://localhost:8000
3. Restart both servers

### Issue 9: Database Connection Failed
```
Error: "could not connect to server... No such file or directory"
```
**Solution**: PostgreSQL must be running
```powershell
# On Windows, start PostgreSQL service
Get-Service postgresql-x64-* | Start-Service
```

### Issue 10: Token Expired (after 30 days)
```
Error: "Token has expired"
```
**Solution**: Login again to get a new token. Token is valid for 30 days.

---

## 🔍 Debugging Steps

### Step 1: Check Backend is Running
```powershell
curl http://localhost:8000/api/courses/list
# Should return 200 with course data
```

### Step 2: Check Frontend can Reach Backend
```
Open browser Console (F12) > Network tab
Click "Start Course" button
Look for request to http://localhost:8000/api/assessment/generate-questions
Check if Status is 200 or 401 (401 = needs auth, but request reached server)
```

### Step 3: Verify Token is Sent
```
In browser Console:
localStorage.getItem('authToken')
# Should show a long string like: eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Step 4: Check Backend Logs
```
Look at terminal running "python manage.py runserver"
Should show:
[03/Dec/2025 11:22:45] "POST /api/assessment/generate-questions HTTP/1.1" 200 1234
(200 = success, 401 = auth needed, 404 = endpoint not found, 500 = server error)
```

### Step 5: Enable Verbose Logging
Edit `backend/config/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

---

## 📝 Reset Everything (Start Fresh)

### Reset Database
```powershell
cd C:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend

# Delete database
rm db.sqlite3

# Recreate tables
python manage.py migrate

# Load sample data
python manage.py create_initial_data
python manage.py create_admin
```

### Reset Frontend Cache
```
Open browser DevTools (F12)
Application tab > Storage > Local Storage > http://localhost:8001
Click "Clear All"
```

---

## 📚 Database Queries (Admin Commands)

### Count Courses
```powershell
python manage.py shell
>>> from courses.models import Course
>>> Course.objects.count()
```

### Check User Profiles
```powershell
python manage.py shell
>>> from users.models import UserProfile
>>> UserProfile.objects.all()
```

### View Assessments
```powershell
python manage.py shell
>>> from assessments.models import Assessment
>>> Assessment.objects.all().values('id', 'user__user__email', 'score', 'skill_level')
```

### View Roadmaps
```powershell
python manage.py shell
>>> from assessments.models import Roadmap
>>> Roadmap.objects.all()
```

---

## 🆘 Still Having Issues?

1. **Check logs**: Look at terminal output when making requests
2. **Check browser console**: F12 > Console tab
3. **Check network**: F12 > Network tab, look at request/response
4. **Restart everything**: Stop and start backend and frontend
5. **Clear cache**: Clear localStorage and browser cache
6. **Fresh database**: Run reset commands above

---

## 📞 Quick Reference

| Component | URL | Status |
|-----------|-----|--------|
| Frontend | http://localhost:8001 | ✅ Running |
| Backend API | http://localhost:8000/api | ✅ Running |
| Admin Panel | http://localhost:8000/admin | ✅ Available |
| Database | PostgreSQL localhost:5432 | ✅ Running |

| Credentials | Value |
|-------------|-------|
| Admin Email | admin@example.com |
| Admin Password | admin123 |
| DB User | postgres |
| DB Password | postgres |

