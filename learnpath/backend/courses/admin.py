from django.contrib import admin
from .models import Course, UserCourse

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'duration_weeks', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('difficulty', 'created_at')

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress_percentage', 'enrollment_date')
    search_fields = ('user__user__email', 'course__title')
    list_filter = ('status', 'enrollment_date')
