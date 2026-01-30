import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Lesson(models.Model):
    """Model for AI-generated lessons."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    tailored_to_interest = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    narration_script = models.TextField()
    board_actions = models.JSONField(default=list, blank=True)
    audio_url = models.URLField(blank=True, null=True)
    duration = models.FloatField(validators=[MinValueValidator(0.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    raw_llm_output = models.JSONField(blank=True, null=True) 

    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
    
    def __str__(self):
        interest_part = f" ({self.tailored_to_interest})" if self.tailored_to_interest else ""
        return f"{self.title} - {self.topic}{interest_part}"


class UserProgress(models.Model):
    """Model to track user progress on lessons."""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    mastery_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(1.00)]
    )
    time_spent_seconds = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_accessed']
        unique_together = [['user', 'lesson']]
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
    
    def __str__(self):
        return f"{self.user.name} - {self.lesson.title} ({self.get_status_display()})"
