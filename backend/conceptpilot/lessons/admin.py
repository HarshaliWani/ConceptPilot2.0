from django.contrib import admin
from .models import Lesson, UserProgress


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin configuration for Lesson model."""
    list_display = ['title', 'topic', 'tailored_to_interest', 'duration', 'created_at']
    list_filter = ['topic', 'created_at']
    search_fields = ['title', 'topic', 'tailored_to_interest']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'topic', 'title', 'tailored_to_interest')
        }),
        ('Content', {
            'fields': ('narration_script', 'board_actions', 'audio_url')
        }),
        ('Metadata', {
            'fields': ('duration', 'created_at')
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """Admin configuration for UserProgress model."""
    list_display = ['user', 'lesson', 'status', 'mastery_score', 'time_spent_seconds', 'last_accessed']
    list_filter = ['status', 'last_accessed']
    search_fields = ['user__email', 'user__name', 'lesson__title', 'lesson__topic']
    raw_id_fields = ['user', 'lesson']
    readonly_fields = ['id', 'last_accessed']
    ordering = ['-last_accessed']
    
    fieldsets = (
        ('Relations', {
            'fields': ('id', 'user', 'lesson')
        }),
        ('Progress', {
            'fields': ('status', 'mastery_score', 'time_spent_seconds', 'last_accessed')
        }),
    )
