from typing import Dict, Union
from langchain_core.tools import tool
import yfinance as yf
import logging

class FinancialDataFetcher:
    """Handles financial metrics retrieval."""

    @classmethod
    @tool
    def get_financial_metrics(cls, ticker: str) -> Union[Dict, str]:
        """Fetches key financial ratios for a given ticker."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "pe_ratio": info.get("forwardPE"),
                "price_to_book": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "profit_margins": info.get("profitMargins"),
            }

        except Exception as e:
            logging.error(f"Error fetching financial metrics for {ticker}: {e}")
            return f"Error fetching financial data: {str(e)}"