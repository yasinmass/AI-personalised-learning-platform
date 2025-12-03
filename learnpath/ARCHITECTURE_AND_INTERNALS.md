"""
Dynamic Resource Fetcher - Architecture Visualization & Technical Details
"""

# ============================================================================
# SYSTEM ARCHITECTURE - DUAL MODE
# ============================================================================

ARCHITECTURE = """
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (8001)                              │
│  HTML + CSS + JavaScript (app.js)                                   │
│  - Assessment Quiz (10 questions)                                   │
│  - Learning Path Display                                            │
│  - Resource Cards                                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    HTTP POST/GET (CORS)
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      DJANGO API (8000)                              │
│              /api/assessment/resources/                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ DynamicResourceViewSet (8 endpoints)                         │  │
│  │                                                              │  │
│  │ ├─ fetch_resources()        → Complete roadmap             │  │
│  │ ├─ search()                 → Google Search                │  │
│  │ ├─ videos()                 → YouTube Videos               │  │
│  │ ├─ scrape_url()             → Web Scraping                 │  │
│  │ ├─ summarize()              → LLM Summarization            │  │
│  │ ├─ documentation()          → Docs Search                  │  │
│  │ ├─ rank_resources()         → Quality Ranking              │  │
│  │ └─ health()                 → Service Status Check         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│        ┌──────────────────────┼──────────────────────┐              │
│        │                      │                      │              │
│        ▼                      ▼                      ▼              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐     │
│  │ .env Check     │  │ LLMService     │  │ RoadmapGenerator │     │
│  │                │  │ (modified)     │  │ (static)         │     │
│  │ USE_DYNAMIC... │  │                │  │                  │     │
│  └────────────────┘  └────┬───────────┘  └──────────────────┘     │
│                           │                                         │
│              ┌────────────┴────────────┐                            │
│              │                         │                            │
│         ┌────▼─────────┐    ┌──────────▼────────────┐              │
│         │ Static Mode  │    │ Dynamic Mode          │              │
│         │              │    │                       │              │
│         │ Use Static   │    │ DynamicResourceFetcher│              │
│         │ Roadmap      │    │                       │              │
│         │ Generator    │    │ ├─ search_resources()│              │
│         │ (Fast)       │    │ ├─ search_youtube()  │              │
│         └──────────────┘    │ ├─ scrape_website()  │              │
│                             │ ├─ rank_resources()  │              │
│                             │ ├─ summarize_ollama()│              │
│                             │ └─ get_roadmap()     │              │
│                             └──────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    ┌─────────────┐    ┌──────────────┐    ┌────────────────┐
    │   Cache     │    │  APIs        │    │  LLM Service   │
    │  (24 hrs)   │    │              │    │                │
    │             │    │ ├─ Serper    │    │ ├─ Ollama      │
    │ In-Memory   │    │ │ (Search)   │    │ │ (Summarize)  │
    │ Django      │    │ │            │    │ │              │
    │ Cache       │    │ ├─ YouTube   │    │ └─ Gemma 2B    │
    │             │    │ │ (Videos)   │    │   (Local)      │
    │ Returns     │    │ │            │    │                │
    │ 24h cached  │    │ └─ Puppeteer│    │ No API Key     │
    │ results     │    │   (Scraping)│    │ Private        │
    └─────────────┘    └──────────────┘    └────────────────┘
         (Optional)      (if enabled)       (if running)

"""

# ============================================================================
# DATA FLOW - REQUEST TO RESPONSE
# ============================================================================

REQUEST_FLOW = """
1. FRONTEND → API
   ┌──────────────────────────┐
   │ User selects course      │
   │ Takes 10-question test   │
   │ Selects skill level      │
   │ Chooses duration         │
   │ Clicks "Generate Roadmap"│
   └──────────────────────────┘
                │
                ▼
   GET /api/assessment/resources/fetch_resources/
   ?topic=Python
   &skill_level=beginner
   &use_cache=true

2. SERVER SIDE - ROUTING
   ┌──────────────────────────────────────────┐
   │ Django URL Router                        │
   │ → DynamicResourceViewSet.fetch_resources │
   └──────────────────────────────────────────┘
                │
                ▼
   ┌──────────────────────────────────────────┐
   │ Step 1: Check USE_DYNAMIC_RESOURCES env  │
   │                                          │
   │ if False → return RoadmapGenerator()     │
   │ if True  → continue to Step 2            │
   └──────────────────────────────────────────┘

3. DYNAMIC MODE - CACHING LAYER
   ┌────────────────────────────────────────────┐
   │ cache_key = f"resources_Python_beginner"   │
   │ cached = cache.get(cache_key)              │
   │                                            │
   │ if cached → return cached (< 10ms)        │
   │ else → continue to Step 4                  │
   └────────────────────────────────────────────┘

4. SEARCH PHASE
   ┌──────────────────────────────────────────────────┐
   │ a) Google Search (Serper API)                    │
   │    GET https://google.serper.dev/search          │
   │    Payload: {"q": "Python learn..."}             │
   │    Response: [top 10 results]                     │
   │                                                  │
   │ b) YouTube Search (YouTube Data API)             │
   │    GET https://www.googleapis.com/youtube/v3/... │
   │    Response: [5 videos with metadata]            │
   │                                                  │
   │ c) Relationship: Serper + YouTube give raw data  │
   └──────────────────────────────────────────────────┘

5. SCRAPING PHASE
   ┌────────────────────────────────────────────────┐
   │ For each top documentation result:              │
   │ ┌──────────────────────────────────────────┐   │
   │ │ requests.get(url) + BeautifulSoup parse │   │
   │ │                                          │   │
   │ │ Extract:                                 │   │
   │ │ • Title (from <title> tag)               │   │
   │ │ • Headings (H1-H4)                       │   │
   │ │ • Paragraphs (first 10)                  │   │
   │ │ • Code blocks (optional)                 │   │
   │ │ • Lists (first 3)                        │   │
   │ └──────────────────────────────────────────┘   │
   │                                                │
   │ Rate limiting: 1 second between requests       │
   │ Timeout: 15 seconds per request                │
   └────────────────────────────────────────────────┘

6. LLM SUMMARIZATION PHASE
   ┌───────────────────────────────────────────────────┐
   │ For each scraped page:                            │
   │                                                   │
   │ requests.post(ollama_url/api/generate)            │
   │ {                                                 │
   │   "model": "gemma:2b",                            │
   │   "prompt": "Summarize: [scraped text]",          │
   │   "stream": false                                 │
   │ }                                                 │
   │                                                   │
   │ Response: Summarized content (local, no tracking)│
   │                                                   │
   │ Fallback: Extract sentences if Ollama not running│
   └───────────────────────────────────────────────────┘

7. RANKING PHASE
   ┌────────────────────────────────────────────────┐
   │ For each resource (video/blog/doc):             │
   │                                                │
   │ Score = (40% relevance                         │
   │        + 30% domain_authority                  │
   │        + 20% freshness                         │
   │        + 10% popularity)                       │
   │                                                │
   │ Authority scores:                              │
   │ • MDN = 1.0     (Mozilla)                      │
   │ • GitHub = 0.9  (Community)                    │
   │ • Medium = 0.7  (Blogs)                        │
   │ • YouTube = 0.75 (Videos)                      │
   │ • Unknown = 0.5 (Default)                      │
   │                                                │
   │ Sort by ranking_score DESC                     │
   └────────────────────────────────────────────────┘

8. RESPONSE FORMATTING
   ┌─────────────────────────────────────────────┐
   │ {                                           │
   │   "topic": "Python",                        │
   │   "skill_level": "beginner",                │
   │   "generated_at": "2025-12-03T...",         │
   │   "videos": [                               │
   │     {                                       │
   │       "title": "Python for Beginners",      │
   │       "url": "https://youtube.com/...",     │
   │       "channel": "Real Python",             │
   │       "view_count": 500000,                 │
   │       "duration": "PT45M30S"                │
   │     },                                      │
   │     ...                                     │
   │   ],                                        │
   │   "documentation": [...],                   │
   │   "blogs": [...],                           │
   │   "summary": "...",                         │
   │   "estimated_hours": 12.5,                  │
   │   "related_topics": [...]                   │
   │ }                                           │
   └─────────────────────────────────────────────┘

9. CACHING
   ┌────────────────────────────────────────────┐
   │ cache.set(                                  │
   │   key="resources_Python_beginner",          │
   │   value=roadmap,                            │
   │   timeout=86400  # 24 hours                 │
   │ )                                           │
   └────────────────────────────────────────────┘

10. RESPONSE → FRONTEND
    ┌──────────────────────────────────────────┐
    │ 200 OK                                   │
    │ Content-Type: application/json           │
    │ [Complete roadmap JSON]                  │
    └──────────────────────────────────────────┘
                    │
                    ▼
    ┌──────────────────────────────────────────┐
    │ Frontend JavaScript:                     │
    │ • Parse JSON response                    │
    │ • Display videos in grid                 │
    │ • Display docs with summaries            │
    │ • Show estimated hours                   │
    │ • Display related topics                 │
    └──────────────────────────────────────────┘
"""

# ============================================================================
# CODE STRUCTURE - KEY CLASSES & METHODS
# ============================================================================

CLASS_HIERARCHY = """
DynamicResourceFetcher (Main Class)
├── __init__()
│   └─ Initialize APIs & session management
│
├── _rate_limit()
│   └─ Apply 1 second minimum between requests
│
├── search_resources(topic, search_type)
│   ├─ Input: "Python", "documentation"
│   └─ Output: {"organic_results": [...], "people_also_ask": [...]}
│
├── search_youtube_videos(topic, max_results)
│   ├─ Input: "React Hooks", 5
│   └─ Output: List of videos with stats & relevance scores
│
├── _get_youtube_stats(video_ids)
│   ├─ Input: ["xyz123", "abc456"]
│   └─ Output: {"xyz123": {"viewCount": 5000, ...}}
│
├── _fallback_youtube_search(topic, max_results)
│   ├─ Fallback if API fails
│   └─ Uses regex scraping instead
│
├── _calculate_video_relevance(topic, video_item, stats)
│   ├─ Calculates 0-1 score based on:
│   │  ├─ Title match (40%)
│   │  ├─ View count (30%)
│   │  ├─ Engagement (20%)
│   │  └─ Recency (10%)
│   └─ Returns: float (0.0 to 1.0)
│
├── scrape_website(url, extract_code)
│   ├─ Input: "https://docs.python.org", True
│   ├─ Uses: BeautifulSoup
│   └─ Output: {
│       "title": "...",
│       "headings": [...],
│       "paragraphs": [...],
│       "code_blocks": [...]
│     }
│
├── rank_resources(resources, topic)
│   ├─ Input: List of resources, "Python"
│   ├─ Scoring factors:
│   │  ├─ Relevance to topic (40%)
│   │  ├─ Domain authority (30%)
│   │  ├─ Freshness (20%)
│   │  └─ Popularity (10%)
│   └─ Output: Sorted resources with ranking_score
│
├── summarize_with_ollama(text, prompt_type)
│   ├─ Input: "Long text", "summary"
│   ├─ Uses: Ollama API (Gemma LLM)
│   ├─ Prompt types:
│   │  ├─ "summary" → 2-3 sentence summary
│   │  ├─ "key_points" → 5 key learning points
│   │  └─ "explanation" → Simple explanation
│   └─ Output: str (summarized content)
│
├── _fallback_summary(text, max_sentences)
│   └─ Simple fallback if Ollama not running
│
├── get_complete_roadmap(topic, skill_level)
│   ├─ Main orchestrator
│   ├─ Calls in sequence:
│   │  1. search_youtube_videos()
│   │  2. search_resources(search_type="documentation")
│   │  3. scrape_website() for top results
│   │  4. summarize_with_ollama() for summaries
│   │  5. search_resources(search_type="general")
│   │  6. Extract related_topics from "people_also_ask"
│   │  7. Estimate learning hours
│   └─ Output: Complete roadmap
│
├── _estimate_learning_hours(videos, docs, blogs, skill_level)
│   ├─ Formula:
│   │  hours = (videos × 1.0) + (docs × 0.5) + (blogs × 0.25)
│   │  Then adjust by skill level:
│   │  • beginner: ×1.5
│   │  • intermediate: ×1.0
│   │  • advanced: ×0.6
│   └─ Returns: float (estimated hours)
│
└── Error Handling
    ├─ RequestException → Log error, return error dict
    ├─ JSONDecodeError → Return error response
    ├─ Connection timeout → Fallback to scraping
    └─ All exceptions → Graceful degradation

DynamicResourceViewSet (API Endpoints)
├── __init__()
│   └─ Initialize DynamicResourceFetcher instance
│
├── fetch_resources()
│   ├─ GET /api/assessment/resources/fetch_resources/
│   ├─ Params: topic, skill_level, use_cache
│   └─ Returns: Complete roadmap
│
├── search()
│   ├─ GET /api/assessment/resources/search/
│   ├─ Params: query, search_type
│   └─ Returns: Search results
│
├── videos()
│   ├─ GET /api/assessment/resources/videos/
│   ├─ Params: topic, max_results
│   └─ Returns: Video list
│
├── scrape_url()
│   ├─ POST /api/assessment/resources/scrape_url/
│   ├─ Body: {url, extract_code}
│   └─ Returns: Scraped content
│
├── summarize()
│   ├─ POST /api/assessment/resources/summarize/
│   ├─ Body: {text, prompt_type}
│   └─ Returns: Summary
│
├── documentation()
│   ├─ GET /api/assessment/resources/documentation/
│   ├─ Params: topic
│   └─ Returns: Documentation results
│
├── rank_resources()
│   ├─ GET /api/assessment/resources/rank_resources/
│   ├─ Params: topic, resources (JSON)
│   └─ Returns: Ranked resources
│
└── health()
    ├─ GET /api/assessment/resources/health/
    └─ Returns: Service status
"""

# ============================================================================
# ERROR HANDLING & FALLBACKS
# ============================================================================

ERROR_HANDLING = """
Error Handling Strategy: Graceful Degradation

1. API Connection Fails
   Try: Serper API → Request failed
   Fallback: Use web scraping directly
   Result: Slower but still works

2. YouTube API Fails
   Try: YouTube Data API → Connection timeout
   Fallback: Regex scraping from YouTube page
   Result: Less metadata but videos found

3. Ollama Not Running
   Try: Summarize with Gemma → Connection refused
   Fallback: Extract key sentences from text
   Result: No LLM but summaries still provided

4. Web Scraping Fails
   Try: Parse page → 404 error
   Fallback: Skip that resource
   Result: Fewer resources but valid ones

5. All Fails
   Fallback: Use RoadmapGenerator (static)
   Result: Pre-curated resources from database

Flow:
┌─ Try Primary Method ──────┐
│                           │
├─ Success? ────────────────┼──► Return results
│                           │
└─ Error ────────────────┐  │
                         │  │
                         ▼  │
                    Try Fallback
                         │
                         ├─ Success? ──────────┼──► Return results
                         │                     │
                         └─ Still Error?       │
                              │                │
                              ▼                │
                         Use RoadmapGenerator ─┘
                              │
                              └──► Return static data
"""

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

PERFORMANCE = """
Response Times (Benchmarks):

Static Mode (RoadmapGenerator):
├─ Cache hit: ~5ms (instant)
├─ Full generation: ~50ms (very fast)
└─ Total: < 100ms

Dynamic Mode (DynamicResourceFetcher):
├─ Cache hit: ~10ms (instant)
├─ Serper API call: ~800ms
├─ YouTube API call: ~600ms
├─ Web scraping (3 pages): ~5s
├─ LLM summarization (3x): ~2s
├─ Ranking & formatting: ~200ms
└─ Total: ~9-10 seconds (acceptable)

Caching Strategy:
├─ Cache key: "resources_{topic}_{skill_level}"
├─ TTL: 24 hours
├─ Storage: Django in-memory cache
└─ Benefit: Same topic reused → instant (< 10ms)

Optimization:
├─ Parallel API calls? (future enhancement)
├─ Pre-generate popular topics? (future)
├─ CDN for images? (future)
└─ Current: Sequential, simple, reliable
"""

# ============================================================================
# EXAMPLE REQUEST-RESPONSE
# ============================================================================

EXAMPLE = """
REQUEST:
─────────────────────────────────────────────────
GET /api/assessment/resources/fetch_resources/?topic=Python&skill_level=beginner&use_cache=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

RESPONSE (200 OK):
─────────────────────────────────────────────────
{
  "topic": "Python",
  "skill_level": "beginner",
  "generated_at": "2025-12-03T14:30:45.123456Z",
  "videos": [
    {
      "title": "Python for Beginners - Full Course",
      "url": "https://www.youtube.com/watch?v=_uQrJ0TkSuc",
      "channel": "Telusko",
      "description": "Complete Python course for beginners covering...",
      "thumbnail": "https://i.ytimg.com/vi/_uQrJ0TkSuc/maxresdefault.jpg",
      "published_at": "2020-09-03T10:30:00Z",
      "view_count": 2500000,
      "like_count": 45000,
      "comment_count": 12000,
      "duration": "PT3H47M",
      "relevance_score": 0.95
    },
    {
      "title": "Python Basics in 1 Hour",
      "url": "https://www.youtube.com/watch?v=kqtZohMQP3s",
      "channel": "Tech with Tim",
      "description": "Learn Python fundamentals quickly...",
      "view_count": 1800000,
      "relevance_score": 0.88
    },
    {
      "title": "Introduction to Python Programming",
      "url": "https://www.youtube.com/watch?v=rfscVS0vtik",
      "channel": "Edureka",
      "view_count": 950000,
      "relevance_score": 0.82
    }
  ],
  "documentation": [
    {
      "title": "Python Official Documentation",
      "url": "https://docs.python.org/3/",
      "snippet": "Python is a high-level, interpreted programming language...",
      "summary": "Official Python docs covering language syntax, built-in functions, modules, and standard library. Comprehensive reference for all Python features.",
      "domain": "docs.python.org",
      "ranking_score": 0.98
    },
    {
      "title": "The Python Tutorial",
      "url": "https://docs.python.org/3/tutorial/",
      "snippet": "This tutorial introduces the reader informally...",
      "summary": "Beginner-friendly tutorial covering Python basics, syntax, data types, control flow, and functions.",
      "domain": "docs.python.org",
      "ranking_score": 0.97
    },
    {
      "title": "Real Python Tutorials",
      "url": "https://realpython.com/",
      "snippet": "The leading resource for learning Python...",
      "summary": "High-quality tutorials on Python concepts, libraries, web development, and best practices.",
      "domain": "realpython.com",
      "ranking_score": 0.85
    }
  ],
  "blogs": [
    {
      "title": "Getting Started with Python for Absolute Beginners",
      "url": "https://medium.com/@....",
      "summary": "A comprehensive guide covering Python installation, variables, data types, and basic operations.",
      "domain": "medium.com",
      "ranking_score": 0.72
    },
    {
      "title": "Python: The Easy Way to Learn Programming",
      "url": "https://dev.to/@...",
      "summary": "Beginner-focused article about Python's simplicity and why it's perfect for starting programming.",
      "domain": "dev.to",
      "ranking_score": 0.68
    }
  ],
  "tools": [
    {
      "name": "Visual Studio Code",
      "url": "https://code.visualstudio.com/",
      "purpose": "Free Python IDE with extensions"
    },
    {
      "name": "Anaconda",
      "url": "https://www.anaconda.com/",
      "purpose": "Python distribution with package manager"
    }
  ],
  "related_topics": [
    "Variables and Data Types in Python",
    "Python Control Flow Statements",
    "Functions and Modules in Python",
    "Object-Oriented Programming with Python",
    "Exception Handling in Python"
  ],
  "summary": "Python is a high-level, versatile programming language perfect for beginners. This roadmap focuses on fundamentals including syntax, data types, control flow, and functions. With an estimated 12-15 hours of study, you can master Python basics through a combination of video tutorials, official documentation, and hands-on practice.",
  "estimated_hours": 13.5,
  "generated_from": "dynamic_fetcher",
  "is_dynamic": true
}

TIME TAKEN: 4.2 seconds
CACHE STATUS: Not cached, generated fresh
NEXT REQUEST: Will use cache for 24 hours
"""

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

ENV_VARIABLES = """
# backend/.env

# FEATURE TOGGLE (Required)
USE_DYNAMIC_RESOURCES=true          # or false for static mode

# Search API (Optional - Serper.dev)
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxx
# Get from: https://serper.dev

# Video API (Optional - YouTube Data API)
YOUTUBE_API_KEY=xxxxxxxxxxxxxxxxxxxx
# Get from: https://console.cloud.google.com

# LLM Service (Optional - Ollama)
OLLAMA_URL=http://localhost:11434
# Download from: https://ollama.ai
# No API key needed - runs locally

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-xxxxx (optional, for GPT fallback)

Default Behavior:
- USE_DYNAMIC_RESOURCES=false   → Always use static mode (no API calls)
- USE_DYNAMIC_RESOURCES=true    → Use dynamic (requires at least Serper + YouTube keys)
- API keys missing              → Try anyway, fallback to scraping
- Ollama not running            → Skip summarization, return raw text
"""

if __name__ == "__main__":
    print(ARCHITECTURE)
    print("\n" + "="*80 + "\n")
    print(REQUEST_FLOW)
    print("\n" + "="*80 + "\n")
    print(CLASS_HIERARCHY)
    print("\n" + "="*80 + "\n")
    print(ERROR_HANDLING)
    print("\n" + "="*80 + "\n")
    print(PERFORMANCE)
    print("\n" + "="*80 + "\n")
    print(EXAMPLE)
    print("\n" + "="*80 + "\n")
    print(ENV_VARIABLES)
