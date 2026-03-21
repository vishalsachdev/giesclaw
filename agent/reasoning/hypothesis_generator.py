"""
Hypothesis Generator - Generate testable business hypotheses.

Creates research-grade hypotheses from observations, market data,
and prior investigation findings.
"""

from typing import Dict, List, Optional, Any
from ..core.llm_client import get_llm_client


class HypothesisGenerator:
    """Generate testable business research hypotheses."""

    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name

    def generate_hypotheses(
        self,
        topic: str,
        observations: Optional[List[str]] = None,
        prior_hypotheses: Optional[List[str]] = None,
        domain: str = "general",
    ) -> Dict[str, Any]:
        """
        Generate business hypotheses for a research topic.

        Args:
            topic: Research area or question
            observations: Prior observations that motivate hypotheses
            prior_hypotheses: Previously tested hypotheses to avoid duplication
            domain: Business domain (finance, strategy, marketing, etc.)

        Returns:
            Dict with generated hypotheses and analysis plans
        """
        obs_str = "\n".join(f"- {o}" for o in (observations or [])[:10])
        prior_str = "\n".join(f"- {h}" for h in (prior_hypotheses or [])[:5])

        client = get_llm_client(self.agent_name)
        prompt = f"""You are a business school researcher generating testable hypotheses.

Research topic: {topic}
Domain: {domain}

{"Prior observations:" + chr(10) + obs_str if obs_str else "No prior observations."}
{"Previously tested (avoid duplicating):" + chr(10) + prior_str if prior_str else ""}

Generate 3 novel, testable business hypotheses. Each should be:
1. Specific and falsifiable
2. Relevant to the business domain
3. Testable with available data and tools

Respond in JSON:
{{
    "topic": "{topic}",
    "hypotheses": [
        {{
            "hypothesis": "...",
            "rationale": "...",
            "test_method": "How to test this hypothesis",
            "required_data": ["..."],
            "required_skills": ["..."],
            "expected_impact": "high/medium/low"
        }}
    ]
}}"""

        response = client.call(prompt, max_tokens=1000, temperature=0.7)

        try:
            import re
            import json
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {"topic": topic, "raw_response": response}

    def evaluate_hypothesis(
        self,
        hypothesis: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate a hypothesis against collected evidence."""
        evidence_str = "\n".join(
            f"- {e.get('finding', e.get('description', str(e)))}"
            for e in evidence[:10]
        )

        client = get_llm_client(self.agent_name)
        prompt = f"""Evaluate this business hypothesis against the evidence:

Hypothesis: {hypothesis}

Evidence:
{evidence_str}

Respond in JSON:
{{
    "hypothesis": "{hypothesis}",
    "verdict": "supported/partially_supported/refuted/insufficient_evidence",
    "confidence": "high/medium/low",
    "supporting_evidence": ["..."],
    "contradicting_evidence": ["..."],
    "additional_tests_needed": ["..."]
}}"""

        response = client.call(prompt, max_tokens=600, temperature=0.3)

        try:
            import re
            import json
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {"hypothesis": hypothesis, "raw_response": response}
