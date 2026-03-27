"""
Module 6-7 - Chat Interface

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

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice


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
        - instruction: System instruction/prompt

    Note:
        - UI chỉ lưu cleaned content (không có reasoning blocks)
        - Engine.memory handles its own buffer cho full context
    """
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")
    
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display existing messages from session_state
    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).markdown(entry["content"])
        global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    # Render chat input box
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        # Strip any internal reasoning blocks from UI view
        # This removes <think>...</think> tags while keeping the visible response
        cleaned_input = re.sub(r"<think>.*?</think>", "", user_input, flags=re.DOTALL | re.IGNORECASE).strip()
        visible_user_msg = cleaned_input if cleaned_input else "[Phần suy nghĩ nội bộ đã được tách ra]"

        global_logger.debug(f"Processing user input: {visible_user_msg[:50]}...")
        with st.chat_message("user"):
            st.markdown(visible_user_msg)

        # Only append to UI chat_history; engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "user", "content": visible_user_msg})

        # Send cleaned input (without <think> blocks) to the model
        with st.spinner("Đang suy nghĩ..."):
            assistant_reply = engine.response(
                model=st.session_state.selected_model,
                input=cleaned_input,
                temperature=st.session_state.temperature,
                tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
                tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
                max_tokens=st.session_state.max_tokens,
                instruction=st.session_state.instruction,
            )
            # st.markdown(type(assistant_reply))

        # Remove any <think> blocks from the assistant's reply before displaying
        assistant_reply_clean = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL | re.IGNORECASE).strip()

        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply_clean)}")

        # Only append to UI chat_history; engine.memory handles its own buffer
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply_clean,
        })

        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")
        st.rerun()