"""
ArtifactReactor - Emergent coordination through pressure-based scoring.

Detects unmet information needs across agents and triggers complementary
analyses. Business school adaptation: agents specializing in different
domains (finance, marketing, strategy) autonomously fill each other's gaps.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class ArtifactReactor:
    """
    Monitors the global artifact index for unmet needs and triggers
    complementary research across agents.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = str(Path.home() / ".giesclaw" / "artifacts")
        self.base_dir = Path(base_dir)
        self.needs_path = self.base_dir / "needs.jsonl"
        self.global_index_path = self.base_dir / "global_index.json"

    def broadcast_need(
        self,
        agent_name: str,
        investigation_id: str,
        need_type: str,
        description: str,
        required_skills: Optional[List[str]] = None,
        priority: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Broadcast an unmet information need to the shared needs index.

        Args:
            agent_name: Agent broadcasting the need
            investigation_id: Investigation this need relates to
            need_type: Type of need (e.g., "financial_data", "market_analysis",
                       "competitive_intel", "expert_opinion")
            description: Natural language description of what's needed
            required_skills: Skills that could fulfill this need
            priority: Priority score (higher = more urgent)
        """
        need = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "investigation_id": investigation_id,
            "need_type": need_type,
            "description": description,
            "required_skills": required_skills or [],
            "priority": priority,
            "fulfilled": False,
        }

        self.needs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.needs_path, "a") as f:
            f.write(json.dumps(need) + "\n")

        return need

    def scan_needs(
        self,
        agent_name: str,
        agent_capabilities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan for unfulfilled needs that this agent can address.

        Returns needs from OTHER agents that match this agent's capabilities.
        """
        if not self.needs_path.exists():
            return []

        capabilities = set(agent_capabilities or [])
        actionable = []

        with open(self.needs_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    need = json.loads(line)
                    # Skip own needs and fulfilled needs
                    if need["agent"] == agent_name or need.get("fulfilled"):
                        continue
                    # Check capability overlap
                    required = set(need.get("required_skills", []))
                    if not capabilities or required & capabilities:
                        # Score by priority and recency
                        score = need.get("priority", 1.0)
                        actionable.append({**need, "match_score": score})
                except Exception:
                    continue

        return sorted(actionable, key=lambda x: x["match_score"], reverse=True)

    def fulfill_need(
        self,
        need: Dict[str, Any],
        fulfilling_agent: str,
        artifact_id: str,
    ):
        """Mark a need as fulfilled by linking to the produced artifact."""
        if not self.needs_path.exists():
            return

        lines = []
        with open(self.needs_path) as f:
            for line in f:
                if not line.strip():
                    lines.append(line)
                    continue
                try:
                    n = json.loads(line)
                    if (n["agent"] == need["agent"]
                            and n["investigation_id"] == need["investigation_id"]
                            and n["description"] == need["description"]):
                        n["fulfilled"] = True
                        n["fulfilled_by"] = fulfilling_agent
                        n["fulfilling_artifact"] = artifact_id
                        n["fulfilled_at"] = datetime.now(timezone.utc).isoformat()
                    lines.append(json.dumps(n) + "\n")
                except Exception:
                    lines.append(line)

        with open(self.needs_path, "w") as f:
            f.writelines(lines)
