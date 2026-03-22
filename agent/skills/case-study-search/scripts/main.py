#!/usr/bin/env python3
"""Case study search skill - find relevant business school cases."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from agent.core.llm_client import get_llm_client
from agent.skills._shared.web_search import search_web, format_search_context


# Classic case study database (curated knowledge)
CLASSIC_CASES = {
    "strategy": [
        {"title": "Cola Wars Continue: Coke and Pepsi in 2010", "source": "HBS 711-462",
         "topics": ["competitive rivalry", "industry analysis", "duopoly"]},
        {"title": "Apple Inc. in 2023", "source": "HBS 723-406",
         "topics": ["ecosystem strategy", "platform competition", "services transition"]},
        {"title": "Netflix: Disrupting the Video Industry", "source": "Kellogg KEL633",
         "topics": ["disruption", "business model innovation", "streaming"]},
        {"title": "Amazon.com, 2021", "source": "HBS 722-420",
         "topics": ["platform strategy", "diversification", "cloud computing"]},
    ],
    "finance": [
        {"title": "Marriott Corporation: The Cost of Capital", "source": "HBS 289-047",
         "topics": ["WACC", "cost of capital", "divisional hurdle rates"]},
        {"title": "Leveraged Buyout of Congoleum Corporation", "source": "HBS 295-089",
         "topics": ["LBO", "leveraged buyout", "financial engineering"]},
        {"title": "Airbus A380: Superjumbo of the 21st Century", "source": "Darden UV0170",
         "topics": ["capital budgeting", "NPV", "real options"]},
    ],
    "marketing": [
        {"title": "Dove: Evolution of a Brand", "source": "HBS 508-047",
         "topics": ["brand positioning", "cause marketing", "brand evolution"]},
        {"title": "IKEA's Global Strategy", "source": "HBS 710-414",
         "topics": ["global marketing", "standardization", "localization"]},
    ],
    "operations": [
        {"title": "Toyota Production System", "source": "HBS 693-019",
         "topics": ["lean manufacturing", "JIT", "continuous improvement"]},
        {"title": "Benihana of Tokyo", "source": "HBS 673-057",
         "topics": ["operations strategy", "capacity management", "service operations"]},
    ],
    "entrepreneurship": [
        {"title": "Dropbox: 'It Just Works'", "source": "HBS 811-065",
         "topics": ["product-market fit", "viral growth", "freemium"]},
        {"title": "Airbnb, Pair Programming", "source": "HBS 812-046",
         "topics": ["marketplace", "platform", "sharing economy"]},
    ],
}


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    query = params.get("query", "")
    action = params.get("action", "search")

    if action == "search":
        return _search_cases(query)
    elif action == "frameworks":
        return _suggest_frameworks(query)
    elif action == "suggest_cases":
        return _llm_suggest_cases(query)
    else:
        return {"error": f"Unknown action: {action}"}


def _search_cases(query: str):
    """Search curated case database and use LLM for additional suggestions."""
    query_lower = query.lower()
    matches = []

    for category, cases in CLASSIC_CASES.items():
        for case in cases:
            score = 0
            if query_lower in case["title"].lower():
                score += 3
            for topic in case["topics"]:
                if query_lower in topic.lower() or topic.lower() in query_lower:
                    score += 2
            if query_lower in category:
                score += 1
            if score > 0:
                matches.append({**case, "category": category, "relevance": score})

    matches.sort(key=lambda x: x["relevance"], reverse=True)
    return {"query": query, "matches": matches[:10]}


def _suggest_frameworks(query: str):
    """Suggest business frameworks relevant to a topic."""
    # Web search grounding
    search_queries = [f"{query} business framework analysis methodology"]
    web_results = search_web(search_queries[0], max_results=5)
    search_context = format_search_context(web_results)

    grounding_block = ""
    if search_context:
        grounding_block = (
            f"Use the following recent web search results as grounding data:\n"
            f"{search_context}\n\n"
            f"Based on this information and your knowledge, "
        )

    client = get_llm_client("GiesClaw")
    prompt = f"""{grounding_block}For the business topic "{query}", suggest the most relevant
business school frameworks and analytical tools. Respond in JSON:
{{
    "topic": "{query}",
    "frameworks": [
        {{"name": "...", "relevance": "high/medium", "how_to_apply": "..."}}
    ]
}}"""
    response = client.call(prompt, max_tokens=600, temperature=0.3)
    try:
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result["search_grounded"] = bool(search_context)
            result["search_queries"] = search_queries
            return result
    except Exception:
        pass
    return {
        "topic": query,
        "raw": response,
        "search_grounded": bool(search_context),
        "search_queries": search_queries,
    }


def _llm_suggest_cases(query: str):
    """Use LLM to suggest relevant case studies."""
    # Web search grounding
    search_queries = [f"{query} Harvard business school case study"]
    web_results = search_web(search_queries[0], max_results=5)
    search_context = format_search_context(web_results)

    grounding_block = ""
    if search_context:
        grounding_block = (
            f"Use the following recent web search results as grounding data:\n"
            f"{search_context}\n\n"
            f"Based on this information and your knowledge, "
        )

    client = get_llm_client("GiesClaw")
    prompt = f"""{grounding_block}Suggest 5 relevant business school case studies for: "{query}"
Include well-known HBS, Stanford, Kellogg, Darden, or INSEAD cases.
Respond in JSON:
{{
    "query": "{query}",
    "suggested_cases": [
        {{"title": "...", "source": "HBS/Stanford/etc + number", "relevance": "..."}}
    ]
}}"""
    response = client.call(prompt, max_tokens=600, temperature=0.3)
    try:
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result["search_grounded"] = bool(search_context)
            result["search_queries"] = search_queries
            return result
    except Exception:
        pass
    return {
        "query": query,
        "raw": response,
        "search_grounded": bool(search_context),
        "search_queries": search_queries,
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
