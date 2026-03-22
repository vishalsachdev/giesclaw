#!/usr/bin/env python3
"""Porter's Five Forces analysis skill - LLM-powered strategic analysis."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from agent.core.llm_client import get_llm_client


def run(**kwargs):
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    company = params.get("company", "")
    industry = params.get("industry", "")
    detail = params.get("detail_level", "detailed")

    subject = f"{company} in the {industry} industry" if company and industry else company or industry

    prompt = f"""Perform a Porter's Five Forces analysis for: {subject}

For each force, provide:
1. Rating (Low / Medium / High)
2. Key factors (2-3 bullet points)
3. Trend direction (increasing / stable / decreasing)

Respond in JSON format:
{{
    "subject": "{subject}",
    "forces": {{
        "competitive_rivalry": {{
            "rating": "...",
            "factors": ["...", "..."],
            "trend": "..."
        }},
        "supplier_power": {{
            "rating": "...",
            "factors": ["...", "..."],
            "trend": "..."
        }},
        "buyer_power": {{
            "rating": "...",
            "factors": ["...", "..."],
            "trend": "..."
        }},
        "threat_of_substitutes": {{
            "rating": "...",
            "factors": ["...", "..."],
            "trend": "..."
        }},
        "threat_of_new_entrants": {{
            "rating": "...",
            "factors": ["...", "..."],
            "trend": "..."
        }}
    }},
    "overall_industry_attractiveness": "...",
    "strategic_implications": ["...", "...", "..."]
}}"""

    client = get_llm_client("GiesClaw")
    response = client.call(prompt, max_tokens=1200, temperature=0.3)

    try:
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return {"subject": subject, "raw_analysis": response}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
