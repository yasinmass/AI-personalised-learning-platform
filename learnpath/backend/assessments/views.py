from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from courses.models import Course, UserCourse
from users.models import UserProfile
from .models import Assessment, Roadmap
from .serializers import AssessmentDetailSerializer, RoadmapSerializer
from .llm_service import LLMService
from django.conf import settings
import concurrent.futures
import threading

llm_service = LLMService()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_assessment_questions(request):
    """Generate 10 MCQ questions for course assessment"""
    course_id = request.data.get('course_id')
    
    try:
        course = Course.objects.get(id=course_id)
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Generate questions using LLM
        questions = llm_service.generate_assessment_questions(
            course.title,
            course.description
        )
        
        # Create assessment record
        assessment = Assessment.objects.create(
            user=user_profile,
            course=course,
            questions_data={'questions': questions}
        )
        
        return Response({
            'assessment_id': assessment.id,
            'course_id': course.id,
            'questions': questions,
            'total_questions': len(questions)
        }, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """Submit assessment answers and calculate score"""
    assessment_id = request.data.get('assessment_id')
    answers = request.data.get('answers')  # Dict: {question_index: selected_answer}
    
    try:
        assessment = Assessment.objects.get(id=assessment_id, user__user=request.user)
        questions = assessment.questions_data.get('questions', [])
        
        # Calculate score
        correct_count = 0
        for idx, answer in enumerate(answers.items()):
            question_idx = int(answer[0])
            selected_answer = answer[1]
            
            if question_idx < len(questions):
                correct_answer = questions[question_idx]['correct_answer']
                if selected_answer == correct_answer:
                    correct_count += 1
        
        # Update assessment
        assessment.score = correct_count
        assessment.percentage = (correct_count / len(questions)) * 100
        assessment.calculate_skill_level()
        assessment.save()
        
        # Update user course status if enrolled
        try:
            user_course = UserCourse.objects.get(
                user__user=request.user,
                course=assessment.course
            )
            user_course.status = 'in_progress'
            user_course.save()
        except UserCourse.DoesNotExist:
            pass
        
        return Response({
            'assessment_id': assessment.id,
            'score': assessment.score,
            'total_questions': assessment.total_questions,
            'percentage': assessment.percentage,
            'skill_level': assessment.skill_level
        }, status=status.HTTP_200_OK)
    except Assessment.DoesNotExist:
        return Response({'error': 'Assessment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_roadmap(request):
    """Generate personalized roadmap based on assessment"""
    assessment_id = request.data.get('assessment_id')
    duration_weeks = request.data.get('duration_weeks', 12)
    user_answers = request.data.get('user_answers', {})
    
    try:
        assessment = Assessment.objects.get(id=assessment_id, user__user=request.user)
        course = assessment.course
        user_profile = assessment.user
        
        # Determine assigned topics for this user (admin-assigned)
        assigned_topics_list = []
        try:
            profile_obj = UserProfile.objects.get(user=request.user)
            assigned_raw = (profile_obj.assigned_topics or '').strip()
            if assigned_raw:
                assigned_topics_list = [t.strip() for t in assigned_raw.split(',') if t.strip()]
        except Exception:
            assigned_topics_list = []

        # Check if roadmap already exists
        existing_roadmap = Roadmap.objects.filter(assessment=assessment).first()
        if existing_roadmap:
            serializer = RoadmapSerializer(existing_roadmap)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Attempt dynamic LLM-based generation (do this even in DEBUG so developers
        # can see dynamic output). Force the llm_service into dynamic mode for
        # this call to ensure live resources are used. If dynamic generation
        # fails or times out, a quick fallback roadmap will be used.
        try:
            llm_service.use_dynamic_mode = True
        except Exception:
            pass

        def _generate():
            # Prefer assigned topics or user answers for personalization
            personalization_input = user_answers or assigned_topics_list or None
            return llm_service.generate_roadmap(
                course.title,
                course.description,
                assessment.skill_level,
                duration_weeks,
                user_answers=personalization_input,
                course_data=assessment.questions_data
            )

        roadmap_data = None
        # Use a thread pool to limit blocking time
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_generate)
            try:
                # Wait up to 10 seconds for dynamic generation (keep below client timeout)
                roadmap_data = future.result(timeout=10)
            except concurrent.futures.TimeoutError:
                # Dynamic generation timed out — return a lightweight quick fallback roadmap
                roadmap_data = {
                    "chapters": [
                        {
                            "chapter_number": 1,
                            "title": f"Introduction to {course.title}",
                            "duration_hours": max(1, int(duration_weeks * 0.1)),
                            "topics": [course.title],
                            "learning_resources": [],
                            "checkpoint": "Start learning",
                            "prerequisites": [],
                            "personalized_for_skill_level": assessment.skill_level
                        }
                    ],
                    "total_duration_hours": max(1, int(duration_weeks * 2)),
                    "summary": f"Quick starter roadmap for {course.title}",
                    "skill_level": assessment.skill_level,
                    "weak_topics": [],
                    "user_answers_integrated": False,
                    "related_topics": [],
                    "generated_from": "quick_fallback",
                    "is_dynamic": False
                }
            except Exception as e:
                # Unexpected error from generation — try static fallback
                try:
                    roadmap_data = llm_service._fallback_to_static_roadmap(
                        course.title,
                        assessment.skill_level,
                        duration_weeks,
                        user_answers=user_answers
                    )
                except Exception:
                    roadmap_data = None

        # Ensure roadmap_data is always a dict before saving
        if not isinstance(roadmap_data, dict):
            roadmap_data = {
                "chapters": [
                    {
                        "chapter_number": 1,
                        "title": f"Introduction to {course.title}",
                        "duration_hours": max(1, int(duration_weeks * 0.1)),
                        "topics": [course.title],
                        "learning_resources": [],
                        "checkpoint": "Start learning",
                        "prerequisites": [],
                        "personalized_for_skill_level": assessment.skill_level
                    }
                ],
                "total_duration_hours": max(1, int(duration_weeks * 2)),
                "summary": f"Quick starter roadmap for {course.title}",
                "skill_level": assessment.skill_level,
                "weak_topics": [],
                "user_answers_integrated": False,
                "related_topics": [],
                "generated_from": "quick_fallback",
                "is_dynamic": False
            }
        
        # Create roadmap record
        roadmap = Roadmap.objects.create(
            user=user_profile,
            course=course,
            assessment=assessment,
            skill_level=assessment.skill_level,
            duration_weeks=duration_weeks,
            roadmap_data=roadmap_data
        )
        
        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Assessment.DoesNotExist:
        return Response({'error': 'Assessment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_assessment_status(request):
    """Check if user has completed assessment for a course"""
    course_id = request.query_params.get('course_id')
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        course = Course.objects.get(id=course_id)
        
        # Check if a roadmap exists for this user and course
        # If roadmap exists, it means assessment was completed and roadmap was generated
        roadmap = Roadmap.objects.filter(
            user=user_profile,
            course=course
        ).first()
        
        if roadmap:
            return Response({
                'assessment_completed': True,
                'assessment_id': roadmap.assessment.id,
                'roadmap_id': roadmap.id,
                'skill_level': roadmap.skill_level
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'assessment_completed': False,
                'assessment_id': None,
                'roadmap_id': None
            }, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_roadmap_detail(request, roadmap_id):
    """Get detailed roadmap information"""
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id)
        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Roadmap.DoesNotExist:
        return Response({'error': 'Roadmap not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_roadmaps(request):
    """Get all roadmaps for authenticated user"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        roadmaps = Roadmap.objects.filter(user=user_profile)
        serializer = RoadmapSerializer(roadmaps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
