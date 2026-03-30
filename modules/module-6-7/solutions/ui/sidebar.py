"""
Module 6-7 - Sidebar UI (Solution)

Mô tả: Streamlit sidebar component cho chatbot demo. Sidebar này cung cấp
các controls để cấu hình:
- LLM provider (Groq, Ollama)
- Model selection
- Temperature (creativity level)
- Max output tokens
- System instruction
- Context management mode (off, sliding window)
- Tool usage toggle

Kiến trúc / Dependencies:
- Streamlit: Web UI framework
- custom_types: Provider, ContextManagementMode enums
- constants: MODELS_BY_PROVIDER mapping

Session State Managed:
    - selected_provider: Provider name (groq, ollama)
    - selected_model: Model identifier
    - temperature: Float 0.0-1.0
    - max_tokens: Integer 2048-131072
    - instruction: System prompt string
    - context_management_mode: Memory mode
    - sliding_window_turns: Number of turns for sliding window
    - enable_tools: Boolean for tool usage
    - chat_history: Reset when settings updated

Usage:
    from ui.sidebar import render_sidebar
    render_sidebar()
"""

import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode
from constants import MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls để cấu hình chatbot.

    Sidebar components (theo thứ tự):
    1. Provider selection dropdown
    2. Model selection dropdown (dynamic based on provider)
    3. Temperature slider
    4. Max tokens number input
    5. System instruction textarea
    6. Context management mode radio
    7. Sliding window turns input (conditional)
    8. Tools toggle
    9. Update settings button

    Side Effects:
        - Updates st.session_state với các giá trị từ controls
        - Auto-toggles context mode khi bật tools
        - Resets chat_history khi click "Cập nhật cài đặt"
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

    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Giá trị cao hơn sẽ làm cho phản hồi của mô hình sáng tạo hơn, trong khi giá trị thấp hơn sẽ làm cho phản hồi an toàn và tập trung hơn",
        key="temperature"
    )

    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=16384,
        step=256,
        help="Giới hạn số token trong phản hồi của mô hình, bao gồm cả token suy luận nếu có",
        key="max_tokens"
    )

    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Instruction)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        help="Câu lệnh hệ thống là một phần của prompt được gửi đến mô hình để hướng dẫn cách thức phản hồi. Bạn có thể sử dụng nó để thiết lập bối cảnh, vai trò của chatbot, hoặc bất kỳ hướng dẫn đặc biệt nào mà bạn muốn mô hình tuân theo khi tạo phản hồi.",
        key="instruction"
    )

    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0,
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại để tạo phản hồi. 'Tắt' sẽ không sử dụng lịch sử nào, 'Cửa sổ trượt' sẽ chỉ sử dụng một số lượng tin nhắn gần đây nhất dựa trên kích thước cửa sổ đã định.",
        key="context_management_mode"
    )

    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 2
        st.sidebar.number_input(
            label="Số tin nhắn trong cửa sổ trượt",
            min_value=1,
            max_value=50,
            value=st.session_state.sliding_window_turns,
            step=1,
            key="sliding_window_turns",
            help="Số tin nhắn user-assistant được giữ lại trong cửa sổ trượt để cung cấp ngữ cảnh cho phản hồi. Ví dụ: nếu bạn đặt 3, chatbot sẽ sử dụng 3 tin nhắn gần nhất",
        )

    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value

    st.sidebar.toggle(
        label="Sử dụng công cụ",
        value=False,
        key="enable_tools",
        help="Bật nếu bạn muốn cho phép chatbot sử dụng các công cụ đã tích hợp (ví dụ: truy vấn cơ sở dữ liệu, gọi API, v.v.) để trả lời câu hỏi của người dùng. Nếu tắt, chatbot sẽ chỉ dựa vào kiến thức đã được huấn luyện mà không sử dụng công cụ bên ngoài nào.",
        on_change=on_enable_tools_change,
    )

    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info("Settings updated: Selected provider: {}, model: {}, Temperature: {}, Max tokens: {}, Context Management Mode: {}, Tools enabled: {}".format(
            st.session_state.get("selected_provider"),
            st.session_state.get("selected_model"),
            st.session_state.get("temperature"),
            st.session_state.get("max_tokens"),
            str(ContextManagementMode(st.session_state.get("context_management_mode"))),
            st.session_state.get("enable_tools")
        ))
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình!")
