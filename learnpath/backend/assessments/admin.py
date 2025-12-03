from django.contrib import admin
from .models import Assessment, Roadmap

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'score', 'percentage', 'skill_level', 'created_at')
    search_fields = ('user__user__email', 'course__title')
    list_filter = ('skill_level', 'created_at')

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'skill_level', 'duration_weeks', 'created_at')
    search_fields = ('user__user__email', 'course__title')
    list_filter = ('skill_level', 'created_at')
