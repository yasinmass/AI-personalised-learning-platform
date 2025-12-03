from django.urls import path
from . import views

urlpatterns = [
    path('list', views.list_courses, name='list_courses'),
    path('<int:course_id>', views.get_course, name='get_course'),
    path('<int:course_id>/enroll', views.enroll_course, name='enroll_course'),
    path('my-courses', views.get_user_courses, name='get_user_courses'),
]
