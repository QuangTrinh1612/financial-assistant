import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

def get_stock_price(ticker: str):
    return str(yf.Ticker(ticker).history(period='1y').iloc[-1].Close)

def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    return str(data.rolling(window=window).mean().iloc[-1])

def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1])

def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14-1, adjust=False).mean()
    ema_down = down.ewm(com=14-1, adjust=False).mean()
    rs = ema_up / ema_down
    return str(100 - (100 / (1 + rs)).iloc[-1])

def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False)

    MACD_histogram = MACD - signal

    return f'{MACD[-1]}, {signal[-1]}, {MACD_histogram[-1]}'

def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    plt.figure(figsize=(10,5))
    plt.plot(data.index, data.Close)
    plt.title(f"{ticker} Stock Price Over Last Year")
    plt.xlabel('Date')
    plt.ylabel('Stock Price ($)')
    plt.grid(True)
    plt.savefig('assets/stock.png')
    plt.close()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Gets the latest stock price given the ticker symbol of a company.",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_SMA",
            "description": "Calculate the simple moving average for a given stock ticker and a window",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    },
                    "window": {
                        "type": "integer",
                        "description": "The timeframe to consider when calculating the SMA"
                    }
                },
                "required": ["ticker", "window"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_EMA",
            "description": "Calculate the exponential moving average for a given stock ticker and a window",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    },
                    "window": {
                        "type": "integer",
                        "description": "The timeframe to consider when calculating the SMA"
                    }
                },
                "required": ["ticker", "window"]
            }
        }
    },
    {
        "type": "function",
        "function": {
                "name": "calculate_RSI",
            "description": "Calculate the RSI for a given stock ticker",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_MACD",
            "description": "Calculate the MACD for a given stock ticker",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_stock_price",
            "description": "Plot the stock price for the last year given the ticker symbol of a company.",
            "parameters": {
                "type": "object",
                "property": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol for a company (for example APPL for Apple)"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
]

available_functions = {
    "get_stock_price": get_stock_price,
    "calculate_SMA": calculate_SMA,
    "calculate_EMA": calculate_EMA,
    "calculate_RSI": calculate_RSI,
    "calculate_MACD": calculate_MACD,
    "plot_stock_price": plot_stock_price
}

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

st.title('Stock Analysis Assistant')
user_input = st.text_input("Your input:")

if user_input:
    try:
        st.session_state['messages'].append({
            "role": "user",
            "content": f"{user_input}"
        })

        response = client.chat.completions.create(
            model='qwen2.5:7b',
            messages=st.session_state["messages"],
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        if response_message.tool_calls:
            tool_id = response_message.tool_calls[0].id
            function_name = response_message.tool_calls[0].function.name
            function_args = json.loads(response_message.tool_calls[0].function.arguments)
            if function_name in ["get_stock_price", "calculate_RSI", 'calculate_MACD', 'plot_stock_price']:
                args_dict = {'ticker': function_args.get('ticker')}
            elif function_name in ["calculate_SMA", "calculate_EMA"]:
                args_dict = {
                    'ticker': function_args.get('ticker'),
                    'window': function_args.get('window')
                }

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)

            if function_name == 'plot_stock_price':
                st.image("assets/stock.png")
            else:
                st.session_state['messages'].append({
                    "role": "assistant",
                    "content": response_message.content
                })

                st.session_state['messages'].append({
                    "tool_call_id": tool_id,
                    "role": "tool",
                    "content": function_response
                })
                
                second_response = client.chat.completions.create(
                    model='qwen2.5:7b',
                    messages=st.session_state["messages"]
                )

                st.text(second_response.choices[0].message.content)

                st.session_state['messages'].append({
                    "role": "assistant",
                    "content": second_response.choices[0].message.content
                })
        else:
            st.text(response_message.content)
            st.session_state["messages"].append({
                "role": "assistant",
                "content": response_message.content
            })
    except Exception as e:
        st.text(e)