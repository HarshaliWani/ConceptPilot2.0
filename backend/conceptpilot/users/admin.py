from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserInterest, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin configuration for CustomUser model."""
    list_display = ['email', 'name', 'username', 'is_staff', 'is_active', 'created_at']
    list_filter = ['is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'name', 'username']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'created_at')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('name', 'email')}),
    )


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    """Admin configuration for UserInterest model."""
    list_display = ['user', 'interest_category', 'specific_interest', 'proficiency_level', 'created_at']
    list_filter = ['interest_category', 'proficiency_level', 'created_at']
    search_fields = ['user__email', 'user__name', 'specific_interest']
    raw_id_fields = ['user']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = ['user', 'learning_style', 'preferred_difficulty', 'updated_at']
    list_filter = ['learning_style', 'preferred_difficulty', 'updated_at']
    search_fields = ['user__email', 'user__name']
    raw_id_fields = ['user']
    ordering = ['-updated_at']
