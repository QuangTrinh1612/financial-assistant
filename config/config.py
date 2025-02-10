import os
import yaml
from dotenv import load_dotenv

import yfinance as yf
import matplotlib.pyplot as plt

def get_config():
    """Load environment variables and function mappings dynamically."""
    
    # Load environment variables
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")

    return {
        "base_url": base_url,
        "api_key": api_key
    }