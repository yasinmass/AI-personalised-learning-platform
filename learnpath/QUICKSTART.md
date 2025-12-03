# Quick Start Guide

Get LearnPath up and running in 5 minutes!

## Step 1: Backend Setup (3 minutes)

### Windows PowerShell
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Configure Database & API Key
Edit `.env`:
```
OPENAI_API_KEY=sk-your-openai-key
DB_USER=postgres
DB_PASSWORD=your-db-password
```

### Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### Start Backend
```bash
python manage.py runserver
```
✅ Backend runs on `http://localhost:8000`

## Step 2: Frontend Setup (1 minute)

### Option A: Direct File Access
1. Open `frontend/index.html` in your browser
2. Update `API_BASE_URL` in `js/app.js` if needed

### Option B: Local Server
```bash
cd frontend
python -m http.server 8001
```
Then open `http://localhost:8001` in browser

✅ Frontend is ready!

## Step 3: Test the Application (1 minute)

1. **Register** a new account
2. **Login** with your credentials
3. **Select a Course** from the available options
4. **Take Assessment** (10 questions)
5. **View Results** and set learning duration
6. **Generate Roadmap** to see personalized learning path

## Default Courses to Add (via Django Admin)

1. Go to `http://localhost:8000/admin`
2. Login with superuser credentials
3. Add these courses:

```
Title: AI & Machine Learning
Description: Master AI and ML fundamentals
Difficulty: Beginner
Duration: 12 weeks

Title: Full Stack Web Development
Description: Complete guide to web development
Difficulty: Intermediate
Duration: 16 weeks

Title: Cloud Computing with AWS
Description: Learn AWS services and deployment
Difficulty: Intermediate
Duration: 10 weeks

Title: Data Science Mastery
Description: Data analysis and visualization
Difficulty: Intermediate
Duration: 14 weeks
```

## API Testing with cURL

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Get Courses
```bash
curl http://localhost:8000/api/courses/list
```

## Troubleshooting

### Port Already in Use
```bash
# Windows: Find process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux: Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
# Verify DB credentials in .env
python manage.py dbshell
```

### CORS Error in Browser
- Ensure backend is running
- Check `CORS_ALLOWED_ORIGINS` in `config/settings.py`
- Verify frontend and backend URLs match

### OpenAI API Error
- Verify API key in `.env`
- Check API quota and billing
- Test with: `python -c "import openai; print(openai.__version__)"`

## Next Steps

1. **Add More Courses**: Use Django admin interface
2. **Customize Styling**: Modify `css/style.css`
3. **Extend Features**: Add new endpoints in `<app>/views.py`
4. **Deploy**: See [Deployment Guide](DEPLOYMENT.md)
5. **Monitor**: Check logs and usage analytics

## Important Notes

⚠️ **Before Production**:
- Change `DEBUG=False` in `.env`
- Use strong `SECRET_KEY`
- Configure allowed hosts
- Set up HTTPS/SSL
- Use environment variables for secrets
- Enable rate limiting
- Set up proper logging

💡 **Tips**:
- Keep `.env` out of version control
- Use `.env.example` as template
- Regularly update dependencies
- Monitor OpenAI API costs
- Backup PostgreSQL regularly

## Support

For detailed documentation, see [README.md](README.md)

**You're all set!** 🚀

Need help? Check the troubleshooting section above or refer to full documentation.
