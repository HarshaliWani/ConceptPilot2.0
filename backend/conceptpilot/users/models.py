import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with UUID primary key and additional fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class UserInterest(models.Model):
    """Model to store user interests and proficiency levels."""
    
    INTEREST_CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('sports', 'Sports'),
        ('cooking', 'Cooking'),
        ('music', 'Music'),
        ('art', 'Art'),
    ]
    
    PROFICIENCY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interests')
    interest_category = models.CharField(max_length=50, choices=INTEREST_CATEGORY_CHOICES)
    specific_interest = models.TextField()
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.get_interest_category_display()}: {self.specific_interest}"


class UserProfile(models.Model):
    """Model to store user learning preferences and context."""
    
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES)
    preferred_difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    weak_concepts = models.JSONField(default=list, blank=True)
    strong_concepts = models.JSONField(default=list, blank=True)
    llm_context = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.name}"
