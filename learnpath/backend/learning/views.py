from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from datetime import timedelta
from users.models import UserProfile
from assessments.models import Roadmap
from .models import ChapterProgress, ChapterTest, LearningActivity
from .serializers import ChapterProgressSerializer, ChapterTestDetailSerializer, LearningActivitySerializer
from assessments.llm_service import LLMService

llm_service = LLMService()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_roadmap_chapters(request, roadmap_id):
    """Get all chapters of a roadmap"""
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id, user__user=request.user)
        chapters_data = roadmap.roadmap_data.get('chapters', [])
        
        chapter_progress = ChapterProgress.objects.filter(roadmap=roadmap)
        serializer = ChapterProgressSerializer(chapter_progress, many=True)
        
        return Response({
            'roadmap_id': roadmap.id,
            'chapters': serializer.data,
            'total_chapters': len(chapters_data)
        }, status=status.HTTP_200_OK)
    except Roadmap.DoesNotExist:
        return Response({'error': 'Roadmap not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_chapter_progress(request):
    """Update chapter progress and time spent"""
    roadmap_id = request.data.get('roadmap_id')
    chapter_number = request.data.get('chapter_number')
    status_update = request.data.get('status')  # 'in_progress' or 'completed'
    time_spent = request.data.get('time_spent_minutes', 0)
    
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id, user__user=request.user)
        user_profile = roadmap.user
        
        chapter_progress, created = ChapterProgress.objects.get_or_create(
            roadmap=roadmap,
            chapter_number=chapter_number,
            defaults={'user': user_profile}
        )
        
        # Update progress
        chapter_progress.status = status_update
        chapter_progress.time_spent_minutes += int(time_spent)
        chapter_progress.last_accessed = timezone.now()
        
        if status_update == 'completed':
            chapter_progress.completion_date = timezone.now()
        
        chapter_progress.save()
        
        # Log activity
        LearningActivity.objects.create(
            user=user_profile,
            roadmap=roadmap,
            activity_type='time_logged',
            chapter_name=chapter_progress.chapter_name,
            duration_minutes=time_spent,
            details={'chapter_number': chapter_number}
        )
        
        serializer = ChapterProgressSerializer(chapter_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Roadmap.DoesNotExist:
        return Response({'error': 'Roadmap not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_chapter_test(request):
    """Generate chapter test questions"""
    roadmap_id = request.data.get('roadmap_id')
    chapter_number = request.data.get('chapter_number')
    
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id, user__user=request.user)
        user_profile = roadmap.user
        
        chapters_data = roadmap.roadmap_data.get('chapters', [])
        if chapter_number > len(chapters_data):
            return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)
        
        chapter_info = chapters_data[chapter_number - 1]
        chapter_name = chapter_info.get('title', f'Chapter {chapter_number}')
        course_title = roadmap.course.title
        
        # Generate test questions using LLM
        questions = llm_service.generate_chapter_test(course_title, chapter_name)
        
        # Get or create chapter progress
        chapter_progress, _ = ChapterProgress.objects.get_or_create(
            roadmap=roadmap,
            chapter_number=chapter_number,
            defaults={'user': user_profile, 'chapter_name': chapter_name}
        )
        
        # Create test record
        test = ChapterTest.objects.create(
            user=user_profile,
            roadmap=roadmap,
            chapter_progress=chapter_progress,
            chapter_name=chapter_name,
            total_questions=len(questions),
            questions_data={'questions': questions}
        )
        
        return Response({
            'test_id': test.id,
            'chapter_number': chapter_number,
            'chapter_name': chapter_name,
            'questions': questions,
            'total_questions': len(questions)
        }, status=status.HTTP_200_OK)
    except Roadmap.DoesNotExist:
        return Response({'error': 'Roadmap not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_chapter_test(request):
    """Submit chapter test and update progress"""
    test_id = request.data.get('test_id')
    answers = request.data.get('answers')  # Dict: {question_index: selected_answer}
    
    try:
        test = ChapterTest.objects.get(id=test_id, user__user=request.user)
        questions = test.questions_data.get('questions', [])
        
        # Calculate score
        correct_count = 0
        for idx, answer in enumerate(answers.items()):
            question_idx = int(answer[0])
            selected_answer = answer[1]
            
            if question_idx < len(questions):
                correct_answer = questions[question_idx]['correct_answer']
                if selected_answer == correct_answer:
                    correct_count += 1
        
        # Update test
        test.score = correct_count
        test.percentage = (correct_count / len(questions)) * 100
        test.save()
        
        # Log activity
        LearningActivity.objects.create(
            user=test.user,
            roadmap=test.roadmap,
            activity_type='test_taken',
            chapter_name=test.chapter_name,
            details={
                'test_id': test.id,
                'score': test.score,
                'percentage': test.percentage
            }
        )
        
        serializer = ChapterTestDetailSerializer(test)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChapterTest.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_dashboard(request, roadmap_id):
    """Get learning dashboard data for user"""
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id, user__user=request.user)
        user_profile = roadmap.user
        
        # Chapter statistics
        total_chapters = len(roadmap.roadmap_data.get('chapters', []))
        completed_chapters = ChapterProgress.objects.filter(
            roadmap=roadmap,
            status='completed'
        ).count()
        
        # Total time spent
        total_time = ChapterProgress.objects.filter(
            roadmap=roadmap
        ).aggregate(
            total=models.Sum('time_spent_minutes')
        )['total'] or 0
        
        # Recent activity
        activities = LearningActivity.objects.filter(
            roadmap=roadmap
        ).order_by('-created_at')[:10]
        
        # Test scores
        tests = ChapterTest.objects.filter(roadmap=roadmap)
        avg_score = 0
        if tests.exists():
            avg_score = tests.aggregate(
                avg=models.Avg('percentage')
            )['avg'] or 0
        
        # Weak areas
        weak_areas = []
        for test in tests:
            if test.percentage < 60:
                weak_areas.append({
                    'chapter': test.chapter_name,
                    'score': test.percentage
                })
        
        activities_serializer = LearningActivitySerializer(activities, many=True)
        
        return Response({
            'roadmap_id': roadmap.id,
            'course_title': roadmap.course.title,
            'progress': {
                'total_chapters': total_chapters,
                'completed_chapters': completed_chapters,
                'progress_percentage': (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
            },
            'time_tracking': {
                'total_hours': total_time / 60,
                'total_minutes': total_time,
            },
            'performance': {
                'average_test_score': avg_score,
                'weak_areas': weak_areas,
            },
            'recent_activity': activities_serializer.data
        }, status=status.HTTP_200_OK)
    except Roadmap.DoesNotExist:
        return Response({'error': 'Roadmap not found'}, status=status.HTTP_404_NOT_FOUND)
