import streamlit as st
from logger import global_logger


def render_sidebar():
    global_logger.debug("Rendering sidebar")
    st.sidebar.title("Cài đặt Chatbot")
    model_id = st.sidebar.selectbox(
        label="Chọn mô hình",
        options=[
            "groq#openai/gpt-oss-20b", 
            "groq#openai/gpt-oss-120b", 
            "ollama#qwen3:0.6b",
            "ollama#qwen3.5:0.8b",
        ],
        index=0
    )

    provider, model_name = model_id.split("#")
    global_logger.info(f"Selected provider: {provider}, model: {model_name}")
    st.session_state.selected_provider = provider
    st.session_state.selected_model = model_name

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
        value=65536,
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
            "Tắt",
            "Cửa sổ trượt (sliding window)",
            "Tóm tắt (summarization)"
        ],
        index=0,
        key="context_management_mode"
    )
    st.sidebar.toggle(
        label="Cho phép sử dụng công cụ",
        value=False,
        key="enable_tools",
    )
    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info(f"Settings updated - Temperature: {st.session_state.temperature}, Max tokens: {st.session_state.max_output_tokens}")
        st.sidebar.success("Đã cập nhật cấu hình!")