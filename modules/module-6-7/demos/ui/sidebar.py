import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode


MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b", 
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b"
    ],
    Provider.OLLAMA.value: [
        "qwen3:0.6b", 
        "qwen3.5:0.8b"
    ],
}



def render_sidebar():
    global_logger.debug("Rendering sidebar")
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
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
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        key="temperature"
    )
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=16384,
        step=256,
        key="max_output_tokens"
    )
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Instruction)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        key="instruction"
    )
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
            ContextManagementMode.RELEVANCE_FILTERING.value
        ],
        index=0,
        key="context_management_mode"
    )
    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value
    st.sidebar.toggle(
        label="Cho phép sử dụng công cụ",
        value=False,
        key="enable_tools",
        on_change=on_enable_tools_change,
    )
    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info(f"Settings updated: Selected provider: {st.session_state.selected_provider}, model: {st.session_state.selected_model}, Temperature: {st.session_state.temperature}, Max tokens: {st.session_state.max_output_tokens}, Context Management Mode: {ContextManagementMode(st.session_state.context_management_mode)}, Tools enabled: {st.session_state.enable_tools}")
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình! Lịch sử chat đã được xóa.")