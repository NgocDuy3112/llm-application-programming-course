import json
import streamlit as st
from settings import Settings
from chat_service import *


settings = Settings()




def sidebar():
    with st.sidebar:
        api_key = st.text_input(
            "Nhập API key",
            value=settings.GROQ_API_KEY,
            type="password"
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
        )
        max_output_tokens = st.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=65000,
            value=65000,
            step=1
        )
        custom_instructions = st.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)",
            value="",
            height=200,
        )
        
    state = {
        "api_key": api_key,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "custom_instructions": custom_instructions,
    }
    return state



def display_response(content: str) -> None:
    if content.startswith("[ERROR]"):
        st.error(content.replace("[ERROR] ", "❌ "))
    elif content.strip().startswith("{") and content.strip().endswith("}"):
        json_data = json.loads(content)
        st.json(json_data)
    else:
        st.markdown(content)



def render_chat_history(chat_history: list[dict[str, str]]) -> None:
    """
    Render chat history in Streamlit
    
    Args:
        chat_history: List of chat messages
    """
    for msg in chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        with st.chat_message(role):
            display_response(content)