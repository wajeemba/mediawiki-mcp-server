import argparse
import os
import urllib.request
import urllib.parse
import json
import inspect
from typing import Dict, Any, List

from loguru import logger
from mcp.server.fastmcp import FastMCP

USER_AGENT = "mediawiki-mcp-server/1.0"
SERVER_VERSION = "1.0.0"


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
async def get_server_info():
    """
    Get information about this MCP server, including version, capabilities, and connected wiki.
    
    Returns:
        dict: Server information including version, wiki URL, and available functions
        
    Example:
        >>> await get_server_info()
        {
            "server_name": "Cosmere DM MCP Server",
            "server_version": "1.0.0",
            "wiki_info": {"name": "Coppermind", "url": "https://coppermind.net/w/"}
        }
    """
    # Get site info from the connected wiki
    try:
        site_info_response = await make_request({
            "action": "query",
            "meta": "siteinfo",
            "siprop": "general"
        })
        
        if "query" in site_info_response and "general" in site_info_response["query"]:
            site_info = site_info_response["query"]["general"]
            wiki_name = site_info.get("sitename", "Unknown")
            wiki_main_page = site_info.get("mainpage", "Unknown")
            wiki_version = site_info.get("generator", "Unknown")
        else:
            wiki_name = "Unknown"
            wiki_main_page = "Unknown"
            wiki_version = "Unknown"
    except Exception as e:
        wiki_name = "Connection Error"
        wiki_main_page = "Unknown"
        wiki_version = "Unknown"
    
    return {
        "server_name": "Cosmere DM MCP Server",
        "server_version": SERVER_VERSION,
        "user_agent": USER_AGENT,
        "wiki_info": {
            "name": wiki_name,
            "url": config.base_url,
            "main_page": wiki_main_page,
            "version": wiki_version
        },
        "purpose": "Provides canon-compliant access to Cosmere wiki information for AI Dungeon Masters",
        "total_functions": 4,  # get_server_info, help, search, get_page
        "use_help_function": "Call help() to see all available functions and their usage"
    }


def _parse_docstring(docstring: str) -> Dict[str, Any]:
    """Parse a function docstring into structured information"""
    if not docstring:
        return {"description": "No description available"}
    
    lines = docstring.strip().split('\n')
    sections = {
        "description": [],
        "args": [],
        "returns": [],
        "example": []
    }
    
    current_section = "description"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for section headers
        if line.lower().startswith('args:') or line.lower().startswith('arguments:'):
            current_section = "args"
            continue
        elif line.lower().startswith('returns:') or line.lower().startswith('return:'):
            current_section = "returns"
            continue
        elif line.lower().startswith('example:') or line.lower().startswith('examples:'):
            current_section = "example"
            continue
            
        sections[current_section].append(line)
    
    return {
        "description": ' '.join(sections["description"]),
        "args": sections["args"],
        "returns": ' '.join(sections["returns"]),
        "example": ' '.join(sections["example"])
    }


def _get_function_signature(func) -> str:
    """Get a readable function signature"""
    try:
        sig = inspect.signature(func)
        params = []
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                params.append(param_name)
            else:
                params.append(f"{param_name}={repr(param.default)}")
        return f"{func.__name__}({', '.join(params)})"
    except Exception:
        return f"{func.__name__}(...)"


@mcp.tool()
async def help(function_name: str = ""):
    """
    Get help information about available functions. Call without arguments to see all functions.
    
    Args:
        function_name (str, optional): Specific function to get help for (e.g., "search", "get_page")
        
    Returns:
        dict: Help information about MCP server functions with descriptions, parameters, and examples
        
    Example:
        >>> await help()
        {"available_functions": {"search": {"description": "Search for wiki pages...", ...}}}
        >>> await help("search")
        {"function": "search", "description": "Search for wiki pages...", "parameters": "..."}
    """
    
    # Get all registered MCP tool functions by inspecting the current module
    current_module = inspect.getmodule(help)
    tool_functions = {}
    
    # Find all functions decorated with @mcp.tool()
    for name, obj in inspect.getmembers(current_module):
        if (inspect.iscoroutinefunction(obj) and 
            hasattr(obj, '__annotations__') and 
            name in ['get_server_info', 'help', 'search', 'get_page']):  # Known MCP tools
            
            # Parse the docstring
            parsed_doc = _parse_docstring(obj.__doc__)
            
            # Get function signature
            signature = _get_function_signature(obj)
            
            tool_functions[name] = {
                "description": parsed_doc["description"],
                "signature": signature,
                "parameters": parsed_doc["args"],
                "returns": parsed_doc["returns"],
                "example": parsed_doc["example"]
            }
    
    if function_name:
        # Get help for specific function
        if function_name in tool_functions:
            func_info = tool_functions[function_name]
            return {
                "function": function_name,
                "description": func_info["description"],
                "signature": func_info["signature"],
                "parameters": func_info["parameters"],
                "returns": func_info["returns"],
                "example": func_info["example"]
            }
        else:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": list(tool_functions.keys())
            }
    else:
        # Get help for all functions
        return {
            "server_info": "Cosmere DM MCP Server - Canon-compliant wiki access for AI Dungeon Masters",
            "wiki_source": config.base_url,
            "available_functions": tool_functions,
            "workflow_example": {
                "step_1": "search('Stormlight Archive', 5) - Find pages about the series",
                "step_2": "get_page('The Way of Kings') - Get detailed information about the first book",
                "step_3": "search('Kaladin') - Find character information",
                "step_4": "get_page('Kaladin') - Get detailed character information for DMing"
            },
            "dm_tips": [
                "Search for character names to get their abilities and relationships",
                "Search for magic systems (Surgebinding, Allomancy) to understand mechanics",
                "Search for locations to get cultural and geographical context",
                "Use specific terms rather than general ones for better results",
                "Page content includes categories and links to related concepts"
            ]
        }


@mcp.tool()
async def search(query: str, limit: int = 5):
    """
    Search for wiki pages using keywords. Use short, specific terms for best results.
    
    Args:
        query (str): The search term - preferably short and focused (e.g., character names, locations)
        limit (int, optional): Maximum number of results to return (default: 5)
        
    Returns:
        dict: Search results containing list of pages with titles, snippets, and metadata
        
    Example:
        >>> await search("Kaladin", 3)
        {"results": [{"title": "Kaladin", "snippet": "Knight Radiant...", "pageid": 1234}]}
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
    """
    Get the full content of a specific wiki page with detailed canon information.
    
    Args:
        title (str): The exact title of the page to retrieve (from search results)
        
    Returns:
        dict: Page content with HTML, categories, links, templates, and metadata
        
    Example:
        >>> await get_page("Kaladin")
        {"title": "Kaladin", "html": "<div>Kaladin is a Knight Radiant...</div>", "categories": [...]}
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
