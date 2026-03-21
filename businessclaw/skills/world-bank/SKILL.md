---
name: world-bank
category: economics
type: database
keywords: [World Bank, development, GDP per capita, global, country data, indicators]
dependencies: [requests]
---

# World Bank Open Data

Access World Bank development indicators for countries worldwide.
GDP, population, trade, education, health, and governance metrics.

## Capabilities
- Query development indicators for any country
- Compare countries on key metrics
- Track indicator trends over time
- Access 16,000+ development indicators

## Parameters
- `indicator`: World Bank indicator code (e.g., "NY.GDP.MKTP.CD")
- `country`: ISO country code or "all"
- `action`: "get_data", "search_indicators", "compare_countries"
- `countries`: List of country codes for comparison
