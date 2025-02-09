import yfinance as yf

class StockDataFetcher:
    @staticmethod
    def get_stock_data(ticker, period='1y'):
        return yf.Ticker(ticker).history(period=period)