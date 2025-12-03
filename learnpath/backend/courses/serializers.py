from rest_framework import serializers
from .models import Course, UserCourse

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'difficulty', 'icon_url', 'duration_weeks', 'created_at')

class UserCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = UserCourse
        fields = ('id', 'course', 'status', 'enrollment_date', 'completion_date', 'progress_percentage')
