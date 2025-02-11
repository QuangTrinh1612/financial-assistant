import yfinance as yf
from utils.function_metadata import function_schema

class StockAnalyzer:

    @classmethod
    @function_schema(
        name="get_stock_price",
        description="Gets the latest stock price given the ticker symbol of a company.",
        required_params=["ticker"]
    )
    def get_stock_price(cls, ticker: str):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        """
        return str(yf.Ticker(ticker).history(period='1y').iloc[-1].Close)