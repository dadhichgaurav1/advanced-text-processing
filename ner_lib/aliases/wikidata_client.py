"""Wikidata API client with rate limiting and caching."""

from typing import Dict, List, Optional
import logging
import time
from cachetools import TTLCache
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class WikidataClient:
    """Client for querying Wikidata API with rate limiting and caching."""
    
    def __init__(
        self,
        api_endpoint: str = "https://www.wikidata.org/w/api.php",
        search_limit: int = 10,
        requests_per_minute: int = 10000,
        cache_ttl_seconds: int = 3600,
        cache_maxsize: int = 1000,
        timeout_seconds: int = 10
    ):
        """
        Initialize Wikidata client.
        
        Args:
            api_endpoint: Wikidata API endpoint
            search_limit: Number of entities per search
            requests_per_minute: Rate limit for API requests
            cache_ttl_seconds: Cache TTL in seconds
            cache_maxsize: Maximum cache size
            timeout_seconds: Request timeout in seconds
        """
        self.api_endpoint = api_endpoint
        self.search_limit = search_limit
        self.requests_per_minute = requests_per_minute
        self.timeout_seconds = timeout_seconds
        
        # Rate limiting
        self.min_request_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
        
        # Caching
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)
        
        # Session with retries
        self.session = requests.Session()
        
        # Set User-Agent to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'NER-Library/0.2.0 (https://github.com/ner-lib; contact@example.com) Python-Requests'
        })
        
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
    
    def _rate_limit(self):
        """Apply rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_entity(self, query: str, language: str = "en") -> Dict:
        """
        Search for an entity in Wikidata.
        
        Args:
            query: Search query (entity name)
            language: Language code (default: "en")
        
        Returns:
            Dictionary with:
            - entities: List of matched entities with id, label, description
            - success: Whether the search was successful
        """
        # Check cache
        cache_key = f"search:{query}:{language}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for search: {query}")
            return self.cache[cache_key]
        
        # Apply rate limiting
        self._rate_limit()
        
        # Build request
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": language,
            "limit": self.search_limit,
            "format": "json"
        }
        
        try:
            response = self.session.get(
                self.api_endpoint,
                params=params,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            entities = []
            if "search" in data:
                for item in data["search"]:
                    entities.append({
                        "id": item.get("id", ""),
                        "label": item.get("label", ""),
                        "description": item.get("description", ""),
                        "url": item.get("concepturi", "")
                    })
            
            result = {
                "entities": entities,
                "success": True
            }
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Wikidata search error for '{query}': {e}")
            return {
                "entities": [],
                "success": False,
                "error": str(e)
            }
    
    def get_entity_data(self, entity_id: str, language: str = "en") -> Dict:
        """
        Get detailed data for a Wikidata entity.
        
        Args:
            entity_id: Wikidata entity ID (e.g., "Q312" for Apple Inc.)
            language: Language code (default: "en")
        
        Returns:
            Dictionary with:
            - aliases: List of aliases
            - description: Entity description
            - labels: Entity labels in different languages
            - success: Whether the fetch was successful
        """
        # Check cache
        cache_key = f"entity:{entity_id}:{language}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for entity: {entity_id}")
            return self.cache[cache_key]
        
        # Apply rate limiting
        self._rate_limit()
        
        # Build request
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "format": "json",
            "languages": language
        }
        
        try:
            response = self.session.get(
                self.api_endpoint,
                params=params,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            if "entities" in data and entity_id in data["entities"]:
                entity = data["entities"][entity_id]
                
                # Extract aliases
                aliases = []
                if "aliases" in entity and language in entity["aliases"]:
                    aliases = [alias["value"] for alias in entity["aliases"][language]]
                
                # Extract description
                description = ""
                if "descriptions" in entity and language in entity["descriptions"]:
                    description = entity["descriptions"][language]["value"]
                
                # Extract label
                label = ""
                if "labels" in entity and language in entity["labels"]:
                    label = entity["labels"][language]["value"]
                
                result = {
                    "aliases": aliases,
                    "description": description,
                    "label": label,
                    "success": True
                }
                
                # Cache result
                self.cache[cache_key] = result
                
                return result
            else:
                return {
                    "aliases": [],
                    "description": "",
                    "label": "",
                    "success": False,
                    "error": f"Entity {entity_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Wikidata entity fetch error for '{entity_id}': {e}")
            return {
                "aliases": [],
                "description": "",
                "label": "",
                "success": False,
                "error": str(e)
            }
    
    def get_aliases_for_entity(self, entity_name: str, language: str = "en") -> Dict:
        """
        Get aliases and description for an entity by searching for it.
        
        Args:
            entity_name: Name of the entity to search for
            language: Language code (default: "en")
        
        Returns:
            Dictionary with:
            - aliases: List of aliases
            - description: Short description
            - success: Whether the operation was successful
        """
        # First, search for the entity
        search_result = self.search_entity(entity_name, language)
        
        if not search_result["success"] or not search_result["entities"]:
            return {
                "aliases": [],
                "description": "",
                "success": False,
                "error": "Entity not found in search"
            }
        
        # Get the first (most relevant) entity
        best_match = search_result["entities"][0]
        entity_id = best_match["id"]
        
        # Get detailed entity data
        entity_data = self.get_entity_data(entity_id, language)
        
        # Add the label as an alias if not already present
        if best_match["label"] and best_match["label"] not in entity_data["aliases"]:
            entity_data["aliases"].insert(0, best_match["label"])
        
        # Use description from search if entity data doesn't have one
        if not entity_data["description"] and best_match["description"]:
            entity_data["description"] = best_match["description"]
        
        return entity_data
