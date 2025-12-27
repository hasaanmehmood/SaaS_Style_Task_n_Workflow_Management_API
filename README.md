# 🚀 Task & Workflow Management API

A production-ready SaaS-style task management system built with Django REST Framework, featuring role-based access control, async notifications, comprehensive audit logging, and real-time task tracking.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Redis](https://img.shields.io/badge/Redis-7.0-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Production Deployment](#-production-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Functionality
- ✅ **Multi-Project Management**: Organize work across multiple projects
- ✅ **Kanban Boards**: Visual task organization with customizable boards
- ✅ **Task Lifecycle Management**: Full CRUD with status tracking (Backlog → Done)
- ✅ **Role-Based Access Control**: Admin, Manager, and Member roles
- ✅ **Advanced Filtering**: Filter by status, priority, assignee, due date, and more
- ✅ **Full-Text Search**: Search across task titles and descriptions
- ✅ **SLA Tracking**: Automatic breach detection for overdue tasks

### Production Features
- 🔐 **JWT Authentication**: Stateless, secure authentication
- 📝 **Comprehensive Audit Logging**: Track all changes with IP and user agent
- 🔔 **Async Notifications**: Email notifications via Celery
- ⚡ **Redis Caching**: Optimized performance
- 🛡️ **Rate Limiting**: Prevent API abuse
- 📊 **API Documentation**: Auto-generated Swagger/ReDoc docs
- 🐳 **Docker Ready**: Multi-container setup with docker-compose
- 🧪 **Testing Suite**: Pytest with 70%+ coverage

### Advanced Features
- 📌 **Task Comments**: Threaded discussions on tasks
- 👥 **Project Membership**: Granular access control per project
- 📅 **Due Date Tracking**: With SLA breach notifications
- 🎯 **Priority Management**: Four-level priority system
- 📈 **Performance Optimized**: Database indexes and query optimization

---

## 🏗️ Architecture

### Tech Stack

**Backend Framework**
- Django 4.2 + Django REST Framework
- Python 3.11

**Database & Caching**
- MySQL 8.0 (Primary database)
- Redis 7.0 (Caching + message broker)

**Async Processing**
- Celery (Background tasks)
- Celery Beat (Scheduled tasks)

**Infrastructure**
- Docker + Docker Compose
- Gunicorn (WSGI server)

### Key Design Patterns

1. **Repository Pattern**: Clean separation of data access logic
2. **Signal-Based Audit Trail**: Automatic change tracking
3. **RBAC (Role-Based Access Control)**: Fine-grained permissions
4. **Task Queue Pattern**: Async email/webhook processing
5. **API Versioning**: URL-based versioning for backward compatibility

### Database Schema

```
users
├── id, email, username, role, created_at

projects
├── id, name, owner_id, is_archived
└── project_members (many-to-many with roles)

boards
├── id, name, project_id, position

tasks
├── id, title, status, priority
├── board_id, assignee_id, reporter_id
├── due_date, sla_breached
└── comments (one-to-many)

audit_logs
└── user_id, action, model_name, changes, ip_address, timestamp
```

---

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Installation (Automated)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/task-management-api.git
cd task-management-api

# 2. Run the quick start script
chmod +x quick-start.sh
./quick-start.sh
```

The script will:
- Create `.env` from template
- Build Docker images
- Start all services
- Run migrations
- Create superuser
- Display access URLs

### Installation (Manual)

```bash
# 1. Clone and setup environment
git clone https://github.com/yourusername/task-management-api.git
cd task-management-api
cp .env.example .env

# 2. Start services
docker-compose up -d --build

# 3. Run migrations
docker-compose exec api python manage.py migrate

# 4. Create superuser
docker-compose exec api python manage.py createsuperuser

# 5. Access the API
open http://localhost:8000/api/docs/
```

### Verify Installation

```bash
# Check service health
curl http://localhost:8000/api/health/

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```

---

## 📁 Project Structure

```
task-management-api/
├── config/                    # Django configuration
│   ├── settings.py           # Main settings
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI config
│   └── celery.py             # Celery config
│
├── apps/                      # Application modules
│   ├── users/                # User authentication & management
│   │   ├── models.py         # User model
│   │   ├── serializers.py    # API serializers
│   │   ├── views.py          # API views
│   │   └── urls.py           # URL routes
│   │
│   ├── projects/             # Project & board management
│   │   ├── models.py         # Project, Board, ProjectMember
│   │   ├── permissions.py    # Custom permissions
│   │   └── ...
│   │
│   ├── tasks/                # Task management
│   │   ├── models.py         # Task, Comment models
│   │   ├── tasks.py          # Celery tasks
│   │   ├── filters.py        # Query filters
│   │   └── tests/            # Test suite
│   │
│   └── audit/                # Audit logging
│       ├── models.py         # AuditLog model
│       ├── signals.py        # Change tracking
│       └── middleware.py     # Request context
│
├── docker-compose.yml         # Service orchestration
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── .env.example              # Environment template
└── quick-start.sh            # Setup automation
```

---

## 📚 API Documentation

### Access Interactive Docs

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Full Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### Quick Examples

#### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

#### Create Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement feature X",
    "board": 1,
    "priority": "HIGH",
    "status": "TODO"
  }'
```

#### Filter Tasks
```bash
# Get high-priority tasks in progress
curl "http://localhost:8000/api/v1/tasks/?priority=HIGH&status=IN_PROGRESS" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
docker-compose exec api pytest

# With coverage report
docker-compose exec api pytest --cov=apps --cov-report=html

# Specific test file
docker-compose exec api pytest apps/tasks/tests/test_tasks.py

# Verbose output
docker-compose exec api pytest -v

# Run only unit tests
docker-compose exec api pytest -m unit
```

### Coverage Goals
- **Unit Tests**: >80% coverage
- **Integration Tests**: All critical paths
- **API Tests**: 100% endpoint coverage

### View Coverage Report
```bash
docker-compose exec api pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

---

## 🐳 Docker Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f celery

# Restart service
docker-compose restart api

# Rebuild service
docker-compose up -d --build api

# Access container shell
docker-compose exec api bash

# Run Django commands
docker-compose exec api python manage.py createsuperuser
docker-compose exec api python manage.py makemigrations
docker-compose exec api python manage.py migrate
```

### Database Operations

```bash
# Access MySQL
docker-compose exec mysql mysql -u taskuser -p

# Backup database
docker-compose exec mysql mysqldump -u taskuser -p taskdb > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u taskuser -p taskdb < backup.sql
```

---

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=taskdb
DB_USER=taskuser
DB_PASSWORD=taskpass123
DB_HOST=mysql

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Rate Limiting
THROTTLE_ANON_RATE=100/hour
THROTTLE_USER_RATE=1000/hour
```

### Production Settings

For production deployment, ensure:

```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📊 Monitoring & Logging

### View Logs

```bash
# API logs
docker-compose logs -f api

# Celery worker logs
docker-compose logs -f celery

# All services
docker-compose logs -f
```

### Health Check

```bash
curl http://localhost:8000/api/health/
```

### Performance Monitoring

The API includes built-in optimizations:
- Database query optimization with select_related/prefetch_related
- Redis caching for frequently accessed data
- Database indexes on high-traffic queries
- Connection pooling

---

## 🚀 Production Deployment

### Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure production database credentials
- [ ] Set up SSL/TLS certificates
- [ ] Enable security headers (HSTS, CSP)
- [ ] Configure email backend (SMTP)
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure log aggregation
- [ ] Set up automated backups
- [ ] Enable firewall rules
- [ ] Configure rate limiting
- [ ] Set up CDN for static files

### Scaling Recommendations

**Horizontal Scaling**
- Deploy multiple API containers behind load balancer (Nginx, HAProxy)
- Use Redis Sentinel for cache high availability
- Implement read replicas for MySQL

**Vertical Scaling**
- Increase worker count: `--workers 8`
- Tune MySQL buffer pool size
- Increase Redis maxmemory

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run linting
docker-compose exec api flake8 apps/
docker-compose exec api black apps/ --check

# Format code
docker-compose exec api black apps/
```

---



## 🙏 Acknowledgments

- Django REST Framework team for the excellent framework
- Celery project for async task processing
- Docker for containerization
- Me for developing

---

## 📞 Support

- **Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/task-management-api/issues)
- **Email**: reachasaan@gmail.com

---

**Built with ❤️ for production-grade Django APIs**
