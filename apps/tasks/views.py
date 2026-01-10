"""Views for Task API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters import rest_framework as filters

from .models import Task, Comment
from .serializers import TaskSerializer, TaskDetailSerializer, CommentSerializer
from apps.projects.permissions import IsProjectMember
from .tasks import send_task_assignment_email


class TaskFilter(filters.FilterSet):
    """Filter for task queries."""
    status = filters.MultipleChoiceFilter(choices=Task.Status.choices)
    priority = filters.MultipleChoiceFilter(choices=Task.Priority.choices)
    assignee = filters.NumberFilter()
    board = filters.NumberFilter()
    due_date_from = filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'assignee', 'board', 'sla_breached']


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for task CRUD operations."""
    permission_classes = [IsProjectMember]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'status']

    def get_queryset(self):
        queryset = Task.objects.all()

        # Filter by user's accessible projects
        user = self.request.user
        if not user.is_admin:
            queryset = queryset.filter(
                Q(board__project__owner=user) |
                Q(board__project__members__user=user)
            ).distinct()

        # Annotate comment count
        queryset = queryset.annotate(
            comment_count=Count('comments', distinct=True)
        ).select_related(
            'board__project',
            'assignee',
            'reporter'
        )

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to a user."""
        task = self.get_object()
        assignee_id = request.data.get('assignee_id')

        if not assignee_id:
            return Response(
                {'detail': 'assignee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.assignee_id = assignee_id
        task.save()

        # Send async email notification
        send_task_assignment_email.delay(task.id, assignee_id)

        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Change task status."""
        task = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Task.Status.choices):
            return Response(
                {'detail': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()

        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to the task."""
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comment operations."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsProjectMember]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)