import openai
from django.conf import settings
import json
import logging
from .roadmap_generator import RoadmapGenerator
from .dynamic_resource_fetcher import DynamicResourceFetcher
from decouple import config

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using OpenAI with fallback to dynamic fetcher"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.roadmap_generator = RoadmapGenerator()
        
        # Initialize dynamic resource fetcher
        self.dynamic_fetcher = DynamicResourceFetcher(
            serper_api_key=config("SERPER_API_KEY", default=None),
            youtube_api_key=config("YOUTUBE_API_KEY", default=None),
            ollama_url=config("OLLAMA_URL", default="http://localhost:11434")
        )
        
        # Use dynamic mode if env var is set
        self.use_dynamic_mode = config("USE_DYNAMIC_RESOURCES", default="false").lower() == "true"
    
    def generate_assessment_questions(self, course_title, course_description):
        """Generate 10 MCQ questions for initial assessment"""
        prompt = f"""
        Generate 10 multiple-choice questions for assessing a learner's knowledge in "{course_title}".
        
        Course Description: {course_description}
        
        For each question, provide:
        1. Question text
        2. Four options (A, B, C, D)
        3. Correct answer
        4. Difficulty level (easy, medium, hard)
        
        Return the response as a JSON array with this structure:
        [
            {{
                "question": "Question text",
                "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
                "correct_answer": "A",
                "difficulty": "easy",
                "explanation": "Brief explanation"
            }}
        ]
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating assessment questions. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Parse JSON from response
            questions = json.loads(content)
            return questions
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._get_fallback_questions(course_title)
    
    def generate_roadmap(self, course_title, course_description, skill_level, duration_weeks):
        """Generate personalized learning roadmap based on skill level"""
        
        # Use dynamic mode if enabled
        if self.use_dynamic_mode:
            logger.info(f"Generating roadmap using DYNAMIC MODE for '{course_title}'")
            return self._generate_dynamic_roadmap(course_title, skill_level, duration_weeks)
        
        # Fallback to static roadmap generator
        logger.info(f"Generating roadmap using STATIC MODE for '{course_title}'")
        roadmap = self.roadmap_generator.generate_roadmap(
            course_title, skill_level, duration_weeks
        )
        
        if roadmap:
            return roadmap
        
        # If both fail, return fallback
        return self._get_fallback_roadmap(course_title, duration_weeks)
    
    def _generate_dynamic_roadmap(self, course_title, skill_level, duration_weeks):
        """Generate roadmap dynamically from real-time resources"""
        try:
            logger.info(f"Fetching dynamic resources for '{course_title}'")
            
            # Fetch resources dynamically
            dynamic_resources = self.dynamic_fetcher.get_complete_roadmap(
                course_title,
                skill_level
            )
            
            # Convert dynamic resources to roadmap format
            roadmap = self._convert_dynamic_to_roadmap(
                dynamic_resources,
                course_title,
                skill_level,
                duration_weeks
            )
            
            return roadmap
            
        except Exception as e:
            logger.error(f"Dynamic roadmap generation failed: {str(e)}")
            return self._get_fallback_roadmap(course_title, duration_weeks)
    
    def _convert_dynamic_to_roadmap(self, dynamic_resources, course_title, skill_level, duration_weeks):
        """Convert dynamic resource structure to roadmap format"""
        try:
            # Group resources into chapters
            chapters = []
            
            # Chapter 1: Video-based learning
            if dynamic_resources.get("videos"):
                chapters.append({
                    "chapter_number": 1,
                    "title": f"{course_title}: Video Tutorials",
                    "duration_hours": 8,
                    "topics": [f"{course_title} Overview"],
                    "learning_resources": [
                        {
                            "type": "youtube",
                            "title": video.get("title", ""),
                            "url": video.get("url", ""),
                            "channel": video.get("channel", ""),
                            "duration": video.get("duration", "Unknown")
                        }
                        for video in dynamic_resources.get("videos", [])
                    ],
                    "checkpoint": "Complete video tutorials",
                    "prerequisites": []
                })
            
            # Chapter 2: Documentation
            if dynamic_resources.get("documentation"):
                chapters.append({
                    "chapter_number": 2,
                    "title": f"{course_title}: Official Documentation",
                    "duration_hours": 6,
                    "topics": [f"{course_title} Concepts"],
                    "learning_resources": [
                        {
                            "type": "documentation",
                            "title": doc.get("title", ""),
                            "url": doc.get("url", ""),
                            "summary": doc.get("summary", "")
                        }
                        for doc in dynamic_resources.get("documentation", [])
                    ],
                    "checkpoint": "Read core documentation",
                    "prerequisites": ["Chapter 1"]
                })
            
            # Chapter 3: Blogs and Articles
            if dynamic_resources.get("blogs"):
                chapters.append({
                    "chapter_number": 3,
                    "title": f"{course_title}: Deep Dives & Articles",
                    "duration_hours": 5,
                    "topics": [f"Advanced {course_title} Topics"],
                    "learning_resources": [
                        {
                            "type": "blog",
                            "title": blog.get("title", ""),
                            "url": blog.get("url", ""),
                            "summary": blog.get("summary", "")
                        }
                        for blog in dynamic_resources.get("blogs", [])
                    ],
                    "checkpoint": "Complete article deep-dives",
                    "prerequisites": ["Chapter 2"]
                })
            
            # Calculate total hours
            total_hours = sum(ch.get("duration_hours", 0) for ch in chapters)
            
            roadmap = {
                "chapters": chapters,
                "total_duration_hours": total_hours,
                "summary": dynamic_resources.get("summary", f"Complete learning roadmap for {course_title}"),
                "skill_level": skill_level,
                "related_topics": dynamic_resources.get("related_topics", []),
                "generated_from": "dynamic_fetcher",
                "is_dynamic": True
            }
            
            return roadmap
            
        except Exception as e:
            logger.error(f"Failed to convert dynamic resources: {str(e)}")
            raise
    
    def generate_chapter_test(self, course_title, chapter_name):
        """Generate 3-5 MCQ questions for chapter test"""
        prompt = f"""
        Generate 4 multiple-choice questions to test understanding of "{chapter_name}" in "{course_title}".
        
        Return as JSON array with structure:
        [
            {{
                "question": "Question text",
                "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
                "correct_answer": "A",
                "explanation": "Explanation"
            }}
        ]
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating assessment questions. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            return questions
        except Exception as e:
            print(f"Error generating chapter test: {str(e)}")
            return []
    
    def generate_adaptive_recommendations(self, weak_areas, user_skill_level):
        """Generate recommendations to update roadmap based on weak areas"""
        prompt = f"""
        A learner at {user_skill_level} level has identified these weak areas:
        {', '.join(weak_areas)}
        
        Provide recommendations to improve the learning roadmap:
        1. Additional chapters to focus on
        2. Extra resources per weak area
        3. Adjusted time allocation
        4. Suggested revision topics
        
        Return as JSON:
        {{
            "additional_chapters": [],
            "extra_resources_per_topic": {{}},
            "time_adjustment": {{"increase_hours": 0, "reason": ""}},
            "revision_topics": []
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an educational advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            recommendations = json.loads(content)
            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return {}
    
    @staticmethod
    def _get_fallback_questions(course_title):
        """Fallback questions if LLM fails - returns 10 questions"""
        return [
            {
                "question": f"What is the primary focus of {course_title}?",
                "options": {
                    "A": "Fundamentals and core concepts",
                    "B": "Advanced techniques only",
                    "C": "Tools and software specific",
                    "D": "Historical overview"
                },
                "correct_answer": "A",
                "difficulty": "easy",
                "explanation": "Most introductory courses focus on fundamentals and core concepts first."
            },
            {
                "question": f"Which of the following is a key benefit of learning {course_title}?",
                "options": {
                    "A": "Enhanced problem-solving skills",
                    "B": "Guaranteed high salary",
                    "C": "No need for further learning",
                    "D": "Immediate job placement"
                },
                "correct_answer": "A",
                "difficulty": "easy",
                "explanation": "Learning any subject enhances problem-solving and critical thinking skills."
            },
            {
                "question": f"What is the typical duration to master {course_title}?",
                "options": {
                    "A": "3-6 months of consistent learning",
                    "B": "1 week",
                    "C": "Instant understanding",
                    "D": "Never possible to master"
                },
                "correct_answer": "A",
                "difficulty": "medium",
                "explanation": "Most technical skills require 3-6 months of consistent practice and learning."
            },
            {
                "question": f"Which learning method is most effective for {course_title}?",
                "options": {
                    "A": "Hands-on practice combined with theory",
                    "B": "Passive reading only",
                    "C": "Listening to lectures only",
                    "D": "Memorization without practice"
                },
                "correct_answer": "A",
                "difficulty": "medium",
                "explanation": "Active learning through hands-on practice combined with theory is the most effective method."
            },
            {
                "question": f"What prerequisite knowledge is typically needed for {course_title}?",
                "options": {
                    "A": "Depends on the course level and objectives",
                    "B": "No prerequisites needed",
                    "C": "Advanced degree required",
                    "D": "Decades of experience"
                },
                "correct_answer": "A",
                "difficulty": "medium",
                "explanation": "Prerequisites vary based on course difficulty level and learning objectives."
            },
            {
                "question": f"How can you apply knowledge from {course_title} in practice?",
                "options": {
                    "A": "Through real-world projects and hands-on assignments",
                    "B": "Only in theoretical discussions",
                    "C": "Cannot be applied practically",
                    "D": "Only in academic settings"
                },
                "correct_answer": "A",
                "difficulty": "medium",
                "explanation": "Real-world projects and practical assignments are the best way to apply learned concepts."
            },
            {
                "question": f"What is the role of feedback in learning {course_title}?",
                "options": {
                    "A": "Crucial for identifying gaps and improving performance",
                    "B": "Not important for learning",
                    "C": "Only needed for beginners",
                    "D": "Discourages learners"
                },
                "correct_answer": "A",
                "difficulty": "hard",
                "explanation": "Feedback is essential for identifying knowledge gaps and continuous improvement."
            },
            {
                "question": f"Which of these is a common challenge when learning {course_title}?",
                "options": {
                    "A": "Balancing theory with practical application",
                    "B": "There are no challenges",
                    "C": "Too much free time",
                    "D": "Lack of resources"
                },
                "correct_answer": "A",
                "difficulty": "hard",
                "explanation": "Most learners struggle with balancing theoretical knowledge and practical implementation."
            },
            {
                "question": f"What is the best approach to master {course_title}?",
                "options": {
                    "A": "Consistent practice, revision, and real-world application",
                    "B": "One-time learning is enough",
                    "C": "Cramming before assessments",
                    "D": "Copying solutions from others"
                },
                "correct_answer": "A",
                "difficulty": "hard",
                "explanation": "Mastery requires consistent practice, regular revision, and application to real scenarios."
            },
            {
                "question": f"How can you stay updated with the latest trends in {course_title}?",
                "options": {
                    "A": "Through continuous learning, online communities, and industry resources",
                    "B": "One-time learning is sufficient",
                    "C": "No need to stay updated",
                    "D": "Only through paid premium courses"
                },
                "correct_answer": "A",
                "difficulty": "hard",
                "explanation": "Staying updated requires engaging with communities, reading blogs, and continuous learning."
            }
        ]
    
    @staticmethod
    def _get_fallback_roadmap(course_title, duration_weeks):
        """Generate comprehensive roadmap using RoadmapGenerator"""
        generator = RoadmapGenerator()
        return generator.generate_roadmap(course_title, 'beginner', duration_weeks)
