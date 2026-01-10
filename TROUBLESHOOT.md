# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Failures

#### **Symptom**: API container keeps restarting with MySQL connection errors

**Solution A: Wait for Database Script**
```bash
# Make sure wait_for_db.py exists in root directory
# It should be automatically called in docker-compose command

# Check if database is actually running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Manually test database connection
docker-compose exec mysql mysql -u taskuser -p
# Password: taskpass123
```

**Solution B: Increase healthcheck wait time**
```yaml
# In docker-compose.yml, increase start_period
healthcheck:
  start_period: 60s  # Increase from 30s
```

**Solution C: Reset database completely**
```bash
# Stop all services
docker-compose down -v

# Remove volumes (WARNING: deletes all data)
docker volume prune

# Start fresh
docker-compose up -d --build
```

---

### 2. App Container Keeps Restarting

#### **Check logs first:**
```bash
docker-compose logs api
docker-compose logs --tail=100 api
```

#### **Common causes:**

**A. Migration Issues**
```bash
# Run migrations manually
docker-compose exec api python manage.py migrate

# Check migration status
docker-compose exec api python manage.py showmigrations

# If stuck, fake migrations (CAREFUL!)
docker-compose exec api python manage.py migrate --fake-initial
```

**B. Import Errors**
```bash
# Check if all apps are properly configured
docker-compose exec api python manage.py check

# Test imports
docker-compose exec api python manage.py shell
>>> from apps.users.models import User
>>> from apps.projects.models import Project
>>> from apps.tasks.models import Task
```

**C. Missing Dependencies**
```bash
# Rebuild with no cache
docker-compose build --no-cache api

# Check installed packages
docker-compose exec api pip list
```

---

### 3. Celery Not Processing Tasks

#### **Check Celery logs:**
```bash
docker-compose logs celery
docker-compose logs celery-beat
```

#### **Common fixes:**

**A. Redis connection issues**
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Check if Redis is accessible from API
docker-compose exec api python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 10)
>>> cache.get('test')
```

**B. Restart Celery workers**
```bash
docker-compose restart celery celery-beat
```

**C. Clear Celery tasks**
```bash
docker-compose exec api python manage.py shell
>>> from celery import current_app
>>> current_app.control.purge()
```

---

### 4. Port Already in Use

#### **Symptom**: Error binding to port 8000, 3306, or 6379

```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :3306
sudo lsof -i :6379

# Kill process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

---

### 5. Permission Denied Errors

#### **On Linux:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Make scripts executable
chmod +x quick-start.sh
chmod +x wait_for_db.py
```

---

### 6. Static Files Not Loading

```bash
# Collect static files manually
docker-compose exec api python manage.py collectstatic --noinput

# Check static files volume
docker volume inspect task-management-api_static_volume
```

---

### 7. Database Already Exists Error

#### **Symptom**: Error creating database during initialization

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p
# Password: rootpass123

# Drop and recreate database
DROP DATABASE IF EXISTS taskdb;
CREATE DATABASE taskdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON taskdb.* TO 'taskuser'@'%';
FLUSH PRIVILEGES;
exit;

# Run migrations
docker-compose exec api python manage.py migrate
```

---

### 8. Environment Variables Not Loading

#### **Check .env file exists:**
```bash
ls -la .env

# If missing, create from template
cp .env.example .env
```

#### **Verify variables are loaded:**
```bash
docker-compose exec api python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES)
>>> print(settings.SECRET_KEY)
```

---

### 9. API Returns 500 Internal Server Error

#### **Enable debug mode temporarily:**
```bash
# In .env file
DEBUG=True

# Restart
docker-compose restart api
```

#### **Check error logs:**
```bash
docker-compose logs api | grep -i error
docker-compose logs api | grep -i exception
```

#### **Test API directly:**
```bash
docker-compose exec api python manage.py shell
>>> from apps.users.models import User
>>> User.objects.all()
```

---

### 10. Complete Reset (Nuclear Option)

**WARNING: This deletes ALL data!**

```bash
# Stop everything
docker-compose down -v

# Remove all Docker resources
docker system prune -a --volumes

# Delete local files (be careful!)
rm -rf staticfiles/ media/

# Start fresh
docker-compose up -d --build

# Wait for services to be ready
sleep 30

# Run migrations
docker-compose exec api python manage.py migrate

# Create superuser
docker-compose exec api python manage.py createsuperuser
```

---

## 🔍 Diagnostic Commands

### Check Service Status
```bash
docker-compose ps
```

### Check Service Health
```bash
docker-compose exec api curl -f http://localhost:8000/api/health/
```

### View All Logs
```bash
docker-compose logs -f
```

### Check Container Resources
```bash
docker stats
```

### Inspect Network
```bash
docker network inspect task-management-api_taskapi_network
```

### Test Database Connection
```bash
docker-compose exec api python wait_for_db.py
```

---

## 🚨 Emergency Debugging

### Enter Container Shell
```bash
# API container
docker-compose exec api bash

# Inside container:
python manage.py check
python manage.py showmigrations
python manage.py dbshell
```

### Check Django Configuration
```bash
docker-compose exec api python manage.py diffsettings
```

### Test Imports
```bash
docker-compose exec api python -c "
import django
django.setup()
from apps.users.models import User
print('✅ Imports working!')
"
```

---

## 📞 Still Having Issues?

### Collect Debug Information
```bash
# Create debug report
echo "=== Docker Version ===" > debug_report.txt
docker --version >> debug_report.txt
docker-compose --version >> debug_report.txt

echo "\n=== Container Status ===" >> debug_report.txt
docker-compose ps >> debug_report.txt

echo "\n=== API Logs ===" >> debug_report.txt
docker-compose logs --tail=50 api >> debug_report.txt

echo "\n=== MySQL Logs ===" >> debug_report.txt
docker-compose logs --tail=50 mysql >> debug_report.txt

echo "\n=== Environment ===" >> debug_report.txt
cat .env >> debug_report.txt

# Share debug_report.txt
```

### Get Help
1. Check the logs first: `docker-compose logs api`
2. Review this troubleshooting guide
3. Search for the error message online
4. Open an issue on GitHub with the debug report

---

## ✅ Success Indicators

Your setup is working correctly when:

1. **All services are running:**
   ```bash
   docker-compose ps
   # All services should show "Up" status
   ```

2. **Health check passes:**
   ```bash
   curl http://localhost:8000/api/health/
   # Should return: {"status": "healthy", ...}
   ```

3. **API docs are accessible:**
   ```bash
   curl http://localhost:8000/api/docs/
   # Should return HTML
   ```

4. **Database is accessible:**
   ```bash
   docker-compose exec mysql mysql -u taskuser -p -e "SHOW DATABASES;"
   # Should list taskdb
   ```

5. **No continuous restarts:**
   ```bash
   docker-compose logs api | grep -i restart
   # Should show no recent restarts
   ```