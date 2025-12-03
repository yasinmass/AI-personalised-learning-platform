from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .dynamic_resource_views import DynamicResourceViewSet

router = DefaultRouter()
router.register(r'resources', DynamicResourceViewSet, basename='resources')

urlpatterns = [
    path('generate-questions', views.generate_assessment_questions, name='generate_questions'),
    path('submit', views.submit_assessment, name='submit_assessment'),
    path('generate-roadmap', views.generate_roadmap, name='generate_roadmap'),
    path('check-status', views.check_assessment_status, name='check_assessment_status'),
    path('get-roadmap/<int:roadmap_id>', views.get_roadmap_detail, name='get_roadmap_detail'),
    path('my-roadmaps', views.get_user_roadmaps, name='get_user_roadmaps'),
] + router.urls
