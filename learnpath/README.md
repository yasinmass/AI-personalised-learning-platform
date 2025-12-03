# LearnPath - AI Personalized Learning Platform

An intelligent, AI-powered learning platform that personalizes the educational experience for each user based on their skill level and learning pace.

## Features

- **User Authentication**: Secure login/registration with JWT tokens
- **AI-Powered Assessment**: Generates 10 MCQ questions to assess current skill level
- **Personalized Roadmaps**: LLM generates customized learning paths based on assessment results
- **Learning Management**: Track progress, chapters, and time spent
- **Chapter Tests**: Auto-generated assessments at the end of each chapter
- **Adaptive Learning**: Roadmap adjusts based on weak areas identified in tests
- **Dashboard Analytics**: View progress, performance metrics, and learning activity
- **Resource Curation**: Links to YouTube tutorials, documentation, and official websites
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Coursera-style UI**: Modern, professional interface inspired by leading e-learning platforms

## Tech Stack

### Frontend
- HTML5
- CSS3 (with responsive design)
- Vanilla JavaScript (ES6+)

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL
- OpenAI API (GPT-4)
- JWT Authentication

## Project Structure

```
learnpath/
├── backend/
│   ├── config/              # Django project settings
│   ├── users/               # User authentication & profiles
│   ├── courses/             # Course management
│   ├── assessments/         # Assessment & roadmap generation
│   ├── learning/            # Learning progress tracking
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html           # Main HTML file
    ├── css/
    │   ├── style.css        # Main styles
    │   └── responsive.css   # Mobile responsive styles
    └── js/
        ├── app.js           # Main application logic
        └── api.js           # API client helper
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (optional, for serving frontend)
- PostgreSQL
- OpenAI API Key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   copy .env.example .env  # On Windows
   cp .env.example .env    # On macOS/Linux
   ```
   
   Edit `.env` and configure:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=learnpath_db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb learnpath_db  # On macOS/Linux
   # Or use pgAdmin on Windows
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional, for admin panel)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load initial course data (optional)**
   ```bash
   python manage.py loaddata courses  # If fixtures are provided
   ```

9. **Start development server**
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Start a local server** (optional, you can open index.html directly)
   ```bash
   # Using Python
   python -m http.server 8001
   
   # Using Node.js http-server
   npx http-server
   ```

3. **Open in browser**
   - Open `index.html` or navigate to `http://localhost:8001`
   - Update `API_BASE_URL` in `js/app.js` if backend runs on different port

## API Documentation

### Authentication Endpoints

```
POST /api/auth/register
- Register new user
- Body: { email, username, password, password2, first_name, last_name }

POST /api/auth/login
- Login user
- Body: { email, password }
- Returns: { token, user }

GET /api/auth/profile
- Get user profile (requires auth)

PUT /api/auth/profile/update
- Update user profile (requires auth)
- Body: { learning_duration_preference }
```

### Course Endpoints

```
GET /api/courses/list
- Get all available courses

GET /api/courses/{id}
- Get specific course details

POST /api/courses/{id}/enroll
- Enroll in course (requires auth)

GET /api/courses/my-courses
- Get user's enrolled courses (requires auth)
```

### Assessment Endpoints

```
POST /api/assessment/generate-questions
- Generate 10 MCQ questions for assessment
- Body: { course_id }
- Returns: { assessment_id, questions }

POST /api/assessment/submit
- Submit assessment answers
- Body: { assessment_id, answers }
- Returns: { score, percentage, skill_level }

POST /api/assessment/generate-roadmap
- Generate personalized learning roadmap
- Body: { assessment_id, duration_weeks }
- Returns: { roadmap with chapters and resources }

GET /api/assessment/my-roadmaps
- Get all user's roadmaps (requires auth)
```

### Learning Endpoints

```
GET /api/learning/chapters/{roadmap_id}
- Get chapters of a roadmap (requires auth)

POST /api/learning/track-progress
- Update chapter progress (requires auth)
- Body: { roadmap_id, chapter_number, status, time_spent_minutes }

POST /api/learning/chapter-test/generate
- Generate chapter test (requires auth)
- Body: { roadmap_id, chapter_number }
- Returns: { test_id, questions }

POST /api/learning/chapter-test/submit
- Submit chapter test (requires auth)
- Body: { test_id, answers }
- Returns: { score, percentage }

GET /api/learning/dashboard/{roadmap_id}
- Get learning dashboard data (requires auth)
- Returns: { progress, performance, weak_areas, recent_activity }
```

## Usage Guide

### For Users

1. **Register/Login**
   - Create account or login with credentials

2. **Select Course**
   - Browse available courses and click "Start Course"

3. **Take Initial Assessment**
   - Answer 10 questions to determine your skill level

4. **View Results & Generate Roadmap**
   - See assessment score and select learning duration
   - LLM generates personalized roadmap

5. **Learn & Track Progress**
   - Read chapter content and resources
   - Mark chapters as complete
   - Take chapter tests

6. **Monitor Dashboard**
   - View overall progress
   - Check weak areas
   - Review learning activity

### For Administrators

1. **Access Admin Panel**
   - Navigate to `/admin`
   - Login with superuser credentials

2. **Manage Courses**
   - Add/edit/delete courses
   - Set difficulty levels and duration

3. **View User Progress**
   - Monitor user assessments
   - Check learning analytics
   - Track roadmap progress

## Database Models

### User Models
- `UserProfile`: Extended user information with learning preferences

### Course Models
- `Course`: Available courses
- `UserCourse`: User enrollment tracking

### Assessment Models
- `Assessment`: Initial skill level assessments
- `Roadmap`: Personalized learning paths

### Learning Models
- `ChapterProgress`: Chapter completion tracking
- `ChapterTest`: Chapter assessments
- `LearningActivity`: Activity logging

## Configuration

### OpenAI API

The system uses OpenAI's GPT-4 for generating:
- Assessment questions
- Learning roadmaps
- Chapter tests
- Adaptive recommendations

**Cost Consideration**: API calls consume credits. Monitor usage and set appropriate rate limits.

### Database

PostgreSQL is recommended for production. For development, SQLite can be used by modifying `.env`:
```
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

## Troubleshooting

### Common Issues

**CORS Errors**
- Ensure CORS is configured in Django settings
- Update `CORS_ALLOWED_ORIGINS` if running on different ports

**API Not Found (404)**
- Check that backend is running on correct port
- Verify `API_BASE_URL` in frontend matches backend URL

**Authentication Failed**
- Verify JWT token is being stored correctly
- Check token expiration (set to 30 days by default)

**OpenAI API Errors**
- Verify API key is correct
- Check quota and billing status
- Ensure using supported model (GPT-4)

**Database Errors**
- Ensure PostgreSQL is running
- Verify credentials in `.env`
- Run migrations: `python manage.py migrate`

## Development Tips

### Adding New Courses

1. Use Django admin or create via API:
```python
from courses.models import Course

Course.objects.create(
    title="Python Programming",
    description="Learn Python from basics to advanced",
    difficulty="beginner",
    duration_weeks=12
)
```

### Customizing LLM Prompts

Edit prompts in `assessments/llm_service.py`:
- `generate_assessment_questions()`: Initial assessment prompts
- `generate_roadmap()`: Roadmap generation prompts
- `generate_chapter_test()`: Chapter test prompts

### Extending Dashboard

Add new metrics in `learning/views.py` `get_learning_dashboard()` function and update frontend display in `js/app.js`.

## Future Enhancements

- [ ] Video integration with embedded player
- [ ] Social features (peer learning, discussions)
- [ ] Certification upon course completion
- [ ] Mobile native apps (React Native)
- [ ] Real-time collaboration tools
- [ ] Advanced analytics and reporting
- [ ] Gamification (badges, leaderboards)
- [ ] Offline learning support
- [ ] Multi-language support
- [ ] AI-powered personalized coaching

## Performance Optimization

- Cache roadmap data after generation
- Implement pagination for large datasets
- Use lazy loading for course images
- Minify CSS/JS for production
- Enable gzip compression
- Use CDN for static files

## Security Considerations

- Always use HTTPS in production
- Rotate JWT secret periodically
- Implement rate limiting on API endpoints
- Validate and sanitize all user inputs
- Use environment variables for sensitive data
- Enable CORS selectively
- Implement CSRF protection
- Regular security audits

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Submit pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support & Feedback

For issues, questions, or feedback:
- Create an issue on GitHub
- Email: support@learnpath.ai
- Documentation: [Full docs link]

## Acknowledgments

- OpenAI for GPT-4 API
- Django and Django REST Framework communities
- Coursera for UI/UX inspiration
- All contributors and testers

---

**Last Updated**: December 2024
**Version**: 1.0.0 Beta
