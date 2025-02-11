import yfinance as yf
import matplotlib.pyplot as plt
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
    
    @classmethod
    @function_schema(
        name="calculate_SMA",
        description="Calculate the simple moving average for a given stock ticker and a window",
        required_params=["ticker", "window"]
    )
    def calculate_SMA(cls, ticker: str, window: int):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        :param window: The timeframe to consider when calculating the SMA
        """
        data = yf.Ticker(ticker).history(period='1y').Close
        return str(data.rolling(window=window).mean().iloc[-1])

    @classmethod
    @function_schema(
        name="calculate_EMA",
        description="Calculate the exponential moving average for a given stock ticker and a window",
        required_params=["ticker", "window"]
    )
    def calculate_EMA(cls, ticker: str, window: int):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        :param window: The timeframe to consider when calculating the EMA
        """
        data = yf.Ticker(ticker).history(period='1y').Close
        return str(data.ewm(span=window, adjust=False).mean().iloc[-1])

    @classmethod
    @function_schema(
        name="calculate_RSI",
        description="Calculate the RSI for a given stock ticker",
        required_params=["ticker"]
    )
    def calculate_RSI(cls, ticker: str):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        """
        data = yf.Ticker(ticker).history(period='1y').Close
        delta = data.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=14-1, adjust=False).mean()
        ema_down = down.ewm(com=14-1, adjust=False).mean()
        rs = ema_up / ema_down
        return str(100 - (100 / (1 + rs)).iloc[-1])

    @classmethod
    @function_schema(
        name="calculate_MACD",
        description="Calculate the MACD for a given stock ticker",
        required_params=["ticker"]
    )
    def calculate_MACD(cls, ticker: str):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        """
        data = yf.Ticker(ticker).history(period='1y').Close
        short_EMA = data.ewm(span=12, adjust=False).mean()
        long_EMA = data.ewm(span=26, adjust=False).mean()

        MACD = short_EMA - long_EMA
        signal = MACD.ewm(span=9, adjust=False)

        MACD_histogram = MACD - signal

        return f'{MACD[-1]}, {signal[-1]}, {MACD_histogram[-1]}'

    @classmethod
    @function_schema(
        name="plot_stock_price",
        description="Plot the stock price for the last year given the ticker symbol of a company.",
        required_params=["ticker"]
    )
    def plot_stock_price(cls, ticker: str):
        """
        :param ticker: The stock ticker symbol for a company (for example APPL for Apple)
        """
        data = yf.Ticker(ticker).history(period='1y')
        plt.figure(figsize=(10,5))
        plt.plot(data.index, data.Close)
        plt.title(f"{ticker} Stock Price Over Last Year")
        plt.xlabel('Date')
        plt.ylabel('Stock Price ($)')
        plt.grid(True)
        plt.savefig('assets/stock.png')
        plt.close()