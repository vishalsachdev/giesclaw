---
name: fred-data
category: economics
type: database
keywords: [FRED, Federal Reserve, macroeconomics, GDP, inflation, interest rates, unemployment]
dependencies: [requests]
---

# FRED - Federal Reserve Economic Data

Access the Federal Reserve Bank of St. Louis economic database (FRED)
for macroeconomic indicators, interest rates, employment data, and more.

## Capabilities
- Retrieve time series data for 800,000+ economic indicators
- Access GDP, CPI, unemployment, interest rates, money supply
- Get historical and current economic data
- Search for series by keyword

## Parameters
- `series_id`: FRED series ID (e.g., "GDP", "CPIAUCSL", "UNRATE", "DFF")
- `action`: Operation ("get_series", "search", "popular")
- `start_date`: Start date for data (YYYY-MM-DD)
- `end_date`: End date for data (YYYY-MM-DD)
- `query`: Search query for finding series

## Common Series IDs
- GDP: Gross Domestic Product
- CPIAUCSL: Consumer Price Index
- UNRATE: Unemployment Rate
- DFF: Federal Funds Effective Rate
- T10Y2Y: 10-Year minus 2-Year Treasury Spread
- DEXUSEU: US/Euro Exchange Rate
- M2SL: M2 Money Supply
- HOUST: Housing Starts
