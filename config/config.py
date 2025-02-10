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

    # Load functions from YAML config
    with open("config/func.yaml", "r") as file:
        functions = yaml.safe_load(file).get("functions", [])

    # Dynamically map function names to actual function references
    available_functions = {
        func["name"]: globals().get(func["name"])
        for func in functions
        if func["name"] in globals()  # Ensure the function exists
    }

    # Log missing functions (optional, for debugging)
    missing_functions = [func["name"] for func in functions if func["name"] not in available_functions]
    if missing_functions:
        print(f"Warning: Missing function definitions for {missing_functions}")

    return {
        "base_url": base_url,
        "api_key": api_key,
        "functions": functions,
        "available_functions": available_functions
    }