import streamlit as st
from custom_types import Provider, ContextManagementMode, MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls cấu hình chung của chatbot.
    
    Side effects: cập nhật các keys trong `st.session_state` và reset
    `st.session_state.chat_history` khi nhấn nút "Cập nhật cài đặt".
    """
    
    # Khởi tạo các giá trị mặc định trong session_state
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]
    
    # TODO[1]: Tạo sidebar title "Cài đặt Chatbot"
    
    # TODO[1]: Tạo selectbox chọn Provider
    
    # TODO[1]: Tạo selectbox chọn Model dựa trên Provider
    
    # TODO[1]: Tạo slider cho Temperature (0.0 - 1.0, value=0.25, step=0.05)
    
    # TODO[1]: Tạo number_input cho Max Completion Tokens (min=2048, max=131072, value=5120, step=256)
    
    # TODO[1]: Tạo text_area cho System Prompt (height=200)
    
    # TODO[1]: Tạo radio cho Context Management Mode
    # options=[ContextManagementMode.OFF.value, ContextManagementMode.SLIDING_WINDOW.value]
    
    # TODO[1]: Nếu chọn SLIDING_WINDOW, tạo number_input cho số tin nhắn (min=1, max=50, value=5, step=1)
    
    # TODO[1]: Tạo toggle cho "Sử dụng công cụ" (value=False)
    
    # TODO[1]: Tạo button "Cập nhật cài đặt"
    # Khi nhấn: reset chat_history và xóa chatbot_engine trong session_state
    pass
