from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import json

from utils.function_registry import FunctionsRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)

def main() -> None:
    load_dotenv()

    try:
        client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("API_KEY")
        )

        tools = FunctionsRegistry()
        function_map = tools.get_function_callable()
        
        # This might not work as the context is short, You have to stich up the prompt better to make it work in this particular example
        messages: List[Dict[str, str]] = [
            {"role": "user", "content": "What is stock price of APPLE"}
        ]

        completion = client.chat.completions.create(
            model='qwen2.5:7b',
            messages=messages,
            tools=tools.mapped_functions(),
            tool_choice="auto"
        )

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                if function_name in function_map:
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        function_response = function_map[function_name](
                            **function_args)
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        })
                    except Exception as e:
                        logging.error(f"Error in {function_name}: {e}")

            second_completion = client.chat.completions.create(
                model="qwen2.5:7b",
                messages=messages
            )

            logging.info(second_completion)
        else:
            logging.info(completion)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()