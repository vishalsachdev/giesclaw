---
name: news-search
category: databases
type: database
keywords: [news, RSS, business news, current events, press releases]
dependencies: [feedparser, requests]
---

# News Search - Business News Aggregation

Search and aggregate business news from RSS feeds and news APIs.
Track company mentions, industry developments, and market-moving events.

## Capabilities
- Search business news by keyword or company
- Aggregate from multiple RSS sources
- Track company-specific news
- Monitor industry developments

## Parameters
- `query`: Search query (company name, topic, ticker)
- `sources`: List of sources ("reuters", "wsj", "ft", "bloomberg")
- `limit`: Maximum articles to return (default: 10)
