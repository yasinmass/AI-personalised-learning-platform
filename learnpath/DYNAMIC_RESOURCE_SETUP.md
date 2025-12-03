# Dynamic Resource Fetcher - Complete Setup Guide

## Overview
Your learning platform now has **two modes**:

### 1. **Static Mode** (Default - Fast & Offline)
- Uses hardcoded resources in `roadmap_generator.py`
- Works without internet after initial setup
- Pre-curated 80+ resources
- Instant responses
- **Status**: ✅ Already implemented

### 2. **Dynamic Mode** (Real-time Resource Fetching)
- Fetches resources from internet in real-time
- Uses APIs (Google Search, YouTube, Web Scraping)
- Powered by Gemma LLM for summarization
- Always up-to-date content
- **Status**: 🔧 Ready to install

---

## Installation Steps

### Step 1: Install Required Packages

```bash
cd backend
pip install -r assessments/dynamic_requirements.txt
```

**Packages installed:**
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests
- `playwright` - JavaScript-heavy pages (optional)
- `ollama` - Local LLM integration
- `python-decouple` - Environment variables
- `pandas` - Data processing

---

### Step 2: Get API Keys

#### For Search Results (Serper.dev API)
1. Go to https://serper.dev
2. Sign up for free account
3. Copy your API key
4. Add to `.env`:
   ```
   SERPER_API_KEY=your-serper-api-key-here
   ```

#### For YouTube Videos (YouTube Data API)
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable YouTube Data API v3
4. Create API key
5. Add to `.env`:
   ```
   YOUTUBE_API_KEY=your-youtube-api-key-here
   ```

#### For Summarization (Ollama - Local LLM)
1. Download Ollama from https://ollama.ai
2. Install and start Ollama
3. Pull Gemma model:
   ```bash
   ollama pull gemma:2b
   ```
4. Default runs on `http://localhost:11434` (no API key needed)

---

### Step 3: Update Settings

Edit `backend/.env`:

```env
# Enable dynamic mode
USE_DYNAMIC_RESOURCES=true

# Search API
SERPER_API_KEY=your-serper-api-key

# YouTube API
YOUTUBE_API_KEY=your-youtube-api-key

# Local LLM
OLLAMA_URL=http://localhost:11434
```

---

### Step 4: Start Services

#### Terminal 1 - Django Server
```bash
cd backend
python manage.py runserver
```

#### Terminal 2 - Frontend Server
```bash
cd frontend
python -m http.server 8001
```

#### Terminal 3 - Ollama (if using dynamic mode)
```bash
ollama serve
```

---

## New API Endpoints

### 1. Fetch Complete Resources
```bash
GET /api/assessment/resources/fetch_resources/?topic=Python&skill_level=beginner
```

**Response:**
```json
{
  "topic": "Python",
  "videos": [
    {
      "title": "Python for Beginners",
      "url": "https://youtube.com/watch?v=...",
      "channel": "Real Python",
      "view_count": 500000,
      "duration": "PT45M30S"
    }
  ],
  "documentation": [
    {
      "title": "Python Official Docs",
      "url": "https://docs.python.org",
      "summary": "Official Python documentation..."
    }
  ],
  "blogs": [...],
  "summary": "...",
  "estimated_hours": 12.5
}
```

### 2. Search Resources
```bash
GET /api/assessment/resources/search/?query=Python&search_type=documentation
```

### 3. Get Videos Only
```bash
GET /api/assessment/resources/videos/?topic=Python&max_results=5
```

### 4. Scrape & Summarize
```bash
POST /api/assessment/resources/summarize/

{
  "text": "Long text to summarize...",
  "prompt_type": "summary"  // or "key_points", "explanation"
}
```

### 5. Health Check
```bash
GET /api/assessment/resources/health/
```

**Response:**
```json
{
  "api": "healthy",
  "services": {
    "serper": "configured",
    "youtube": "configured",
    "ollama": "running"
  }
}
```

---

## How It Works

### Request Flow (Dynamic Mode):

```
User clicks "Generate Roadmap"
         ↓
Frontend calls /api/assessment/resources/fetch_resources/?topic=JavaScript
         ↓
DynamicResourceViewSet.fetch_resources()
         ↓
1. Check cache (24 hours)
2. If cached → Return immediately
3. If not cached:
   a. Search Google (Serper API)
   b. Fetch YouTube videos (YouTube API)
   c. Scrape top 3 documentation pages
   d. Summarize with Gemma LLM
   e. Rank resources by relevance
   f. Cache result
   g. Return to frontend
         ↓
Frontend displays:
- 3 highest-ranked videos
- Top documentation links
- Blog articles
- Learning summary
- Estimated hours
```

### Request Flow (Static Mode - Default):

```
User clicks "Generate Roadmap"
         ↓
Frontend calls /api/assessment/generate-roadmap/
         ↓
LLMService.generate_roadmap()
         ↓
RoadmapGenerator.generate_roadmap()
         ↓
Look up in ROADMAPS dictionary
         ↓
Apply skill level customization
         ↓
Calculate time multipliers
         ↓
Return to frontend
```

---

## Switching Between Modes

### To Use Dynamic Mode:
```env
USE_DYNAMIC_RESOURCES=true
SERPER_API_KEY=xxx
YOUTUBE_API_KEY=xxx
```

### To Use Static Mode:
```env
USE_DYNAMIC_RESOURCES=false
# No API keys needed
```

**Note:** Switching modes requires server restart.

---

## Error Handling

### If Serper API fails:
- Falls back to web scraping
- Logs warning, continues

### If YouTube API fails:
- Falls back to YouTube page scraping
- Returns limited metadata

### If Ollama is not running:
- Skips LLM summarization
- Returns raw text snippets
- No error thrown

### If all APIs fail:
- Uses cached results if available
- Falls back to static RoadmapGenerator
- Returns offline fallback roadmap

---

## Rate Limiting

The system implements automatic rate limiting:
- 1 second minimum between API calls
- Respects API rate limits
- Implements retry logic for failures
- Caches results for 24 hours

---

## Code Architecture

```
assessments/
├── dynamic_resource_fetcher.py (640 lines)
│   ├── DynamicResourceFetcher class
│   │   ├── search_resources() - Google Search
│   │   ├── search_youtube_videos() - YouTube API
│   │   ├── scrape_website() - Web scraping
│   │   ├── rank_resources() - Quality ranking
│   │   ├── summarize_with_ollama() - LLM summarization
│   │   └── get_complete_roadmap() - Main orchestrator
│   └── get_dynamic_resources() - Utility function
│
├── dynamic_resource_views.py (370 lines)
│   └── DynamicResourceViewSet
│       ├── fetch_resources() - Complete pipeline
│       ├── search() - Search only
│       ├── videos() - Videos only
│       ├── scrape_url() - Scrape URL
│       ├── summarize() - Summarize text
│       ├── documentation() - Docs only
│       └── health() - Health check
│
├── llm_service.py (MODIFIED)
│   └── LLMService.generate_roadmap()
│       ├── Check USE_DYNAMIC_RESOURCES flag
│       ├── If true → _generate_dynamic_roadmap()
│       ├── If false → RoadmapGenerator.generate_roadmap()
│       └── Fallback → _get_fallback_roadmap()
│
├── urls.py (MODIFIED)
│   └── Register DynamicResourceViewSet router
│
└── roadmap_generator.py (UNCHANGED)
    └── Static fallback system
```

---

## Feature Comparison

| Feature | Static Mode | Dynamic Mode |
|---------|------------|--------------|
| Speed | ⚡ Instant | 🔄 2-5 seconds |
| Works Offline | ✅ Yes | ❌ No |
| Latest Resources | ❌ Static | ✅ Real-time |
| API Keys | ❌ None | ✅ Required |
| Customization | 📝 Pre-curated | 🔍 Any topic |
| Reliability | ✅ 100% | 🔀 API dependent |
| Cost | 💰 Free | 💳 $0-10/month |
| LLM Summaries | ❌ No | ✅ Yes (Gemma) |

---

## Example Usage

### Using Frontend

1. Select a course
2. Take assessment quiz
3. Click "Generate Roadmap"
   - If `USE_DYNAMIC_RESOURCES=true` → Fetches real-time resources
   - If `USE_DYNAMIC_RESOURCES=false` → Uses static resources
4. View comprehensive learning path with resources

### Using API Directly

```python
import requests

# Fetch resources dynamically
response = requests.get(
    "http://localhost:8000/api/assessment/resources/fetch_resources/",
    params={
        "topic": "Python Web Development",
        "skill_level": "intermediate"
    },
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)

resources = response.json()
print(f"Videos: {len(resources['videos'])}")
print(f"Documentation: {len(resources['documentation'])}")
print(f"Summary: {resources['summary']}")
```

---

## Troubleshooting

### "SERPER_API_KEY not configured"
- Make sure `.env` has `SERPER_API_KEY=xxx`
- Restart Django server
- Check `.env` is in `backend/` folder

### "Ollama not running"
- Install Ollama from https://ollama.ai
- Run: `ollama serve`
- Check: `http://localhost:11434/api/tags`

### "YouTube API not configured"
- Get key from Google Cloud Console
- Add to `.env`: `YOUTUBE_API_KEY=xxx`
- Restart Django server

### "Resources endpoint returns 500 error"
- Check server logs for detailed error
- Verify API keys are valid
- Ensure internet connection
- Try `GET /api/assessment/resources/health/`

### "Scraping returns empty results"
- Website might have rate limiting
- Website might require authentication
- Try different URL format
- Check if website allows scraping (robots.txt)

---

## Next Steps

1. ✅ Install packages: `pip install -r assessments/dynamic_requirements.txt`
2. ✅ Get API keys (Serper, YouTube)
3. ✅ Update `.env` with API keys
4. ✅ Install and run Ollama (optional)
5. ✅ Set `USE_DYNAMIC_RESOURCES=true` in `.env`
6. ✅ Restart Django server
7. ✅ Test using `GET /api/assessment/resources/health/`
8. ✅ Use frontend as normal (will fetch dynamic resources)

---

## Support

For issues:
1. Check logs: `python manage.py runserver` (shows errors)
2. Test API directly: Use curl or Postman
3. Verify API keys are valid
4. Check network connectivity
5. Review troubleshooting section above

---

**You now have TWO complete systems:**
- 🔧 **Static Mode**: Fast, reliable, pre-curated (ready now)
- 🌐 **Dynamic Mode**: Real-time, scalable, customizable (requires setup)

Choose which mode fits your needs!
