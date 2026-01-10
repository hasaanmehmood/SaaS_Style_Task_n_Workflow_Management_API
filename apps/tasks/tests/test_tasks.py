"""Tests for Task API."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.projects.models import Project, Board
from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        role=User.Role.ADMIN
    )


@pytest.fixture
def project(user):
    return Project.objects.create(
        name='Test Project',
        description='Test Description',
        owner=user
    )


@pytest.fixture
def board(project):
    return Board.objects.create(
        name='Test Board',
        project=project
    )


@pytest.fixture
def task(board, user):
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        board=board,
        reporter=user,
        status=Task.Status.TODO,
        priority=Task.Priority.MEDIUM
    )


@pytest.mark.django_db
class TestTaskAPI:
    """Test Task API endpoints."""

    def test_create_task(self, api_client, user, board):
        """Test creating a new task."""
        api_client.force_authenticate(user=user)
        url = reverse('task-list')

        data = {
            'title': 'New Task',
            'description': 'New task description',
            'board': board.id,
            'status': Task.Status.TODO,
            'priority': Task.Priority.HIGH
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['reporter'] == user.id

    def test_list_tasks(self, api_client, user, task):
        """Test listing tasks."""
        api_client.force_authenticate(user=user)
        url = reverse('task-list')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_filter_tasks_by_status(self, api_client, user, task):
        """Test filtering tasks by status."""
        api_client.force_authenticate(user=user)
        url = reverse('task-list')

        response = api_client.get(url, {'status': Task.Status.TODO})

        assert response.status_code == status.HTTP_200_OK
        for item in response.data['results']:
            assert item['status'] == Task.Status.TODO

    def test_update_task_status(self, api_client, user, task):
        """Test updating task status."""
        api_client.force_authenticate(user=user)
        url = reverse('task-move', kwargs={'pk': task.id})

        data = {'status': Task.Status.IN_PROGRESS}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Task.Status.IN_PROGRESS

    def test_assign_task(self, api_client, user, task, admin_user):
        """Test assigning task to user."""
        api_client.force_authenticate(user=user)
        url = reverse('task-assign', kwargs={'pk': task.id})

        data = {'assignee_id': admin_user.id}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['assignee'] == admin_user.id

    def test_delete_task(self, api_client, user, task):
        """Test deleting a task."""
        api_client.force_authenticate(user=user)
        url = reverse('task-detail', kwargs={'pk': task.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_unauthorized_access(self, api_client, task):
        """Test unauthorized access is denied."""
        url = reverse('task-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTaskModel:
    """Test Task model."""

    def test_task_creation(self, board, user):
        """Test creating a task."""
        task = Task.objects.create(
            title='Model Test Task',
            board=board,
            reporter=user
        )

        assert task.title == 'Model Test Task'
        assert task.status == Task.Status.BACKLOG
        assert task.priority == Task.Priority.MEDIUM
        assert task.completed_at is None

    def test_task_completion(self, task):
        """Test task completion updates completed_at."""
        task.status = Task.Status.DONE
        task.save()

        assert task.completed_at is not None

    def test_task_string_representation(self, task):
        """Test task __str__ method."""
        assert str(task) == task.title