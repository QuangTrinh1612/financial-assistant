import matplotlib.pyplot as plt
from services.stock_data import StockDataFetcher

class StockPlotter:
    @staticmethod
    def plot_stock_price(ticker):
        data = StockDataFetcher.get_stock_data(ticker).Close
        plt.figure(figsize=(10,5))
        plt.plot(data.index, data)
        plt.title(f"{ticker} Stock Price Over Last Year")
        plt.xlabel('Date')
        plt.ylabel('Stock Price ($)')
        plt.grid(True)
        plt.savefig('stock.png')
        plt.close()