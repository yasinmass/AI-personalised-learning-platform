from django.contrib import admin
from .models import Course, UserCourse
from .models import CourseVideo
from django.urls import path
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from assessments.models import Roadmap

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


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'topic', 'is_active', 'created_at')
    search_fields = ('title', 'course__title', 'topic')
    list_filter = ('is_active', 'created_at')

    class Media:
        # Use app-static relative path so Django staticfiles finds it in dev and production
        js = ('courses/admin_coursevideo.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-topics/', self.admin_site.admin_view(self.fetch_topics), name='coursevideo_fetch_topics'),
        ]
        return custom_urls + urls

    def fetch_topics(self, request):
        """Return JSON list of LLM-generated topics for the latest Roadmap of a course."""
        course_id = request.GET.get('course_id')
        if not course_id:
            return JsonResponse({'topics': []})

        try:
            roadmap = Roadmap.objects.filter(course_id=course_id).order_by('-created_at').first()
            topics = []
            if roadmap and isinstance(roadmap.roadmap_data, dict):
                data = roadmap.roadmap_data
                # Collect topics from chapters (new shape)
                for ch in data.get('chapters', []) or []:
                    ch_topics = ch.get('topics') or []
                    if isinstance(ch_topics, str):
                        ch_topics = [ch_topics]
                    for t in ch_topics:
                        t = (t or '').strip()
                        if t and t not in topics:
                            topics.append(t)
                # Also include related_topics
                for rt in data.get('related_topics', []) or []:
                    r = (rt or '').strip()
                    if r and r not in topics:
                        topics.append(r)

                # Legacy/alternate shape: some roadmaps use 'modules' instead of 'chapters'
                # Extract module names or module-level topics when present.
                for m in data.get('modules', []) or []:
                    if isinstance(m, str):
                        mname = m.strip()
                        if mname and mname not in topics:
                            topics.append(mname)
                        continue
                    if isinstance(m, dict):
                        # module title/name
                        mname = m.get('title') or m.get('name') or None
                        if mname:
                            mname = (mname or '').strip()
                            if mname and mname not in topics:
                                topics.append(mname)
                        # module topics/lessons
                        for t in (m.get('topics') or m.get('lessons') or []) or []:
                            if isinstance(t, dict):
                                tn = t.get('title') or t.get('name') or ''
                            else:
                                tn = t
                            tn = (tn or '').strip()
                            if tn and tn not in topics:
                                topics.append(tn)

            return JsonResponse({'topics': topics})
        except Exception:
            return JsonResponse({'topics': []})
