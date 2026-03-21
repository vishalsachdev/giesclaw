---
name: yahoo-finance
category: finance
type: database
keywords: [stocks, market data, price, volume, dividends, financials, ticker]
dependencies: [yfinance]
---

# Yahoo Finance - Market Data & Financials

Retrieve real-time and historical stock market data, company financials,
and key metrics using the yfinance Python library.

## Capabilities
- Fetch current stock price, volume, and market cap
- Download historical OHLCV data (daily, weekly, monthly)
- Retrieve income statements, balance sheets, and cash flow statements
- Get key financial ratios and valuation metrics
- Access dividend and split history
- Compare multiple tickers side-by-side

## Parameters
- `ticker`: Stock ticker symbol (e.g., "AAPL", "MSFT")
- `period`: Data period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
- `action`: What to retrieve ("price", "financials", "info", "history", "dividends", "compare")
- `tickers`: List of tickers for comparison mode

## Example Usage
```python
# Get Apple's key info
params = {"ticker": "AAPL", "action": "info"}

# Get 1-year price history
params = {"ticker": "AAPL", "action": "history", "period": "1y"}

# Compare tech stocks
params = {"tickers": ["AAPL", "MSFT", "GOOGL"], "action": "compare"}
```
