"""Create a superuser and sample CourseVideo entries for development.

Usage:
    python create_admin_and_sample_data.py

Environment variables (optional):
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL
    DJANGO_SUPERUSER_PASSWORD
    SAMPLE_COURSE_TITLE  (default: "Advanced JavaScript & Node.js")
"""
import os
import sys

# Ensure project path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, CourseVideo

# Read env vars or defaults
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123')

sample_course_title = os.environ.get('SAMPLE_COURSE_TITLE', 'Advanced JavaScript & Node.js')


def create_superuser():
    try:
        user = User.objects.filter(username=username).first()
        if user:
            print(f"Superuser '{username}' already exists (id={user.id}).")
            # ensure is_staff / superuser
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                print("Granted staff/superuser flags to existing user.")
            return user

        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Created superuser '{username}'.")
        return user
    except Exception as e:
        print('Failed to create superuser:', e)
        raise


def create_sample_videos(target_title):
    try:
        course = Course.objects.filter(title__icontains=target_title).first()
        if not course:
            print(f"No course found matching title '{target_title}'. Skipping sample videos.")
            return

        # Check existing sample videos for this course
        existing = CourseVideo.objects.filter(course=course)
        if existing.exists():
            print(f"Course '{course.title}' already has {existing.count()} CourseVideo entries. Skipping creation.")
            return

        samples = [
            {
                'title': 'JavaScript Fundamentals - Traversy Media',
                'url': 'https://www.youtube.com/watch?v=hdI2bqOjy3c',
                'topic': 'fundamentals'
            },
            {
                'title': 'Async JavaScript - The Net Ninja',
                'url': 'https://www.youtube.com/watch?v=PoRJizFVubE',
                'topic': 'asynchronous'
            },
            {
                'title': 'ES6 Features - Programming with Mosh',
                'url': 'https://www.youtube.com/watch?v=W6NZfCO5tTE',
                'topic': 'es6'
            }
        ]

        for s in samples:
            v = CourseVideo.objects.create(course=course, title=s['title'], url=s['url'], topic=s['topic'], is_active=True)
            print(f"Created CourseVideo: {v.title}")

        print(f"Created {len(samples)} sample videos for course '{course.title}'.")
    except Exception as e:
        print('Failed to create sample videos:', e)
        raise


if __name__ == '__main__':
    print('Creating superuser...')
    admin = create_superuser()
    print('\nCreating sample videos (if course exists and no videos present)...')
    create_sample_videos(sample_course_title)
    print('\nDone.');
