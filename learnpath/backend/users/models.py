from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    learning_duration_preference = models.IntegerField(default=12, help_text="Duration in weeks")
    total_learning_hours = models.IntegerField(default=0)
    # Comma-separated assigned topics for the user (admin assigns topics)
    assigned_topics = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated topics assigned by admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"
