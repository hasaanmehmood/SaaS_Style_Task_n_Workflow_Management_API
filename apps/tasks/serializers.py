"""Serializers for Task API."""
from rest_framework import serializers
from .models import Task, Comment
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for tasks."""
    assignee_detail = UserSerializer(source='assignee', read_only=True)
    reporter_detail = UserSerializer(source='reporter', read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'board', 'status', 'priority',
            'assignee', 'assignee_detail', 'reporter', 'reporter_detail',
            'due_date', 'sla_breached', 'estimated_hours', 'comment_count',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'reporter', 'sla_breached', 'created_at',
            'updated_at', 'completed_at'
        ]

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    """Detailed task serializer with comments."""
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['comments']