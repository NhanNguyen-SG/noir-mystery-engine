from dotenv import load_dotenv
load_dotenv()

import httpx
from pydantic_ai import ModelRetry

async def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Search the web for information relevant to a noir mystery investigation.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 3).

    Returns:
        List of dicts with title, url, and snippet fields.

    Raises:
        ModelRetry: If the search query is empty or the request fails.
    """
    if not query or not query.strip():
        raise ModelRetry("Search query cannot be empty. Please provide a valid query.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                },
                timeout=10.0,
                follow_redirects=True,
            )
            data = response.json()
            results = []

            # Pull from RelatedTopics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    })

            # Fallback to Abstract if no results
            if not results and data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                })

            if not results:
                return [{"title": query, "url": "", "snippet": "No results found."}]

            return results

    except httpx.TimeoutException:
        raise ModelRetry("Search timed out. Please try again with a simpler query.")
    except Exception as e:
        raise ModelRetry(f"Search failed: {str(e)}")


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(web_search("Sherlock Holmes locked room mystery"))
    for r in results:
        print(f"{r['title']}\n{r['snippet'][:150]}\n")