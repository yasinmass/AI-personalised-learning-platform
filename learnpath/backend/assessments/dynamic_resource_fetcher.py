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
        Search for YouTube videos using YouTube Data API
        
        Args:
            topic: Video topic to search
            max_results: Maximum videos to return
        
        Returns:
            List of video results with metadata
        """
        if not self.youtube_api_key:
            logger.warning("YouTube API key not configured. Using Serper fallback.")
            return self._fallback_youtube_search(topic, max_results)
        
        try:
            self._rate_limit()
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "q": f"{topic} tutorial course",
                "part": "snippet",
                "type": "video",
                "maxResults": max_results,
                "order": "relevance",
                "relevanceLanguage": "en",
                "key": self.youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            videos = []
            
            # Extract video IDs for getting statistics
            video_ids = [item["id"]["videoId"] for item in results.get("items", [])]
            video_stats = self._get_youtube_stats(video_ids) if video_ids else {}
            
            for item in results.get("items", []):
                video_id = item["id"]["videoId"]
                stats = video_stats.get(video_id, {})
                
                videos.append({
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": item["snippet"]["channelTitle"],
                    "description": item["snippet"]["description"][:200],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": stats.get("viewCount", 0),
                    "like_count": stats.get("likeCount", 0),
                    "comment_count": stats.get("commentCount", 0),
                    "duration": stats.get("duration", "Unknown"),
                    "relevance_score": self._calculate_video_relevance(topic, item, stats)
                })
            
            # Sort by relevance score
            videos.sort(key=lambda x: x["relevance_score"], reverse=True)
            logger.info(f"Found {len(videos)} YouTube videos for '{topic}'")
            return videos
            
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {str(e)}")
            return self._fallback_youtube_search(topic, max_results)
    
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
        """Fallback YouTube search using web scraping"""
        try:
            self._rate_limit()
            
            search_url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Extract video data from initial data
            pattern = r'"videoId":"([^"]+)".*?"title":{"simpleText":"([^"]+)"}'
            matches = re.findall(pattern, response.text)
            
            videos = []
            for video_id, title in matches[:max_results]:
                videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": "Unknown",
                    "description": "Fetched via YouTube fallback",
                    "relevance_score": 0.5
                })
            
            return videos
        except Exception as e:
            logger.error(f"YouTube fallback search failed: {str(e)}")
            return []
    
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
    
    def get_complete_roadmap(self, topic: str, skill_level: str = "beginner") -> Dict:
        """
        Complete pipeline: Search → Scrape → Rank → Summarize → Return
        
        Args:
            topic: Learning topic
            skill_level: "beginner", "intermediate", "advanced"
        
        Returns:
            Complete learning roadmap with all resources
        """
        logger.info(f"Generating roadmap for '{topic}' ({skill_level})")
        
        try:
            roadmap = {
                "topic": topic,
                "skill_level": skill_level,
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
            
            # Step 1: Search for videos
            logger.info("Step 1: Searching for videos...")
            videos = self.search_youtube_videos(topic, max_results=5)
            roadmap["videos"] = videos[:3]
            
            # Step 2: Search for documentation
            logger.info("Step 2: Searching for documentation...")
            docs_search = self.search_resources(topic, search_type="documentation")
            
            if "organic_results" in docs_search:
                for result in docs_search["organic_results"][:3]:
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
            
            # Step 3: Search for blogs/articles
            logger.info("Step 3: Searching for blogs...")
            blog_search = self.search_resources(topic, search_type="general")
            
            if "organic_results" in blog_search:
                blogs = blog_search["organic_results"][3:6]  # Get different results
                
                for result in blogs[:2]:
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
            
            # Step 4: Extract related topics from People Also Ask
            logger.info("Step 4: Extracting related topics...")
            if "people_also_ask" in blog_search:
                roadmap["related_topics"] = [
                    qa["question"] for qa in blog_search.get("people_also_ask", [])[:5]
                ]
            
            # Step 5: Generate overall summary
            logger.info("Step 5: Generating summary...")
            content_for_summary = '\n'.join([
                doc.get("summary", "") for doc in roadmap["documentation"][:2]
            ])
            
            if content_for_summary:
                roadmap["summary"] = self.summarize_with_ollama(
                    content_for_summary,
                    prompt_type="explanation"
                )
            
            # Step 6: Estimate learning hours
            roadmap["estimated_hours"] = self._estimate_learning_hours(
                len(roadmap["videos"]),
                len(roadmap["documentation"]),
                len(roadmap["blogs"]),
                skill_level
            )
            
            logger.info(f"Successfully generated roadmap for '{topic}'")
            return roadmap
            
        except Exception as e:
            logger.error(f"Failed to generate roadmap: {str(e)}")
            return {
                "error": str(e),
                "topic": topic,
                "generated_at": datetime.now().isoformat()
            }
    
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
