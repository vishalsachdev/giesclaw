#!/usr/bin/env python3
"""Business Model Canvas skill - generate and analyze business models."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from agent.core.llm_client import get_llm_client
from agent.skills._shared.web_search import search_web, format_search_context


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "generate")
    company = params.get("company", params.get("idea", ""))

    client = get_llm_client("GiesClaw")

    if action == "generate":
        # Web search grounding
        search_queries = [
            f"{company} business model revenue strategy",
            f"{company} value proposition customers partnerships",
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

        prompt = f"""{grounding_block}Generate a Business Model Canvas for: {company}

Fill in all nine blocks of the Osterwalder Business Model Canvas.
Respond in JSON format:
{{
    "company": "{company}",
    "canvas": {{
        "customer_segments": ["..."],
        "value_propositions": ["..."],
        "channels": ["..."],
        "customer_relationships": ["..."],
        "revenue_streams": ["..."],
        "key_resources": ["..."],
        "key_activities": ["..."],
        "key_partnerships": ["..."],
        "cost_structure": ["..."]
    }},
    "business_model_type": "...",
    "key_insight": "..."
}}"""

    elif action == "compare":
        companies = params.get("companies", [company])
        # Web search grounding
        search_queries = [f"{c} business model strategy" for c in companies[:3]]
        all_results = []
        for q in search_queries:
            all_results.extend(search_web(q, max_results=2))
        search_context = format_search_context(all_results)

        grounding_block = ""
        if search_context:
            grounding_block = (
                f"Use the following recent web search results as grounding data:\n"
                f"{search_context}\n\n"
                f"Based on this information and your knowledge, "
            )

        prompt = f"""{grounding_block}Compare the business models of: {', '.join(companies)}

For each company, identify the key differentiators in their business model.
Respond in JSON format:
{{
    "companies": {json.dumps(companies)},
    "comparison": {{
        "key_differences": ["..."],
        "shared_elements": ["..."],
        "strongest_model": "...",
        "reasoning": "..."
    }}
}}"""

    else:
        return {"error": f"Unknown action: {action}"}

    response = client.call(prompt, max_tokens=1200, temperature=0.3)
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
        "company": company,
        "raw_analysis": response,
        "search_grounded": bool(search_context),
        "search_queries": search_queries,
    }


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
