from django.urls import path
from . import views

urlpatterns = [
    path('chapters/<int:roadmap_id>', views.get_roadmap_chapters, name='get_chapters'),
    path('track-progress', views.track_chapter_progress, name='track_progress'),
    path('chapter-test/generate', views.generate_chapter_test, name='generate_chapter_test'),
    path('chapter-test/submit', views.submit_chapter_test, name='submit_chapter_test'),
    path('dashboard/<int:roadmap_id>', views.get_learning_dashboard, name='get_dashboard'),
]
