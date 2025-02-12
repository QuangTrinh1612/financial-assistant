from typing import Dict, Union

from langchain_core.tools import tool
import yfinance as yf
import datetime as dt
import logging

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volume import volume_weighted_average_price

class StockDataFetcher:
    """Handles stock price and technical indicator retrieval."""

    @staticmethod
    @tool(parse_docstring=True)
    def get_stock_prices(ticker: str) -> Union[Dict, str]:
        """Fetches historical stock price data and technical indicators for a given ticker.
        
        Args:
            ticker: The stock ticker symbol for a company (for example APPL for Apple)
        """
        try:
            data = yf.download(
                ticker,
                start=dt.datetime.now() - dt.timedelta(weeks=24 * 3),
                end=dt.datetime.now(),
                interval="1d",
            )

            if data.empty:
                return f"Error: No data found for {ticker}"

            df = data.copy()
            df.reset_index(inplace=True)
            df["Date"] = df["Date"].astype(str)

            indicators = {}

            # RSI
            rsi_series = RSIIndicator(df["Close"], window=14).rsi().iloc[-12:]
            indicators["RSI"] = {str(date): int(value) for date, value in rsi_series.dropna().to_dict().items()}

            # Stochastic Oscillator
            sto_series = StochasticOscillator(df["High"], df["Low"], df["Close"], window=14).stoch().iloc[-12:]
            indicators["Stochastic_Oscillator"] = {str(date): int(value) for date, value in sto_series.dropna().to_dict().items()}

            # MACD
            macd = MACD(df["Close"])
            macd_series = macd.macd().iloc[-12:]
            indicators["MACD"] = {str(date): int(value) for date, value in macd_series.to_dict().items()}

            # VWAP
            vwap_series = volume_weighted_average_price(df["High"], df["Low"], df["Close"], df["Volume"]).iloc[-12:]
            indicators["VWAP"] = {str(date): int(value) for date, value in vwap_series.to_dict().items()}

            return {"stock_price": df.to_dict(orient="records"), "indicators": indicators}

        except Exception as e:
            logging.error(f"Error fetching stock prices for {ticker}: {e}")
            return f"Error fetching price data: {str(e)}"