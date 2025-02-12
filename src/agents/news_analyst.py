import yfinance as yf
import pandas as pd
from pprint import pprint
import requests
import re
import traceback

def get_news(stock: str) -> list:
    """
    Fetch relevant news articles for a given stock ticker.

    Parameters:
    - stock (str): The stock ticker symbol.

    Returns:
    - list: A list of dictionaries containing title, summary, URL, and publication date of relevant news articles.
    """
    try:
        # Fetch the ticker object and retrieve its news
        ticker = yf.Ticker(stock)
        news = ticker.news

        if not news:
            print(f"No news found for {stock}.")
            return []

        # Filter news with contentType='STORY'
        relevant_news = [
            item for item in news if item.get('content', {}).get('contentType') == 'STORY'
        ]

        all_news = []
        for i, item in enumerate(relevant_news):
            try:
                content = item.get('content', {})
                current_news = {
                    'title': content.get('title'),
                    'summary': content.get('summary'),
                    'url': content.get('canonicalUrl', {}).get('url'),
                    'pubdate': content.get('pubDate', '').split('T')[0],
                }
                all_news.append(current_news)
            except Exception as e:
                print(f"Error processing news {i}: {e}")
                continue

        return all_news

    except Exception as e:
        print(f"An error occurred while fetching news for {stock}: {e}")
        return None