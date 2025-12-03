from django.db import models
import json

class Assessment(models.Model):
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='assessments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assessments')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    percentage = models.FloatField(default=0.0)
    questions_data = models.JSONField(default=dict, help_text="Store MCQ questions and answers")
    skill_level = models.CharField(max_length=20, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.user.email} - {self.course.title} Assessment"
    
    def calculate_skill_level(self):
        """Determine skill level based on score"""
        if self.percentage < 33:
            self.skill_level = 'beginner'
        elif self.percentage < 67:
            self.skill_level = 'intermediate'
        else:
            self.skill_level = 'advanced'


class Roadmap(models.Model):
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='roadmaps')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='roadmaps')
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='roadmap')
    skill_level = models.CharField(max_length=20)
    duration_weeks = models.IntegerField(default=12)
    roadmap_data = models.JSONField(default=dict, help_text="Store chapters, resources, time estimates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Roadmap - {self.user.user.email} - {self.course.title}"
