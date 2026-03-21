"""
Topic Analyzer - Classify and decompose business research topics.

Maps natural language research questions to relevant business domains,
skill categories, and investigation strategies.
"""

from typing import Dict, List, Any, Optional
from .llm_client import get_llm_client


BUSINESS_DOMAINS = {
    "corporate_finance": {
        "keywords": ["valuation", "capital structure", "dividend", "ipo", "debt", "equity",
                      "wacc", "dcf", "npv", "irr", "cost of capital", "leverage"],
        "skills": ["yahoo-finance", "sec-edgar", "financial-modeling", "valuation-analysis"],
    },
    "investments": {
        "keywords": ["portfolio", "stock", "bond", "hedge fund", "etf", "risk", "return",
                      "capm", "alpha", "beta", "sharpe ratio", "diversification"],
        "skills": ["yahoo-finance", "alpha-vantage", "portfolio-analysis", "risk-metrics"],
    },
    "marketing_strategy": {
        "keywords": ["brand", "positioning", "segmentation", "targeting", "advertising",
                      "customer", "market share", "pricing strategy", "go-to-market"],
        "skills": ["market-research", "google-trends", "sentiment-analysis", "competitor-intel"],
    },
    "competitive_strategy": {
        "keywords": ["competitive advantage", "moat", "disruption", "five forces",
                      "value chain", "differentiation", "cost leadership", "industry analysis"],
        "skills": ["porter-five-forces", "industry-analysis", "sec-edgar", "competitor-intel"],
    },
    "operations_management": {
        "keywords": ["supply chain", "logistics", "lean", "six sigma", "inventory",
                      "manufacturing", "quality", "process improvement", "throughput"],
        "skills": ["supply-chain-analysis", "process-optimization", "statistical-analysis"],
    },
    "entrepreneurship": {
        "keywords": ["startup", "venture capital", "founder", "seed", "series", "mvp",
                      "product-market fit", "tam", "sam", "som", "pitch", "unit economics"],
        "skills": ["crunchbase", "market-sizing", "unit-economics", "business-model-canvas"],
    },
    "macroeconomics": {
        "keywords": ["gdp", "inflation", "interest rate", "federal reserve", "monetary policy",
                      "fiscal policy", "unemployment", "trade balance", "recession"],
        "skills": ["fred-data", "world-bank", "economic-indicators", "macro-forecasting"],
    },
    "accounting": {
        "keywords": ["balance sheet", "income statement", "cash flow", "gaap", "ifrs",
                      "audit", "revenue recognition", "depreciation", "amortization"],
        "skills": ["sec-edgar", "financial-statement-analysis", "ratio-analysis"],
    },
}


def classify_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Classify a research topic into business domains.

    Returns list of matching domains sorted by relevance score.
    """
    topic_lower = topic.lower()
    scored = []

    for domain, info in BUSINESS_DOMAINS.items():
        score = 0
        for kw in info["keywords"]:
            if kw in topic_lower:
                score += 2
            elif any(w in topic_lower for w in kw.split()):
                score += 1
        if score > 0:
            scored.append({
                "domain": domain,
                "score": score,
                "suggested_skills": info["skills"],
            })

    return sorted(scored, key=lambda x: x["score"], reverse=True)


def decompose_topic(topic: str, agent_name: str = "Agent") -> Dict[str, Any]:
    """
    Use LLM to decompose a business research topic into sub-questions and analysis plan.
    """
    client = get_llm_client(agent_name)
    prompt = f"""You are a business school research assistant. Decompose this research topic
into actionable sub-questions and an analysis plan.

Topic: {topic}

Respond in JSON format:
{{
    "main_question": "...",
    "sub_questions": ["q1", "q2", "q3"],
    "domains": ["finance", "strategy", ...],
    "data_sources_needed": ["SEC filings", "market data", ...],
    "analysis_methods": ["DCF valuation", "Porter's Five Forces", ...],
    "expected_outputs": ["financial model", "industry report", ...]
}}"""

    response = client.call(prompt, max_tokens=800, temperature=0.3)
    try:
        # Extract JSON from response
        import re
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return {"status": "success", "plan": __import__("json").loads(json_match.group())}
    except Exception:
        pass

    return {"status": "success", "plan": {"raw_response": response}}
