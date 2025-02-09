import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from services.stock_analysis import StockAnalyzer
from services.stock_plotter import StockPlotter

class ChatbotInterface:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("API_KEY")
        )

    def process_user_input(self, user_input):
        response = self.client.chat.completions.create(
            model='qwen2.5:7b',
            messages=[{"role": "user", "content": user_input}],
            functions=[]
        )
        return response.choices[0].message.content