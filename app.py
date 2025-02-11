from openai import OpenAI
import streamlit as st
import json
import logging

from config.config import get_config
from utils.function_registry import FunctionsRegistry

# Load configuration and available functions
config = get_config()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_user_input(client, user_input, tools):
    """Processes user input and generates AI response."""
    try:
        # Append user message
        st.session_state["messages"].append({"role": "user", "content": user_input})

        tools = FunctionsRegistry()

        # Get response from OpenAI API
        response = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=st.session_state["messages"],
            tools=tools.mapped_functions(),
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        # Check if a tool (function) is called
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            return handle_tool_call(response_message, tools)
        else:
            return display_response(response_message.content)

    except Exception as e:
        logging.error(f"Error processing input: {e}")
        st.error("An error occurred while processing your request. Please try again.")
        return None

def handle_tool_call(response_message, tools):
    """Handles function calls from the AI response."""
    tool_calls = response_message.tool_calls
    function_map = tools.get_function_callable()

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        if function_name in function_map:
            function_args = json.loads(tool_call.function.arguments)

            logging.info(f"Calling function [{function_name}] with arguments as {function_args}")

            try:
                function_response = function_map[function_name](
                    **function_args)

                # Handle function-specific responses
                if function_name == "plot_stock_price":
                    st.image("assets/stock.png")
                else:
                    append_tool_response(tool_call.id, function_name, function_response)
                    return generate_follow_up_response()
                
            except Exception as e:
                logging.error(f"Error in {function_name}: {e}")

def append_tool_response(tool_id, function_name, function_response):
    """Appends the tool response to the chat history."""
    st.session_state["messages"].append({"role": "assistant", "content": "Here is the result:"})
    st.session_state["messages"].append({"tool_call_id": tool_id, "role": "tool", "name": function_name, "content": function_response})

def generate_follow_up_response():
    """Generates a follow-up response after executing a function."""
    follow_up_response = client.chat.completions.create(
        model="qwen2.5:7b",
        messages=st.session_state["messages"],
    )
    follow_up_content = follow_up_response.choices[0].message.content

    st.text(follow_up_content)
    st.session_state["messages"].append({"role": "assistant", "content": follow_up_content})

def display_response(response_content):
    """Displays AI response and updates the chat history."""
    st.text(response_content)
    st.session_state["messages"].append({"role": "assistant", "content": response_content})

if __name__ == '__main__':
    # --- Streamlit UI ---
    st.title("📈 Stock Analysis Assistant")

    client = OpenAI(
        base_url=config.get('base_url'),
        api_key=config.get('api_key')
    )

    tools = FunctionsRegistry()

    # User input field
    user_input = st.text_input("Your input:")
    if user_input:
        process_user_input(client, user_input, tools)