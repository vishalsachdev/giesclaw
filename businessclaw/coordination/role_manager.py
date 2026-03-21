"""
Role Manager - Assign and manage business school agent roles.

Defines specialized agent roles mapped to business school departments:
Finance, Marketing, Strategy, Operations, Economics, Entrepreneurship.
"""

from typing import Dict, List, Any

# Business school agent role definitions
AGENT_ROLES = {
    "finance_analyst": {
        "department": "Finance",
        "description": "Specializes in financial analysis, valuation, and capital markets",
        "core_skills": [
            "yahoo-finance", "sec-edgar", "financial-statement-analysis",
            "ratio-analysis", "fred-data",
        ],
        "frameworks": ["DCF", "Comparable Analysis", "LBO", "WACC", "CAPM"],
        "personality": {
            "analytical_style": "quantitative",
            "risk_tolerance": "moderate",
            "communication": "data-driven",
        },
    },
    "strategy_consultant": {
        "department": "Strategy",
        "description": "Specializes in competitive strategy, industry analysis, and M&A",
        "core_skills": [
            "porter-five-forces", "competitor-intel", "case-study-search",
            "industry-analysis", "business-model-canvas",
        ],
        "frameworks": ["Porter's Five Forces", "SWOT", "Value Chain", "BCG Matrix", "Blue Ocean"],
        "personality": {
            "analytical_style": "qualitative",
            "risk_tolerance": "moderate",
            "communication": "narrative",
        },
    },
    "marketing_researcher": {
        "department": "Marketing",
        "description": "Specializes in market research, consumer behavior, and brand analysis",
        "core_skills": [
            "google-trends", "sentiment-analysis", "market-sizing",
            "news-search", "competitor-intel",
        ],
        "frameworks": ["STP", "4Ps", "Customer Journey", "Brand Equity", "AIDA"],
        "personality": {
            "analytical_style": "mixed",
            "risk_tolerance": "high",
            "communication": "creative",
        },
    },
    "operations_analyst": {
        "department": "Operations",
        "description": "Specializes in supply chain, process optimization, and efficiency",
        "core_skills": [
            "supply-chain-analysis", "statistical-analysis",
            "process-optimization", "case-study-search",
        ],
        "frameworks": ["Lean", "Six Sigma", "Theory of Constraints", "Kanban", "Value Stream Mapping"],
        "personality": {
            "analytical_style": "quantitative",
            "risk_tolerance": "low",
            "communication": "process-oriented",
        },
    },
    "economist": {
        "department": "Economics",
        "description": "Specializes in macroeconomic analysis and policy implications",
        "core_skills": [
            "fred-data", "world-bank", "news-search",
            "statistical-analysis", "forecasting",
        ],
        "frameworks": ["IS-LM", "AS-AD", "Phillips Curve", "Solow Model", "Game Theory"],
        "personality": {
            "analytical_style": "quantitative",
            "risk_tolerance": "moderate",
            "communication": "academic",
        },
    },
    "entrepreneur": {
        "department": "Entrepreneurship",
        "description": "Specializes in startup analysis, venture capital, and new ventures",
        "core_skills": [
            "market-sizing", "business-model-canvas", "competitor-intel",
            "case-study-search", "news-search",
        ],
        "frameworks": ["Lean Startup", "Business Model Canvas", "TAM/SAM/SOM", "Unit Economics"],
        "personality": {
            "analytical_style": "mixed",
            "risk_tolerance": "high",
            "communication": "pitch-ready",
        },
    },
}


class RoleManager:
    """Manage agent roles and capabilities."""

    def __init__(self):
        self.roles = AGENT_ROLES

    def get_role(self, role_name: str) -> Dict[str, Any]:
        return self.roles.get(role_name, {})

    def list_roles(self) -> List[str]:
        return list(self.roles.keys())

    def get_skills_for_role(self, role_name: str) -> List[str]:
        role = self.roles.get(role_name, {})
        return role.get("core_skills", [])

    def suggest_role_for_topic(self, topic: str) -> str:
        """Suggest the best agent role for a given research topic."""
        topic_lower = topic.lower()

        role_keywords = {
            "finance_analyst": ["stock", "valuation", "earnings", "revenue", "ipo", "debt",
                                "equity", "dividend", "p/e", "wacc", "dcf"],
            "strategy_consultant": ["competitive", "industry", "acquisition", "merger",
                                     "moat", "disruption", "strategy", "five forces"],
            "marketing_researcher": ["brand", "consumer", "advertising", "market share",
                                      "social media", "segmentation", "positioning"],
            "operations_analyst": ["supply chain", "logistics", "manufacturing",
                                    "efficiency", "lean", "inventory", "process"],
            "economist": ["gdp", "inflation", "interest rate", "unemployment",
                          "monetary", "fiscal", "trade", "recession"],
            "entrepreneur": ["startup", "venture", "founder", "seed", "mvp",
                              "product-market", "pitch", "tam"],
        }

        best_role = "strategy_consultant"  # default
        best_score = 0

        for role, keywords in role_keywords.items():
            score = sum(1 for kw in keywords if kw in topic_lower)
            if score > best_score:
                best_score = score
                best_role = role

        return best_role
