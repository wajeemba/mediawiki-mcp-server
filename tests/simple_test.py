"""
Simple Python 3.8 compatible test for MediaWiki Action API
Uses only built-in libraries to avoid installation issues
"""
import urllib.request
import urllib.parse
import json
import sys

def test_coppermind_api():
    """Test basic connectivity to Coppermind.net Action API"""
    
    # Test parameters
    base_url = "https://coppermind.net/w/api.php"
    params = {
        "action": "query",
        "list": "search", 
        "srsearch": "Kaladin",
        "srlimit": "3",
        "format": "json"
    }
    
    # Build URL
    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    print("🚀 Testing Coppermind.net MediaWiki Action API")
    print("=" * 50)
    print(f"URL: {full_url}")
    
    try:
        # Make request
        headers = {"User-Agent": "mediawiki-mcp-server/1.0"}
        req = urllib.request.Request(full_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        # Check results
        if "query" in data and "search" in data["query"]:
            results = data["query"]["search"]
            print(f"✅ SUCCESS: Found {len(results)} results for 'Kaladin'")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (ID: {result['pageid']})")
                
            print(f"\n🎉 Action API is working with Coppermind.net!")
            print(f"Python version: {sys.version}")
            return True
            
        else:
            print(f"❌ FAILED: Unexpected response format")
            print(f"Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_coppermind_api()
    sys.exit(0 if success else 1) 