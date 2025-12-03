from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect root to frontend dev server
    path('', RedirectView.as_view(url='http://localhost:8001/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assessment/', include('assessments.urls')),
    path('api/learning/', include('learning.urls')),
]
