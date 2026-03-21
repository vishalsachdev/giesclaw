---
name: financial-statement-analysis
category: finance
type: tool
keywords: [financial statements, ratio analysis, DuPont, profitability, liquidity, solvency]
dependencies: [yfinance]
---

# Financial Statement Analysis

Comprehensive financial statement analysis with ratio calculations,
DuPont decomposition, trend analysis, and peer comparison.

## Capabilities
- Calculate key financial ratios (profitability, liquidity, solvency, efficiency)
- DuPont analysis (3-factor and 5-factor)
- Year-over-year trend analysis
- Common-size financial statements
- Peer group comparison

## Parameters
- `ticker`: Company ticker symbol
- `action`: "ratios", "dupont", "trend", "common_size"
- `peers`: List of peer tickers for comparison
