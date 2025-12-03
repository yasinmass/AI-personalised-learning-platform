from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_duration_preference', 'total_learning_hours', 'created_at')
    search_fields = ('user__email',)
