"""
Dynamic Resource Fetcher Views
Django REST API endpoints for dynamic resource fetching
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import logging
import os
from decouple import config

from .dynamic_resource_fetcher import DynamicResourceFetcher, get_dynamic_resources
from .serializers import RoadmapSerializer

logger = logging.getLogger(__name__)


class DynamicResourceViewSet(viewsets.ViewSet):
    """
    API endpoints for dynamic resource fetching
    
    Endpoints:
    - GET /api/resources/fetch-resources/ - Get complete learning resources
    - GET /api/resources/search/ - Search for specific resources
    - GET /api/resources/videos/ - Fetch YouTube videos
    - GET /api/resources/documentation/ - Fetch documentation
    """
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize resource fetcher with environment variables
        self.serper_api_key = config("SERPER_API_KEY", default=None)
        self.youtube_api_key = config("YOUTUBE_API_KEY", default=None)
        self.ollama_url = config("OLLAMA_URL", default="http://localhost:11434")
        
        self.fetcher = DynamicResourceFetcher(
            serper_api_key=self.serper_api_key,
            youtube_api_key=self.youtube_api_key,
            ollama_url=self.ollama_url
        )
    
    @action(detail=False, methods=['get'])
    def fetch_resources(self, request):
        """
        Fetch complete learning resources for a topic
        
        Query Parameters:
            topic (required): Learning topic
            skill_level (optional): beginner, intermediate, advanced
            use_cache (optional): true/false, default true
        
        Returns:
            Complete roadmap with videos, docs, blogs, summary
        """
        topic = request.query_params.get("topic")
        skill_level = request.query_params.get("skill_level", "beginner")
        use_cache = request.query_params.get("use_cache", "true").lower() == "true"
        
        if not topic:
            return Response(
                {"error": "topic parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check cache first
        cache_key = f"resources_{topic}_{skill_level}"
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached resources for '{topic}'")
                return Response(cached_result)
        
        try:
            # Fetch resources
            logger.info(f"Fetching resources for '{topic}' ({skill_level})")
            resources = self.fetcher.get_complete_roadmap(topic, skill_level)
            
            # Cache for 24 hours
            cache.set(cache_key, resources, 86400)
            
            return Response(resources, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to fetch resources: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for resources using Serper API
        
        Query Parameters:
            query (required): Search query
            search_type (optional): general, videos, documentation
        
        Returns:
            Search results with titles, URLs, snippets
        """
        query = request.query_params.get("query")
        search_type = request.query_params.get("search_type", "general")
        
        if not query:
            return Response(
                {"error": "query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Searching for '{query}' ({search_type})")
            results = self.fetcher.search_resources(query, search_type)
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def videos(self, request):
        """
        Search for YouTube videos
        
        Query Parameters:
            topic (required): Video topic
            max_results (optional): Number of results (default 5)
        
        Returns:
            YouTube videos with title, URL, channel, views, duration
        """
        topic = request.query_params.get("topic")
        max_results = int(request.query_params.get("max_results", 5))
        
        if not topic:
            return Response(
                {"error": "topic parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Searching YouTube videos for '{topic}'")
            videos = self.fetcher.search_youtube_videos(topic, max_results)
            
            return Response(
                {"videos": videos, "count": len(videos)},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"YouTube search failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def scrape_url(self, request):
        """
        Scrape content from a URL
        
        Request Body:
            {
                "url": "https://example.com",
                "extract_code": true
            }
        
        Returns:
            Scraped content including headings, paragraphs, code blocks
        """
        url = request.data.get("url")
        extract_code = request.data.get("extract_code", True)
        
        if not url:
            return Response(
                {"error": "url is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Scraping {url}")
            content = self.fetcher.scrape_website(url, extract_code)
            
            return Response(content, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def summarize(self, request):
        """
        Summarize text using Gemma LLM
        
        Request Body:
            {
                "text": "Long text to summarize",
                "prompt_type": "summary"  # or "key_points", "explanation"
            }
        
        Returns:
            Summarized text
        """
        text = request.data.get("text")
        prompt_type = request.data.get("prompt_type", "summary")
        
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Summarizing text ({prompt_type})")
            summary = self.fetcher.summarize_with_ollama(text, prompt_type)
            
            return Response(
                {"summary": summary, "prompt_type": prompt_type},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def rank_resources(self, request):
        """
        Rank resources by quality and relevance
        
        Query Parameters:
            topic (required): Topic for ranking context
            resources (required): JSON array of resources
        
        Returns:
            Ranked resources with ranking scores
        """
        topic = request.query_params.get("topic")
        
        if not topic:
            return Response(
                {"error": "topic parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import json
            resources_json = request.query_params.get("resources", "[]")
            resources = json.loads(resources_json)
            
            logger.info(f"Ranking {len(resources)} resources for '{topic}'")
            ranked = self.fetcher.rank_resources(resources, topic)
            
            return Response(
                {"ranked_resources": ranked},
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid resources JSON"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ranking failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def documentation(self, request):
        """
        Search for official documentation
        
        Query Parameters:
            topic (required): Documentation topic
            max_results (optional): Number of results
        
        Returns:
            Documentation resources with URLs and snippets
        """
        topic = request.query_params.get("topic")
        
        if not topic:
            return Response(
                {"error": "topic parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Searching documentation for '{topic}'")
            docs_search = self.fetcher.search_resources(topic, search_type="documentation")
            
            return Response(docs_search, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Documentation search failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Health check for API and external services
        
        Returns:
            Status of Serper API, YouTube API, and Ollama
        """
        health_status = {
            "api": "healthy",
            "services": {
                "serper": "configured" if self.serper_api_key else "not configured",
                "youtube": "configured" if self.youtube_api_key else "not configured",
                "ollama": "checking..."
            }
        }
        
        # Check Ollama
        try:
            import requests
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            health_status["services"]["ollama"] = "running" if response.status_code == 200 else "error"
        except:
            health_status["services"]["ollama"] = "not running"
        
        return Response(health_status, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def fallback(self, request):
        """
        Retrieve a saved roadmap from the database (DB-only fallback).
        Does NOT attempt dynamic fetching.
        
        Query Parameters:
            topic (required): Learning topic to match against saved Roadmaps
            skill_level (optional): beginner, intermediate, advanced
        
        Returns:
            Saved roadmap from database or 404 if no match found
        """
        topic = request.query_params.get("topic")
        skill_level = request.query_params.get("skill_level", "beginner")
        
        if not topic:
            return Response(
                {"error": "topic parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Retrieving DB fallback roadmap for '{topic}'")
            roadmap = self.fetcher._db_fallback_roadmap(topic, skill_level)
            
            if roadmap:
                return Response(roadmap, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "error": f"No saved roadmap found for topic '{topic}'",
                        "topic": topic,
                        "suggestion": "Create a roadmap first or use /fetch_resources/ for dynamic generation"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            logger.error(f"Fallback retrieval failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
