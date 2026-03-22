#!/usr/bin/env python3
"""Market sizing skill - TAM/SAM/SOM estimation."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from agent.core.llm_client import get_llm_client


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    market = params.get("market", "")
    geography = params.get("geography", "global")
    methodology = params.get("methodology", "both")

    prompt = f"""Perform a market sizing analysis for: {market}
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
            return json.loads(json_match.group())
    except Exception:
        pass

    return {"market": market, "raw_analysis": response}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
