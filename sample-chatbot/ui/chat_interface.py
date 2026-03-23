import re
import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice



def render_chat_interface(engine: object):
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "retrieved_docs_map" not in st.session_state:
        st.session_state.retrieved_docs_map = {}

    with st.container():
        for i, entry in enumerate(st.session_state.chat_history):
            with st.chat_message(entry["role"]):
                st.markdown(entry["content"])
                # Hiển thị lại tài liệu tham khảo từ map riêng
                if i in st.session_state.retrieved_docs_map:
                    with st.expander("📚 Tài liệu tham khảo (Retrieved Documents)"):
                        st.markdown(st.session_state.retrieved_docs_map[i])
        global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        # Extract any <think>...</think> blocks from the user's input and treat them as manual reasoning
        think_matches = re.findall(r"<think>(.*?)</think>", user_input, flags=re.DOTALL | re.IGNORECASE)
        user_thinking = "\n\n".join(m.strip() for m in think_matches).strip() if think_matches else ""
        # Remove the <think> blocks from the visible message sent to the model/UI
        cleaned_input = re.sub(r"<think>.*?</think>", "", user_input, flags=re.DOTALL | re.IGNORECASE).strip()
        visible_user_msg = cleaned_input if cleaned_input else "[Phần suy nghĩ nội bộ đã được tách ra]"

        global_logger.debug(f"Processing user input: {visible_user_msg[:50]}...")
        with st.chat_message("user"):
            st.markdown(visible_user_msg)

        # Only append to UI chat_history, engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=user_input,
            temperature=st.session_state.temperature,
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            max_output_tokens=st.session_state.max_output_tokens,
            instruction=st.session_state.instruction
        )
        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply)}")

        # Lấy retrieved docs (nếu có) từ session_state
        retrieved_docs = st.session_state.pop("last_retrieved_docs", None)

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
            # Hiển thị tài liệu đã retrieve trong expander
            if retrieved_docs:
                with st.expander("📚 Tài liệu tham khảo (Retrieved Documents)"):
                    st.markdown(retrieved_docs)

        # Lưu vào chat history (KHÔNG chứa retrieved_docs để tránh lỗi API)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        # Lưu retrieved docs riêng theo index của message
        if retrieved_docs:
            msg_index = len(st.session_state.chat_history) - 1
            st.session_state.retrieved_docs_map[msg_index] = retrieved_docs
        # Only append to UI chat_history, engine.memory handles its own buffer
        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")
        st.rerun()