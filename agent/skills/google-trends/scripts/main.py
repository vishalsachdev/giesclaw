#!/usr/bin/env python3
"""Google Trends skill - search interest analysis."""

import json
import os
from typing import Dict, Any


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    keywords = params.get("keywords", ["AI"])
    timeframe = params.get("timeframe", "today 12-m")
    geo = params.get("geo", "")
    action = params.get("action", "interest_over_time")

    try:
        from pytrends.request import TrendReq
    except ImportError:
        return {"error": "pytrends not installed. Run: pip install pytrends"}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(keywords[:5], timeframe=timeframe, geo=geo)

        if action == "interest_over_time":
            df = pytrends.interest_over_time()
            if df.empty:
                return {"keywords": keywords, "data": [], "note": "No data available"}
            records = []
            for date, row in df.iterrows():
                record = {"date": str(date.date())}
                for kw in keywords[:5]:
                    if kw in row:
                        record[kw] = int(row[kw])
                records.append(record)
            return {"action": action, "keywords": keywords, "data": records[-30:]}

        elif action == "related_queries":
            related = pytrends.related_queries()
            result = {}
            for kw in keywords[:5]:
                if kw in related:
                    top = related[kw].get("top")
                    rising = related[kw].get("rising")
                    result[kw] = {
                        "top": top.to_dict("records")[:10] if top is not None and not top.empty else [],
                        "rising": rising.to_dict("records")[:10] if rising is not None and not rising.empty else [],
                    }
            return {"action": action, "keywords": keywords, "data": result}

        elif action == "regional_interest":
            regional = pytrends.interest_by_region(resolution="COUNTRY")
            if regional.empty:
                return {"keywords": keywords, "data": {}}
            # Get top 15 regions for first keyword
            kw = keywords[0]
            if kw in regional.columns:
                top_regions = regional[kw].sort_values(ascending=False).head(15)
                return {
                    "action": action,
                    "keyword": kw,
                    "data": {str(k): int(v) for k, v in top_regions.items()},
                }
            return {"keywords": keywords, "data": {}}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        return {"error": str(e), "keywords": keywords}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2, default=str))
