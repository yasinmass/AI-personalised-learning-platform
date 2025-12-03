# 🐘 PostgreSQL Setup Guide

## Step 1: Install PostgreSQL

### Windows
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. When prompted, set password for 'postgres' user (remember this!)
4. Keep port as 5432 (default)
5. Complete the installation

### Alternative (Using Chocolatey)
```powershell
choco install postgresql
```

### Alternative (Using Windows Subsystem for Linux - WSL)
```bash
wsl
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

---

## Step 2: Create Database and User

### Using pgAdmin (GUI)
1. Open pgAdmin (installed with PostgreSQL)
2. Connect to the server (default: localhost:5432)
3. Right-click "Databases" → Create → Database
4. Name: `learnpath_db`
5. Owner: `postgres`
6. Click Create

### Using Command Line (PowerShell)
```powershell
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE learnpath_db;
\q  # Exit
```

---

## Step 3: Update .env File

Create a `.env` file in `backend/` folder with:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
OPENAI_API_KEY=sk-your-openai-api-key-here

# PostgreSQL Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=learnpath_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

**Replace:** `your_postgres_password` with the password you set during PostgreSQL installation.

---

## Step 4: Install Python Packages

```powershell
cd "c:\Users\Yasin\OneDrive\Desktop\ag\learnpath\backend"
.\venv\Scripts\activate
pip install -r requirements.txt
```

This includes:
- `djangorestframework-simplejwt` - JWT authentication
- `psycopg2-binary` - PostgreSQL driver

---

## Step 5: Run Migrations

```powershell
python manage.py migrate
```

This creates all database tables in PostgreSQL.

---

## Step 6: Create Superuser

```powershell
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## Step 7: Load Sample Data

```powershell
python manage.py create_initial_data
```

This loads 8 sample courses into the database.

---

## Step 8: Start the Server

```powershell
python manage.py runserver
```

Backend will be running at: **http://localhost:8000**

---

## 🔍 Verify PostgreSQL is Working

### Check if PostgreSQL is Running
```powershell
# Windows Services
services.msc  # Look for "postgresql-x64-15" service

# Or via command line:
pg_isready -h localhost -p 5432
# Output should be: "accepting connections"
```

### Connect to Database
```powershell
psql -U postgres -d learnpath_db

# List tables:
\dt

# Exit:
\q
```

### View Django Tables
```powershell
python manage.py dbshell
```

---

## 🐛 Troubleshooting

### Error: "could not connect to server"
- **Check**: Is PostgreSQL running? (Check Services)
- **Fix**: Start PostgreSQL service from Services or command line

### Error: "database 'learnpath_db' does not exist"
- **Check**: Run `psql -U postgres -l` to list databases
- **Fix**: Create the database (see Step 2)

### Error: "password authentication failed"
- **Check**: Is your password correct in `.env`?
- **Fix**: Update DB_PASSWORD in `.env` with correct password

### Error: "psycopg2 failed to build"
- **Check**: Do you have Visual C++ build tools?
- **Fix**: Install from https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Port Already in Use
```powershell
# Find process using port 5432
netstat -ano | findstr :5432

# Kill the process (replace PID with actual ID)
taskkill /PID <PID> /F
```

---

## 📊 Database Tools

### pgAdmin (GUI)
- URL: http://localhost:5050
- Default username: `pgadmin4@pgadmin.org`
- Default password: `admin`

### Command Line (psql)
```powershell
# Connect to database
psql -U postgres -d learnpath_db

# Useful commands:
\dt              # List all tables
\d users_user    # Describe table structure
SELECT * FROM users_user;  # View data
\q               # Quit
```

---

## 🔐 Security Tips

1. **Change postgres password** (see PostgreSQL documentation)
2. **Use strong DB_PASSWORD** in production
3. **Never commit .env** to Git
4. **Set DEBUG=False** in production
5. **Use environment variables** for sensitive data

---

## 📈 Performance Tips

1. **Create indexes** on frequently queried columns
2. **Use VACUUM** regularly to optimize storage
3. **Monitor connections**: `psql -U postgres -d learnpath_db -c "SELECT * FROM pg_stat_activity;"`
4. **Backup regularly**: `pg_dump -U postgres learnpath_db > backup.sql`

---

## 🚀 Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database
3. ✅ Update `.env` file
4. ✅ Install Python packages
5. ✅ Run migrations
6. ✅ Create superuser
7. ✅ Load sample data
8. ✅ Start server

**Then start the frontend:**
```powershell
cd "..\frontend"
python -m http.server 8001
```

Access at: http://localhost:8001

---

## 📞 Quick Help

| Issue | Command |
|-------|---------|
| Check if running | `pg_isready -h localhost` |
| View databases | `psql -U postgres -l` |
| Connect to DB | `psql -U postgres -d learnpath_db` |
| Reset password | `ALTER USER postgres WITH PASSWORD 'newpassword';` |
| Backup database | `pg_dump -U postgres learnpath_db > backup.sql` |
| Restore database | `psql -U postgres learnpath_db < backup.sql` |

---

**PostgreSQL is now configured! 🎉**
