"""
Test script for our modified MediaWiki MCP Server
Tests both search and get_page functions directly
"""
import asyncio
import sys
sys.path.insert(0, 'src')

# Import our modified server functions
from mediawiki_mcp_server.main import search, get_page, make_request

async def test_search_function():
    """Test the search function"""
    print("🔍 Testing search function...")
    
    # Test 1: Search for Kaladin
    print("\n--- Search Test 1: 'Kaladin' ---")
    result = await search("Kaladin", 3)
    
    if "results" in result and len(result["results"]) > 0:
        print(f"✅ Found {len(result['results'])} results:")
        for i, item in enumerate(result["results"], 1):
            print(f"  {i}. {item['title']} (ID: {item['pageid']})")
    else:
        print(f"❌ Search failed: {result}")
        return False
    
    # Test 2: Search for magic system
    print("\n--- Search Test 2: 'Surgebinding' ---")
    result = await search("Surgebinding", 2)
    
    if "results" in result:
        print(f"✅ Found {len(result['results'])} results:")
        for i, item in enumerate(result["results"], 1):
            print(f"  {i}. {item['title']}")
    else:
        print(f"❌ Search failed: {result}")
        return False
    
    return True

async def test_get_page_function():
    """Test the get_page function"""
    print("\n📄 Testing get_page function...")
    
    # Test 1: Get Kaladin page
    print("\n--- Page Test 1: 'Kaladin' ---")
    result = await get_page("Kaladin")
    
    if "html" in result and result["html"]:
        print(f"✅ Successfully retrieved page:")
        print(f"  Title: {result['title']}")
        print(f"  Page ID: {result['pageid']}")
        print(f"  Content length: {len(result['html'])} characters")
        print(f"  Categories: {len(result.get('categories', []))}")
        print(f"  Links: {len(result.get('links', []))}")
        
        # Show some categories
        if result.get('categories'):
            cats = [cat.get('*', cat) for cat in result['categories'][:3]]
            print(f"  Sample categories: {cats}")
            
    else:
        print(f"❌ Failed to get page: {result}")
        return False
    
    # Test 2: Get a magic system page  
    print("\n--- Page Test 2: 'Surgebinding' ---")
    result = await get_page("Surgebinding")
    
    if "html" in result and result["html"]:
        print(f"✅ Successfully retrieved Surgebinding page:")
        print(f"  Title: {result['title']}")
        print(f"  Content length: {len(result['html'])} characters")
    else:
        print(f"❌ Failed to get Surgebinding page: {result}")
    
    return True

async def test_direct_api():
    """Test the make_request function directly"""
    print("\n🔧 Testing direct API access...")
    
    # Test a simple API info request
    params = {
        "action": "query",
        "meta": "siteinfo",
        "siprop": "general"
    }
    
    result = await make_request(params)
    
    if "query" in result and "general" in result["query"]:
        site_info = result["query"]["general"]
        print(f"✅ Site info retrieved:")
        print(f"  Site name: {site_info.get('sitename', 'Unknown')}")
        print(f"  Main page: {site_info.get('mainpage', 'Unknown')}")
        print(f"  Wiki version: {site_info.get('generator', 'Unknown')}")
        return True
    else:
        print(f"❌ API test failed: {result}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Modified MediaWiki MCP Server for Coppermind.net")
    print("=" * 65)
    print(f"Python version: {sys.version}")
    print()
    
    all_passed = True
    
    try:
        # Test 1: Direct API
        if not await test_direct_api():
            all_passed = False
            
        # Test 2: Search function
        if not await test_search_function():
            all_passed = False
            
        # Test 3: Get page function  
        if not await test_get_page_function():
            all_passed = False
            
        print("\n" + "=" * 65)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Your modified MCP server is ready for Coppermind.net!")
            print("✅ Action API implementation is working perfectly!")
        else:
            print("❌ Some tests failed")
            
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 