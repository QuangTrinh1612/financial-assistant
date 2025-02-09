from dotenv import load_dotenv
import os
import yaml

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

with open("config/func.yaml", "r") as file:
    functions = yaml.safe_load(file).get("functions")