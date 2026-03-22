"""Shared web search utility for grounding LLM-only skills with real data."""

import re
from html import unescape


def _sanitize(text: str, max_len: int = 500) -> str:
    """Strip HTML tags and limit length. Search results are untrusted input."""
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags
    text = unescape(text)  # decode &amp; etc.
    text = text.strip()
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Run a DuckDuckGo web search. Returns list of {title, url, snippet}.

    Falls back to an empty list if the package is missing or search fails,
    so callers can always proceed without grounding.
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return []

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))
    except Exception:
        return []

    results = []
    for item in raw:
        results.append({
            "title": _sanitize(item.get("title", ""), max_len=200),
            "url": item.get("href", ""),
            "snippet": _sanitize(item.get("body", "")),
        })
    return results


def format_search_context(results: list[dict]) -> str:
    """Format search results into a text block suitable for LLM prompts."""
    if not results:
        return ""
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}")
        lines.append(f"    URL: {r['url']}")
        lines.append(f"    {r['snippet']}")
        lines.append("")
    return "\n".join(lines).strip()
