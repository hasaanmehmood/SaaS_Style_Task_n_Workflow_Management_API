"""Views for Project and Board APIs."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Project, ProjectMember, Board
from .serializers import ProjectSerializer, ProjectMemberSerializer, BoardSerializer
from .permissions import IsProjectMember, IsProjectAdmin


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for project CRUD operations."""
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        user = self.request.user

        # Admins see all, others see their projects
        if user.is_admin:
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(
                Q(owner=user) | Q(members__user=user)
            ).distinct()

        # Annotate counts
        queryset = queryset.annotate(
            board_count=Count('boards', distinct=True),
            member_count=Count('members', distinct=True)
        ).select_related('owner').prefetch_related('members__user')

        # Filter archived
        is_archived = self.request.query_params.get('is_archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def add_member(self, request, pk=None):
        """Add a member to the project."""
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data.get('role', ProjectMember.Role.MEMBER)

        member, created = ProjectMember.objects.get_or_create(
            project=project,
            user_id=user_id,
            defaults={'role': role}
        )

        if not created:
            return Response(
                {'detail': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ProjectMemberSerializer(member).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], permission_classes=[IsProjectAdmin])
    def remove_member(self, request, pk=None):
        """Remove a member from the project."""
        project = self.get_object()
        user_id = request.data.get('user_id')

        member = get_object_or_404(ProjectMember, project=project, user_id=user_id)

        if member.user == project.owner:
            return Response(
                {'detail': 'Cannot remove project owner'},
                status=status.HTTP_400_BAD_REQUEST
            )

        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardViewSet(viewsets.ModelViewSet):
    """ViewSet for board CRUD operations."""
    serializer_class = BoardSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        queryset = Board.objects.all()

        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Annotate task count
        queryset = queryset.annotate(
            task_count=Count('tasks', distinct=True)
        ).select_related('project')

        return queryset

    def perform_create(self, serializer):
        """Auto-set position on create."""
        project = serializer.validated_data['project']
        last_position = Board.objects.filter(project=project).count()
        serializer.save(position=last_position)