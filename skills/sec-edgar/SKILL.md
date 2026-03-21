---
name: sec-edgar
category: finance
type: database
keywords: [SEC, EDGAR, filings, 10-K, 10-Q, 8-K, proxy, annual report, regulatory]
dependencies: [requests, beautifulsoup4]
---

# SEC EDGAR - Regulatory Filings Database

Access SEC EDGAR to retrieve company filings including 10-K annual reports,
10-Q quarterly reports, 8-K current reports, and proxy statements.

## Capabilities
- Search for company filings by ticker or CIK
- Download and parse 10-K, 10-Q, 8-K filings
- Extract financial data from XBRL filings
- Access management discussion and analysis (MD&A) sections
- Retrieve insider trading (Form 4) filings
- Search full-text of filings

## Parameters
- `ticker`: Company ticker symbol
- `filing_type`: Type of filing ("10-K", "10-Q", "8-K", "DEF 14A", "4")
- `count`: Number of recent filings to retrieve (default: 5)
- `action`: Operation ("search", "download", "parse")
