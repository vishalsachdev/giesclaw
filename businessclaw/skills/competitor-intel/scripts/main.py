#!/usr/bin/env python3
"""Competitive intelligence skill - competitor analysis and benchmarking."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from businessclaw.core.llm_client import get_llm_client


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    company = params.get("company", "AAPL")
    action = params.get("action", "compare")
    competitors = params.get("competitors", [])

    if action == "identify":
        return _identify_competitors(company)
    elif action == "compare":
        return _compare_financials(company, competitors)
    elif action == "positioning":
        return _analyze_positioning(company, competitors)
    else:
        return {"error": f"Unknown action: {action}"}


def _identify_competitors(company: str):
    client = get_llm_client("BusinessClaw")
    prompt = f"""Identify the top 5 direct competitors for {company}.
Respond in JSON:
{{
    "company": "{company}",
    "competitors": [
        {{"name": "...", "ticker": "...", "overlap": "...", "threat_level": "high/medium/low"}}
    ]
}}"""
    response = client.call(prompt, max_tokens=500, temperature=0.3)
    try:
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {"company": company, "raw": response}


def _compare_financials(company: str, competitors: list):
    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed"}

    tickers = [company] + competitors
    comparison = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            comparison[ticker] = {
                "name": info.get("longName", ticker),
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "profit_margin": info.get("profitMargins"),
                "pe_ratio": info.get("trailingPE"),
                "revenue_growth": info.get("revenueGrowth"),
                "roe": info.get("returnOnEquity"),
            }
        except Exception:
            comparison[ticker] = {"error": "Data unavailable"}

    return {"company": company, "comparison": comparison}


def _analyze_positioning(company: str, competitors: list):
    client = get_llm_client("BusinessClaw")
    comp_str = ", ".join(competitors) if competitors else "main competitors"
    prompt = f"""Analyze the competitive positioning of {company} vs {comp_str}.
Respond in JSON:
{{
    "company": "{company}",
    "positioning": {{
        "strategy_type": "cost leadership / differentiation / focus",
        "key_advantages": ["..."],
        "key_vulnerabilities": ["..."],
        "moat_strength": "strong/moderate/weak",
        "moat_sources": ["..."]
    }}
}}"""
    response = client.call(prompt, max_tokens=600, temperature=0.3)
    try:
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {"company": company, "raw": response}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2, default=str))
