from django.db import models

class ChapterProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='chapter_progress')
    roadmap = models.ForeignKey('assessments.Roadmap', on_delete=models.CASCADE, related_name='chapters')
    chapter_name = models.CharField(max_length=200)
    chapter_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    time_spent_minutes = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['chapter_number']
        unique_together = ('roadmap', 'chapter_number')

    def __str__(self):
        return f"{self.chapter_name} - {self.user.user.email}"


class ChapterTest(models.Model):
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='chapter_tests')
    roadmap = models.ForeignKey('assessments.Roadmap', on_delete=models.CASCADE, related_name='tests')
    chapter_progress = models.ForeignKey(ChapterProgress, on_delete=models.CASCADE, related_name='tests')
    chapter_name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=4)
    percentage = models.FloatField(default=0.0)
    questions_data = models.JSONField(default=dict, help_text="Store test questions and answers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Test - {self.chapter_name} - {self.user.user.email}"


class LearningActivity(models.Model):
    ACTIVITY_TYPES = [
        ('chapter_viewed', 'Chapter Viewed'),
        ('test_taken', 'Test Taken'),
        ('resource_accessed', 'Resource Accessed'),
        ('time_logged', 'Time Logged'),
    ]
    
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='learning_activities')
    roadmap = models.ForeignKey('assessments.Roadmap', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    chapter_name = models.CharField(max_length=200, blank=True)
    duration_minutes = models.IntegerField(default=0)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} - {self.user.user.email}"
