#!/usr/bin/env python3
"""Sentiment analysis skill - analyze text sentiment for business contexts."""

import json
import os
from typing import Dict, Any


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "analyze")

    try:
        from textblob import TextBlob
    except ImportError:
        return {"error": "textblob not installed. Run: pip install textblob"}

    try:
        if action == "analyze":
            text = params.get("text", "")
            blob = TextBlob(text)
            return {
                "action": "analyze",
                "polarity": round(blob.sentiment.polarity, 3),
                "subjectivity": round(blob.sentiment.subjectivity, 3),
                "interpretation": _interpret_polarity(blob.sentiment.polarity),
                "word_count": len(text.split()),
            }

        elif action == "compare":
            texts = params.get("texts", [])
            labels = params.get("labels", [f"text_{i}" for i in range(len(texts))])
            results = []
            for text, label in zip(texts, labels):
                blob = TextBlob(text)
                results.append({
                    "label": label,
                    "polarity": round(blob.sentiment.polarity, 3),
                    "subjectivity": round(blob.sentiment.subjectivity, 3),
                    "interpretation": _interpret_polarity(blob.sentiment.polarity),
                })
            return {"action": "compare", "results": results}

        elif action == "earnings_tone":
            text = params.get("text", "")
            blob = TextBlob(text)
            sentences = blob.sentences
            positive = sum(1 for s in sentences if s.sentiment.polarity > 0.1)
            negative = sum(1 for s in sentences if s.sentiment.polarity < -0.1)
            neutral = len(sentences) - positive - negative
            return {
                "action": "earnings_tone",
                "overall_polarity": round(blob.sentiment.polarity, 3),
                "sentence_count": len(sentences),
                "positive_sentences": positive,
                "negative_sentences": negative,
                "neutral_sentences": neutral,
                "tone": _interpret_polarity(blob.sentiment.polarity),
            }

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        return {"error": str(e)}


def _interpret_polarity(polarity: float) -> str:
    if polarity > 0.3:
        return "strongly positive"
    elif polarity > 0.1:
        return "positive"
    elif polarity > -0.1:
        return "neutral"
    elif polarity > -0.3:
        return "negative"
    else:
        return "strongly negative"


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2))
