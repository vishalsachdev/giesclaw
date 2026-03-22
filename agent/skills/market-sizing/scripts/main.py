#!/usr/bin/env python3
"""Market sizing skill - TAM/SAM/SOM estimation."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from agent.core.llm_client import get_llm_client
from agent.skills._shared.web_search import search_web, format_search_context


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    market = params.get("market", "")
    geography = params.get("geography", "global")
    methodology = params.get("methodology", "both")

    # Web search grounding
    search_queries = [
        f"{market} market size TAM revenue {geography}",
        f"{market} market growth forecast analysis",
    ]
    all_results = []
    for q in search_queries:
        all_results.extend(search_web(q, max_results=3))
    search_context = format_search_context(all_results)

    grounding_block = ""
    if search_context:
        grounding_block = (
            f"Use the following recent web search results as grounding data:\n"
            f"{search_context}\n\n"
            f"Based on this information and your knowledge, "
        )

    prompt = f"""{grounding_block}Perform a market sizing analysis for: {market}
Geography: {geography}
Methodology: {methodology}

Provide:
1. TAM (Total Addressable Market) - entire market demand
2. SAM (Serviceable Addressable Market) - segment you can reach
3. SOM (Serviceable Obtainable Market) - realistic capture

For each, provide the estimate in USD and your reasoning.

Respond in JSON format:
{{
    "market": "{market}",
    "geography": "{geography}",
    "tam": {{
        "estimate_usd": "...",
        "reasoning": "...",
        "growth_rate": "..."
    }},
    "sam": {{
        "estimate_usd": "...",
        "reasoning": "...",
        "percentage_of_tam": "..."
    }},
    "som": {{
        "estimate_usd": "...",
        "reasoning": "...",
        "percentage_of_sam": "..."
    }},
    "key_assumptions": ["...", "..."],
    "data_sources": ["...", "..."],
    "risks_to_estimate": ["...", "..."]
}}"""

    client = get_llm_client("GiesClaw")
    response = client.call(prompt, max_tokens=1000, temperature=0.3)

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
        "market": market,
        "raw_analysis": response,
        "search_grounded": bool(search_context),
        "search_queries": search_queries,
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
