import pandas as pd
from services.stock_data import StockDataFetcher

class StockAnalyzer:
    @staticmethod
    def calculate_SMA(ticker, window):
        data = StockDataFetcher.get_stock_data(ticker).Close
        return data.rolling(window=window).mean().iloc[-1]
    
    @staticmethod
    def calculate_EMA(ticker, window):
        data = StockDataFetcher.get_stock_data(ticker).Close
        return data.ewm(span=window, adjust=False).mean().iloc[-1]
    
    @staticmethod
    def calculate_RSI(ticker, window=14):
        data = StockDataFetcher.get_stock_data(ticker).Close
        delta = data.diff()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)
        ema_up, ema_down = up.ewm(com=window-1, adjust=False).mean(), down.ewm(com=window-1, adjust=False).mean()
        rs = ema_up / ema_down
        return 100 - (100 / (1 + rs)).iloc[-1]

    @staticmethod
    def calculate_MACD(ticker):
        data = StockDataFetcher.get_stock_data(ticker).Close
        short_EMA, long_EMA = data.ewm(span=12, adjust=False).mean(), data.ewm(span=26, adjust=False).mean()
        MACD, signal = short_EMA - long_EMA, (short_EMA - long_EMA).ewm(span=9, adjust=False).mean()
        return MACD.iloc[-1], signal.iloc[-1], (MACD - signal).iloc[-1]