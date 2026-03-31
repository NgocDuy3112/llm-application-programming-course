"""
Module 6-7 - Chat Interface (Solution)

Mô tả: Streamlit chat UI component cho demo chatbot. Component này xử lý:
- Hiển thị chat history
- Nhận user input
- Gọi engine để lấy response
- Xử lý reasoning blocks (<think>...</think>)

Kiến trúc / Dependencies:
- Streamlit: Web UI framework
- FullChatbotEngine: Engine để xử lý user input và generate response
- DEFAULT_TOOLS: Tool definitions cho function calling
- ToolChoice: Enum cho tool usage mode

UI Flow:
1. Display existing chat history từ session_state
2. Render chat input box
3. Khi user gửi message:
   a. Strip reasoning blocks khỏi UI view
   b. Lưu vào chat_history
   c. Gọi engine.response()
   d. Strip reasoning blocks khỏi response
   e. Lưu và hiển thị response
   f. Rerun để update UI

Usage:
    from ui.chat_interface import render_chat_interface
    render_chat_interface(engine=chatbot_engine)
"""

import re
import streamlit as st


def render_chat_interface(engine: object):
    """
    Render the chat UI và forward user input đến engine.response().

    Function này:
    - Giữ UI state trong st.session_state.chat_history
    - Strip các internal <think>...</think> blocks khỏi UI view
    - Gửi cleaned input đến engine để xử lý
    - Engine's memory được dùng cho audit/logging và full context

    Args:
        engine (object): Object implementing `.response(...)` method
            để lấy assistant's reply

    Session State Used:
        - chat_history: List of {"role": str, "content": str} messages
        - selected_model: Model name/ID to use
        - temperature: Creativity level (0.0-1.0)
        - max_tokens: Maximum tokens in response
        - enable_tools: Whether to enable function calling
        - system_prompt: System system_prompt/prompt

    Note:
        - UI chỉ lưu cleaned content (không có reasoning blocks)
        - Engine.memory handles its own buffer cho full context
    """
    st.title("Xây dựng chatbot cơ bản")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).markdown(entry["content"])

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Đang suy nghĩ..."):
            assistant_reply = engine.response(
                model="openai/gpt-oss-20b",
                user_prompt=user_input,
            )

        assistant_reply_clean = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL | re.IGNORECASE).strip()

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply_clean,
        })
        # Do not modify `st.session_state['chat_input']` (Streamlit forbids changing
        # a widget-backed key after the widget is created). We use `_last_handled_input`
        # to detect duplicates instead. Now re-run to refresh the UI.
        st.rerun()
