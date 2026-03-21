"""
Artifact - Immutable research record with provenance tracking.

Each skill execution produces an artifact with a unique ID, content hash,
and parent lineage pointers, forming a directed acyclic graph (DAG) of
business research outputs.
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


# Map business skills to the artifact types they produce
SKILL_DOMAIN_MAP = {
    # Finance & Accounting
    "yahoo-finance": "market_data",
    "alpha-vantage": "market_data",
    "sec-edgar": "regulatory_filing",
    "financial-modeling": "financial_model",
    "valuation-analysis": "valuation_report",
    "ratio-analysis": "financial_ratios",
    "financial-statement-analysis": "financial_analysis",
    "portfolio-analysis": "portfolio_report",
    "risk-metrics": "risk_assessment",
    "fred-data": "economic_data",
    # Marketing
    "market-research": "market_report",
    "google-trends": "trend_data",
    "sentiment-analysis": "sentiment_report",
    "competitor-intel": "competitive_intelligence",
    "brand-analysis": "brand_report",
    "consumer-survey": "survey_data",
    # Strategy
    "porter-five-forces": "industry_analysis",
    "industry-analysis": "industry_report",
    "swot-analysis": "swot_report",
    "business-model-canvas": "business_model",
    # Operations
    "supply-chain-analysis": "operations_report",
    "process-optimization": "process_analysis",
    # Economics
    "world-bank": "economic_data",
    "economic-indicators": "economic_report",
    "macro-forecasting": "economic_forecast",
    # Entrepreneurship
    "crunchbase": "startup_data",
    "market-sizing": "market_size_estimate",
    "unit-economics": "unit_economics_model",
    # Analytics
    "statistical-analysis": "statistical_output",
    "regression-analysis": "regression_results",
    "visualization": "chart",
    "forecasting": "forecast",
    # Research
    "case-study-search": "case_study",
    "academic-search": "literature_review",
    "news-search": "news_digest",
    "web-scraper": "scraped_data",
}


class Artifact:
    """Immutable record of a business research output."""

    def __init__(
        self,
        skill: str,
        content: Any,
        agent_name: str,
        investigation_id: Optional[str] = None,
        parent_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.skill = skill
        self.content = content
        self.agent_name = agent_name
        self.investigation_id = investigation_id
        self.parent_ids = parent_ids or []
        self.metadata = metadata or {}
        self.artifact_type = SKILL_DOMAIN_MAP.get(skill, "general")

        # Generate content hash and unique ID
        content_str = json.dumps(content, sort_keys=True, default=str)
        self.content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        self.artifact_id = f"bc-{self.artifact_type[:8]}-{self.content_hash[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "timestamp": self.timestamp,
            "skill": self.skill,
            "artifact_type": self.artifact_type,
            "agent_name": self.agent_name,
            "investigation_id": self.investigation_id,
            "parent_ids": self.parent_ids,
            "content_hash": self.content_hash,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artifact":
        art = cls(
            skill=data["skill"],
            content=data["content"],
            agent_name=data["agent_name"],
            investigation_id=data.get("investigation_id"),
            parent_ids=data.get("parent_ids", []),
            metadata=data.get("metadata", {}),
        )
        art.artifact_id = data["artifact_id"]
        art.timestamp = data["timestamp"]
        art.content_hash = data["content_hash"]
        art.artifact_type = data["artifact_type"]
        return art


class ArtifactStore:
    """
    Append-only JSONL storage for artifacts with indexing.

    Storage: ~/.businessclaw/artifacts/{agent_name}/store.jsonl
    Index:   ~/.businessclaw/artifacts/{agent_name}/index.json
    Global:  ~/.businessclaw/artifacts/global_index.json
    """

    def __init__(self, agent_name: str, base_dir: Optional[str] = None):
        self.agent_name = agent_name
        if base_dir is None:
            base_dir = os.path.expanduser("~/.businessclaw/artifacts")
        self.store_dir = Path(base_dir) / agent_name
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.store_dir / "store.jsonl"
        self.index_path = self.store_dir / "index.json"
        self.global_index_path = Path(base_dir) / "global_index.json"

        if not self.store_path.exists():
            self.store_path.touch()

        self._index: Dict[str, int] = {}
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    self._index = json.load(f)
            except Exception:
                self._rebuild_index()
        else:
            self._rebuild_index()

    def _rebuild_index(self):
        self._index = {}
        if not self.store_path.exists():
            return
        with open(self.store_path) as f:
            offset = 0
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        self._index[data["artifact_id"]] = offset
                    except Exception:
                        pass
                offset = f.tell()
        self._save_index()

    def _save_index(self):
        try:
            with open(self.index_path, "w") as f:
                json.dump(self._index, f)
        except Exception:
            pass

    def _update_global_index(self, artifact: Artifact):
        global_idx = {}
        if self.global_index_path.exists():
            try:
                with open(self.global_index_path) as f:
                    global_idx = json.load(f)
            except Exception:
                pass

        global_idx[artifact.artifact_id] = {
            "agent": self.agent_name,
            "type": artifact.artifact_type,
            "skill": artifact.skill,
            "timestamp": artifact.timestamp,
            "investigation_id": artifact.investigation_id,
        }

        try:
            with open(self.global_index_path, "w") as f:
                json.dump(global_idx, f, indent=2)
        except Exception:
            pass

    def create(
        self,
        skill: str,
        content: Any,
        investigation_id: Optional[str] = None,
        parent_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Create and persist a new artifact."""
        artifact = Artifact(
            skill=skill,
            content=content,
            agent_name=self.agent_name,
            investigation_id=investigation_id,
            parent_ids=parent_ids,
            metadata=metadata,
        )
        return self.save(artifact)

    def save(self, artifact: Artifact) -> Artifact:
        """Persist an artifact to store."""
        with open(self.store_path, "a") as f:
            offset = f.tell()
            f.write(json.dumps(artifact.to_dict(), default=str) + "\n")
        self._index[artifact.artifact_id] = offset
        self._save_index()
        self._update_global_index(artifact)
        return artifact

    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Retrieve artifact by ID using indexed lookup."""
        if artifact_id not in self._index:
            return None
        offset = self._index[artifact_id]
        try:
            with open(self.store_path) as f:
                f.seek(offset)
                line = f.readline()
                if line.strip():
                    return Artifact.from_dict(json.loads(line))
        except Exception:
            pass
        return None

    def list(
        self,
        artifact_type: Optional[str] = None,
        skill: Optional[str] = None,
        investigation_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Artifact]:
        """List artifacts with optional filters."""
        results = []
        if not self.store_path.exists():
            return results

        with open(self.store_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if artifact_type and data.get("artifact_type") != artifact_type:
                        continue
                    if skill and data.get("skill") != skill:
                        continue
                    if investigation_id and data.get("investigation_id") != investigation_id:
                        continue
                    results.append(Artifact.from_dict(data))
                except Exception:
                    continue

        results.reverse()
        return results[:limit]

    def get_lineage(self, artifact_id: str) -> List[Artifact]:
        """Trace the full parent lineage of an artifact."""
        lineage = []
        visited = set()
        queue = [artifact_id]

        while queue:
            aid = queue.pop(0)
            if aid in visited:
                continue
            visited.add(aid)
            art = self.get(aid)
            if art:
                lineage.append(art)
                queue.extend(art.parent_ids)

        return lineage

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        types: Dict[str, int] = {}
        skills: Dict[str, int] = {}
        total = 0

        if self.store_path.exists():
            with open(self.store_path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        total += 1
                        t = data.get("artifact_type", "unknown")
                        types[t] = types.get(t, 0) + 1
                        s = data.get("skill", "unknown")
                        skills[s] = skills.get(s, 0) + 1
                    except Exception:
                        continue

        return {"total_artifacts": total, "by_type": types, "by_skill": skills}
