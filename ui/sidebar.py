import streamlit as st
from custom_types import Provider, ContextManagementMode, MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls cấu hình chung của chatbot.
    
    Side effects: cập nhật các keys trong `st.session_state` và reset
    `st.session_state.chat_history` khi nhấn nút "Cập nhật cài đặt".
    """
    
    # TODO 1a: Khởi tạo các giá trị mặc định trong session_state
    # if "selected_provider" not in st.session_state:
    #     st.session_state.selected_provider = Provider.GROQ.value
    # if "selected_model" not in st.session_state:
    #     st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]
    # (tương tự cho temperature, max_completion_tokens, system_prompt, 
    #  context_management_mode, sliding_window_turns, enable_tools)
    
    # TODO 1b: Tạo sidebar title "Cài đặt Chatbot"
    
    # TODO 1c: Tạo selectbox chọn Provider
    # st.sidebar.selectbox(
    #     label="Chọn nhà cung cấp mô hình",
    #     options=[Provider.GROQ.value, Provider.OLLAMA.value],
    #     index=0,
    #     key="selected_provider"
    # )
    
    # TODO 1d: Tạo selectbox chọn Model dựa trên Provider
    # available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    # st.sidebar.selectbox(
    #     label="Chọn mô hình",
    #     options=available_models,
    #     index=0,
    #     key="selected_model"
    # )
    
    # TODO 1e: Tạo slider cho Temperature (0.0 - 1.0, value=0.25, step=0.05)
    
    # TODO 1f: Tạo number_input cho Max Completion Tokens (min=2048, max=131072, value=5120, step=256)
    
    # TODO 1g: Tạo text_area cho System Prompt (height=200)
    
    # TODO 1h: Tạo radio cho Context Management Mode
    # options=[ContextManagementMode.OFF.value, ContextManagementMode.SLIDING_WINDOW.value]
    
    # TODO 1i: Nếu chọn SLIDING_WINDOW, tạo number_input cho số tin nhắn (min=1, max=50, value=5, step=1)
    
    # TODO 1j: Tạo toggle cho "Sử dụng công cụ" (value=False)
    
    # TODO 1k: Tạo button "Cập nhật cài đặt"
    # Khi nhấn: reset chat_history và xóa chatbot_engine trong session_state
    pass