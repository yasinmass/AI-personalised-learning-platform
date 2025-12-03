from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Course, UserCourse
from users.models import UserProfile
from .serializers import CourseSerializer, UserCourseSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def list_courses(request):
    """List all available courses"""
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_course(request, course_id):
    """Get course details"""
    try:
        course = Course.objects.get(id=course_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    """Enroll user in a course"""
    try:
        course = Course.objects.get(id=course_id)
        user_profile = UserProfile.objects.get(user=request.user)
        
        user_course, created = UserCourse.objects.get_or_create(
            user=user_profile,
            course=course,
            defaults={'status': 'enrolled'}
        )
        
        if not created:
            return Response({'message': 'Already enrolled in this course'}, status=status.HTTP_200_OK)
        
        serializer = UserCourseSerializer(user_course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_courses(request):
    """Get all courses enrolled by user"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_courses = UserCourse.objects.filter(user=user_profile)
        serializer = UserCourseSerializer(user_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
