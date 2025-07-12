"""
Pytest-based tests for the Cosmere DM MCP Server
"""
import pytest
import asyncio
from typing import Dict, List, Any
import time

from mediawiki_mcp_server.main import search, get_page, make_request, get_server_info


class TestBasicFunctionality:
    """Test basic MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_api_connection(self):
        """Test basic API connectivity"""
        params = {
            "action": "query",
            "meta": "siteinfo",
            "siprop": "general"
        }
        
        result = await make_request(params)
        
        assert "query" in result, f"Expected 'query' in response, got: {result}"
        assert "general" in result["query"], f"Expected 'general' in query, got: {result['query']}"
        
        site_info = result["query"]["general"]
        assert "sitename" in site_info, "Expected sitename in site info"
        assert "mainpage" in site_info, "Expected mainpage in site info"
    
    @pytest.mark.asyncio
    async def test_search_function_basic(self):
        """Test basic search functionality"""
        result = await search("Kaladin", 3)
        
        assert "results" in result, f"Expected 'results' in response, got: {result}"
        assert len(result["results"]) > 0, "Expected at least one search result"
        
        # Check result structure
        first_result = result["results"][0]
        assert "title" in first_result, "Expected 'title' in search result"
        assert "pageid" in first_result, "Expected 'pageid' in search result"
        assert "snippet" in first_result, "Expected 'snippet' in search result"
    
    @pytest.mark.asyncio
    async def test_get_page_function_basic(self):
        """Test basic get_page functionality"""
        result = await get_page("Kaladin")
        
        assert "title" in result, f"Expected 'title' in response, got: {result}"
        assert "html" in result, f"Expected 'html' in response, got: {result}"
        assert "pageid" in result, f"Expected 'pageid' in response, got: {result}"
        assert len(result["html"]) > 0, "Expected non-empty HTML content"
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test search with empty query"""
        result = await search("", 1)
        
        # Should handle empty query gracefully
        assert isinstance(result, dict), "Expected dict response for empty query"
        # Either returns empty results or error - both are acceptable
    
    @pytest.mark.asyncio
    async def test_get_page_nonexistent(self):
        """Test getting a non-existent page"""
        result = await get_page("ThisPageDoesNotExist123456789")
        
        # Should handle non-existent page gracefully
        assert isinstance(result, dict), "Expected dict response for non-existent page"
        assert "error" in result, "Expected error for non-existent page"


class TestSelfDocumentation:
    """Test self-documentation functionality"""
    
    @pytest.mark.asyncio
    async def test_get_server_info(self):
        """Test server info function"""
        result = await get_server_info()
        
        assert "server_name" in result, "Expected server_name in server info"
        assert "server_version" in result, "Expected server_version in server info"
        assert "wiki_info" in result, "Expected wiki_info in server info"
        assert "purpose" in result, "Expected purpose in server info"
        
        # Check wiki info structure
        wiki_info = result["wiki_info"]
        assert "name" in wiki_info, "Expected name in wiki_info"
        assert "url" in wiki_info, "Expected url in wiki_info"
        assert "main_page" in wiki_info, "Expected main_page in wiki_info"
        
        # Check that purpose mentions Cosmere/DM
        assert "Cosmere" in result["purpose"], "Expected purpose to mention Cosmere"
        assert "DM" in result["purpose"] or "Dungeon Master" in result["purpose"], "Expected purpose to mention DM"
    
    

class TestCanonValidation:
    """Test canon validation functionality"""
    
    @pytest.mark.canon
    @pytest.mark.asyncio
    async def test_kaladin_canon_accuracy(self, canon_validator):
        """Test that Kaladin page contains expected canon information"""
        result = await get_page("Kaladin")
        
        validation = canon_validator.validate_character_info("Kaladin", result)
        
        assert validation["status"] == "valid", f"Canon validation failed: {validation.get('issues', [])}"
    
    @pytest.mark.canon
    @pytest.mark.asyncio
    async def test_surgebinding_canon_accuracy(self, canon_validator):
        """Test that Surgebinding page contains expected canon information"""
        result = await get_page("Surgebinding")
        
        validation = canon_validator.validate_character_info("Surgebinding", result)
        
        assert validation["status"] == "valid", f"Canon validation failed: {validation.get('issues', [])}"
    
    @pytest.mark.canon
    @pytest.mark.asyncio
    async def test_stormlight_search_results(self, canon_validator):
        """Test that Stormlight searches return expected results"""
        result = await search("Stormlight", 10)
        
        assert "results" in result, "Expected results in search response"
        
        validation = canon_validator.validate_search_results("Stormlight", result["results"])
        
        assert validation["status"] == "valid", f"Search validation failed: {validation.get('message', '')}"
    
    @pytest.mark.canon
    @pytest.mark.asyncio
    async def test_magic_systems_exist(self, canon_facts):
        """Test that all major magic systems can be found"""
        magic_systems = canon_facts["magic_systems"]["search_terms"]
        
        for system in magic_systems:
            result = await search(system, 1)
            
            assert "results" in result, f"Search failed for {system}: {result}"
            assert len(result["results"]) > 0, f"No results found for magic system: {system}"
            
            # Check that we can get the page
            if result["results"]:
                page_result = await get_page(result["results"][0]["title"])
                assert "html" in page_result, f"Failed to get page for {system}: {page_result}"


class TestPerformance:
    """Test performance requirements"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_search_performance(self, performance_thresholds):
        """Test search performance meets thresholds"""
        start_time = time.time()
        
        result = await search("Kaladin", 5)
        
        elapsed = time.time() - start_time
        
        assert elapsed < performance_thresholds["search_max_time"], \
            f"Search took {elapsed:.2f}s, expected < {performance_thresholds['search_max_time']}s"
        
        assert "results" in result, "Expected successful search within time limit"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_get_page_performance(self, performance_thresholds):
        """Test get_page performance meets thresholds"""
        start_time = time.time()
        
        result = await get_page("Kaladin")
        
        elapsed = time.time() - start_time
        
        assert elapsed < performance_thresholds["get_page_max_time"], \
            f"Get page took {elapsed:.2f}s, expected < {performance_thresholds['get_page_max_time']}s"
        
        assert "html" in result, "Expected successful page retrieval within time limit"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_request_performance(self, performance_thresholds):
        """Test API request performance meets thresholds"""
        start_time = time.time()
        
        params = {"action": "query", "meta": "siteinfo", "siprop": "general"}
        result = await make_request(params)
        
        elapsed = time.time() - start_time
        
        assert elapsed < performance_thresholds["api_request_max_time"], \
            f"API request took {elapsed:.2f}s, expected < {performance_thresholds['api_request_max_time']}s"
        
        assert "query" in result, "Expected successful API request within time limit"
    



class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_search_with_special_characters(self):
        """Test search with special characters"""
        result = await search("Kaladin's", 1)
        
        # Should handle special characters gracefully
        assert isinstance(result, dict), "Expected dict response for special characters"
    
    @pytest.mark.asyncio
    async def test_search_with_numbers(self):
        """Test search with numbers"""
        result = await search("Bridge Four", 1)
        
        assert isinstance(result, dict), "Expected dict response for numbers"
        if "results" in result:
            assert len(result["results"]) >= 0, "Expected non-negative result count"
    
    @pytest.mark.asyncio
    async def test_get_page_with_special_characters(self):
        """Test getting page with special characters in title"""
        result = await get_page("Kaladin's")
        
        # Should handle gracefully - either success or appropriate error
        assert isinstance(result, dict), "Expected dict response for special characters"
    
    @pytest.mark.asyncio
    async def test_large_search_limit(self):
        """Test search with large limit"""
        result = await search("Stormlight", 50)
        
        assert isinstance(result, dict), "Expected dict response for large limit"
        if "results" in result:
            # Should either return results or handle gracefully
            assert len(result["results"]) >= 0, "Expected non-negative result count"


class TestIntegration:
    """Integration tests that combine multiple functions"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_then_get_page(self):
        """Test searching then getting the first result"""
        # Search for Kaladin
        search_result = await search("Kaladin", 1)
        
        assert "results" in search_result, "Expected search results"
        assert len(search_result["results"]) > 0, "Expected at least one result"
        
        # Get the first result
        first_result = search_result["results"][0]
        page_result = await get_page(first_result["title"])
        
        assert "html" in page_result, "Expected page content"
        assert page_result["title"] == first_result["title"], "Page title should match search result"
    

    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_searches(self):
        """Test multiple searches in sequence"""
        queries = ["Kaladin", "Shallan", "Adolin"]
        
        for query in queries:
            result = await search(query, 1)
            
            assert "results" in result, f"Search failed for {query}"
            assert len(result["results"]) > 0, f"No results for {query}"
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        # Test concurrent searches
        tasks = [
            search("Kaladin", 2),
            search("Shallan", 2),
            search("Adolin", 2)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            assert "results" in result, f"Concurrent search {i} failed"
            assert len(result["results"]) > 0, f"No results for concurrent search {i}"


@pytest.mark.canon
class TestCanonFramework:
    """Test the canon validation framework itself"""
    
    def test_canon_validator_initialization(self, canon_validator):
        """Test that canon validator initializes correctly"""
        assert canon_validator is not None
        assert hasattr(canon_validator, 'canon_facts')
        assert hasattr(canon_validator, 'validate_character_info')
        assert hasattr(canon_validator, 'validate_search_results')
    
    def test_canon_facts_structure(self, canon_facts):
        """Test that canon facts are properly structured"""
        assert isinstance(canon_facts, dict)
        assert "kaladin" in canon_facts
        assert "surgebinding" in canon_facts
        
        # Check kaladin structure
        kaladin_facts = canon_facts["kaladin"]
        assert "title" in kaladin_facts
        assert "categories_should_include" in kaladin_facts
        assert "should_mention" in kaladin_facts


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 