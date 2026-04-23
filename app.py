import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, MODELS_BY_PROVIDER

from orchestrator.engine import ChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface




def get_chatbot_engine():
    """
    Tạo và trả về chatbot engine với adapter được cấu hình.
    """
    return ChatbotEngine()


def main():
    """
    Entry point của Streamlit application.
    """
    st.set_page_config(layout="wide")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    engine = get_chatbot_engine()

    render_sidebar()
    render_chat_interface(engine=engine)


if __name__ == "__main__":
    main()
