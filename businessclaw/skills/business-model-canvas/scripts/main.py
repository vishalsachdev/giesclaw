#!/usr/bin/env python3
"""Business Model Canvas skill - generate and analyze business models."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from businessclaw.core.llm_client import get_llm_client


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "generate")
    company = params.get("company", params.get("idea", ""))

    client = get_llm_client("BusinessClaw")

    if action == "generate":
        prompt = f"""Generate a Business Model Canvas for: {company}

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
        prompt = f"""Compare the business models of: {', '.join(companies)}

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
            return json.loads(json_match.group())
    except Exception:
        pass
    return {"company": company, "raw_analysis": response}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
