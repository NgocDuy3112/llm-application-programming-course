"""
Module 5 - Sidebar Component

Mô tả: Sidebar với các controls để cấu hình chatbot.
"""

import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode
from custom_types import MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls để cấu hình chatbot.
    """
    global_logger.debug("Rendering sidebar")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    st.sidebar.title("Cài đặt Chatbot")

    st.sidebar.selectbox(
        label="Chọn nhà cung cấp mô hình",
        options=[
            Provider.GROQ.value,
            Provider.OLLAMA.value
        ],
        index=0,
        key="selected_provider"
    )

    available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    st.sidebar.selectbox(
        label="Chọn mô hình",
        options=available_models,
        index=0,
        key="selected_model"
    )

    st.sidebar.radio(
        label="Chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0,
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại.",
        key="context_management_mode"
    )

    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 2
        st.sidebar.number_input(
            label="Số tin nhắn trong cửa sổ trượt",
            min_value=1,
            max_value=10,
            value=st.session_state.sliding_window_turns,
            step=1,
            key="sliding_window_turns",
            help="Số tin nhắn được giữ lại trong cửa sổ trượt.",
        )

    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info(f"Settings updated: provider={st.session_state.get('selected_provider')}, model={st.session_state.get('selected_model')}")
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình!")