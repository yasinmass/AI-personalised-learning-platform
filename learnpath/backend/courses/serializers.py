from rest_framework import serializers
from .models import Course, UserCourse
from courses.models import CourseVideo
from users.models import UserProfile
from rest_framework import serializers as drf_serializers

class CourseSerializer(serializers.ModelSerializer):
    videos = drf_serializers.SerializerMethodField()

    def get_videos(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        videos_qs = CourseVideo.objects.filter(course=obj, is_active=True)

        # If request and authenticated, filter by user's assigned topics
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                assigned = (profile.assigned_topics or '').strip()
                if assigned:
                    topics = [t.strip().lower() for t in assigned.split(',') if t.strip()]
                    if topics:
                        matched = CourseVideo.objects.none()
                        for t in topics:
                            matched = matched | videos_qs.filter(topic__icontains=t)
                        if matched.exists():
                            videos_qs = matched.distinct()
            except Exception:
                # fallback to course videos
                pass

        return [{'title': v.title, 'url': v.url, 'topic': v.topic} for v in videos_qs]

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'difficulty', 'icon_url', 'duration_weeks', 'created_at', 'videos')

class UserCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = UserCourse
        fields = ('id', 'course', 'status', 'enrollment_date', 'completion_date', 'progress_percentage')
