#!/usr/bin/env python3
"""FRED data skill - access Federal Reserve economic data."""

import json
import os
import requests
from typing import Dict, Any

FRED_API_BASE = "https://api.stlouisfed.org/fred"


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "get_series")
    api_key = os.environ.get("FRED_API_KEY")

    if not api_key:
        return {
            "error": "FRED_API_KEY not set. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
            "note": "Set FRED_API_KEY environment variable",
        }

    try:
        if action == "get_series":
            return _get_series(params, api_key)
        elif action == "search":
            return _search_series(params, api_key)
        elif action == "popular":
            return _get_popular_series()
        else:
            return {"error": f"Unknown action: {action}"}
    except Exception as e:
        return {"error": str(e)}


def _get_series(params: dict, api_key: str) -> Dict[str, Any]:
    series_id = params.get("series_id", "GDP")
    url = f"{FRED_API_BASE}/series/observations"
    resp = requests.get(
        url,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": params.get("limit", 20),
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    observations = []
    for obs in data.get("observations", []):
        try:
            observations.append({
                "date": obs["date"],
                "value": float(obs["value"]) if obs["value"] != "." else None,
            })
        except (ValueError, KeyError):
            continue

    return {"series_id": series_id, "observations": observations}


def _search_series(params: dict, api_key: str) -> Dict[str, Any]:
    query = params.get("query", "GDP")
    url = f"{FRED_API_BASE}/series/search"
    resp = requests.get(
        url,
        params={
            "search_text": query,
            "api_key": api_key,
            "file_type": "json",
            "limit": 10,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    series = []
    for s in data.get("seriess", []):
        series.append({
            "id": s["id"],
            "title": s["title"],
            "frequency": s.get("frequency"),
            "units": s.get("units"),
            "seasonal_adjustment": s.get("seasonal_adjustment"),
        })
    return {"query": query, "results": series}


def _get_popular_series() -> Dict[str, Any]:
    return {
        "popular_series": {
            "GDP": "Gross Domestic Product",
            "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
            "UNRATE": "Unemployment Rate",
            "DFF": "Federal Funds Effective Rate",
            "T10Y2Y": "10-Year Treasury Minus 2-Year Treasury Spread",
            "DEXUSEU": "US/Euro Foreign Exchange Rate",
            "M2SL": "M2 Money Stock",
            "HOUST": "New Privately-Owned Housing Units Started",
            "RSAFS": "Advance Retail Sales: Retail and Food Services",
            "INDPRO": "Industrial Production: Total Index",
        }
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
