---
name: google-trends
category: marketing
type: database
keywords: [Google Trends, search interest, trend analysis, consumer interest, seasonal]
dependencies: [pytrends]
---

# Google Trends - Search Interest Analysis

Track and analyze search interest trends using Google Trends data.
Useful for understanding consumer interest, brand awareness, and market timing.

## Capabilities
- Track search interest over time for keywords
- Compare search interest across terms
- Analyze geographic distribution of interest
- Identify related queries and rising topics
- Detect seasonal patterns

## Parameters
- `keywords`: List of keywords to analyze (max 5)
- `timeframe`: Time range ("today 1-m", "today 3-m", "today 12-m", "today 5-y")
- `geo`: Geographic region ("US", "GB", "DE", "" for worldwide)
- `action`: "interest_over_time", "related_queries", "regional_interest"
