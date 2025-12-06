from django.db import models

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    icon_url = models.URLField(blank=True, null=True)
    duration_weeks = models.IntegerField(default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class UserCourse(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='enrolled_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    progress_percentage = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.user.user.email} - {self.course.title}"


class CourseVideo(models.Model):
    """Admin-managed video resources for courses and topics"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    topic = models.CharField(max_length=200, blank=True, null=True, help_text='Optional topic/tag for this video')
    title = models.CharField(max_length=300)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
