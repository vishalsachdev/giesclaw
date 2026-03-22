"""
Post Generator - Generate structured business research posts.

Creates publishable research outputs from investigation results,
formatted for sharing with peers and community feedback.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..core.llm_client import get_llm_client


class PostGenerator:
    """Generate structured business research posts from investigation results."""

    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name

    def generate_post(
        self,
        investigation: Dict[str, Any],
        style: str = "research_brief",
    ) -> Dict[str, Any]:
        """
        Generate a post from investigation results.

        Args:
            investigation: Investigation result dict
            style: Post style - "research_brief", "case_analysis", "market_report",
                   "investment_memo", "executive_summary"

        Returns:
            Structured post with title, body, metadata
        """
        topic = investigation.get("topic", "Unknown")
        hypothesis = investigation.get("hypothesis", "")
        findings = investigation.get("findings", [])
        conclusion = investigation.get("conclusion", "")

        findings_str = "\n".join(f"- {f['finding']}" for f in findings)

        style_instructions = {
            "research_brief": "Write a concise 300-word research brief suitable for a business school audience.",
            "case_analysis": "Write as a mini case analysis with situation, analysis, and recommendations.",
            "market_report": "Write as a market research report with data-driven insights.",
            "investment_memo": "Write as an investment memo with thesis, evidence, and risks.",
            "executive_summary": "Write as a C-suite executive summary with key takeaways and action items.",
        }

        client = get_llm_client(self.agent_name)
        prompt = f"""Generate a business research post.

Topic: {topic}
{"Hypothesis: " + hypothesis if hypothesis else ""}
Findings:
{findings_str}
Conclusion: {conclusion}

Style: {style_instructions.get(style, style_instructions['research_brief'])}

Respond in JSON:
{{
    "title": "...",
    "subtitle": "...",
    "body": "...",
    "key_takeaways": ["...", "...", "..."],
    "tags": ["...", "..."]
}}"""

        response = client.call(prompt, max_tokens=1500, temperature=0.5)

        try:
            import re
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                post_content = json.loads(json_match.group())
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent": self.agent_name,
                    "investigation_id": investigation.get("investigation_id"),
                    "style": style,
                    **post_content,
                }
        except Exception:
            pass

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.agent_name,
            "title": f"Research: {topic}",
            "body": conclusion,
            "raw_response": response,
        }

    def save_post(self, post: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        """Save a post to disk."""
        from pathlib import Path

        if output_dir is None:
            output_dir = str(Path.home() / ".giesclaw" / "posts" / self.agent_name)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"post_{timestamp}.json"
        filepath = out_path / filename

        with open(filepath, "w") as f:
            json.dump(post, f, indent=2)

        return str(filepath)
