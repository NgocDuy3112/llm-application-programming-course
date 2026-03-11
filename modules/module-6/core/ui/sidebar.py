import streamlit as st



def sidebar():
    with st.sidebar:
        st.title("Cài đặt Chatbot")
        st.selectbox(
            "Chọn mô hình",
            options=[
                "groq:openai/gpt-oss-20b",
                "groq:openai/gpt-oss-safeguard-20b",
                "groq:openai/gpt-oss-120b", 
                "ollama:qwen3.5:0.8b",
                "ollama:qwen3.5:2b",
            ],
            index=0,
            key="model"
        )
        st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
            key="temperature"
        )
        st.slider(
            "Số tokens tối đa",
            min_value=2048,
            max_value=131072,
            value=65536,
            step=256,
            key="max_output_tokens"
        )
        st.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)", 
            value="", 
            height=200,
            key="instruction"
        )
        st.toggle(
            "Bật công cụ",
            value=st.session_state.get("enable_tools", True),
            key="enable_tools",
        )