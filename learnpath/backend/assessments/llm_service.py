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
    
    def generate_roadmap(self, course_title, course_description, skill_level, duration_weeks, user_answers=None, course_data=None):
        """
        Generate personalized learning roadmap based on skill level and user answers
        
        Args:
            course_title: Title of the course
            course_description: Description of the course
            skill_level: User's skill level (beginner, intermediate, advanced)
            duration_weeks: Desired duration in weeks
            user_answers: Dictionary of user's assessment answers for personalization
            course_data: Assessment questions data for context
        
        Priority:
        1. If USE_DYNAMIC_RESOURCES=true, try dynamic (with fallback to static if it fails)
        2. If USE_DYNAMIC_RESOURCES=false, use static roadmap
        3. Check DB for saved roadmap
        4. Use fallback placeholder
        """
        
        # Prefer static/safe route unless explicitly enabled
        if not self.use_dynamic_mode:
            logger.info(f"Dynamic mode disabled. Using static roadmap for '{course_title}'")
            
            # Try static generator first with user answers for personalization
            roadmap = self.roadmap_generator.generate_roadmap(
                course_title, skill_level, duration_weeks, user_answers=user_answers
            )
            if roadmap:
                return roadmap
            
            # Then try DB fallback
            logger.info(f"Static roadmap not found. Checking DB fallback for '{course_title}'")
            db_roadmap = self.dynamic_fetcher._db_fallback_roadmap(course_title, skill_level)
            if db_roadmap:
                return db_roadmap
            
            # Final fallback
            return self._get_fallback_roadmap(course_title, duration_weeks)
        
        # Dynamic mode is explicitly enabled
        logger.info(f"Dynamic mode enabled. Generating roadmap for '{course_title}'")
        return self._generate_dynamic_roadmap(course_title, skill_level, duration_weeks, user_answers=user_answers, course_data=course_data)
    
    def _generate_dynamic_roadmap(self, course_title, skill_level, duration_weeks, user_answers=None, course_data=None):
        """Generate roadmap dynamically from real-time resources with fallback to static"""
        try:
            logger.info(f"Fetching dynamic resources for '{course_title}'")
            
            # Fetch resources dynamically
            dynamic_resources = self.dynamic_fetcher.get_complete_roadmap(
                course_title,
                skill_level,
                user_answers=user_answers  # Pass user answers for context-aware resource selection
            )
            
            # Check if dynamic resources have actual content (not just errors)
            has_content = False
            try:
                # dynamic_resources can include videos, documentation, blogs, summary or related_topics
                if isinstance(dynamic_resources, dict):
                    if dynamic_resources.get('videos') or dynamic_resources.get('documentation') or dynamic_resources.get('blogs') or dynamic_resources.get('summary') or dynamic_resources.get('related_topics'):
                        has_content = True
            except Exception:
                has_content = False

            if "error" in dynamic_resources or not has_content:
                logger.warning(f"Dynamic resources incomplete for '{course_title}'. Falling back to static.")
                return self._fallback_to_static_roadmap(course_title, skill_level, duration_weeks, user_answers=user_answers)
            
            # Use LLM to convert dynamic resources and course info into a rich chapter/topic roadmap
            try:
                roadmap = self._build_roadmap_with_llm(
                    course_title,
                    course_data or {},
                    dynamic_resources,
                    skill_level,
                    duration_weeks,
                    user_answers=user_answers
                )
                return roadmap
            except Exception as e:
                logger.warning(f"LLM chapter generation failed, falling back to converter: {e}")
                roadmap = self._convert_dynamic_to_roadmap(
                    dynamic_resources,
                    course_title,
                    skill_level,
                    duration_weeks,
                    user_answers=user_answers,
                    course_data=course_data
                )
                return roadmap
            
        except Exception as e:
            logger.error(f"Dynamic roadmap generation failed: {str(e)}. Falling back to static.")
            return self._fallback_to_static_roadmap(course_title, skill_level, duration_weeks, user_answers=user_answers)
    
    def _fallback_to_static_roadmap(self, course_title, skill_level, duration_weeks, user_answers=None):
        """Fallback to static roadmap generator when dynamic fails"""
        try:
            logger.info(f"Using static roadmap generator for '{course_title}'")
            roadmap = self.roadmap_generator.generate_roadmap(
                course_title, skill_level, duration_weeks, user_answers=user_answers
            )
            if roadmap:
                return roadmap
        except Exception as e:
            logger.error(f"Static roadmap generation also failed: {str(e)}")
        
        return self._get_fallback_roadmap(course_title, duration_weeks)
    
    def _convert_dynamic_to_roadmap(self, dynamic_resources, course_title, skill_level, duration_weeks, user_answers=None, course_data=None):
        """Convert dynamic resource structure to roadmap format, personalized with user answers"""
        try:
            # Identify weak areas from user answers for personalization
            weak_topics = []
            if user_answers:
                # Identify topics where user answered incorrectly
                logger.info(f"Analyzing user answers to identify weak areas for personalization")
                # Note: Actual mapping of answers to topics depends on question structure
                # For now, we'll use skill_level as the primary personalization factor
                weak_topics = self._identify_weak_topics(user_answers, course_data)
            
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
                            "duration": video.get("duration", "Unknown"),
                            "relevance": "high" if any(weak in video.get("title", "").lower() for weak in weak_topics) else "medium"
                        }
                        for video in dynamic_resources.get("videos", [])
                    ],
                    "checkpoint": "Complete video tutorials",
                    "prerequisites": [],
                    "personalized_for_skill_level": skill_level
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
                            "summary": doc.get("summary", ""),
                            "relevance": "high" if any(weak in doc.get("title", "").lower() for weak in weak_topics) else "medium"
                        }
                        for doc in dynamic_resources.get("documentation", [])
                    ],
                    "checkpoint": "Read core documentation",
                    "prerequisites": ["Chapter 1"],
                    "personalized_for_skill_level": skill_level
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
                            "summary": blog.get("summary", ""),
                            "relevance": "high" if any(weak in blog.get("title", "").lower() for weak in weak_topics) else "medium"
                        }
                        for blog in dynamic_resources.get("blogs", [])
                    ],
                    "checkpoint": "Complete article deep-dives",
                    "prerequisites": ["Chapter 2"],
                    "personalized_for_skill_level": skill_level
                })
            
            # Calculate total hours
            total_hours = sum(ch.get("duration_hours", 0) for ch in chapters)
            
            roadmap = {
                "chapters": chapters,
                "total_duration_hours": total_hours,
                "summary": dynamic_resources.get("summary", f"Complete learning roadmap for {course_title}"),
                "skill_level": skill_level,
                "weak_topics": weak_topics,
                "user_answers_integrated": bool(user_answers),
                "related_topics": dynamic_resources.get("related_topics", []),
                "generated_from": "dynamic_fetcher",
                "is_dynamic": True
            }
            
            logger.info(f"Converted dynamic resources to roadmap with {len(chapters)} chapters")
            return roadmap
            
        except Exception as e:
            logger.error(f"Failed to convert dynamic resources: {str(e)}")
            raise
    
    def _identify_weak_topics(self, user_answers, course_data):
        """Identify weak topics from user answers for targeted learning"""
        weak_topics = []
        try:
            # Simple extraction of topic keywords from answers
            # In a more sophisticated system, this would map answers to specific topics
            if isinstance(user_answers, dict):
                # Get keys (question numbers) where user might have answered incorrectly
                # For now, return empty list - this can be enhanced with actual answer mapping
                pass
        except Exception as e:
            logger.error(f"Error identifying weak topics: {str(e)}")
        
        return weak_topics

    def _build_roadmap_with_llm(self, course_title, course_data, dynamic_resources, skill_level, duration_weeks, user_answers=None):
        """Ask the LLM to produce chapters and topics, then attach admin videos to matching topics.

        Returns a structured roadmap dict suitable for saving to DB and returning via API.
        """
        import re
        # Prepare context for LLM
        prompt_parts = []
        prompt_parts.append(f"Course title: {course_title}")
        if course_data and isinstance(course_data, dict):
            brief = course_data.get('questions', [])
            prompt_parts.append(f"Assessment context: {len(brief)} questions available.")
        prompt_parts.append(f"Skill level: {skill_level}")
        prompt_parts.append(f"Duration weeks: {duration_weeks}")
        if user_answers:
            prompt_parts.append(f"User answers provided for personalization.")

        # Include short lists of dynamic resources as context (titles + urls)
        def summarize_list(items, key_fields):
            lines = []
            for it in items[:8]:
                parts = []
                for k in key_fields:
                    if it.get(k):
                        parts.append(str(it.get(k)))
                lines.append(' - '.join(parts))
            return '\n'.join(lines)

        if isinstance(dynamic_resources, dict):
            if dynamic_resources.get('videos'):
                prompt_parts.append("Videos:\n" + summarize_list(dynamic_resources.get('videos', []), ['title', 'url']))
            if dynamic_resources.get('documentation'):
                prompt_parts.append("Docs:\n" + summarize_list(dynamic_resources.get('documentation', []), ['title', 'url']))
            if dynamic_resources.get('blogs'):
                prompt_parts.append("Blogs:\n" + summarize_list(dynamic_resources.get('blogs', []), ['title', 'url']))

        instruction = (
            "Using the above context, generate a learning roadmap as JSON. "
            "The JSON must be valid and use this structure:\n" 
            "{\n  \"chapters\": [\n    {\"chapter_number\": 1, \"title\": \"...\", \"duration_hours\": 5, \"topics\": [\"t1\", \"t2\"], \"learning_resources\": [{\"type\": \"youtube|documentation|blog|tool|project\", \"title\": \"...\", \"url\": \"...\", \"summary\": \"...\"}], \"checkpoint\": \"...\", \"prerequisites\": [] }\n  ],\n  \"total_duration_hours\": 10,\n  \"summary\": \"...\",\n  \"skill_level\": \"...\",\n  \"weak_topics\": [],\n  \"user_answers_integrated\": true,\n  \"related_topics\": [],\n  \"generated_from\": \"llm_dynamic\",\n  \"is_dynamic\": true\n}"
        )

        messages = [
            {"role": "system", "content": "You are an expert curriculum designer. Produce clean JSON only."},
            {"role": "user", "content": '\n'.join(prompt_parts) + '\n\n' + instruction}
        ]

        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=1500
            )
            content = resp.choices[0].message.content
            # Ensure we extract the JSON blob
            try:
                roadmap_obj = json.loads(content)
            except Exception:
                # Try to extract JSON substring
                m = re.search(r"(\{\s*\"chapters\"[\s\S]+\})", content)
                if m:
                    roadmap_obj = json.loads(m.group(1))
                else:
                    raise

            # Attach admin CourseVideo items to matching LLM topics
            try:
                from courses.models import CourseVideo
                # For each chapter and each topic, find admin videos matching topic
                for ch in roadmap_obj.get('chapters', []):
                    ch_topics = ch.get('topics') or []
                    if not isinstance(ch_topics, list):
                        ch_topics = [ch_topics]
                    attached = ch.get('learning_resources', []) or []
                    for topic in ch_topics:
                        qset = CourseVideo.objects.filter(is_active=True, topic__icontains=topic)
                        for v in qset:
                            # Avoid duplicates by URL
                            exists = any((res.get('url') or '') == (v.url or '') for res in attached)
                            if not exists:
                                attached.append({
                                    'type': 'youtube' if ('youtube.com' in (v.url or '') or 'youtu.be' in (v.url or '')) else 'video',
                                    'title': v.title or '',
                                    'url': v.url,
                                    'summary': '',
                                    'source': 'admin'
                                })
                    ch['learning_resources'] = attached
            except Exception as e:
                logger.debug(f"Failed to attach admin videos: {e}")

            # Ensure required top-level fields
            roadmap_obj.setdefault('skill_level', skill_level)
            roadmap_obj.setdefault('user_answers_integrated', bool(user_answers))
            roadmap_obj.setdefault('generated_from', 'llm_dynamic')
            roadmap_obj.setdefault('is_dynamic', True)

            # Calculate total_duration_hours if missing
            if 'total_duration_hours' not in roadmap_obj:
                total = 0
                for ch in roadmap_obj.get('chapters', []):
                    total += ch.get('duration_hours', 0) or 0
                roadmap_obj['total_duration_hours'] = total

            return roadmap_obj
        except Exception as e:
            logger.error(f"LLM chapter-generation failed: {e}")
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
