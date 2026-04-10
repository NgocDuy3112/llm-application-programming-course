"""Bài tập Buổi 7 — Thêm Knowledge Base section vào sidebar.

Phần trên divider (đã có sẵn) — không cần sửa.
Nhiệm vụ: implement phần KB bên dưới divider (TODO 1 → 5).
"""

import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode


MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b",
        "llama-3.3-70b-versatile",
    ],
    Provider.OLLAMA.value: ["qwen3:0.6b", "qwen3.5:0.8b"],
}


def render_sidebar():
    global_logger.debug("Rendering sidebar")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    st.sidebar.title("Cài đặt Chatbot")

    st.sidebar.selectbox(
        label="Chọn nhà cung cấp mô hình",
        options=[Provider.GROQ.value, Provider.OLLAMA.value],
        index=0,
        key="selected_provider",
    )

    available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    st.sidebar.selectbox(label="Chọn mô hình", options=available_models, index=0, key="selected_model")
    st.sidebar.slider(label="Độ sáng tạo (Temperature)", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="temperature")
    st.sidebar.number_input(label="Max Output Tokens", min_value=2048, max_value=131072, value=16384, step=256, key="max_tokens")
    st.sidebar.text_area(label="System Instruction", height=200, placeholder="Bạn là một trợ lý hữu ích.", key="instruction")

    st.sidebar.radio(
        label="Chế độ quản lý ngữ cảnh",
        options=[ContextManagementMode.OFF.value, ContextManagementMode.SLIDING_WINDOW.value],
        index=0,
        key="context_management_mode",
    )

    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 5
        st.sidebar.number_input(
            label="Số turn (sliding window)", min_value=1, max_value=50,
            value=st.session_state.sliding_window_turns, step=1, key="sliding_window_turns",
        )

    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value

    st.sidebar.toggle(label="Sử dụng công cụ", value=False, key="enable_tools", on_change=on_enable_tools_change)

    # ================================================================
    # TODO: Knowledge Base Section
    # ================================================================

    st.sidebar.divider()
    st.sidebar.subheader("📚 Knowledge Base")

    # Lấy RAG instance từ session_state (do app.py set vào)
    rag = st.session_state.get("rag")

    # TODO 1: Hiển thị số chunks hiện có
    # Gợi ý:
    #   chunk_count = rag.doc_count()
    #   Nếu > 0 → st.sidebar.info("📄 {} chunks trong Knowledge Base".format(chunk_count))
    #   Nếu = 0 → st.sidebar.caption("Knowledge base đang trống")
    if rag:
        # YOUR CODE HERE
        pass

    # TODO 2: File uploader
    # Gợi ý:
    #   uploaded_files = st.sidebar.file_uploader(
    #       label="Upload tài liệu",
    #       type=["txt", "md", "pdf", "docx", "pptx", "xlsx", "html"],
    #       accept_multiple_files=True,
    #       key="rag_file_uploader",
    #   )
    # YOUR CODE HERE

    # TODO 3: Nút "Thêm tài liệu vào KB"
    # Gợi ý:
    #   if st.sidebar.button("📥 Thêm tài liệu vào KB", use_container_width=True):
    #       - Kiểm tra uploaded_files và rag tồn tại
    #       - với st.spinner(): gọi rag.add_documents(uploaded_files)
    #       - Hiển thị st.sidebar.success() hoặc st.sidebar.error()
    # YOUR CODE HERE

    # TODO 4: Danh sách file + xóa từng file
    # Gợi ý:
    #   if rag and rag.doc_count() > 0:
    #       sources = rag.list_sources()  → [{"source": "file.pdf", "chunk_count": 10}, ...]
    #       with st.sidebar.expander("📁 Tài liệu ({} file)".format(len(sources))):
    #           for item in sources:
    #               col1, col2 = st.columns([3, 1])
    #               col1: st.caption("📄 {} ({} chunks)".format(source, count))
    #               col2: if st.button("🗑️", key="del_{}".format(source)):
    #                         rag.delete_source(item["source"])
    #                         st.rerun()
    # YOUR CODE HERE

    # TODO 5: Nút xóa toàn bộ KB
    # Gợi ý:
    #   if rag and rag.doc_count() > 0:
    #       if st.sidebar.button("🗑️ Xóa toàn bộ Knowledge Base", use_container_width=True):
    #           rag.clear()
    #           st.rerun()
    # YOUR CODE HERE
