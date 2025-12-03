"""
Django management command to load initial course data
Run: python manage.py create_initial_data
"""

from django.core.management.base import BaseCommand
from courses.models import Course


class Command(BaseCommand):
    help = 'Create initial course data'

    def handle(self, *args, **options):
        courses_data = [
            {
                'title': 'Python Programming Basics',
                'description': 'Master Python fundamentals including data types, control structures, functions, and object-oriented programming. Perfect for beginners wanting to start their coding journey.',
                'difficulty': 'beginner',
                'duration_weeks': 12,
            },
            {
                'title': 'Artificial Intelligence & Machine Learning',
                'description': 'Learn AI and ML concepts, algorithms, neural networks, and practical implementations using TensorFlow and scikit-learn. Build intelligent applications from scratch.',
                'difficulty': 'intermediate',
                'duration_weeks': 14,
            },
            {
                'title': 'Full Stack Web Development',
                'description': 'Complete guide to modern web development. Learn frontend (HTML, CSS, JavaScript, React) and backend (Node.js, Express, databases) to build complete web applications.',
                'difficulty': 'intermediate',
                'duration_weeks': 16,
            },
            {
                'title': 'Cloud Computing with AWS',
                'description': 'Master Amazon Web Services (AWS). Learn about EC2, S3, RDS, Lambda, and deployment strategies. Get hands-on experience with cloud infrastructure.',
                'difficulty': 'intermediate',
                'duration_weeks': 10,
            },
            {
                'title': 'Data Science & Analytics',
                'description': 'Become a data scientist. Learn data analysis, visualization, statistical methods, and real-world applications using Python and popular libraries.',
                'difficulty': 'intermediate',
                'duration_weeks': 14,
            },
            {
                'title': 'DevOps & Container Technologies',
                'description': 'Master Docker, Kubernetes, and CI/CD pipelines. Learn containerization, orchestration, and continuous deployment for modern applications.',
                'difficulty': 'advanced',
                'duration_weeks': 12,
            },
            {
                'title': 'Cybersecurity Fundamentals',
                'description': 'Essential cybersecurity concepts, network security, ethical hacking, and security best practices. Protect systems and data from threats.',
                'difficulty': 'intermediate',
                'duration_weeks': 13,
            },
            {
                'title': 'Advanced JavaScript & Node.js',
                'description': 'Deep dive into JavaScript ES6+, asynchronous programming, Node.js backend development, and building scalable server applications.',
                'difficulty': 'advanced',
                'duration_weeks': 11,
            },
        ]

        created_count = 0
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'difficulty': course_data['difficulty'],
                    'duration_weeks': course_data['duration_weeks'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {course.title}')
                )
            else:
                self.stdout.write(f'- Already exists: {course.title}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {created_count} new courses!')
        )
