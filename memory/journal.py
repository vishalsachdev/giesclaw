"""
Agent Journal - JSONL append-only log for business research observations.

Stores chronological records of:
- Observations (from reading reports, filings, market data)
- Hypotheses (business research questions)
- Analyses (tool executions and parameters)
- Conclusions (findings and strategic recommendations)

File format: ~/.businessclaw/journals/{agent_name}/journal.jsonl
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


class AgentJournal:
    """Persistent journal for agent memories and business investigations."""

    def __init__(self, agent_name: str, base_dir: Optional[str] = None):
        self.agent_name = agent_name
        if base_dir is None:
            base_dir = os.path.expanduser("~/.businessclaw/journals")
        self.journal_dir = Path(base_dir) / agent_name
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.journal_path = self.journal_dir / "journal.jsonl"
        if not self.journal_path.exists():
            self.journal_path.touch()

    def _log_entry(self, entry_type: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": entry_type,
            "content": content,
            "metadata": metadata or {},
        }
        with open(self.journal_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def log_observation(self, content: str, source: Optional[str] = None,
                        tags: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Log an observation from reading reports, filings, or market data.

        Example:
            journal.log_observation(
                content="Apple's services revenue grew 14% YoY in Q4 2025",
                source="sec:AAPL:10-Q:2025-Q4",
                tags=["AAPL", "services", "revenue growth"],
                relevance="high"
            )
        """
        metadata = {"source": source, "tags": tags or [], **kwargs}
        return self._log_entry("observation", content, metadata)

    def log_hypothesis(self, hypothesis: str, motivation: Optional[str] = None,
                       related_observations: Optional[List[str]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Log a business hypothesis or research question.

        Example:
            journal.log_hypothesis(
                hypothesis="Apple's services moat is widening vs hardware competitors",
                motivation="Services margin expansion + ecosystem lock-in metrics",
                related_observations=["sec:AAPL:10-Q:2025-Q4"]
            )
        """
        metadata = {
            "motivation": motivation,
            "related_observations": related_observations or [],
            **kwargs,
        }
        return self._log_entry("hypothesis", hypothesis, metadata)

    def log_analysis(self, description: str, tool: str, parameters: Dict[str, Any],
                     results: Optional[Any] = None, hypothesis_id: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Log a business analysis (tool execution).

        Example:
            journal.log_analysis(
                description="DCF valuation of Apple using 10-year projection",
                tool="financial-modeling",
                parameters={"ticker": "AAPL", "method": "DCF", "years": 10},
                results={"intrinsic_value": 245.50, "current_price": 230.00}
            )
        """
        metadata = {
            "tool": tool,
            "parameters": parameters,
            "results": results,
            "hypothesis_id": hypothesis_id,
            **kwargs,
        }
        if isinstance(results, dict) and "_artifact_id" in results:
            metadata["artifact_id"] = results["_artifact_id"]
        return self._log_entry("analysis", description, metadata)

    def log_conclusion(self, conclusion: str, evidence: Optional[List[str]] = None,
                       confidence: Optional[str] = None,
                       next_steps: Optional[List[str]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Log a conclusion or strategic recommendation.

        Example:
            journal.log_conclusion(
                conclusion="Apple undervalued by ~7% based on DCF; services growth underpriced",
                evidence=["dcf_model_2025", "sec:AAPL:10-Q:2025-Q4"],
                confidence="medium",
                next_steps=["Analyze competitor services margins", "Model subscription churn"]
            )
        """
        metadata = {
            "evidence": evidence or [],
            "confidence": confidence,
            "next_steps": next_steps or [],
            **kwargs,
        }
        return self._log_entry("conclusion", conclusion, metadata)

    def search(self, query: str, entry_types: Optional[List[str]] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search journal entries by text or type."""
        if not self.journal_path.exists():
            return []

        query_lower = query.lower()
        results = []

        with open(self.journal_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry_types and entry.get("type") not in entry_types:
                        continue
                    if query:
                        if query_lower not in json.dumps(entry).lower():
                            continue
                    results.append(entry)
                except json.JSONDecodeError:
                    continue

        results.reverse()
        if limit:
            results = results[:limit]
        return results

    def get_investigated_topics(self) -> set:
        """Get set of topics/tickers/companies that have been investigated."""
        topics = set()
        if not self.journal_path.exists():
            return topics

        with open(self.journal_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    meta = entry.get("metadata", {})

                    if "tags" in meta:
                        topics.update(meta["tags"])

                    if entry.get("type") == "hypothesis":
                        content = entry.get("content", "")
                        quoted = re.findall(r'"([^"]+)"', content)
                        topics.update(quoted)
                        # Ticker symbols (1-5 uppercase letters)
                        tickers = re.findall(r'\b[A-Z]{1,5}\b', content)
                        topics.update(tickers)

                    if entry.get("type") == "analysis":
                        params = meta.get("parameters", {})
                        for key in ["ticker", "company", "industry", "query"]:
                            if key in params:
                                topics.add(params[key])
                except json.JSONDecodeError:
                    continue

        return topics

    def get_recent_entries(self, limit: int = 10,
                           entry_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.search("", entry_types=entry_types, limit=limit)

    def export_to_json(self, output_path: Optional[str] = None) -> str:
        if output_path is None:
            output_path = str(self.journal_dir / "journal_export.json")
        entries = []
        if self.journal_path.exists():
            with open(self.journal_path) as f:
                for line in f:
                    if line.strip():
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        with open(output_path, "w") as f:
            json.dump(entries, f, indent=2)
        return output_path

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "total_entries": 0,
            "by_type": {},
            "first_entry": None,
            "last_entry": None,
            "unique_topics": 0,
        }
        if not self.journal_path.exists():
            return stats

        with open(self.journal_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    stats["total_entries"] += 1
                    t = entry.get("type", "unknown")
                    stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
                    ts = entry.get("timestamp")
                    if ts:
                        if stats["first_entry"] is None:
                            stats["first_entry"] = ts
                        stats["last_entry"] = ts
                except json.JSONDecodeError:
                    continue

        stats["unique_topics"] = len(self.get_investigated_topics())
        return stats
