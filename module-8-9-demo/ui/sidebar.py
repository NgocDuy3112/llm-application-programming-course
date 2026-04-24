# Khai báo module docstring - mô tả chức năng của module sidebar này
"""
UI - Sidebar Module

Mô tả: Xử lý giao diện sidebar của ứng dụng Streamlit, bao gồm:
- Cài đặt provider và model
- Điều chỉnh temperature, max tokens, system system_prompt
- Cấu hình chế độ quản lý ngữ cảnh (context management)
- Bật/tắt công cụ (tools)
- Quản lý Knowledge Base (RAG): upload, xem, xóa tài liệu

Kiến trúc / Dependencies:
- streamlit: Framework cho giao diện web
- logger: Global logger để tracking
- custom_types: Provider và ContextManagementMode enums
"""

# Import streamlit - thư viện framework để xây dựng giao diện web app
import streamlit as st
# Import global_logger từ logger module để ghi log hoạt động
from logger import global_logger
# Import Provider enum (GROQ, OLLAMA) và ContextManagementMode enum từ custom_types
from custom_types import Provider, ContextManagementMode


# Dictionary khai báo danh sách các model có sẵn cho từng provider
# Key: tên provider (string), Value: list các model names
MODELS_BY_PROVIDER = {
    # Danh sách models cho provider GROQ
    Provider.GROQ.value: [
        "openai/gpt-oss-20b",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b",
        "llama-3.3-70b-versatile"
    ],
    # Danh sách models cho provider OLLAMA (local models)
    Provider.OLLAMA.value: [
        "qwen3:0.6b",
        "qwen3.5:0.8b"
    ],
}


# Hàm render_sidebar - hàm chính của module, hiển thị toàn bộ sidebar
def render_sidebar():
    """
    Render sidebar với các cài đặt chatbot.

    Các thành phần trong sidebar:
    1. Chọn provider (Groq/Ollama)
    2. Chọn model từ danh sách models của provider
    3. Slider điều chỉnh temperature (độ sáng tạo)
    4. Input số lượng max tokens (độ dài phản hồi)
    5. Text area cho system system_prompt
    6. Radio button chọn chế độ quản lý ngữ cảnh
    7. Toggle bật/tắt tools
    8. Knowledge Base section: upload, xem, xóa tài liệu
    """
    # Ghi log debug: bắt đầu render sidebar
    global_logger.debug("Rendering sidebar")
    
    # Kiểm tra nếu 'selected_provider' chưa tồn tại trong session_state
    # session_state là nơi lưu trữ trạng thái giữa các lần rerun của Streamlit
    if "selected_provider" not in st.session_state:
        # Khởi tạo giá trị mặc định là GROQ
        st.session_state.selected_provider = Provider.GROQ.value
    
    # Kiểm tra nếu 'selected_model' chưa tồn tại trong session_state
    if "selected_model" not in st.session_state:
        # Khởi tạo model mặc định là "openai/gpt-oss-20b"
        st.session_state.selected_model = "openai/gpt-oss-20b"
    
    # Tạo tiêu đề cho sidebar với text "Cài đặt Chatbot"
    st.sidebar.title("Cài đặt Chatbot")
    
    # Tạo dropdown (selectbox) để người dùng chọn provider
    st.sidebar.selectbox(
        # Label hiển thị phía trên dropdown
        label="Chọn nhà cung cấp mô hình",
        # Danh sách các options: GROQ và OLLAMA
        options=[
            Provider.GROQ.value,
            Provider.OLLAMA.value
        ],
        # Index được chọn mặc định (0 = option đầu tiên)
        index=0,
        # Key để lưu giá trị vào session_state
        key="selected_provider"
    )

    # Lấy danh sách models tương ứng với provider đã chọn
    # Nếu provider không có trong dictionary, trả về list rỗng []
    available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    
    # Tạo dropdown để chọn model, danh sách này phụ thuộc vào provider đã chọn
    st.sidebar.selectbox(
        label="Chọn mô hình",
        options=available_models,  # Danh sách models động theo provider
        index=0,  # Chọn model đầu tiên làm mặc định
        key="selected_model"  # Lưu vào session_state["selected_model"]
    )
    
    # Tạo slider để điều chỉnh temperature (độ sáng tạo của model)
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,  # Giá trị nhỏ nhất: 0.0 (hoàn toàn deterministic)
        max_value=1.0,  # Giá trị lớn nhất: 1.0 (rất sáng tạo/ngẫu nhiên)
        value=0.25,     # Giá trị mặc định
        step=0.05,      # Bước nhảy khi kéo slider
        key="temperature"  # Lưu vào session_state["temperature"]
    )
    
    # Tạo input số để chọn số tokens tối đa cho phản hồi
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,    # Giá trị nhỏ nhất: 2048 tokens
        max_value=131072,  # Giá trị lớn nhất: 131072 tokens
        value=16384,       # Giá trị mặc định
        step=256,          # Bước nhảy khi tăng/giảm
        key="max_tokens"   # Lưu vào session_state["max_tokens"]
    )
    
    # Tạo text area để nhập system_prompt (hướng dẫn cho AI)
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System prompt)",
        height=200,  # Chiều cao của text area (pixels)
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",  # Text gợi ý
        key="system_prompt"  # Lưu vào session_state["system_prompt"]
    )
    
    # Tạo radio button để chọn chế độ quản lý ngữ cảnh (context management)
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,  # Tắt quản lý ngữ cảnh
            ContextManagementMode.SLIDING_WINDOW.value,  # Dùng sliding window
        ],
        index=1,  # Mặc định chọn SLIDING_WINDOW
        key="context_management_mode"  # Lưu vào session_state
    )
    
    # Kiểm tra nếu chế độ SLIDING_WINDOW được chọn
    # Sliding window: chỉ giữ lại N cặp user-assistant gần nhất
    if st.session_state.get("context_management_mode", ContextManagementMode.OFF.value) == ContextManagementMode.SLIDING_WINDOW.value:
        # Kiểm tra nếu biến sliding_window_turns chưa tồn tại trong session_state
        if "sliding_window_turns" not in st.session_state:
            # Khởi tạo mặc định là 5 messages
            st.session_state.sliding_window_turns = 6
        
        # Tạo input số để chọn số messages được giữ lại
        st.sidebar.number_input(
            label="Số messages (sliding window)",
            min_value=1,   # Tối thiểu 1 turn
            max_value=50,  # Tối đa 50 turns
            value=st.session_state.sliding_window_turns,  # Giá trị hiện tại
            step=1,  # Bước nhảy là 1
            key="sliding_window_turns",  # Lưu vào session_state
            # Tooltip hiển thị khi hover
            help="Số cặp user-assistant được giữ lại trong sliding window",
        )

    # Tạo toggle (nút bật/tắt) để cho phép sử dụng tools
    st.sidebar.toggle(
        label="Cho phép sử dụng công cụ",
        value=True,  # Mặc định là tắt (False)
        key="enable_tools",  # Lưu vào session_state["enable_tools"]
        # Callback function được gọi khi giá trị thay đổi
    )

    # Tạo toggle bật/tắt chuyển đổi nội dung phản hồi sang Markdown
    st.sidebar.toggle(
        label="Hiển thị phản hồi dạng Markdown",
        value=True,  # Mặc định bật (hiển thị Markdown)
        key="render_markdown",  # Lưu vào session_state["render_markdown"]
        help="Bật: hiển thị Markdown có định dạng. Tắt: hiển thị văn bản thuần (plain text)",
    )

    # ================================================================
    # KNOWLEDGE BASE (RAG) SECTION
    # ================================================================
    # Knowledge Base: nơi lưu trữ tài liệu đã upload để RAG có thể tìm kiếm
    
    # Tạo đường kẻ ngang phân cách các section trong sidebar
    st.sidebar.divider()
    
    # Tạo subheader cho section Knowledge Base với icon 📚
    st.sidebar.subheader("📚 Knowledge Base")

    # Lấy RAG instance từ session_state (đã được khởi tạo trong app.py)
    rag = st.session_state.get("rag")
    
    # Kiểm tra nếu rag tồn tại (không phải None)
    if rag:
        # Gọi method doc_count() để lấy số lượng chunks trong knowledge base
        chunk_count = rag.doc_count()

        # Nếu có chunks (> 0), hiển thị thông tin số lượng (dùng .format thay f-string)
        if chunk_count > 0:
            st.sidebar.info(f"📄 {chunk_count} chunks trong Knowledge Base")
        else:
            # Nếu không có chunks, hiển thị message "đang trống"
            st.sidebar.caption("Knowledge base đang trống")

    # Tạo file uploader cho phép người dùng upload nhiều file cùng lúc
    uploaded_files = st.sidebar.file_uploader(
        label="Upload tài liệu",
        # Các loại file được chấp nhận
        type=["txt", "md", "pdf", "docx", "pptx", "xlsx", "html"],
        accept_multiple_files=True,  # Cho phép chọn nhiều file
        # Tooltip hướng dẫn
        help="Hỗ trợ: TXT, MD, PDF, DOCX, PPTX, XLSX, HTML",
        key="rag_file_uploader",  # Key cho session_state
    )

    # Tạo button để thêm tài liệu vào knowledge base
    if st.sidebar.button("📥 Thêm tài liệu vào KB", use_container_width=True):
        # Kiểm tra nếu không có file nào được chọn
        if not uploaded_files:
            st.sidebar.warning("Vui lòng chọn file trước!")
        # Kiểm tra nếu RAG instance chưa được khởi tạo
        elif not rag:
            st.sidebar.error("RAG chưa được khởi tạo!")
        # Nếu mọi thứ đã sẵn sàng, tiến hành xử lý
        else:
            try:
                # Hiển thị spinner trong khi đang xử lý
                with st.spinner("Đang xử lý tài liệu..."):
                    # Gọi method add_documents() để xử lý và lưu tài liệu
                    num_chunks = rag.add_documents(uploaded_files)

                # Hiển thị message thành công với số chunks đã thêm
                st.sidebar.success(f"✅ Đã thêm {num_chunks} chunks!")
                # Ghi log thông tin
                global_logger.info(f"Added {num_chunks} chunks to knowledge base")
            except Exception as e:
                # Hiển thị lỗi cho người dùng (dùng .format)
                st.sidebar.error(f"❌ Lỗi: {str(e)}")
                # Ghi log lỗi
                global_logger.error(f"Error adding documents: {str(e)}")

    # Danh sách file + xóa riêng lẻ
    # Hiển thị tất cả nguồn tài liệu đã upload và cho phép xóa từng file
    
    # Kiểm tra nếu rag tồn tại và có ít nhất 1 chunk
    if rag and rag.doc_count() > 0:
        # Gọi method list_sources() để lấy danh sách các file đã upload
        # Trả về list của dict: [{"source": "file.pdf", "chunk_count": 10}, ...]
        sources = rag.list_sources()
        
        # Kiểm tra nếu có sources
        if sources:
            # Tạo expander (collapsible section) để hiển thị danh sách files
            # Hiển thị expander danh sách files đã upload
            with st.sidebar.expander(f"📁 Tài liệu ({len(sources)}) file", expanded=False):
                # Lặp qua từng item trong danh sách sources
                for item in sources:
                    # Tạo 2 columns với tỉ lệ 3:1 (cột 1 rộng hơn cột 2)
                    col1, col2 = st.columns([3, 1])

                    # Cột 1: Hiển thị thông tin file
                    with col1:
                        # Hiển thị tên file và số chunk
                        st.caption(f"📄 {item.get('source', '')} ({item.get('chunk_count', 0)} chunks)")

                    # Cột 2: Nút xóa file
                    with col2:
                        # Tạo button xóa với icon 🗑️; key và help dùng f-strings
                        key_name = f"del_{item.get('source', '')}"
                        help_text = f"Xóa {item.get('source', '')}"
                        if st.button("🗑️", key=key_name, help=help_text):
                            # Xóa file khỏi knowledge base
                            deleted = rag.delete_source(item.get("source"))
                            # Hiển thị message thành công
                            st.success(f"✅ Đã xóa {deleted} chunks!")
                            # Ghi log
                            global_logger.info(f"Deleted source: {item.get('source')} ({deleted} chunks)")
                            # Rerun app để cập nhật UI
                            st.rerun()

        # Nút xóa toàn bộ: xóa tất cả chunks khỏi knowledge base
    if st.sidebar.button("🗑️ Xóa toàn bộ Knowledge Base", use_container_width=True):
            # Gọi method clear() để xóa toàn bộ knowledge base
            rag.clear()
            # Hiển thị message thành công
            st.sidebar.success("✅ Đã xóa toàn bộ Knowledge Base!")
            # Ghi log
            global_logger.info("Knowledge base cleared by user")
            # Rerun app để cập nhật UI
            st.rerun()

    # Tạo đường kẻ ngang phân cách
    st.sidebar.divider()

    # Tạo button "Cập nhật cài đặt"
    if st.sidebar.button("Cập nhật cài đặt"):
        # Nút cập nhật: log cấu hình mới và xóa lịch sử chat để áp dụng cài đặt
        settings_msg = f"Settings updated: Selected provider: {st.session_state.get('selected_provider')}, model: {st.session_state.get('selected_model')}, Temperature: {st.session_state.get('temperature')}, Max tokens: {st.session_state.get('max_tokens')}, Context Management Mode: {str(ContextManagementMode(st.session_state.get('context_management_mode')))}, Tools enabled: {st.session_state.get('enable_tools')}"
        # Ghi log cấu hình
        global_logger.info(settings_msg)
        # Xóa lịch sử chat để áp dụng cài đặt mới
        st.session_state.chat_history = []
        # Hiển thị message thành công
        st.sidebar.success("Đã cập nhật cấu hình! Lịch sử chat đã được xóa.")
