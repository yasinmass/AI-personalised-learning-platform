"""
Dynamic Resource Fetcher Module
Retrieves learning resources in real-time from:
- Google Search (via Serper.dev API)
- YouTube Data API
- Web Scraping (BeautifulSoup)
- Local LLM (Gemma via Ollama) for summarization
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

# Django model fallback will be imported lazily inside methods to avoid
# import-time dependency issues when running scripts outside Django context.


class DynamicResourceFetcher:
    """Fetch resources dynamically from internet sources"""
    
    def __init__(self, serper_api_key: str = None, youtube_api_key: str = None, ollama_url: str = None):
        """
        Initialize fetcher with API keys
        
        Args:
            serper_api_key: Serper.dev API key for search
            youtube_api_key: YouTube Data API key
            ollama_url: Ollama server URL (default: http://localhost:11434)
        """
        self.serper_api_key = serper_api_key
        self.youtube_api_key = youtube_api_key
        self.ollama_url = ollama_url or "http://localhost:11434"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # 1 second between requests
    
    def _rate_limit(self):
        """Apply rate limiting to avoid API throttling"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def search_resources(self, topic: str, search_type: str = "general") -> Dict:
        """
        Search for resources using Serper.dev API (Google Search)
        
        Args:
            topic: Learning topic to search
            search_type: "general", "videos", "documentation"
        
        Returns:
            Dictionary with search results
        """
        if not self.serper_api_key:
            logger.warning("Serper API key not configured. Skipping search.")
            return {"error": "API key not configured"}
        
        try:
            self._rate_limit()
            
            # Enhance search query based on type
            if search_type == "videos":
                query = f"{topic} tutorial video course"
            elif search_type == "documentation":
                query = f"{topic} official documentation guide"
            else:
                query = f"{topic} learn education"
            
            # Call Serper API
            url = "https://google.serper.dev/search"
            payload = {
                "q": query,
                "num": 10
            }
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            # Extract and clean results
            processed_results = {
                "organic_results": [],
                "people_also_ask": [],
                "total_results": results.get("searchParameters", {}).get("cl", "0")
            }
            
            # Process organic search results
            for result in results.get("organic", []):
                processed_results["organic_results"].append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0),
                    "domain": urlparse(result.get("link", "")).netloc
                })
            
            # Process people also ask
            for qa in results.get("peopleAlsoAsk", [])[:5]:
                processed_results["people_also_ask"].append({
                    "question": qa.get("question", ""),
                    "answer": qa.get("answer", ""),
                    "source": qa.get("source", "")
                })
            
            logger.info(f"Found {len(processed_results['organic_results'])} search results for '{topic}'")
            return processed_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse search response: {str(e)}")
            return {"error": "Invalid response format"}
    
    def search_youtube_videos(self, topic: str, max_results: int = 5) -> List[Dict]:
        """
        Search for YouTube videos using YouTube Data API with strict validation
        Only returns real, playable videos that work when clicked

        Args:
            topic: Video topic to search
            max_results: Maximum videos to return (minimum 3)

        Returns:
            List of validated video results with metadata
        """
        if not self.youtube_api_key:
            logger.warning("YouTube API key not configured.")
            return []

        # Ensure minimum of 3 results
        min_results = max(max_results, 3)

        # Primary search
        videos = self._search_youtube_with_validation(topic, min_results)

        # Fallback searches if needed
        if len(videos) < 3:
            logger.info(f"Primary search returned {len(videos)} videos, running fallback searches...")

            fallback_queries = [
                f"{topic} tutorial",
                f"{topic} crash course",
                f"learn {topic}",
                f"{topic} basics"
            ]

            for query in fallback_queries:
                if len(videos) >= 3:
                    break
                fallback_videos = self._search_youtube_with_validation(query, 3)
                # Add only videos not already in results
                existing_urls = {v["url"] for v in videos}
                for video in fallback_videos:
                    if video["url"] not in existing_urls:
                        videos.append(video)
                        if len(videos) >= 3:
                            break

        # Return only the requested fields
        final_videos = []
        for video in videos[:max_results]:
            final_videos.append({
                "title": video["title"],
                "url": video["url"],
                "channel": video["channel"],
                "duration": video["duration"],
                "view_count": video["view_count"]
            })

        logger.info(f"Returning {len(final_videos)} validated YouTube videos for '{topic}'")
        return final_videos

    def _search_youtube_with_validation(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Internal method to search YouTube with strict validation

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of validated videos
        """
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                # Step 1: Search for videos
                search_url = "https://www.googleapis.com/youtube/v3/search"
                search_params = {
                    "q": query,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": max_results * 3,  # Get more for validation
                    "order": "relevance",
                    "relevanceLanguage": "en",
                    "key": self.youtube_api_key
                }

                search_response = requests.get(search_url, params=search_params, timeout=15)
                search_response.raise_for_status()

                search_results = search_response.json()

                if "error" in search_results:
                    logger.error(f"YouTube API search error: {search_results['error']}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return []

                video_ids = [item["id"]["videoId"] for item in search_results.get("items", [])]
                if not video_ids:
                    return []

                # Step 2: Validate videos using videos API endpoint
                validated_videos = self._validate_videos_strict(video_ids)

                # Step 3: Get statistics for validated videos
                if validated_videos:
                    stats = self._get_youtube_stats(list(validated_videos.keys()))
                    videos = []

                    for video_id, video_data in validated_videos.items():
                        stat_data = stats.get(video_id, {})
                        if stat_data:  # Only include if we got stats
                            videos.append({
                                "title": video_data["title"][:200],
                                "url": f"https://www.youtube.com/watch?v={video_id}",
                                "channel": video_data["channel"],
                                "duration": stat_data.get("duration", "Unknown"),
                                "view_count": stat_data.get("viewCount", 0),
                                "source": "youtube_api"
                            })

                    logger.info(f"Validated {len(videos)} videos for query '{query}'")
                    return videos[:max_results]

            except requests.exceptions.Timeout:
                logger.warning(f"YouTube API timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"YouTube API request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in YouTube search on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        return []

    def _validate_videos_strict(self, video_ids: List[str]) -> Dict:
        """
        Strict validation using YouTube videos API endpoint + URL availability check
        Only returns videos that are:
        - uploadStatus = "processed"
        - privacyStatus = "public"
        - embeddable = true
        - not age restricted
        - AND actually accessible via direct URL check

        Args:
            video_ids: List of video IDs to validate

        Returns:
            Dictionary of validated video data
        """
        if not video_ids or not self.youtube_api_key:
            return {}

        max_retries = 2
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                # Validate in batches of 50 (YouTube API limit)
                validated_videos = {}
                batch_size = 50

                for i in range(0, len(video_ids), batch_size):
                    batch_ids = video_ids[i:i + batch_size]

                    validate_url = "https://www.googleapis.com/youtube/v3/videos"
                    validate_params = {
                        "id": ",".join(batch_ids),
                        "part": "snippet,status,contentDetails",
                        "key": self.youtube_api_key
                    }

                    validate_response = requests.get(validate_url, params=validate_params, timeout=15)
                    validate_response.raise_for_status()

                    validate_results = validate_response.json()

                    if "error" in validate_results:
                        logger.error(f"YouTube validation API error: {validate_results['error']}")
                        continue

                    for item in validate_results.get("items", []):
                        video_id = item["id"]
                        status = item.get("status", {})
                        content_details = item.get("contentDetails", {})
                        snippet = item.get("snippet", {})

                        # Strict validation criteria
                        if (status.get("uploadStatus") == "processed" and
                            status.get("privacyStatus") == "public" and
                            status.get("embeddable") == True and
                            not content_details.get("contentRating", {}).get("ytRating") == "ytAgeRestricted"):

                            # Additional URL availability check
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            if self._check_video_url_availability(video_url):
                                validated_videos[video_id] = {
                                    "title": snippet.get("title", ""),
                                    "channel": snippet.get("channelTitle", ""),
                                    "description": snippet.get("description", "")
                                }
                            else:
                                logger.warning(f"Video {video_id} failed URL availability check")

                logger.info(f"Validated {len(validated_videos)} out of {len(video_ids)} videos")
                return validated_videos

            except requests.exceptions.Timeout:
                logger.warning(f"YouTube validation timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"YouTube validation request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in video validation on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        return {}

    def _check_video_url_availability(self, video_url: str) -> bool:
        """
        Check if a YouTube video URL is actually accessible and playable
        Simplified check focusing on basic availability

        Args:
            video_url: Full YouTube video URL

        Returns:
            True if video is accessible, False otherwise
        """
        try:
            self._rate_limit()

            # Make a HEAD request first (lighter than GET)
            response = self.session.head(video_url, timeout=10, allow_redirects=True)

            # Check if we get a successful response
            if response.status_code == 200:
                # Check the final URL after redirects
                final_url = response.url
                if "youtube.com/watch?v=" not in final_url:
                    # Redirected away from watch page (likely unavailable)
                    logger.warning(f"Video URL {video_url} redirected to {final_url}")
                    return False

                # Basic check passed - video page loads
                logger.info(f"Video {video_url} passed basic availability check")
                return True
            else:
                logger.warning(f"Video URL {video_url} returned status {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout checking video availability: {video_url}")
            # Don't fail on timeout - assume available
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error checking video availability: {video_url} - {str(e)}")
            # Don't fail on request errors - assume available
            return True
        except Exception as e:
            logger.warning(f"Unexpected error checking video availability: {video_url} - {str(e)}")
            # Don't fail on unexpected errors - assume available
            return True
    


    def _get_youtube_stats(self, video_ids: List[str]) -> Dict:
        """Get video statistics (views, likes, duration)"""
        if not self.youtube_api_key or not video_ids:
            return {}

        try:
            self._rate_limit()

            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "id": ",".join(video_ids),
                "part": "statistics,contentDetails",
                "key": self.youtube_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            stats = {}
            for item in response.json().get("items", []):
                video_id = item["id"]
                stats[video_id] = {
                    "viewCount": int(item["statistics"].get("viewCount", 0)),
                    "likeCount": int(item["statistics"].get("likeCount", 0)),
                    "commentCount": int(item["statistics"].get("commentCount", 0)),
                    "duration": item["contentDetails"]["duration"]
                }
            return stats
        except Exception as e:
            logger.error(f"Failed to get YouTube stats: {str(e)}")
            return {}
    
    def _fallback_youtube_search(self, topic: str, max_results: int = 5) -> List[Dict]:
        """Fallback YouTube search using web scraping with improved video ID extraction"""
        try:
            self._rate_limit()
            
            search_url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            videos = []
            
            # Try multiple regex patterns to extract video IDs (more robust)
            patterns = [
                r'"videoId":"([a-zA-Z0-9_-]{11})"',  # Standard video ID format
                r'data-video-id="([a-zA-Z0-9_-]{11})"',
                r'href="/watch\?v=([a-zA-Z0-9_-]{11})"'
            ]
            
            video_ids_found = set()
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                video_ids_found.update(matches)
                if len(video_ids_found) >= max_results:
                    break
            
            # Extract titles and build video objects
            # Look for titles paired with video IDs
            title_pattern = r'"title":{"simpleText":"([^"]+)"}'
            titles = re.findall(title_pattern, response.text)
            
            for i, video_id in enumerate(list(video_ids_found)[:max_results]):
                # Validate video ID format (must be exactly 11 characters, alphanumeric + _ -)
                if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    logger.warning(f"Skipping invalid video ID: {video_id}")
                    continue
                
                title = titles[i] if i < len(titles) else f"Video: {topic}"
                
                videos.append({
                    "title": title[:100],  # Truncate long titles
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": "Unknown",
                    "description": f"Search result for {topic}",
                    "relevance_score": 0.5,
                    "source": "fallback_scrape"
                })
            
            if not videos:
                logger.warning(f"No valid videos found via fallback scrape for '{topic}'")
                # Return a generic placeholder
                return [{
                    "title": f"YouTube search: {topic}",
                    "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}",
                    "channel": "YouTube Search",
                    "description": f"Direct search results for {topic} on YouTube",
                    "relevance_score": 0.3,
                    "source": "youtube_search_redirect"
                }]
            
            logger.info(f"Fallback scrape found {len(videos)} videos for '{topic}'")
            return videos
            
        except Exception as e:
            logger.error(f"YouTube fallback search failed: {str(e)}")
            # Return search redirect as last resort
            return [{
                "title": f"YouTube search: {topic}",
                "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}",
                "channel": "YouTube Search",
                "description": f"Direct search results for {topic} on YouTube",
                "relevance_score": 0.2,
                "source": "youtube_search_redirect"
            }]
    
    def _calculate_video_relevance(self, topic: str, video_item: Dict, stats: Dict) -> float:
        """
        Calculate relevance score for a video
        
        Factors:
        - Title match with topic (40%)
        - View count (30%)
        - Likes/engagement (20%)
        - Recency (10%)
        """
        score = 0.0
        
        # Title relevance
        title = video_item["snippet"]["title"].lower()
        topic_words = set(topic.lower().split())
        title_words = set(title.split())
        overlap = len(topic_words & title_words) / len(topic_words) if topic_words else 0
        score += overlap * 0.4
        
        # View count (normalized to 0-1)
        view_count = stats.get("viewCount", 0)
        if view_count > 0:
            # Log scale: 10k views = 0.5, 1M views = 1.0
            normalized_views = min(1.0, (view_count / 1000000) ** 0.5)
            score += normalized_views * 0.3
        
        # Engagement (likes + comments)
        like_count = stats.get("likeCount", 0)
        comment_count = stats.get("commentCount", 0)
        engagement = (like_count + comment_count) / max(view_count, 1)
        score += min(1.0, engagement * 100) * 0.2
        
        # Recency (videos from last year score higher)
        published_date = datetime.fromisoformat(
            video_item["snippet"]["publishedAt"].replace('Z', '+00:00')
        )
        days_old = (datetime.now(published_date.tzinfo) - published_date).days
        recency = max(0.0, 1.0 - (days_old / 365))
        score += recency * 0.1
        
        return score
    
    def scrape_website(self, url: str, extract_code: bool = True) -> Dict:
        """
        Scrape content from a website
        
        Args:
            url: Website URL to scrape
            extract_code: Whether to extract code blocks
        
        Returns:
            Dictionary with extracted content
        """
        try:
            self._rate_limit()
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract content
            content = {
                "url": url,
                "title": soup.title.string if soup.title else "Unknown",
                "headings": [],
                "paragraphs": [],
                "code_blocks": [] if extract_code else [],
                "lists": [],
                "extracted_at": datetime.now().isoformat()
            }
            
            # Extract headings
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                text = heading.get_text(strip=True)
                if text:
                    content["headings"].append({
                        "level": heading.name,
                        "text": text
                    })
            
            # Extract paragraphs
            for para in soup.find_all('p')[:10]:  # Limit to first 10 paragraphs
                text = para.get_text(strip=True)
                if text and len(text) > 50:  # Only include substantial paragraphs
                    content["paragraphs"].append(text)
            
            # Extract code blocks
            if extract_code:
                for code_block in soup.find_all(['code', 'pre']):
                    code_text = code_block.get_text(strip=True)
                    if code_text:
                        content["code_blocks"].append(code_text[:500])  # Limit to 500 chars
            
            # Extract lists
            for ul in soup.find_all(['ul', 'ol'])[:3]:  # Limit to first 3 lists
                items = []
                for li in ul.find_all('li')[:5]:  # Limit to first 5 items
                    text = li.get_text(strip=True)
                    if text:
                        items.append(text)
                if items:
                    content["lists"].append(items)
            
            logger.info(f"Successfully scraped {url}")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return {"error": str(e), "url": url}
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return {"error": str(e), "url": url}
    
    def rank_resources(self, resources: List[Dict], topic: str) -> List[Dict]:
        """
        Rank resources by relevance, quality, and authority
        
        Ranking factors:
        - Relevance to topic (40%)
        - Domain authority (30%)
        - Freshness (20%)
        - User signals (10%)
        """
        if not resources:
            return []
        
        # Known authoritative domains
        authority_domains = {
            "mdn.mozilla.org": 1.0,
            "python.org": 0.95,
            "nodejs.org": 0.95,
            "djangoproject.com": 0.95,
            "github.com": 0.9,
            "stackoverflow.com": 0.85,
            "medium.com": 0.7,
            "dev.to": 0.7,
            "freecodecamp.org": 0.85,
            "youtube.com": 0.75,
        }
        
        for resource in resources:
            score = 0.0
            
            # Relevance score
            relevance = resource.get("relevance_score", 0.5)
            if relevance == 0.5:
                # Calculate if not provided
                title = resource.get("title", "").lower()
                snippet = resource.get("snippet", "").lower()
                content = f"{title} {snippet}"
                
                topic_words = set(topic.lower().split())
                content_words = set(content.split())
                overlap = len(topic_words & content_words) / len(topic_words)
                relevance = min(1.0, overlap)
            
            score += relevance * 0.4
            
            # Domain authority
            domain = urlparse(resource.get("url", "")).netloc
            domain_score = authority_domains.get(domain, 0.5)
            score += domain_score * 0.3
            
            # Freshness (if date available)
            if "published_at" in resource or "extracted_at" in resource:
                published = resource.get("published_at") or resource.get("extracted_at")
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                    freshness = max(0.0, 1.0 - (days_old / 730))  # 2 years reference
                    score += freshness * 0.2
                except:
                    score += 0.15
            else:
                score += 0.15
            
            # User signals (views, likes, comments)
            if "view_count" in resource:
                views = resource.get("view_count", 0)
                user_signal = min(1.0, (views / 1000000) ** 0.5)
                score += user_signal * 0.1
            else:
                score += 0.05
            
            resource["ranking_score"] = score
        
        # Sort by ranking score
        ranked = sorted(resources, key=lambda x: x.get("ranking_score", 0), reverse=True)
        logger.info(f"Ranked {len(ranked)} resources for '{topic}'")
        return ranked
    
    def summarize_with_ollama(self, text: str, prompt_type: str = "summary") -> str:
        """
        Use local Gemma LLM (via Ollama) to summarize content
        
        Args:
            text: Text to summarize
            prompt_type: "summary", "key_points", "explanation"
        
        Returns:
            Summarized text
        """
        try:
            # Check if Ollama is running
            self._rate_limit()
            
            # Different prompts based on type
            prompts = {
                "summary": f"Summarize the following text in 2-3 sentences:\n\n{text}",
                "key_points": f"Extract 5 key learning points from this text:\n\n{text}",
                "explanation": f"Explain the following text in simple terms:\n\n{text}"
            }
            
            prompt = prompts.get(prompt_type, prompts["summary"])
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "gemma:2b",  # Using Gemma 2B model
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            summary = result.get("response", "").strip()
            
            logger.info(f"Generated {prompt_type} using Gemma LLM")
            return summary
            
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not running. Skipping LLM summarization.")
            return self._fallback_summary(text)
        except Exception as e:
            logger.error(f"Ollama summarization failed: {str(e)}")
            return self._fallback_summary(text)
    
    def _fallback_summary(self, text: str, max_sentences: int = 3) -> str:
        """Simple fallback summary using sentence extraction"""
        sentences = text.split('.')
        return '. '.join(sentences[:max_sentences]).strip() + "."

    def _db_fallback_roadmap(self, topic: str, skill_level: str = "beginner") -> Optional[Dict]:
        """
        Attempt to load a stored Roadmap from the database that matches the
        requested topic. This method is tolerant — it will inspect recent
        Roadmap entries and try to match the `topic` field inside the
        `roadmap_data` JSON or the related course title.
        Returns a roadmap dict compatible with `get_complete_roadmap` or
        `None` when no suitable fallback is found.
        """
        try:
            # Import models lazily so this module can be imported outside Django
            from .models import Roadmap

            # Get recent roadmaps to inspect
            recent = Roadmap.objects.all().order_by('-updated_at')[:50]

            topic_low = (topic or '').strip().lower()

            for rm in recent:
                data = rm.roadmap_data or {}
                # Match by explicit 'topic' in saved data
                saved_topic = (data.get('topic') or '').strip().lower()
                course_title = (rm.course.title or '').strip().lower() if hasattr(rm, 'course') else ''

                if topic_low and (topic_low in saved_topic or topic_low in course_title):
                    # Build a minimal roadmap shape
                    return {
                        'topic': data.get('topic', topic),
                        'skill_level': rm.skill_level or skill_level,
                        'generated_at': rm.updated_at.isoformat(),
                        'videos': data.get('videos', []),
                        'documentation': data.get('documentation', []),
                        'blogs': data.get('blogs', []),
                        'tools': data.get('tools', []),
                        'related_topics': data.get('related_topics', []),
                        'summary': data.get('summary', ''),
                        'estimated_hours': data.get('estimated_hours', 0),
                        'source': 'db_fallback'
                    }

            return None
        except Exception as e:
            logger.warning(f"Exception while attempting DB fallback: {e}")
            return None
    
    def get_complete_roadmap(self, topic: str, skill_level: str = "beginner", user_answers: dict = None) -> Dict:
        """
        Dynamic pipeline: Adaptive Search → Scrape → Rank → Summarize → Return
        Adapts search strategy based on resource availability and personalization

        Args:
            topic: Learning topic
            skill_level: "beginner", "intermediate", "advanced"
            user_answers: User's assessment answers for personalized resource ranking

        Returns:
            Complete learning roadmap with all resources
        """
        logger.info(f"Generating dynamic roadmap for '{topic}' ({skill_level}) with {'personalization' if user_answers else 'default ranking'}")

        try:
            roadmap = {
                "topic": topic,
                "skill_level": skill_level,
                "personalized": bool(user_answers),
                "generated_at": datetime.now().isoformat(),
                "videos": [],
                "documentation": [],
                "blogs": [],
                "tools": [],
                "related_topics": [],
                "summary": "",
                "estimated_hours": 0,
                "errors": []
            }

            # First, prefer admin-provided static videos stored in DB (CourseVideo)
            try:
                from courses.models import CourseVideo
                # If user provided weak topics, try to match them first
                matched_videos = []
                if user_answers:
                    # Attempt to identify weak topics from user_answers (simple heuristic)
                    weak_topics = []
                    # If user_answers is a dict of question idx -> answer, we can't map yet
                    # but if it's a list of topic strings, use them
                    if isinstance(user_answers, (list, tuple)):
                        weak_topics = user_answers
                    elif isinstance(user_answers, dict):
                        # placeholder: could be expanded to map question indices to topics
                        weak_topics = []

                    for wt in weak_topics:
                        qset = CourseVideo.objects.filter(is_active=True, topic__icontains=wt)
                        for v in qset:
                            matched_videos.append({
                                'title': v.title,
                                'url': v.url,
                                'channel': '',
                                'duration': 'Unknown',
                                'source': 'admin'
                            })

                # If no weak-topic matches, fallback to any active video for the course title
                if not matched_videos:
                    qset2 = CourseVideo.objects.filter(is_active=True, course__title__icontains=topic)
                    for v in qset2:
                        matched_videos.append({
                            'title': v.title,
                            'url': v.url,
                            'channel': '',
                            'duration': 'Unknown',
                            'source': 'admin'
                        })

                if matched_videos:
                    # Attach admin-provided videos but do NOT return early.
                    # We want LLM-generated chapters/topics to still be created
                    # and have these admin videos attached to matching topics.
                    roadmap['videos'] = matched_videos[:5]
                    roadmap['admin_videos_used'] = True
                    roadmap['admin_videos_count'] = len(matched_videos)
                    # Append to summary rather than replacing it
                    existing_summary = roadmap.get('summary', '') or ''
                    roadmap['summary'] = (existing_summary + ' ').strip() + f"Admin-provided videos available for {topic}."
                    logger.info(f"Attached {len(matched_videos)} admin videos for '{topic}' and will continue dynamic enrichment")
            except Exception as e:
                logger.debug(f"No admin videos available or DB error: {e}")

            # Dynamic search strategy based on resource availability
            search_strategy = self._determine_search_strategy(topic)

            # Step 1: Search for videos with adaptive fallback
            logger.info("Step 1: Searching for videos...")
            videos = self.search_youtube_videos(topic, max_results=search_strategy["video_limit"])
            roadmap["videos"] = videos[:3]

            # If limited videos found, expand search to related topics
            if len(videos) < 2:
                logger.info("Limited videos found, searching related topics...")
                related_videos = self._search_related_topic_videos(topic, max_results=3)
                roadmap["videos"].extend(related_videos[:2])

            # Step 2: Search for documentation with increased limit if videos are limited
            logger.info("Step 2: Searching for documentation...")
            docs_limit = search_strategy["docs_limit"]
            docs_search = self.search_resources(topic, search_type="documentation")

            if "organic_results" in docs_search:
                for result in docs_search["organic_results"][:docs_limit]:
                    # Scrape each documentation page
                    scraped = self.scrape_website(result["url"])

                    if "error" not in scraped:
                        doc_summary = self.summarize_with_ollama(
                            '\n'.join(scraped.get("paragraphs", [])[:3]),
                            prompt_type="summary"
                        )

                        roadmap["documentation"].append({
                            "title": result["title"],
                            "url": result["url"],
                            "snippet": result["snippet"],
                            "summary": doc_summary,
                            "domain": result["domain"]
                        })

            # Step 3: Search for blogs/articles with adaptive limits
            logger.info("Step 3: Searching for blogs and articles...")
            blog_limit = search_strategy["blog_limit"]
            blog_search = self.search_resources(topic, search_type="general")

            if "organic_results" in blog_search:
                # Get different results from docs search
                blogs = blog_search["organic_results"][len(roadmap["documentation"]):len(roadmap["documentation"])+blog_limit]

                for result in blogs:
                    scraped = self.scrape_website(result["url"])

                    if "error" not in scraped:
                        blog_summary = self.summarize_with_ollama(
                            '\n'.join(scraped.get("paragraphs", [])[:2]),
                            prompt_type="key_points"
                        )

                        roadmap["blogs"].append({
                            "title": result["title"],
                            "url": result["url"],
                            "summary": blog_summary,
                            "domain": result["domain"]
                        })

            # Step 4: If still limited resources, search for additional content types
            if len(roadmap["videos"]) + len(roadmap["documentation"]) + len(roadmap["blogs"]) < 5:
                logger.info("Limited resources found, expanding search...")
                additional_resources = self._search_additional_resources(topic)
                roadmap["blogs"].extend(additional_resources)

            # Step 5: Extract related topics from People Also Ask
            logger.info("Step 5: Extracting related topics...")
            if "people_also_ask" in blog_search:
                roadmap["related_topics"] = [
                    qa["question"] for qa in blog_search.get("people_also_ask", [])[:5]
                ]

            # Step 6: Generate overall summary
            logger.info("Step 6: Generating summary...")
            content_for_summary = '\n'.join([
                doc.get("summary", "") for doc in roadmap["documentation"][:2]
            ])

            if content_for_summary:
                roadmap["summary"] = self.summarize_with_ollama(
                    content_for_summary,
                    prompt_type="explanation"
                )
            else:
                # Fallback summary from available content
                all_content = []
                for video in roadmap["videos"][:2]:
                    all_content.append(video.get("description", ""))
                for blog in roadmap["blogs"][:2]:
                    all_content.append(blog.get("summary", ""))

                if all_content:
                    roadmap["summary"] = self.summarize_with_ollama(
                        '\n'.join(all_content),
                        prompt_type="explanation"
                    )

            # Step 7: Estimate learning hours
            roadmap["estimated_hours"] = self._estimate_learning_hours(
                len(roadmap["videos"]),
                len(roadmap["documentation"]),
                len(roadmap["blogs"]),
                skill_level
            )

            logger.info(f"Successfully generated dynamic roadmap for '{topic}' with {len(roadmap['videos'])} videos, {len(roadmap['documentation'])} docs, {len(roadmap['blogs'])} blogs")
            return roadmap

        except Exception as e:
            logger.error(f"Failed to generate roadmap: {str(e)}")
            # Try to fall back to a saved roadmap in the database (if available)
            try:
                fallback = self._db_fallback_roadmap(topic, skill_level)
                if fallback:
                    logger.info(f"Returning DB fallback roadmap for '{topic}'")
                    return fallback
            except Exception as fb_err:
                logger.warning(f"DB fallback failed: {fb_err}")

            return {
                "error": str(e),
                "topic": topic,
                "generated_at": datetime.now().isoformat()
            }
    
    def _determine_search_strategy(self, topic: str) -> Dict:
        """
        Determine adaptive search strategy based on topic characteristics

        Args:
            topic: Learning topic

        Returns:
            Dictionary with search limits for different resource types
        """
        # Default strategy
        strategy = {
            "video_limit": 5,
            "docs_limit": 3,
            "blog_limit": 3
        }

        # Adjust based on topic popularity/complexity
        topic_lower = topic.lower()

        # For popular topics, increase video search
        popular_topics = ["python", "javascript", "react", "machine learning", "data science"]
        if any(pt in topic_lower for pt in popular_topics):
            strategy["video_limit"] = 8
            strategy["blog_limit"] = 5

        # For niche/advanced topics, focus more on documentation
        niche_topics = ["quantum", "blockchain", "cryptography", "advanced"]
        if any(nt in topic_lower for nt in niche_topics):
            strategy["docs_limit"] = 5
            strategy["video_limit"] = 3

        # For beginner topics, prioritize tutorials
        beginner_indicators = ["basics", "introduction", "beginner", "fundamentals"]
        if any(bi in topic_lower for bi in beginner_indicators):
            strategy["video_limit"] = 7
            strategy["blog_limit"] = 4

        return strategy

    def _search_related_topic_videos(self, topic: str, max_results: int = 3) -> List[Dict]:
        """
        Search for videos on related topics when primary topic has limited results

        Args:
            topic: Original topic
            max_results: Maximum related videos to return

        Returns:
            List of related topic videos
        """
        try:
            # Generate related search terms
            related_queries = [
                f"{topic} tutorial",
                f"learn {topic}",
                f"{topic} course",
                f"{topic} basics",
                f"{topic} guide"
            ]

            all_videos = []
            for query in related_queries[:2]:  # Limit to 2 related queries
                videos = self.search_youtube_videos(query, max_results=2)
                all_videos.extend(videos)

            # Remove duplicates and limit results
            seen_urls = set()
            unique_videos = []
            for video in all_videos:
                if video["url"] not in seen_urls:
                    seen_urls.add(video["url"])
                    unique_videos.append(video)
                    if len(unique_videos) >= max_results:
                        break

            logger.info(f"Found {len(unique_videos)} related topic videos for '{topic}'")
            return unique_videos

        except Exception as e:
            logger.error(f"Failed to search related topic videos: {str(e)}")
            return []

    def _search_additional_resources(self, topic: str) -> List[Dict]:
        """
        Search for additional resources when primary searches yield limited results

        Args:
            topic: Learning topic

        Returns:
            List of additional blog/article resources
        """
        try:
            # Try alternative search queries
            alternative_queries = [
                f"{topic} explained",
                f"{topic} examples",
                f"{topic} tips and tricks",
                f"{topic} best practices"
            ]

            additional_resources = []
            for query in alternative_queries[:2]:  # Limit to 2 alternative queries
                search_results = self.search_resources(query, search_type="general")

                if "organic_results" in search_results:
                    for result in search_results["organic_results"][:2]:  # 2 per query
                        # Skip if already in main results (basic check)
                        if not any(res.get("url") == result["url"] for res in additional_resources):
                            # Quick scrape to get summary
                            scraped = self.scrape_website(result["url"])
                            if "error" not in scraped:
                                summary = self.summarize_with_ollama(
                                    '\n'.join(scraped.get("paragraphs", [])[:2]),
                                    prompt_type="key_points"
                                )

                                additional_resources.append({
                                    "title": result["title"],
                                    "url": result["url"],
                                    "summary": summary,
                                    "domain": result["domain"],
                                    "source": "additional_search"
                                })

            logger.info(f"Found {len(additional_resources)} additional resources for '{topic}'")
            return additional_resources

        except Exception as e:
            logger.error(f"Failed to search additional resources: {str(e)}")
            return []

    def _estimate_learning_hours(self, videos: int, docs: int, blogs: int, skill_level: str) -> float:
        """
        Estimate learning hours based on resources and skill level

        Rough estimates:
        - Video: 1 hour each
        - Documentation: 0.5 hours each
        - Blog: 0.25 hours each
        """
        hours = (videos * 1.0) + (docs * 0.5) + (blogs * 0.25)

        # Adjust by skill level
        if skill_level == "beginner":
            hours *= 1.5  # More time needed
        elif skill_level == "advanced":
            hours *= 0.6  # Less time needed

        return round(hours, 1)


# Utility function for easy integration
def get_dynamic_resources(topic: str, serper_key: str = None, youtube_key: str = None, skill_level: str = "beginner") -> Dict:
    """
    Main entry point for getting dynamic resources
    
    Usage:
        resources = get_dynamic_resources("Python Basics", serper_key="xxx", youtube_key="yyy")
    """
    fetcher = DynamicResourceFetcher(
        serper_api_key=serper_key,
        youtube_api_key=youtube_key
    )
    
    return fetcher.get_complete_roadmap(topic, skill_level)
