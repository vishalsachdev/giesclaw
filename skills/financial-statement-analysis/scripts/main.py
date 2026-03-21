#!/usr/bin/env python3
"""Financial statement analysis skill - ratios, DuPont, trends."""

import json
import os
from typing import Dict, Any


def run(**kwargs) -> Dict[str, Any]:
    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "AAPL")
    action = params.get("action", "ratios")

    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if action == "ratios":
            return {
                "ticker": ticker,
                "action": "ratios",
                "profitability": {
                    "gross_margin": info.get("grossMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "profit_margin": info.get("profitMargins"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                },
                "liquidity": {
                    "current_ratio": info.get("currentRatio"),
                    "quick_ratio": info.get("quickRatio"),
                },
                "solvency": {
                    "debt_to_equity": info.get("debtToEquity"),
                    "total_debt": info.get("totalDebt"),
                    "total_cash": info.get("totalCash"),
                },
                "valuation": {
                    "pe_trailing": info.get("trailingPE"),
                    "pe_forward": info.get("forwardPE"),
                    "peg_ratio": info.get("pegRatio"),
                    "price_to_book": info.get("priceToBook"),
                    "price_to_sales": info.get("priceToSalesTrailing12Months"),
                    "ev_to_ebitda": info.get("enterpriseToEbitda"),
                    "ev_to_revenue": info.get("enterpriseToRevenue"),
                },
                "efficiency": {
                    "revenue_per_employee": (
                        info.get("totalRevenue", 0) / info.get("fullTimeEmployees", 1)
                        if info.get("fullTimeEmployees")
                        else None
                    ),
                },
            }

        elif action == "dupont":
            # DuPont 3-factor: ROE = Profit Margin × Asset Turnover × Equity Multiplier
            profit_margin = info.get("profitMargins", 0)
            revenue = info.get("totalRevenue", 0)
            total_assets = info.get("totalAssets", 1)
            equity = total_assets - info.get("totalDebt", 0) if total_assets else 1

            asset_turnover = revenue / total_assets if total_assets else 0
            equity_multiplier = total_assets / equity if equity else 0
            roe_dupont = profit_margin * asset_turnover * equity_multiplier

            return {
                "ticker": ticker,
                "action": "dupont",
                "profit_margin": round(profit_margin, 4) if profit_margin else None,
                "asset_turnover": round(asset_turnover, 4),
                "equity_multiplier": round(equity_multiplier, 4),
                "roe_dupont": round(roe_dupont, 4),
                "roe_reported": info.get("returnOnEquity"),
            }

        elif action == "common_size":
            income = stock.income_stmt
            if income is None or income.empty:
                return {"ticker": ticker, "error": "No income statement data"}

            latest = income.iloc[:, 0]
            revenue = latest.get("Total Revenue", 1)
            if not revenue or revenue == 0:
                return {"ticker": ticker, "error": "Revenue is zero or unavailable"}

            common_size = {}
            for item in latest.index:
                try:
                    val = float(latest[item])
                    common_size[str(item)] = round(val / float(revenue) * 100, 2)
                except (ValueError, TypeError):
                    continue

            return {"ticker": ticker, "action": "common_size", "base": "revenue", "data": common_size}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2, default=str))
