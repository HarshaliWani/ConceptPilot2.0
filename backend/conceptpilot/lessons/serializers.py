from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""
    board_actions = serializers.JSONField()
    
    class Meta:
        model = Lesson
        fields = '__all__'

