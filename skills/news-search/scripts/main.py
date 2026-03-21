#!/usr/bin/env python3
"""News search skill - aggregate business news from RSS feeds."""

import json
import os
from typing import Dict, Any, List


# RSS feed URLs for major business news sources
RSS_FEEDS = {
    "reuters_business": "https://feeds.reuters.com/reuters/businessNews",
    "reuters_tech": "https://feeds.reuters.com/reuters/technologyNews",
    "wsj_markets": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "cnbc_top": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "ft_companies": "https://www.ft.com/companies?format=rss",
    "bbc_business": "http://feeds.bbci.co.uk/news/business/rss.xml",
}


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    query = params.get("query", "")
    limit = params.get("limit", 10)

    try:
        import feedparser
    except ImportError:
        return {"error": "feedparser not installed. Run: pip install feedparser"}

    articles: List[Dict[str, Any]] = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))

                # Filter by query if provided
                if query:
                    query_lower = query.lower()
                    searchable = f"{title} {summary}".lower()
                    if query_lower not in searchable:
                        continue

                articles.append({
                    "title": title,
                    "source": source_name,
                    "published": entry.get("published", ""),
                    "link": entry.get("link", ""),
                    "summary": summary[:300],
                })
        except Exception:
            continue

    # Sort by recency (published date) and limit
    articles = articles[:limit]

    return {
        "query": query,
        "article_count": len(articles),
        "articles": articles,
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
