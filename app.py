import streamlit as st
from services.chatbot_interface import ChatbotInterface

def main():
    st.title("Stock Analysis Assistant")
    chatbot = ChatbotInterface()
    user_input = st.text_input("Your input:")
    
    if user_input:
        response = chatbot.process_user_input(user_input)
        st.text(response)

if __name__ == "__main__":
    main()