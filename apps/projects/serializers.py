"""Serializers for Project and Board APIs."""
from rest_framework import serializers
from .models import Project, ProjectMember, Board
from apps.users.serializers import UserSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for project members."""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects."""
    owner = UserSerializer(read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    board_count = serializers.IntegerField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'members',
            'is_archived', 'board_count', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        project = super().create(validated_data)

        # Add owner as admin member
        ProjectMember.objects.create(
            project=project,
            user=project.owner,
            role=ProjectMember.Role.ADMIN
        )
        return project


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for boards."""
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'description', 'project',
            'position', 'task_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']