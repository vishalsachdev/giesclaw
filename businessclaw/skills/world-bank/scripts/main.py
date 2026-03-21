#!/usr/bin/env python3
"""World Bank data skill - access development indicators."""

import json
import os
import requests
from typing import Dict, Any

WB_API = "https://api.worldbank.org/v2"


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "get_data")

    try:
        if action == "get_data":
            return _get_data(params)
        elif action == "search_indicators":
            return _search_indicators(params)
        elif action == "compare_countries":
            return _compare_countries(params)
        else:
            return {"error": f"Unknown action: {action}"}
    except Exception as e:
        return {"error": str(e)}


def _get_data(params: dict) -> Dict[str, Any]:
    indicator = params.get("indicator", "NY.GDP.MKTP.CD")
    country = params.get("country", "US")
    url = f"{WB_API}/country/{country}/indicator/{indicator}"
    resp = requests.get(url, params={"format": "json", "per_page": 20}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if len(data) < 2:
        return {"indicator": indicator, "country": country, "data": []}

    records = []
    for item in data[1] or []:
        if item.get("value") is not None:
            records.append({"year": item["date"], "value": item["value"]})

    return {
        "indicator": indicator,
        "indicator_name": data[1][0]["indicator"]["value"] if data[1] else indicator,
        "country": country,
        "country_name": data[1][0]["country"]["value"] if data[1] else country,
        "data": records,
    }


def _search_indicators(params: dict) -> Dict[str, Any]:
    query = params.get("query", "GDP")
    url = f"{WB_API}/indicator"
    resp = requests.get(
        url, params={"format": "json", "per_page": 10, "source": 2}, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    indicators = []
    query_lower = query.lower()
    if len(data) >= 2 and data[1]:
        for ind in data[1]:
            name = ind.get("name", "")
            if query_lower in name.lower() or query_lower in ind.get("id", "").lower():
                indicators.append({
                    "id": ind["id"],
                    "name": name,
                    "source": ind.get("source", {}).get("value", ""),
                })
    return {"query": query, "indicators": indicators[:10]}


def _compare_countries(params: dict) -> Dict[str, Any]:
    countries = params.get("countries", ["US", "CN", "GB"])
    indicator = params.get("indicator", "NY.GDP.MKTP.CD")
    results = {}

    for country in countries:
        try:
            data = _get_data({"indicator": indicator, "country": country})
            if data.get("data"):
                latest = data["data"][0]
                results[country] = {
                    "country_name": data.get("country_name", country),
                    "latest_value": latest["value"],
                    "latest_year": latest["year"],
                }
        except Exception:
            results[country] = {"error": "Data unavailable"}

    return {"indicator": indicator, "comparison": results}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
