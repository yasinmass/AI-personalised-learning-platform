from rest_framework import serializers
from .models import Assessment, Roadmap
from courses.serializers import CourseSerializer

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('id', 'user', 'course', 'score', 'total_questions', 'percentage', 'skill_level', 'created_at')

class AssessmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('id', 'user', 'course', 'score', 'total_questions', 'percentage', 'questions_data', 'skill_level', 'created_at')

class RoadmapSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Roadmap
        fields = ('id', 'user', 'course', 'skill_level', 'duration_weeks', 'roadmap_data', 'created_at', 'updated_at')
