# 🚀 Complete Setup & Run Guide

## Step 1: Backend Setup

### 1.1 Create Virtual Environment
```powershell
cd "c:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend"
python -m venv venv
.\venv\Scripts\activate
```

### 1.2 Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.3 Create .env File
Create a file called `.env` in the `backend/` folder with:
```
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=localhost
DATABASE_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

**IMPORTANT**: Get your OpenAI API key from https://platform.openai.com/api-keys

### 1.4 Run Database Migrations
```powershell
python manage.py migrate
```

### 1.5 Create Superuser (Admin)
```powershell
python manage.py createsuperuser
# Follow the prompts to create admin account
```

### 1.6 Load Sample Courses
```powershell
python manage.py create_initial_data
```

### 1.7 Start Backend Server
```powershell
python manage.py runserver
```

The backend will be running at: **http://localhost:8000**

---

## Step 2: Frontend Setup

### 2.1 Open a New Terminal/PowerShell Window
Keep the backend running in the first terminal!

### 2.2 Navigate to Frontend
```powershell
cd "c:\Users\Yasin\OneDrive\Desktop\ag\learnpath\frontend"
```

### 2.3 Start a Local Server
```powershell
python -m http.server 8001
```

Or if you have Node.js installed:
```powershell
npx http-server -p 8001
```

The frontend will be running at: **http://localhost:8001**

---

## Step 3: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8001
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

---

## 📋 Quick Checklist

### Backend Terminal (Terminal 1)
- [ ] Virtual environment activated (`.\venv\Scripts\activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Sample data loaded (`python manage.py create_initial_data`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Console shows: "Starting development server at http://127.0.0.1:8000/"

### Frontend Terminal (Terminal 2)
- [ ] Navigated to frontend folder
- [ ] Server started (`python -m http.server 8001`)
- [ ] Console shows: "Serving HTTP on 0.0.0.0 port 8001"

### Browser
- [ ] Can access http://localhost:8001 (Frontend loads)
- [ ] Can access http://localhost:8000 (Backend API works)
- [ ] Can access http://localhost:8000/admin (Admin panel loads)

---

## 🧪 Test the Application

### 1. Register a New Account
- Go to http://localhost:8001
- Click "Register"
- Fill in: Email, Password, Confirm Password
- Click "Register"

### 2. Login
- Go to login page
- Use your registered credentials
- Click "Login"

### 3. Select a Course
- Click "Courses" in navigation
- Choose a course
- Click "Enroll"

### 4. Take Assessment
- Click "Take Assessment"
- Answer 10 MCQ questions
- Click "Submit"

### 5. Generate Roadmap
- After assessment, click "Generate Learning Path"
- System creates personalized roadmap
- View your custom learning path

### 6. View Dashboard
- Click "Dashboard"
- See your progress, time spent, weak areas
- View performance metrics

---

## ⚠️ Troubleshooting

### Issue: "Port already in use"
```powershell
# Change the port
python manage.py runserver 8080
# Or kill the process using the port
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "No module named 'django'"
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate
# Then reinstall
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not set"
- Check your `.env` file exists in backend folder
- Add your API key: `OPENAI_API_KEY=sk-your-key`
- Restart the server

### Issue: "Database locked"
```powershell
# Delete the database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py create_initial_data
```

### Issue: "CORS errors in browser console"
- Make sure backend is running on 8000
- Make sure frontend is running on 8001
- Backend CORS is configured to allow localhost

### Issue: Frontend doesn't connect to backend
- Check both servers are running
- Open browser console (F12)
- Check for error messages
- Make sure API calls use `http://localhost:8000`

---

## 🎯 Terminal Commands Summary

### Backend (Terminal 1)
```powershell
# Navigate
cd "c:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend"

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Load sample data
python manage.py create_initial_data

# Start server
python manage.py runserver
```

### Frontend (Terminal 2)
```powershell
# Navigate
cd "c:\Users\Yasin\OneDrive\Desktop\ag\learnpath\frontend"

# Start server
python -m http.server 8001
```

---

## 📊 What's Running

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:8001 | Web Interface |
| **Backend API** | http://localhost:8000 | REST API |
| **Admin Panel** | http://localhost:8000/admin | Manage data |

---

## 🔐 Default Credentials

After running `python manage.py createsuperuser`:
- **Admin URL**: http://localhost:8000/admin
- **Username**: (whatever you entered)
- **Password**: (whatever you entered)

Sample courses are loaded automatically.

---

## 📈 Sample Courses Loaded

1. Python Programming Basics (Beginner)
2. AI & Machine Learning (Intermediate)
3. Full Stack Web Development (Intermediate)
4. Cloud Computing with AWS (Intermediate)
5. Data Science & Analytics (Intermediate)
6. DevOps & Container Technologies (Advanced)
7. Cybersecurity Fundamentals (Intermediate)
8. Advanced JavaScript & Node.js (Advanced)

---

## 🔧 Environment Setup Details

### Virtual Environment
- **Location**: `backend/venv/`
- **Python Version**: 3.8+
- **Activation**: `.\venv\Scripts\activate`

### Database
- **Type**: SQLite (development)
- **File**: `backend/db.sqlite3`
- **For Production**: Switch to PostgreSQL

### Dependencies
See `requirements.txt` for all packages:
- Django 4.2
- Django REST Framework
- OpenAI API
- python-decouple
- django-cors-headers
- PyJWT

---

## 📚 Documentation References

- **README.md** - Complete technical documentation
- **QUICKSTART.md** - Quick setup guide
- **ARCHITECTURE.md** - System design & diagrams
- **IMPLEMENTATION_SUMMARY.md** - Feature checklist

---

## ✅ Success Indicators

You'll know everything is working when:

✅ Backend server shows: `Starting development server at http://127.0.0.1:8000/`
✅ Frontend server shows: `Serving HTTP on 0.0.0.0 port 8001`
✅ Browser loads http://localhost:8001
✅ Can register a new account
✅ Can login successfully
✅ Can see courses on dashboard
✅ Can take assessment
✅ Can generate learning roadmap
✅ Can view dashboard with analytics

---

## 🚀 Next Steps

1. **Complete Setup** - Follow steps 1-3 above
2. **Test All Features** - Use the test checklist
3. **Customize** - Update colors, courses, content
4. **Deploy** - When ready for production

---

## 💡 Tips

- Keep both terminals open while developing
- Check terminal output for errors
- Use Django admin (http://localhost:8000/admin) to manage courses
- Use browser F12 console to debug frontend issues
- Never commit `.env` file to Git

---

**Ready to go! Follow the steps above and you'll be running in 5 minutes! 🎉**
