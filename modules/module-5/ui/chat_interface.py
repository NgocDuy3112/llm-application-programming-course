"""
Module 5 - Chat Interface Component

Mô tả: Giao diện chat chính của ứng dụng.
"""

import streamlit as st
from logger import global_logger


def render_chat_interface(engine: object):
    """
    Render giao diện chat chính.

    Args:
        engine (object): Object implementing `.response(model, user_prompt)` method
    """
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Hiển thị lịch sử chat
    for entry in st.session_state.chat_history:
        st.chat_message(entry["role"]).markdown(entry["content"])
    global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    # Input box
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        global_logger.debug(f"Processing user input: {user_input[:50]}...")

        # Hiển thị tin nhắn user
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Đang suy nghĩ..."):
            # Gọi engine với chỉ model và user_prompt
            assistant_reply = engine.response(
                model=st.session_state.selected_model,
                user_prompt=user_input,
            )

        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply)}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply,
        })

        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")
        st.rerun()