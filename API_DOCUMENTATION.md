# Task Management API - Complete Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints except registration and login require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /api/v1/auth/users/
```

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "MEMBER"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "MEMBER",
  "is_active": true,
  "created_at": "2024-12-26T10:00:00Z"
}
```

### Login
```http
POST /api/v1/auth/login/
```

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "MEMBER"
  }
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh/
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
```http
GET /api/v1/auth/users/me/
```

---

## 📁 Project Endpoints

### List Projects
```http
GET /api/v1/projects/
```

**Query Parameters:**
- `is_archived`: boolean
- `page`: integer
- `page_size`: integer

**Response (200):**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "E-commerce Platform",
      "description": "Building next-gen shopping experience",
      "owner": {
        "id": 1,
        "email": "john@example.com",
        "full_name": "John Doe"
      },
      "members": [...],
      "board_count": 3,
      "member_count": 5,
      "is_archived": false,
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

### Create Project
```http
POST /api/v1/projects/
```

**Request:**
```json
{
  "name": "Mobile App Redesign",
  "description": "Complete UI/UX overhaul"
}
```

### Get Project
```http
GET /api/v1/projects/{id}/
```

### Update Project
```http
PUT /api/v1/projects/{id}/
PATCH /api/v1/projects/{id}/
```

### Delete Project
```http
DELETE /api/v1/projects/{id}/
```

### Add Project Member
```http
POST /api/v1/projects/{id}/add_member/
```

**Request:**
```json
{
  "user_id": 5,
  "role": "MANAGER"
}
```

### Remove Project Member
```http
DELETE /api/v1/projects/{id}/remove_member/
```

**Request:**
```json
{
  "user_id": 5
}
```

---

## 📋 Board Endpoints

### List Boards
```http
GET /api/v1/projects/boards/
```

**Query Parameters:**
- `project`: integer (filter by project ID)
- `page`: integer

**Response (200):**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Sprint 1",
      "description": "First sprint board",
      "project": 1,
      "position": 0,
      "task_count": 15,
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

### Create Board
```http
POST /api/v1/projects/boards/
```

**Request:**
```json
{
  "name": "Sprint 2",
  "description": "Second sprint",
  "project": 1
}
```

---

## ✅ Task Endpoints

### List Tasks
```http
GET /api/v1/tasks/
```

**Query Parameters:**
- `board`: integer
- `status`: TODO, IN_PROGRESS, REVIEW, DONE, BACKLOG
- `priority`: LOW, MEDIUM, HIGH, CRITICAL
- `assignee`: integer (user ID)
- `sla_breached`: boolean
- `due_date_from`: ISO datetime
- `due_date_to`: ISO datetime
- `search`: string (searches title and description)
- `ordering`: created_at, -created_at, priority, due_date

**Example:**
```
GET /api/v1/tasks/?status=TODO&priority=HIGH&assignee=5&ordering=-priority
```

**Response (200):**
```json
{
  "count": 42,
  "results": [
    {
      "id": 100,
      "title": "Implement user authentication",
      "description": "Add JWT-based auth system",
      "board": 1,
      "status": "IN_PROGRESS",
      "priority": "HIGH",
      "assignee": 5,
      "assignee_detail": {
        "id": 5,
        "email": "dev@example.com",
        "full_name": "Jane Developer"
      },
      "reporter": 1,
      "reporter_detail": {...},
      "due_date": "2024-12-30T17:00:00Z",
      "sla_breached": false,
      "estimated_hours": "8.00",
      "comment_count": 3,
      "created_at": "2024-12-20T09:00:00Z",
      "completed_at": null
    }
  ]
}
```

### Create Task
```http
POST /api/v1/tasks/
```

**Request:**
```json
{
  "title": "Fix login bug",
  "description": "Users can't login with special characters in password",
  "board": 1,
  "status": "TODO",
  "priority": "CRITICAL",
  "assignee": 5,
  "due_date": "2024-12-28T17:00:00Z",
  "estimated_hours": "4.5"
}
```

### Get Task Details
```http
GET /api/v1/tasks/{id}/
```

**Response includes comments:**
```json
{
  "id": 100,
  "title": "...",
  "comments": [
    {
      "id": 1,
      "author": {...},
      "content": "Started working on this",
      "created_at": "2024-12-21T10:00:00Z"
    }
  ]
}
```

### Update Task
```http
PUT /api/v1/tasks/{id}/
PATCH /api/v1/tasks/{id}/
```

### Delete Task
```http
DELETE /api/v1/tasks/{id}/
```

### Assign Task
```http
POST /api/v1/tasks/{id}/assign/
```

**Request:**
```json
{
  "assignee_id": 7
}
```

*Note: Triggers async email notification*

### Move Task (Change Status)
```http
POST /api/v1/tasks/{id}/move/
```

**Request:**
```json
{
  "status": "IN_PROGRESS"
}
```

### Add Comment
```http
POST /api/v1/tasks/{id}/add_comment/
```

**Request:**
```json
{
  "content": "I've started reviewing the PR"
}
```

---

## 📝 Audit Log Endpoints

### List Audit Logs
```http
GET /api/v1/audit/logs/
```

**Query Parameters:**
- `model_name`: Task, Project, Board, etc.
- `action`: CREATE, UPDATE, DELETE
- `user`: integer (user ID)
- `object_id`: integer
- `date_from`: ISO datetime
- `date_to`: ISO datetime

**Response (200):**
```json
{
  "results": [
    {
      "id": 500,
      "user": 1,
      "user_detail": {...},
      "action": "UPDATE",
      "model_name": "Task",
      "object_id": 100,
      "changes": {
        "status": "IN_PROGRESS",
        "updated": true
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2024-12-26T14:30:00Z"
    }
  ]
}
```

---

## 🔍 Advanced Filtering Examples

### Get all high-priority tasks assigned to me that are overdue
```http
GET /api/v1/tasks/?priority=HIGH&assignee={my_user_id}&due_date_to={current_datetime}&status=TODO,IN_PROGRESS
```

### Search for tasks containing "authentication"
```http
GET /api/v1/tasks/?search=authentication
```

### Get tasks ordered by priority (critical first)
```http
GET /api/v1/tasks/?ordering=-priority,due_date
```

### Get my projects that aren't archived
```http
GET /api/v1/projects/?is_archived=false
```

---

## 📊 Pagination

All list endpoints support pagination:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/tasks/?page=3",
  "previous": "http://localhost:8000/api/v1/tasks/?page=1",
  "results": [...]
}
```

**Custom page size:**
```
GET /api/v1/tasks/?page_size=50
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid status value",
  "field_errors": {
    "status": ["This field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in 59 seconds."
}
```

---

## 🎯 Rate Limits

- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour

Limits are enforced per IP address for anonymous users and per user for authenticated requests.

---

## 📚 Interactive Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

These interfaces allow you to test API endpoints directly from your browser.