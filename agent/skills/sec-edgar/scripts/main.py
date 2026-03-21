#!/usr/bin/env python3
"""SEC EDGAR skill - access regulatory filings."""

import json
import os
import requests
from typing import Dict, Any

EDGAR_BASE = "https://efts.sec.gov/LATEST"
EDGAR_COMPANY = "https://data.sec.gov/submissions"
HEADERS = {
    "User-Agent": "BusinessClaw/0.1 (research@businessclaw.edu)",
    "Accept": "application/json",
}


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "AAPL")
    filing_type = params.get("filing_type", "10-K")
    count = params.get("count", 5)
    action = params.get("action", "search")

    try:
        if action == "search":
            return _search_filings(ticker, filing_type, count)
        elif action == "company_info":
            return _get_company_info(ticker)
        else:
            return {"error": f"Unknown action: {action}"}
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def _search_filings(ticker: str, filing_type: str, count: int) -> Dict[str, Any]:
    """Search EDGAR for company filings."""
    url = f"{EDGAR_BASE}/search-index"
    params = {
        "q": f'"{ticker}"',
        "dateRange": "custom",
        "forms": filing_type,
        "from": 0,
        "size": count,
    }

    # Use full-text search API
    search_url = "https://efts.sec.gov/LATEST/search-index"
    try:
        resp = requests.get(
            search_url,
            params={"q": ticker, "forms": filing_type},
            headers=HEADERS,
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            filings = []
            for hit in data.get("hits", {}).get("hits", [])[:count]:
                src = hit.get("_source", {})
                filings.append({
                    "form_type": src.get("forms", filing_type),
                    "filing_date": src.get("file_date"),
                    "company": src.get("display_names", [ticker])[0] if src.get("display_names") else ticker,
                    "description": src.get("display_description", ""),
                })
            return {"ticker": ticker, "filing_type": filing_type, "filings": filings}
    except Exception:
        pass

    return {
        "ticker": ticker,
        "filing_type": filing_type,
        "note": "EDGAR search requires network access. Results may be limited in sandbox.",
        "filings": [],
    }


def _get_company_info(ticker: str) -> Dict[str, Any]:
    """Get company information from EDGAR."""
    # CIK lookup would go here
    return {
        "ticker": ticker,
        "note": "Company info lookup requires CIK mapping",
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
