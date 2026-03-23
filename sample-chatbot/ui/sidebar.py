import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode


MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b", 
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b"
    ],
    Provider.OLLAMA.value: [
        "qwen3:0.6b", 
        "qwen3.5:0.8b"
    ],
}



def render_sidebar():
    global_logger.debug("Rendering sidebar")
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
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
        key="temperature"
    )
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=16384,
        step=256,
        key="max_tokens"
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
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0,
        key="context_management_mode"
    )
    # If sliding window selected, allow user to choose number of turns (pairs) to keep
    if st.session_state.get("context_management_mode", ContextManagementMode.OFF.value) == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 5
        st.sidebar.number_input(
            label="Số turn (sliding window)",
            min_value=1,
            max_value=50,
            value=st.session_state.sliding_window_turns,
            step=1,
            key="sliding_window_turns",
            help="Số cặp user-assistant được giữ lại trong sliding window",
        )
    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value
    st.sidebar.toggle(
        label="Cho phép sử dụng công cụ",
        value=False,
        key="enable_tools",
        on_change=on_enable_tools_change,
    )

    # ================================================================
    # KNOWLEDGE BASE (RAG) SECTION
    # ================================================================
    st.sidebar.divider()
    st.sidebar.subheader("📚 Knowledge Base")

    # Hiển thị số lượng chunks hiện có
    rag = st.session_state.get("rag")
    if rag:
        chunk_count = rag.doc_count()
        if chunk_count > 0:
            st.sidebar.info(f"📄 {chunk_count} chunks trong Knowledge Base")
        else:
            st.sidebar.caption("Knowledge base đang trống")
    
    # Upload file
    uploaded_files = st.sidebar.file_uploader(
        label="Upload tài liệu",
        type=["txt", "md", "pdf", "docx", "pptx", "xlsx", "html"],
        accept_multiple_files=True,
        help="Hỗ trợ: TXT, MD, PDF, DOCX, PPTX, XLSX, HTML",
        key="rag_file_uploader",
    )

    # Nút thêm tài liệu
    if st.sidebar.button("📥 Thêm tài liệu vào KB", use_container_width=True):
        if not uploaded_files:
            st.sidebar.warning("Vui lòng chọn file trước!")
        elif not rag:
            st.sidebar.error("RAG chưa được khởi tạo!")
        else:
            try:
                with st.spinner("Đang xử lý tài liệu..."):
                    num_chunks = rag.add_documents(uploaded_files)
                st.sidebar.success(f"✅ Đã thêm {num_chunks} chunks!")
                global_logger.info(f"Added {num_chunks} chunks to knowledge base")
            except Exception as e:
                st.sidebar.error(f"❌ Lỗi: {str(e)}")
                global_logger.error(f"Error adding documents: {str(e)}")

    # Danh sách file + xóa riêng lẻ
    if rag and rag.doc_count() > 0:
        sources = rag.list_sources()
        if sources:
            with st.sidebar.expander(f"📁 Tài liệu ({len(sources)} file)", expanded=False):
                for item in sources:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"📄 {item['source']} ({item['chunk_count']} chunks)")
                    with col2:
                        if st.button("🗑️", key=f"del_{item['source']}", help=f"Xóa {item['source']}"):
                            deleted = rag.delete_source(item["source"])
                            st.success(f"✅ Đã xóa {deleted} chunks!")
                            global_logger.info(f"Deleted source: {item['source']} ({deleted} chunks)")
                            st.rerun()

        # Nút xóa toàn bộ
        if st.sidebar.button("🗑️ Xóa toàn bộ Knowledge Base", use_container_width=True):
            rag.clear()
            st.sidebar.success("✅ Đã xóa toàn bộ Knowledge Base!")
            global_logger.info("Knowledge base cleared by user")
            st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info(f"Settings updated: Selected provider: {st.session_state.selected_provider}, model: {st.session_state.selected_model}, Temperature: {st.session_state.temperature}, Max tokens: {st.session_state.max_tokens}, Context Management Mode: {ContextManagementMode(st.session_state.context_management_mode)}, Tools enabled: {st.session_state.enable_tools}")
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình! Lịch sử chat đã được xóa.")