import re
import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice


def _render_retrieved_docs(docs_str: str):
    """Helper: render tài liệu tham khảo từ context string."""
    chunks = docs_str.split("\n\n---\n\n")
    with st.expander(f"📚 Tài liệu tham khảo ({len(chunks)} đoạn)", expanded=False):
        for chunk in chunks:
            lines = chunk.strip().split("\n", 1)
            header = lines[0].strip()
            body   = lines[1].strip() if len(lines) > 1 else chunk.strip()
            st.markdown(f"**{header}**")
            st.markdown(
                f"<div style='background:#f8f9fa;border-left:3px solid #4CAF50;"
                f"padding:8px 12px;border-radius:4px;font-size:0.9em;"
                f"white-space:pre-wrap;'>{body}</div>",
                unsafe_allow_html=True,
            )
            st.divider()


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
                if i in st.session_state.retrieved_docs_map:
                    _render_retrieved_docs(st.session_state.retrieved_docs_map[i])
        global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        think_matches = re.findall(r"grounded(.*?)grounded", user_input, flags=re.DOTALL | re.IGNORECASE)
        user_thinking = "\n\n".join(m.strip() for m in think_matches).strip() if think_matches else ""
        cleaned_input = re.sub(r"grounded.*?grounded", "", user_input, flags=re.DOTALL | re.IGNORECASE).strip()
        visible_user_msg = cleaned_input if cleaned_input else "[Phần suy nghĩ nội bộ đã được tách ra]"

        global_logger.debug(f"Processing user input: {visible_user_msg[:50]}...")
        with st.chat_message("user"):
            st.markdown(visible_user_msg)

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=user_input,
            temperature=st.session_state.temperature,
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            max_tokens=st.session_state.max_tokens,
            instruction=st.session_state.instruction
        )
        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply)}")

        retrieved_docs = st.session_state.pop("last_retrieved_docs", None)
        global_logger.debug(f"Retrieved docs: {retrieved_docs if retrieved_docs else 'None'}")

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
            if retrieved_docs:
                _render_retrieved_docs(retrieved_docs)

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        if retrieved_docs:
            msg_index = len(st.session_state.chat_history) - 1
            st.session_state.retrieved_docs_map[msg_index] = retrieved_docs

        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")
        st.rerun()