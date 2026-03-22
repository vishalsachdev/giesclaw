"""
Investigation Tracker - Track multi-step business research investigations.

Manages the lifecycle of investigations from hypothesis through analysis
to conclusion, tracking progress, artifacts produced, and gaps remaining.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid


class InvestigationTracker:
    """Track and manage business research investigations."""

    def __init__(self, agent_name: str, base_dir: Optional[str] = None):
        self.agent_name = agent_name
        if base_dir is None:
            base_dir = os.path.expanduser("~/.giesclaw/investigations")
        self.tracker_dir = Path(base_dir) / agent_name
        self.tracker_dir.mkdir(parents=True, exist_ok=True)
        self.tracker_path = self.tracker_dir / "investigations.json"
        self.investigations: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if self.tracker_path.exists():
            try:
                with open(self.tracker_path) as f:
                    self.investigations = json.load(f)
            except Exception:
                self.investigations = {}

    def _save(self):
        with open(self.tracker_path, "w") as f:
            json.dump(self.investigations, f, indent=2)

    def start_investigation(
        self,
        topic: str,
        hypothesis: Optional[str] = None,
        domains: Optional[List[str]] = None,
        planned_skills: Optional[List[str]] = None,
    ) -> str:
        """
        Start a new business research investigation.

        Args:
            topic: Research topic (e.g., "Apple services segment valuation")
            hypothesis: Initial hypothesis to test
            domains: Business domains involved (finance, strategy, etc.)
            planned_skills: Skills planned for use

        Returns:
            Investigation ID
        """
        inv_id = f"inv-{uuid.uuid4().hex[:8]}"
        self.investigations[inv_id] = {
            "id": inv_id,
            "topic": topic,
            "hypothesis": hypothesis,
            "domains": domains or [],
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "planned_skills": planned_skills or [],
            "completed_skills": [],
            "artifact_ids": [],
            "gaps": [],
            "findings": [],
            "conclusion": None,
        }
        self._save()
        return inv_id

    def record_skill_execution(
        self,
        investigation_id: str,
        skill: str,
        artifact_id: Optional[str] = None,
        finding: Optional[str] = None,
    ):
        """Record that a skill was executed as part of an investigation."""
        inv = self.investigations.get(investigation_id)
        if not inv:
            return

        if skill not in inv["completed_skills"]:
            inv["completed_skills"].append(skill)
        if artifact_id:
            inv["artifact_ids"].append(artifact_id)
        if finding:
            inv["findings"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "skill": skill,
                "finding": finding,
            })
        inv["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def record_gap(self, investigation_id: str, gap_description: str,
                   suggested_skills: Optional[List[str]] = None):
        """Record an identified gap in the investigation."""
        inv = self.investigations.get(investigation_id)
        if not inv:
            return

        inv["gaps"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": gap_description,
            "suggested_skills": suggested_skills or [],
            "resolved": False,
        })
        inv["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def conclude_investigation(self, investigation_id: str, conclusion: str,
                                confidence: str = "medium"):
        """Mark an investigation as concluded with findings."""
        inv = self.investigations.get(investigation_id)
        if not inv:
            return

        inv["status"] = "concluded"
        inv["conclusion"] = {
            "text": conclusion,
            "confidence": confidence,
            "concluded_at": datetime.now(timezone.utc).isoformat(),
        }
        inv["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def get_active_investigations(self) -> List[Dict[str, Any]]:
        return [inv for inv in self.investigations.values() if inv["status"] == "active"]

    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        return self.investigations.get(investigation_id)

    def get_all_gaps(self) -> List[Dict[str, Any]]:
        """Get all unresolved gaps across investigations."""
        gaps = []
        for inv in self.investigations.values():
            if inv["status"] != "active":
                continue
            for gap in inv.get("gaps", []):
                if not gap.get("resolved"):
                    gaps.append({
                        "investigation_id": inv["id"],
                        "topic": inv["topic"],
                        **gap,
                    })
        return gaps

    def get_stats(self) -> Dict[str, Any]:
        active = sum(1 for inv in self.investigations.values() if inv["status"] == "active")
        concluded = sum(1 for inv in self.investigations.values() if inv["status"] == "concluded")
        total_artifacts = sum(len(inv.get("artifact_ids", [])) for inv in self.investigations.values())
        return {
            "total_investigations": len(self.investigations),
            "active": active,
            "concluded": concluded,
            "total_artifacts": total_artifacts,
        }
