"""
Django management command to create or update admin user
Run: python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update admin user'

    def handle(self, *args, **options):
        admin_email = 'admin@example.com'
        admin_password = 'admin123'
        
        try:
            # Try to get existing admin user
            admin_user = User.objects.get(email=admin_email)
            # Update password
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated admin user: {admin_email}')
            )
        except User.DoesNotExist:
            # Create new admin user
            admin_user = User.objects.create_superuser(
                username='admin',
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created admin user: {admin_email}')
            )
        
        # Also create a regular user for testing
        try:
            test_user = User.objects.get(email='testuser@example.com')
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated test user: testuser@example.com')
            )
        except User.DoesNotExist:
            test_user = User.objects.create_user(
                username='testuser',
                email='testuser@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created test user: testuser@example.com')
            )
        
        self.stdout.write(self.style.SUCCESS('\n=== Credentials ==='))
        self.stdout.write(f'Admin: {admin_email} / {admin_password}')
        self.stdout.write(f'Test User: testuser@example.com / testpass123')
        self.stdout.write(self.style.WARNING('\nNote: Change these in production!'))
