"""
Gap Detector - Identify knowledge gaps in business investigations.

Analyzes completed research to find missing data, unexplored angles,
and additional analyses needed for comprehensive business understanding.
"""

from typing import Dict, List, Optional, Any
from ..core.llm_client import get_llm_client


class GapDetector:
    """Detect gaps in business research investigations."""

    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name

    def detect_gaps(
        self,
        topic: str,
        completed_skills: List[str],
        findings: List[Dict[str, Any]],
        available_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze completed research and identify gaps.

        Args:
            topic: Research topic
            completed_skills: Skills already executed
            findings: Findings from completed analyses
            available_skills: All available skills

        Returns:
            Dict with identified gaps and suggested next steps
        """
        findings_summary = "\n".join(
            f"- [{f.get('skill', 'unknown')}]: {f.get('finding', '')}"
            for f in findings[:10]
        )

        available_str = ", ".join(available_skills[:30]) if available_skills else "all business skills"

        client = get_llm_client(self.agent_name)
        prompt = f"""You are a business school research advisor reviewing an investigation.

Topic: {topic}
Skills already used: {', '.join(completed_skills)}
Findings so far:
{findings_summary}

Available skills: {available_str}

Identify gaps in this research. What's missing? What additional analyses are needed?

Respond in JSON:
{{
    "gaps": [
        {{
            "description": "...",
            "importance": "critical/high/medium/low",
            "suggested_skills": ["..."],
            "reasoning": "..."
        }}
    ],
    "overall_completeness": "percentage estimate",
    "recommended_next_skill": "..."
}}"""

        response = client.call(prompt, max_tokens=800, temperature=0.3)

        try:
            import re
            import json
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {"gaps": [], "raw_response": response}

    def prioritize_gaps(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort gaps by importance."""
        importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(
            gaps,
            key=lambda g: importance_order.get(g.get("importance", "low"), 4),
        )
