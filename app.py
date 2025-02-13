import streamlit as st
import json
import logging

from openai import OpenAI
from config.financial_analysis_config import *
from utils.function_registry import FunctionsRegistry

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["display_messages"] = []

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_user_input(client, user_input, tools):
    """Processes user input and generates AI response."""
    try:
        # Append user message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["display_messages"].append({"role": "user", "content": user_input})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        tools = FunctionsRegistry()

        # Get response from OpenAI API
        response = client.chat.completions.create(
            model=st.session_state["llm_model"],
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
                function_response = function_map[function_name](**function_args)

                # Handle function-specific responses
                if function_name == "plot_stock_price":
                    st.image("assets/stock.png")
                else:
                    append_tool_response(tool_call.id, function_name, function_response)
                    logging.info(f"Function response: {function_response}")
                    
                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        response = st.write_stream(generate_follow_up_response())
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state["display_messages"].append({"role": "assistant", "content": response})

            except Exception as e:
                logging.error(f"Error executing {function_name}: {e}")
                st.error(f"Failed to execute {function_name}. Please try again.")

def append_tool_response(tool_id, function_name, function_response):
    """Appends the tool response to the chat history."""
    st.session_state["messages"].append({"role": "assistant", "content": "Here is the result:"})
    st.session_state["messages"].append({
        "tool_call_id": tool_id,
        "role": "tool",
        "name": function_name,
        "content": function_response
    })

def generate_follow_up_response():
    """Generates a follow-up response after executing a function."""
    follow_up_response = client.chat.completions.create(
        model=st.session_state["llm_model"],
        messages=st.session_state["messages"],
        stream=True, # Streaming enabled
    )

    for chunk in follow_up_response:
        if hasattr(chunk.choices[0].delta, "content"):
            yield chunk.choices[0].delta.content

def display_response(response_content):
    """Displays AI response and updates the chat history."""
    st.text(response_content)
    st.session_state["messages"].append({"role": "assistant", "content": response_content})

if __name__ == '__main__':
    # --- Streamlit UI ---
    st.set_page_config(
        page_title="FinGPT Demo",
        layout="centered"
    )
    
    st.title("📈 Stock Analysis Assistant")

    # List of models
    models = ["qwen2.5:14b", "mistral:7b"]

    # Create a select box for the models
    st.session_state["llm_model"] = st.sidebar.selectbox("Select OpenAI model", models, index=0)

    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    tools = FunctionsRegistry()

    # Display chat messages from history on app rerun
    for message in st.session_state["display_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input field
    user_input = st.chat_input("Your input:")
    if user_input:
        process_user_input(client, user_input, tools)