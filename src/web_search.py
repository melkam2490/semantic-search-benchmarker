from ddgs import DDGS


def search_web(query, max_results=5):
    """Search the web when internal documents cannot answer."""

    try:
        results = DDGS().text(
            query,
            max_results=max_results
        )

        web_results = []

        for item in results:
            web_results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
                "source": "DuckDuckGo"
            })

        return web_results

    except Exception as error:
        print(f"Web search error: {error}")
        return []
