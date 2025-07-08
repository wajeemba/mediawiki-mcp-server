import argparse
import os
import urllib.request
import urllib.parse
import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

USER_AGENT = "mediawiki-mcp-server/1.0"


class Config:
    base_url = "https://coppermind.net/w/"
    path_prefix = "api.php"


config = Config()
mcp = FastMCP("mediawiki-mcp-server")


def get_proxy_settings():
    """Get proxy settings from environment variables"""
    http_proxy = os.environ.get("HTTP_PROXY")

    return http_proxy


# helper function to make a request to the mediawiki action api
async def make_request(params: dict) -> dict:
    """Make a request to the MediaWiki Action API using urllib (bypasses CloudFlare blocking)"""
    # Add format=json to all requests
    params["format"] = "json"
    
    # Build URL with parameters
    base_url = config.base_url + config.path_prefix
    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    # Use urllib request with headers that work with Coppermind.net
    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        logger.error(f"HTTP error {e.code}: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        logger.error(f"Request error: {e}")
        return {"error": str(e)}


@mcp.tool()
async def search(query: str, limit: int = 5):
    """
    Search for a wiki page. The shorter the request, the better, preferably containing only the main term to be searched.
    Args:
        query: The query to search for
        limit: The number of results to return
    Returns:
        A list of pages that match the query
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


@mcp.tool()
async def get_page(title: str):
    """Get a page from the MediaWiki site
    Args:
        title: The title of the page to get, which can be found in title field of the search results
    Returns:
        The page content
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


def main():
    parser = argparse.ArgumentParser(description="MediaWiki MCP Server")
    parser.add_argument(
        "--base-url",
        default=config.base_url,
        help=f"Base URL for the MediaWiki API (default: {config.base_url})",
    )
    args = parser.parse_args()

    config.base_url = (
        args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    )

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
