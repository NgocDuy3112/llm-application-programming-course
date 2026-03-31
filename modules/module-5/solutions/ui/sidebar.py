"""
Module 5 - Sidebar (upgraded)

Đồng bộ tính năng sidebar từ module-6-7: thêm toggle công cụ và cấu hình
cho sliding-window. Không phụ thuộc vào Provider/Model selection để giữ
đơn giản cho Module 5.
"""

import streamlit as st


def render_sidebar():
    """
    Render sidebar với các controls cấu hình chung của chatbot:
    - Temperature
    - Max output tokens
    - System prompt
    - Context management (off | sliding window)
    - Sliding window turns (nếu bật)
    - Tools toggle

    Side effects: cập nhật các keys trong `st.session_state` và reset
    `st.session_state.chat_history` khi nhấn nút "Cập nhật cài đặt".
    """

    # Initialize defaults in session_state so widgets have initial values
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.25
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 16384
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = ""
    if "context_management_mode" not in st.session_state:
        st.session_state.context_management_mode = "Tắt"
    if "sliding_window_turns" not in st.session_state:
        st.session_state.sliding_window_turns = 2
    if "enable_tools" not in st.session_state:
        st.session_state.enable_tools = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.sidebar.title("Cài đặt Chatbot")

    st.sidebar.selectbox(
        label="Chế độ ngữ cảnh (Module 5)",
        options=["Tắt", "Cửa sổ trượt (sliding window)"],
        index=0 if st.session_state.context_management_mode == "Tắt" else 1,
        key="context_management_mode"
    )

    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.05,
        key="temperature",
        help="Giá trị cao hơn làm cho phản hồi sáng tạo hơn; giá trị thấp hơn làm cho phản hồi an toàn hơn"
    )

    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=st.session_state.max_tokens,
        step=256,
        key="max_tokens",
        help="Giới hạn số token trong phản hồi của mô hình"
    )

    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Prompt)",
        height=180,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        key="system_prompt",
    )

    # If sliding window selected, allow configuring number of turns
    if st.session_state.get("context_management_mode") == "Cửa sổ trượt (sliding window)":
        st.sidebar.number_input(
            label="Số tin nhắn trong cửa sổ trượt",
            min_value=1,
            max_value=50,
            value=st.session_state.sliding_window_turns,
            step=1,
            key="sliding_window_turns",
            help="Số tin nhắn user-assistant được giữ lại trong cửa sổ trượt",
        )

    # Toggle to enable external tools (RAG, web search, etc.)
    def _on_enable_tools_change():
        if st.session_state.get("enable_tools"):
            st.session_state.context_management_mode = "Cửa sổ trượt (sliding window)"

    st.sidebar.toggle(
        label="Sử dụng công cụ",
        value=st.session_state.enable_tools,
        key="enable_tools",
        help="Bật nếu muốn cho phép chatbot gọi các công cụ bên ngoài (search, date, v.v.)",
        on_change=_on_enable_tools_change,
    )

    if st.sidebar.button("Cập nhật cài đặt"):
        # Reset chat history when settings are updated
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình!")
        with st.sidebar.expander("Xem chi tiết cấu hình", expanded=True):
            st.markdown(f"**Độ sáng tạo (Temperature):** {st.session_state.temperature}")
            st.markdown(f"**Số lượng token tối đa (Max Output Tokens):** {st.session_state.max_tokens}")
            st.markdown(f"**Câu lệnh hệ thống (System Prompt):** {st.session_state.system_prompt}")
            st.markdown(f"**Chế độ quản lý ngữ cảnh:** {st.session_state.context_management_mode}")
            st.markdown(f"**Sử dụng công cụ:** {st.session_state.enable_tools}")
