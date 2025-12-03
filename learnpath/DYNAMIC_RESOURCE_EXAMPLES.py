"""
Dynamic Resource Fetcher - Integration Examples
Quick reference for using the dynamic resource system
"""

# ============================================================================
# EXAMPLE 1: Using via API (Recommended for Frontend)
# ============================================================================

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/assessment/resources"

# Example JWT token (get from login endpoint)
TOKEN = "your-jwt-token-here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ------- FETCH COMPLETE ROADMAP -------
def fetch_complete_roadmap():
    """Fetch videos, docs, blogs, and summary for a topic"""
    
    response = requests.get(
        f"{BASE_URL}/fetch_resources/",
        params={
            "topic": "Machine Learning with Python",
            "skill_level": "intermediate",
            "use_cache": "true"
        },
        headers=HEADERS
    )
    
    result = response.json()
    
    print(f"📹 Videos: {len(result.get('videos', []))}")
    print(f"📚 Documentation: {len(result.get('documentation', []))}")
    print(f"📝 Blogs: {len(result.get('blogs', []))}")
    print(f"⏱️  Estimated Hours: {result.get('estimated_hours', 0)}")
    print(f"📖 Summary:\n{result.get('summary', 'N/A')}")
    
    return result


# ------- FETCH ONLY VIDEOS -------
def fetch_videos_only():
    """Get YouTube videos for a topic"""
    
    response = requests.get(
        f"{BASE_URL}/videos/",
        params={
            "topic": "Python Basics",
            "max_results": 5
        },
        headers=HEADERS
    )
    
    videos = response.json()["videos"]
    
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   Channel: {video['channel']}")
        print(f"   Duration: {video['duration']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   URL: {video['url']}")
    
    return videos


# ------- SEARCH RESOURCES -------
def search_resources():
    """Search for any topic"""
    
    response = requests.get(
        f"{BASE_URL}/search/",
        params={
            "query": "Web Development best practices",
            "search_type": "general"  # or "videos", "documentation"
        },
        headers=HEADERS
    )
    
    results = response.json()
    
    print(f"Found {len(results.get('organic_results', []))} results:")
    for i, result in enumerate(results.get('organic_results', [])[:3], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['snippet'][:150]}...")
        print(f"   {result['url']}")
    
    return results


# ------- SCRAPE A WEBSITE -------
def scrape_website():
    """Extract content from a URL"""
    
    response = requests.post(
        f"{BASE_URL}/scrape_url/",
        json={
            "url": "https://docs.python.org/3/tutorial/",
            "extract_code": True
        },
        headers=HEADERS
    )
    
    content = response.json()
    
    print(f"Title: {content['title']}")
    print(f"\nHeadings found: {len(content['headings'])}")
    for heading in content['headings'][:5]:
        print(f"  - {heading['text']}")
    
    print(f"\nParagraphs found: {len(content['paragraphs'])}")
    print(f"\nCode blocks found: {len(content['code_blocks'])}")
    
    return content


# ------- SUMMARIZE TEXT -------
def summarize_text():
    """Use Gemma LLM to summarize content"""
    
    long_text = """
    Python is a high-level programming language known for its simplicity and readability.
    It was created in 1991 by Guido van Rossum and has since become one of the most
    popular programming languages in the world. Python is used in web development,
    data science, artificial intelligence, scientific computing, and more.
    """
    
    response = requests.post(
        f"{BASE_URL}/summarize/",
        json={
            "text": long_text,
            "prompt_type": "summary"  # or "key_points", "explanation"
        },
        headers=HEADERS
    )
    
    result = response.json()
    print(f"Summary: {result['summary']}")
    
    return result


# ------- HEALTH CHECK -------
def health_check():
    """Check if all services are running"""
    
    response = requests.get(
        f"{BASE_URL}/health/",
        headers=HEADERS
    )
    
    status = response.json()
    
    print("API Status:")
    for service, status_val in status['services'].items():
        emoji = "✅" if "not" not in status_val else "❌"
        print(f"  {emoji} {service}: {status_val}")
    
    return status


# ============================================================================
# EXAMPLE 2: Using Directly in Python (Backend Integration)
# ============================================================================

from assessments.dynamic_resource_fetcher import DynamicResourceFetcher, get_dynamic_resources
import os

# Initialize fetcher
fetcher = DynamicResourceFetcher(
    serper_api_key=os.getenv("SERPER_API_KEY"),
    youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
)

# ------- COMPLETE ROADMAP -------
def backend_fetch_roadmap():
    """Get complete roadmap directly"""
    
    roadmap = fetcher.get_complete_roadmap(
        topic="Django Web Framework",
        skill_level="beginner"
    )
    
    print(f"Roadmap for: {roadmap['topic']}")
    print(f"Videos: {len(roadmap['videos'])}")
    print(f"Docs: {len(roadmap['documentation'])}")
    print(f"Estimated hours: {roadmap['estimated_hours']}")
    
    return roadmap


# ------- SEARCH VIDEOS -------
def backend_search_videos():
    """Search YouTube directly"""
    
    videos = fetcher.search_youtube_videos(
        topic="React.js Basics",
        max_results=5
    )
    
    for video in videos:
        print(f"{video['title']} ({video['relevance_score']:.2f})")
        print(f"  Views: {video['view_count']:,}")
        print(f"  URL: {video['url']}\n")
    
    return videos


# ------- SEARCH RESOURCES -------
def backend_search():
    """Search for resources"""
    
    results = fetcher.search_resources(
        topic="JavaScript Promises",
        search_type="documentation"
    )
    
    for result in results['organic_results'][:3]:
        print(f"{result['title']}")
        print(f"{result['snippet']}\n")
    
    return results


# ------- SCRAPE WEBSITE -------
def backend_scrape():
    """Scrape a website"""
    
    content = fetcher.scrape_website(
        url="https://example.com/tutorial",
        extract_code=True
    )
    
    print(f"Title: {content['title']}")
    print(f"Paragraphs: {len(content['paragraphs'])}")
    print(f"Code blocks: {len(content['code_blocks'])}")
    
    return content


# ------- RANK RESOURCES -------
def backend_rank():
    """Rank resources by quality"""
    
    resources = [
        {
            "title": "Python Tutorial",
            "url": "https://docs.python.org",
            "snippet": "Official Python documentation"
        },
        {
            "title": "Python Reddit Thread",
            "url": "https://reddit.com/r/learnprogramming",
            "snippet": "Community discussion"
        }
    ]
    
    ranked = fetcher.rank_resources(resources, "Python")
    
    for i, resource in enumerate(ranked, 1):
        score = resource.get('ranking_score', 0)
        print(f"{i}. {resource['title']} (Score: {score:.2f})")
    
    return ranked


# ------- SUMMARIZE WITH GEMMA -------
def backend_summarize():
    """Summarize using local Gemma LLM"""
    
    text = """
    Docker is a containerization platform that allows developers to package
    applications and dependencies into standardized units called containers.
    Containers are lightweight, portable, and ensure consistency across
    different environments.
    """
    
    summary = fetcher.summarize_with_ollama(
        text=text,
        prompt_type="summary"
    )
    
    print(f"Summary:\n{summary}")
    return summary


# ============================================================================
# EXAMPLE 3: Frontend Integration (JavaScript)
# ============================================================================

# In your JavaScript (frontend/js/app.js):

JAVASCRIPT_EXAMPLE = """
// Fetch dynamic resources
async function getDynamicResources(topic, skillLevel) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `/api/assessment/resources/fetch_resources/?topic=${topic}&skill_level=${skillLevel}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const resources = await response.json();
  
  // Display videos
  resources.videos.forEach(video => {
    console.log(`📹 ${video.title}`);
    console.log(`   Channel: ${video.channel}`);
    console.log(`   URL: ${video.url}`);
  });
  
  // Display documentation
  resources.documentation.forEach(doc => {
    console.log(`📚 ${doc.title}`);
    console.log(`   Summary: ${doc.summary}`);
    console.log(`   URL: ${doc.url}`);
  });
  
  return resources;
}

// Usage
getDynamicResources('Python', 'beginner');
"""


# ============================================================================
# EXAMPLE 4: In Django Views
# ============================================================================

DJANGO_VIEW_EXAMPLE = """
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from assessments.dynamic_resource_fetcher import get_dynamic_resources

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_custom_resource_endpoint(request):
    topic = request.query_params.get('topic', 'Python')
    skill_level = request.query_params.get('skill_level', 'beginner')
    
    # Get resources dynamically
    resources = get_dynamic_resources(
        topic=topic,
        skill_level=skill_level
    )
    
    # Custom processing
    return Response({
        'resources': resources,
        'user': request.user.username
    })
"""


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*60)
    print("API EXAMPLES (requires authentication)")
    print("="*60)
    
    # Uncomment to test (need valid JWT token):
    # fetch_complete_roadmap()
    # fetch_videos_only()
    # search_resources()
    # scrape_website()
    # summarize_text()
    # health_check()
    
    print("\n" + "="*60)
    print("BACKEND EXAMPLES (direct Python usage)")
    print("="*60)
    
    # Test backend functions
    # backend_fetch_roadmap()
    # backend_search_videos()
    # backend_search()
    # backend_scrape()
    # backend_rank()
    # backend_summarize()
    
    print("\nExamples shown in comments. Uncomment to run.")
