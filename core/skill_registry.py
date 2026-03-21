"""
Skill Registry - Centralized catalog of business research skills.

Discovers, indexes, and recommends business analysis tools organized by domain:
finance, marketing, strategy, operations, economics, and entrepreneurship.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


# Business skill categories (replacing scientific categories)
SKILL_CATEGORIES = {
    "finance": [
        "financial-analysis", "valuation", "risk-assessment", "portfolio",
        "derivatives", "banking", "corporate-finance", "accounting",
    ],
    "marketing": [
        "market-research", "consumer-behavior", "brand-analysis",
        "digital-marketing", "pricing", "segmentation", "advertising",
    ],
    "strategy": [
        "competitive-analysis", "industry-analysis", "swot", "porters-five-forces",
        "business-model", "mergers-acquisitions", "strategic-planning",
    ],
    "operations": [
        "supply-chain", "logistics", "process-optimization", "quality-management",
        "inventory", "lean-operations", "project-management",
    ],
    "economics": [
        "macroeconomics", "microeconomics", "econometrics", "trade",
        "monetary-policy", "labor-economics", "development-economics",
    ],
    "entrepreneurship": [
        "startup-analysis", "venture-capital", "business-plan",
        "market-sizing", "unit-economics", "pitch-deck",
    ],
    "data-analytics": [
        "statistical-analysis", "visualization", "forecasting",
        "regression", "clustering", "sentiment-analysis",
    ],
    "databases": [
        "sec-edgar", "fred", "world-bank", "yahoo-finance",
        "bloomberg", "crunchbase", "pitchbook",
    ],
}


class SkillRegistry:
    """Centralized catalog of business research skills."""

    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir:
            self.skills_dir = Path(skills_dir)
        else:
            self.skills_dir = Path(__file__).parent.parent / "skills"

        self.cache_dir = Path.home() / ".businessclaw"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.cache_dir / "skill_registry.json"

        self.skills: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Load skills from cache or scan directory."""
        force_refresh = os.environ.get("BUSINESSCLAW_FORCE_SKILL_REFRESH", "0") == "1"

        if not force_refresh and self.cache_path.exists():
            try:
                with open(self.cache_path) as f:
                    self.skills = json.load(f)
                return
            except Exception:
                pass

        self._scan_skills()
        self._save_cache()

    def _scan_skills(self):
        """Scan skills directory for SKILL.md files."""
        self.skills = {}
        if not self.skills_dir.exists():
            return

        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_name = skill_dir.name
            metadata = self._parse_skill_md(skill_md)
            metadata["name"] = skill_name
            metadata["path"] = str(skill_dir)

            # Detect scripts
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                metadata["scripts"] = [f.name for f in scripts_dir.iterdir() if f.suffix == ".py"]

            self.skills[skill_name] = metadata

    def _parse_skill_md(self, path: Path) -> Dict[str, Any]:
        """Parse YAML frontmatter and content from SKILL.md."""
        content = path.read_text()
        metadata: Dict[str, Any] = {}

        # Extract YAML frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if val.startswith("[") and val.endswith("]"):
                        val = [v.strip().strip("\"'") for v in val[1:-1].split(",")]
                    metadata[key] = val

        # Extract description from first paragraph
        body = content[fm_match.end():] if fm_match else content
        lines = [l.strip() for l in body.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            metadata["description"] = lines[0]

        # Extract capabilities
        caps = re.findall(r"[-*]\s+(.+)", body)
        if caps:
            metadata["capabilities"] = caps[:10]

        return metadata

    def _save_cache(self):
        """Persist registry to cache file."""
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.skills, f, indent=2)
        except Exception:
            pass

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search skills by keyword."""
        query_lower = query.lower()
        results = []
        for name, meta in self.skills.items():
            score = 0
            searchable = json.dumps(meta).lower()
            if query_lower in searchable:
                score += 1
            if query_lower in name.lower():
                score += 3
            desc = meta.get("description", "").lower()
            if query_lower in desc:
                score += 2
            if score > 0:
                results.append({**meta, "relevance_score": score})
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all skills in a category."""
        keywords = SKILL_CATEGORIES.get(category, [])
        results = []
        for name, meta in self.skills.items():
            cat = meta.get("category", "")
            if cat == category or name in keywords or any(k in name for k in keywords):
                results.append(meta)
        return results

    def suggest_skills_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Recommend skills for a business research topic."""
        topic_lower = topic.lower()
        scored = []

        # Category boost mapping
        category_boosts = {
            "finance": ["stock", "valuation", "revenue", "profit", "earnings", "dividend",
                        "balance sheet", "cash flow", "roi", "p/e", "market cap", "ipo"],
            "marketing": ["brand", "consumer", "advertising", "social media", "campaign",
                          "market share", "customer", "segmentation", "positioning"],
            "strategy": ["competitive", "industry", "acquisition", "merger", "disruption",
                         "moat", "differentiation", "cost leadership", "market entry"],
            "operations": ["supply chain", "logistics", "inventory", "manufacturing",
                           "efficiency", "lean", "six sigma", "quality"],
            "economics": ["gdp", "inflation", "interest rate", "trade", "unemployment",
                          "monetary", "fiscal", "recession", "growth"],
            "entrepreneurship": ["startup", "venture", "founder", "seed", "series a",
                                 "mvp", "product-market fit", "tam", "business model"],
        }

        for name, meta in self.skills.items():
            score = 0
            searchable = json.dumps(meta).lower()

            # Basic relevance
            for word in topic_lower.split():
                if word in searchable:
                    score += 1
                if word in name.lower():
                    score += 2

            # Category boost
            for cat, keywords in category_boosts.items():
                if any(kw in topic_lower for kw in keywords):
                    cat_meta = meta.get("category", "")
                    if cat_meta == cat or any(k in name for k in SKILL_CATEGORIES.get(cat, [])):
                        score += 3

            if score > 0:
                scored.append({**meta, "relevance_score": score})

        return sorted(scored, key=lambda x: x["relevance_score"], reverse=True)[:15]

    def list_all(self) -> List[str]:
        """List all registered skill names."""
        return sorted(self.skills.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        cats: Dict[str, int] = {}
        for meta in self.skills.values():
            cat = meta.get("category", "uncategorized")
            cats[cat] = cats.get(cat, 0) + 1
        return {
            "total_skills": len(self.skills),
            "by_category": cats,
        }


# Module-level singleton
_registry: Optional[SkillRegistry] = None


def get_registry(skills_dir: Optional[str] = None) -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry(skills_dir=skills_dir)
    return _registry
