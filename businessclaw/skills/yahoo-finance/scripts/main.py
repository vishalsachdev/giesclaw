#!/usr/bin/env python3
"""Yahoo Finance skill - fetch market data and company financials."""

import json
import os
import sys

def run(**kwargs):
    """Execute Yahoo Finance data retrieval."""
    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    params = kwargs or json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    action = params.get("action", "info")
    ticker = params.get("ticker", "AAPL")

    try:
        if action == "compare":
            tickers = params.get("tickers", [ticker])
            results = {}
            for t in tickers:
                stock = yf.Ticker(t)
                info = stock.info
                results[t] = {
                    "name": info.get("longName", t),
                    "price": info.get("currentPrice"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "revenue": info.get("totalRevenue"),
                    "profit_margin": info.get("profitMargins"),
                    "52w_high": info.get("fiftyTwoWeekHigh"),
                    "52w_low": info.get("fiftyTwoWeekLow"),
                }
            return {"action": "compare", "data": results}

        stock = yf.Ticker(ticker)

        if action == "info":
            info = stock.info
            return {
                "action": "info",
                "ticker": ticker,
                "data": {
                    "name": info.get("longName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "price": info.get("currentPrice"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "peg_ratio": info.get("pegRatio"),
                    "price_to_book": info.get("priceToBook"),
                    "dividend_yield": info.get("dividendYield"),
                    "beta": info.get("beta"),
                    "52w_high": info.get("fiftyTwoWeekHigh"),
                    "52w_low": info.get("fiftyTwoWeekLow"),
                    "revenue": info.get("totalRevenue"),
                    "gross_margins": info.get("grossMargins"),
                    "operating_margins": info.get("operatingMargins"),
                    "profit_margins": info.get("profitMargins"),
                    "return_on_equity": info.get("returnOnEquity"),
                    "debt_to_equity": info.get("debtToEquity"),
                    "free_cash_flow": info.get("freeCashflow"),
                    "employees": info.get("fullTimeEmployees"),
                    "summary": info.get("longBusinessSummary", "")[:500],
                },
            }

        elif action == "history":
            period = params.get("period", "1y")
            hist = stock.history(period=period)
            records = []
            for date, row in hist.tail(60).iterrows():
                records.append({
                    "date": str(date.date()),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                })
            return {
                "action": "history",
                "ticker": ticker,
                "period": period,
                "data_points": len(records),
                "data": records,
            }

        elif action == "financials":
            income = stock.income_stmt
            balance = stock.balance_sheet
            cashflow = stock.cashflow

            def df_to_dict(df):
                if df is None or df.empty:
                    return {}
                result = {}
                for col in df.columns[:4]:
                    period_data = {}
                    for idx in df.index:
                        val = df.loc[idx, col]
                        if val is not None:
                            try:
                                period_data[str(idx)] = float(val)
                            except (ValueError, TypeError):
                                period_data[str(idx)] = str(val)
                    result[str(col.date()) if hasattr(col, 'date') else str(col)] = period_data
                return result

            return {
                "action": "financials",
                "ticker": ticker,
                "income_statement": df_to_dict(income),
                "balance_sheet": df_to_dict(balance),
                "cash_flow": df_to_dict(cashflow),
            }

        elif action == "dividends":
            divs = stock.dividends
            records = []
            for date, val in divs.tail(20).items():
                records.append({"date": str(date.date()), "dividend": round(float(val), 4)})
            return {"action": "dividends", "ticker": ticker, "data": records}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        return {"error": str(e), "ticker": ticker, "action": action}


if __name__ == "__main__":
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    result = run(**params)
    print(json.dumps(result, indent=2, default=str))
