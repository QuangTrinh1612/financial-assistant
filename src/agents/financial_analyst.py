from typing import Union, Dict, Set, List, TypedDict, Annotated, Any, Sequence
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import yfinance as yf
import datetime as dt
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volume import volume_weighted_average_price
import traceback
import pandas as pd
import dotenv
from langchain_core.messages import BaseMessage

dotenv.load_dotenv()

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {**a, **b}

# Define agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    data: Annotated[Dict[str, Any], merge_dicts]
    metadata: Annotated[Dict[str, Any], merge_dicts]

graph_builder = StateGraph(AgentState)

import os
from typing import Dict, Any, List
import pandas as pd
import requests

import requests

def get_financial_metrics(
    ticker: str,
    report_period: str,
    period: str = 'ttm',
    limit: int = 1
) -> List[Dict[str, Any]]:
    """Fetch financial metrics from the API."""
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f"https://api.financialdatasets.ai/financial-metrics/"
        f"?ticker={ticker}"
        f"&report_period_lte={report_period}"
        f"&limit={limit}"
        f"&period={period}"
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    financial_metrics = data.get("financial_metrics")
    if not financial_metrics:
        raise ValueError("No financial metrics returned")
    return financial_metrics

def search_line_items(
    ticker: str,
    line_items: List[str],
    period: str = 'ttm',
    limit: int = 1
) -> List[Dict[str, Any]]:
    """Fetch cash flow statements from the API."""
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = "https://api.financialdatasets.ai/financials/search/line-items"

    body = {
        "tickers": [ticker],
        "line_items": line_items,
        "period": period,
        "limit": limit
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    search_results = data.get("search_results")
    if not search_results:
        raise ValueError("No search results returned")
    return search_results

def get_insider_trades(
    ticker: str,
    end_date: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetch insider trades for a given ticker and date range.
    """
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f"https://api.financialdatasets.ai/insider-trades/"
        f"?ticker={ticker}"
        f"&filing_date_lte={end_date}"
        f"&limit={limit}"
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    insider_trades = data.get("insider_trades")
    if not insider_trades:
        raise ValueError("No insider trades returned")
    return insider_trades

def get_market_cap(
    ticker: str,
) -> List[Dict[str, Any]]:
    """Fetch market cap from the API."""
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f'https://api.financialdatasets.ai/company/facts'
        f'?ticker={ticker}'
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    company_facts = data.get('company_facts')
    if not company_facts:
        raise ValueError("No company facts returned")
    return company_facts.get('market_cap')

def get_prices(
    ticker: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """Fetch price data from the API."""
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f"https://api.financialdatasets.ai/prices/"
        f"?ticker={ticker}"
        f"&interval=day"
        f"&interval_multiplier=1"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    prices = data.get("prices")
    if not prices:
        raise ValueError("No price data returned")
    return prices

def prices_to_df(prices: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame(prices)
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df

# Update the get_price_data function to use the new functions
def get_price_data(
    ticker: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)