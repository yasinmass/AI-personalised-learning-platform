from rest_framework import serializers
from .models import ChapterProgress, ChapterTest, LearningActivity

class ChapterProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterProgress
        fields = ('id', 'roadmap', 'chapter_name', 'chapter_number', 'status', 'time_spent_minutes', 'last_accessed', 'completion_date')

class ChapterTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterTest
        fields = ('id', 'roadmap', 'chapter_progress', 'chapter_name', 'score', 'total_questions', 'percentage', 'created_at')

class ChapterTestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterTest
        fields = ('id', 'roadmap', 'chapter_progress', 'chapter_name', 'score', 'total_questions', 'percentage', 'questions_data', 'created_at')

class LearningActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningActivity
        fields = ('id', 'roadmap', 'activity_type', 'chapter_name', 'duration_minutes', 'details', 'created_at')
