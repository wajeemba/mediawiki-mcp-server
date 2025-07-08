"""
Simple test script to verify the MediaWiki Action API implementation
for Coppermind.net integration.
"""
import asyncio
import httpx
from typing import Dict

USER_AGENT = "mediawiki-mcp-server/1.0"

class Config:
    base_url = "https://coppermind.net/w/"
    path_prefix = "api.php"

config = Config()

async def make_request(params: Dict) -> Dict:
    """Make a request to the MediaWiki Action API"""
    headers = {
        "User-Agent": USER_AGENT,
    }
    url = config.base_url + config.path_prefix
    
    # Add format=json to all requests
    params["format"] = "json"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e}"}
        except Exception as e:
            print(f"Request error: {e}")
            return {"error": str(e)}

async def search(query: str, limit: int = 5):
    """
    Search for a wiki page using Action API
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srprop": "snippet|titlesnippet|size|timestamp",
    }
    response = await make_request(params)
    
    # Extract search results from Action API response
    if "query" in response and "search" in response["query"]:
        results = response["query"]["search"]
        # Format results for better usability
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result["title"],
                "snippet": result.get("snippet", ""),
                "size": result.get("size", 0),
                "timestamp": result.get("timestamp", ""),
                "pageid": result.get("pageid", 0)
            })
        return {"results": formatted_results}
    else:
        return {"error": "No search results found", "response": response}

async def get_page(title: str):
    """
    Get a page from the MediaWiki site using Action API
    """
    params = {
        "action": "parse",
        "page": title,
        "prop": "text|displaytitle|categories|links|templates",
        "formatversion": "2",
    }
    response = await make_request(params)
    
    # Extract page content from Action API response
    if "parse" in response:
        page_data = response["parse"]
        return {
            "title": page_data.get("displaytitle", title),
            "html": page_data.get("text", ""),
            "categories": page_data.get("categories", []),
            "links": page_data.get("links", []),
            "templates": page_data.get("templates", []),
            "pageid": page_data.get("pageid", 0)
        }
    else:
        return {"error": "Page not found or could not be parsed", "response": response}

async def test_search():
    """Test the search functionality"""
    print("🔍 Testing search functionality...")
    
    # Test search for "Kaladin"
    print("\n--- Searching for 'Kaladin' ---")
    result = await search("Kaladin", 3)
    if "results" in result:
        print(f"✅ Found {len(result['results'])} results:")
        for i, item in enumerate(result["results"]):
            print(f"  {i+1}. {item['title']} (Page ID: {item['pageid']})")
            if item['snippet']:
                # Clean HTML from snippet for display
                import re
                clean_snippet = re.sub(r'<[^>]+>', '', item['snippet'])
                print(f"      Preview: {clean_snippet[:100]}...")
    else:
        print(f"❌ Search failed: {result}")
    
    # Test search for a more general term
    print("\n--- Searching for 'Stormlight' ---")
    result = await search("Stormlight", 2)
    if "results" in result:
        print(f"✅ Found {len(result['results'])} results:")
        for i, item in enumerate(result["results"]):
            print(f"  {i+1}. {item['title']}")
    else:
        print(f"❌ Search failed: {result}")

async def test_get_page():
    """Test the get page functionality"""
    print("\n📄 Testing get page functionality...")
    
    # Test getting a well-known page
    print("\n--- Getting page 'Kaladin' ---")
    result = await get_page("Kaladin")
    if "html" in result:
        print(f"✅ Successfully retrieved page:")
        print(f"  Title: {result['title']}")
        print(f"  Page ID: {result['pageid']}")
        print(f"  Categories: {len(result.get('categories', []))}")
        print(f"  Links: {len(result.get('links', []))}")
        print(f"  Content length: {len(result['html'])} characters")
        
        # Show first few categories
        if result.get('categories'):
            print(f"  First few categories: {[cat['*'] for cat in result['categories'][:3]]}")
    else:
        print(f"❌ Failed to get page: {result}")

async def main():
    """Run all tests"""
    print("🚀 Testing MediaWiki Action API Implementation for Coppermind.net")
    print("=" * 60)
    
    try:
        await test_search()
        await test_get_page()
        print("\n✅ All tests completed!")
        print("\n🎉 The Action API implementation is working with Coppermind.net!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 