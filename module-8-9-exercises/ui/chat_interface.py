"""Bài tập Buổi 7 — Hiển thị tài liệu tham khảo từ RAG trong chat.

Nhiệm vụ:
  TODO 1: Implement _render_retrieved_docs()
  TODO 2: Gọi hàm trong history loop (hiển thị lại docs của tin cũ)
  TODO 3: Gọi hàm sau khi nhận reply mới
"""

import re
import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice


# ================================================================
# TODO 1: Implement helper function
# ================================================================

def _render_retrieved_docs(docs_str: str):
    """
    Hiển thị tài liệu tham khảo từ kết quả RAG retrieval trong expander.

    Args:
        docs_str (str): Context string từ RAG.
            Format: "[Tài liệu 1 — 📄 file.pdf]\nnội dung...\n\n---\n\n[Tài liệu 2 ...]..."

    Các bước cần làm:
        1. Tách: chunks = docs_str.split("\n\n---\n\n")
        2. Tạo expander:
               st.expander("📚 Tài liệu tham khảo ({} đoạn)".format(len(chunks)), expanded=False)
        3. Lặp qua từng chunk:
               lines = chunk.strip().split("\n", 1)
               header = lines[0].strip()
               body   = lines[1].strip() if len(lines) > 1 else chunk.strip()
        4. Hiển thị header: st.markdown("**{}**".format(header))
        5. Hiển thị body trong thẻ div có border-left màu xanh lá:
               st.markdown(
                   "<div style='background:#f8f9fa;border-left:3px solid #4CAF50;"
                   "padding:8px 12px;border-radius:4px;font-size:0.9em;"
                   "white-space:pre-wrap;'>{}</div>".format(body),
                   unsafe_allow_html=True,
               )
        6. st.divider()
    """
    # YOUR CODE HERE
    raise NotImplementedError("TODO 1: Implement _render_retrieved_docs()")


# ================================================================
# Chat Interface — KHÔNG CẦN SỬA (trừ các chỗ TODO 2 và TODO 3)
# ================================================================

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
                # TODO 2: Nếu message index i có trong retrieved_docs_map,
                #         gọi _render_retrieved_docs() với nội dung tương ứng.
                # Gợi ý: if i in st.session_state.retrieved_docs_map:
                #               _render_retrieved_docs(st.session_state.retrieved_docs_map[i])
                # YOUR CODE HERE

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        cleaned_input = re.sub(r"<tool_call>.*?<tool_call>", "", user_input, flags=re.DOTALL | re.IGNORECASE).strip()
        visible_user_msg = cleaned_input if cleaned_input else "[Phần suy nghĩ nội bộ đã được tách ra]"

        with st.chat_message("user"):
            st.markdown(visible_user_msg)

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            user_prompt=user_input,
            temperature=st.session_state.temperature,
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            max_tokens=st.session_state.max_tokens,
            system_prompt=st.session_state.instruction,
        )

        retrieved_docs = st.session_state.pop("last_retrieved_docs", None)

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
            # TODO 3: Nếu retrieved_docs tồn tại,
            #         gọi _render_retrieved_docs(retrieved_docs)
            # YOUR CODE HERE

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        if retrieved_docs:
            msg_index = len(st.session_state.chat_history) - 1
            st.session_state.retrieved_docs_map[msg_index] = retrieved_docs

        global_logger.debug(f"Updated chat history, total: {len(st.session_state.chat_history)}")
        st.rerun()
