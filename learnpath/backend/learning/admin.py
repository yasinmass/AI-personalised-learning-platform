from django.contrib import admin
from .models import ChapterProgress, ChapterTest, LearningActivity

@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter_name', 'status', 'time_spent_minutes', 'last_accessed')
    search_fields = ('user__user__email', 'chapter_name')
    list_filter = ('status', 'created_at')

@admin.register(ChapterTest)
class ChapterTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter_name', 'score', 'percentage', 'created_at')
    search_fields = ('user__user__email', 'chapter_name')
    list_filter = ('created_at',)

@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'chapter_name', 'created_at')
    search_fields = ('user__user__email', 'chapter_name')
    list_filter = ('activity_type', 'created_at')
