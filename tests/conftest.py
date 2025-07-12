"""
Pytest configuration and fixtures for Cosmere DM MCP Server tests
"""
import pytest
import asyncio
from typing import Dict, List, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mediawiki_mcp_server.main import search, get_page, make_request, config


@pytest.fixture
def canon_facts():
    """
    Known canon facts for validation testing
    Format: {"concept": {"expected_data": value, "source": "page_title"}}
    """
    return {
        "kaladin": {
            "title": "Kaladin", 
            "categories_should_include": ["Windrunners", "Knights Radiant"],
            "should_mention": ["Syl", "Bridge Four", "Surgebinding"],
            "source": "Kaladin"
        },
        "surgebinding": {
            "title": "Surgebinding",
            "categories_should_include": ["Magic"],
            "should_mention": ["Stormlight", "spren", "Nahel bond"],
            "source": "Surgebinding"
        },
        "stormlight_archive": {
            "search_terms": ["Stormlight", "Stormlight Archive"],
            "should_find": ["The Way of Kings", "Words of Radiance", "Oathbringer"],
            "min_results": 3
        },
        "magic_systems": {
            "search_terms": ["Allomancy", "Feruchemy", "Hemalurgy", "Surgebinding"],
            "should_all_exist": True
        }
    }


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing"""
    return {
        "search_max_time": 3.0,  # seconds
        "get_page_max_time": 5.0,  # seconds
        "api_request_max_time": 2.0,  # seconds
    }


@pytest.fixture
def mock_responses():
    """Mock responses for testing without hitting the API"""
    return {
        "search_kaladin": {
            "query": {
                "search": [
                    {
                        "title": "Kaladin",
                        "snippet": "Kaladin is a <span class=\"searchmatch\">Knight Radiant</span>",
                        "size": 50000,
                        "timestamp": "2023-01-01T00:00:00Z",
                        "pageid": 1234
                    }
                ]
            }
        },
        "page_kaladin": {
            "parse": {
                "title": "Kaladin",
                "displaytitle": "Kaladin",
                "pageid": 1234,
                "text": "<div>Kaladin is a Knight Radiant of the Windrunners...</div>",
                "categories": [
                    {"*": "Windrunners"},
                    {"*": "Knights Radiant"},
                    {"*": "Bridge Four"}
                ],
                "links": [
                    {"*": "Syl"},
                    {"*": "Bridge Four"},
                    {"*": "Surgebinding"}
                ]
            }
        }
    }


@pytest.fixture
async def test_client():
    """Test client setup"""
    # Store original config
    original_base_url = config.base_url
    
    # Can be overridden for testing
    yield config
    
    # Restore original config
    config.base_url = original_base_url


class CanonValidator:
    """Helper class for validating canon accuracy"""
    
    def __init__(self, canon_facts: Dict[str, Any]):
        self.canon_facts = canon_facts
    
    def validate_character_info(self, character_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character information against canon"""
        character_key = character_name.lower()
        if character_key not in self.canon_facts:
            return {"status": "unknown", "message": f"No canon data for {character_name}"}
        
        expected = self.canon_facts[character_key]
        issues = []
        
        # Check title
        if "title" in expected and result.get("title") != expected["title"]:
            issues.append(f"Title mismatch: got '{result.get('title')}', expected '{expected['title']}'")
        
        # Check categories
        if "categories_should_include" in expected:
            result_categories = [cat.get("*", cat) for cat in result.get("categories", [])]
            for required_cat in expected["categories_should_include"]:
                if required_cat not in result_categories:
                    issues.append(f"Missing category: {required_cat}")
        
        # Check content mentions
        if "should_mention" in expected:
            content = result.get("html", "")
            for mention in expected["should_mention"]:
                if mention not in content:
                    issues.append(f"Should mention: {mention}")
        
        return {
            "status": "valid" if not issues else "invalid",
            "issues": issues,
            "character": character_name
        }
    
    def validate_search_results(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate search results against canon expectations"""
        for fact_key, fact_data in self.canon_facts.items():
            if "search_terms" in fact_data and query in fact_data["search_terms"]:
                # Check minimum results
                if "min_results" in fact_data and len(results) < fact_data["min_results"]:
                    return {
                        "status": "invalid",
                        "message": f"Too few results for '{query}': got {len(results)}, expected at least {fact_data['min_results']}"
                    }
                
                # Check expected results
                if "should_find" in fact_data:
                    result_titles = [r["title"] for r in results]
                    missing = [title for title in fact_data["should_find"] if title not in result_titles]
                    if missing:
                        return {
                            "status": "invalid",
                            "message": f"Missing expected results for '{query}': {missing}"
                        }
        
        return {"status": "valid", "query": query}


@pytest.fixture
def canon_validator(canon_facts):
    """Canon validation helper"""
    return CanonValidator(canon_facts)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close() 