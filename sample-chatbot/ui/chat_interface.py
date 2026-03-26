# Khai báo module docstring - mô tả chức năng của module chat interface
"""
UI - Chat Interface Module

Mô tả: Xử lý giao diện chat của ứng dụng Streamlit, bao gồm:
- Hiển thị lịch sử chat
- Xử lý input từ người dùng
- Hiển thị tài liệu tham khảo từ RAG

Kiến trúc / Dependencies:
- streamlit: Framework cho giao diện web
- orchestrator.tools: Chứa DEFAULT_TOOLS cho function calling
- logger: Global logger để tracking
- custom_types: ToolChoice enum cho tool usage control
"""

# Import re module cho regex operations (không được sử dụng trong code hiện tại)
import re
# Import streamlit - framework để xây dựng giao diện web app
import streamlit as st

# Import DEFAULT_TOOLS từ orchestrator.tools - danh sách các tools mặc định
from orchestrator.tools import DEFAULT_TOOLS
# Import global_logger từ logger module để ghi log hoạt động
from logger import global_logger
# Import ToolChoice enum từ custom_types để điều khiển việc sử dụng tools
from custom_types import ToolChoice


# Hàm helper để hiển thị tài liệu tham khảo từ kết quả RAG retrieval
def _render_retrieved_docs(docs_str: str):
    """
    Hiển thị tài liệu tham khảo từ kết quả RAG retrieval trong expander.

    Format context string từ RAG: mỗi tài liệu được phân cách bằng "\n\n---\n\n"
    và có header chứa source file.

    Args:
        docs_str (str): Context string từ RAG retrieve, format:
            "[Tài liệu 1 — 📄 source.pdf]\ncontent...\n\n---\n\n[Tài liệu 2 — 📄 doc.docx]\ncontent..."
    """
    # Tách context string thành từng chunks dựa trên delimiter "\n\n---\n\n"
    # Kết quả trả về là list các chunk strings
    chunks = docs_str.split("\n\n---\n\n")

    # Tạo expander (collapsible section) để hiển thị tài liệu tham khảo
    # expanded=False nghĩa là mặc định sẽ đóng
    # Dùng .format thay cho f-string để tương thích với yêu cầu
    with st.expander("📚 Tài liệu tham khảo ({}) đoạn".format(len(chunks)), expanded=False):
        # Lặp qua từng chunk trong danh sách chunks
        for chunk in chunks:
            # Tách chunk thành 2 phần: header (dòng đầu) và body (phần còn lại)
            # split("\n", 1) chỉ tách tại dấu newline đầu tiên
            lines = chunk.strip().split("\n", 1)
            
            # Lấy dòng đầu tiên làm header (thông tin source file)
            header = lines[0].strip()

            # Lấy phần còn lại làm body (nội dung chunk)
            # Nếu chỉ có 1 dòng (không có newline), dùng toàn bộ chunk
            body = lines[1].strip() if len(lines) > 1 else chunk.strip()

            # Hiển thị header với format đậm (dùng .format thay f-string)
            st.markdown("**{}**".format(header))

            # Hiển thị body với custom CSS styling; đặt body vào template bằng .format
            html = ("<div style='background:#f8f9fa;border-left:3px solid #4CAF50;"
                    "padding:8px 12px;border-radius:4px;font-size:0.9em;"
                    "white-space:pre-wrap;'>{}</div>").format(body)
            st.markdown(html, unsafe_allow_html=True)
            
            # Tạo đường kẻ ngang phân cách giữa các chunks
            st.divider()


# Hàm chính render giao diện chat
def render_chat_interface(engine: object):
    """
    Render giao diện chat chính với Streamlit.

    Chức năng:
    - Hiển thị tiêu đề và lịch sử chat
    - Xử lý user input và gọi engine để tạo phản hồi
    - Hiển thị tài liệu tham khảo từ RAG (nếu có)
    - Lưu trữ lịch sử chat và retrieved docs vào session_state

    Args:
        engine (object): FullChatbotEngine instance để xử lý phản hồi
    """
    # Ghi log debug: bắt đầu render chat interface
    global_logger.debug("Rendering chat interface")
    
    # Đặt tiêu đề cho trang với text "Xây dựng chatbot cơ bản"
    st.title("Xây dựng chatbot cơ bản")
    
    # Kiểm tra nếu "chat_history" chưa tồn tại trong session_state
    if "chat_history" not in st.session_state:
        # Khởi tạo chat_history là list rỗng
        st.session_state.chat_history = []
    
    # Kiểm tra nếu "retrieved_docs_map" chưa tồn tại trong session_state
    if "retrieved_docs_map" not in st.session_state:
        # Khởi tạo retrieved_docs_map là dict rỗng
        # Map này lưu trữ retrieved docs cho từng message index
        st.session_state.retrieved_docs_map = {}

    # Tạo container để hiển thị toàn bộ lịch sử chat
    with st.container():
        # Lặp qua từng entry trong chat_history với index
        for i, entry in enumerate(st.session_state.chat_history):
            # Tạo chat message bubble với role (user/assistant)
            with st.chat_message(entry["role"]):
                # Hiển thị nội dung message
                st.markdown(entry["content"])
                
                # Kiểm tra nếu message index này có retrieved docs
                if i in st.session_state.retrieved_docs_map:
                    # Gọi hàm helper để hiển thị tài liệu tham khảo
                    _render_retrieved_docs(st.session_state.retrieved_docs_map[i])
        
        # Ghi log số messages đã hiển thị
        # Ghi log số messages đã hiển thị (dùng .format thay f-string)
        global_logger.debug("Displayed {} messages from chat history".format(len(st.session_state.get("chat_history", []))))

    # Tạo chat input field cho người dùng nhập tin nhắn
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    
    # Kiểm tra nếu người dùng đã nhập tin nhắn (không phải None)
    if user_input:
        # Ghi log user input (50 ký tự đầu tiên)
        # Ghi log user input (giới hạn 50 ký tự) - không dùng f-string
        global_logger.debug("Processing user input: {}...".format(user_input[:50]))

        # Thêm message của user vào chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Gọi engine.response() để tạo phản hồi từ chatbot
        assistant_reply = engine.response(
            # Lấy model từ session_state
            model=st.session_state.selected_model,
            # Input là tin nhắn của user
            input=user_input,
            # Lấy temperature từ session_state (độ sáng tạo)
            temperature=st.session_state.temperature,
            # Nếu enable_tools=True thì dùng DEFAULT_TOOLS, ngược lại là None
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            # Nếu enable_tools=True thì dùng ToolChoice.AUTO, ngược lại là NONE
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            # Lấy max_tokens từ session_state
            max_tokens=st.session_state.max_tokens,
            # Lấy system instruction từ session_state
            instruction=st.session_state.instruction
        )
        
        # Ghi log độ dài phản hồi
        # Ghi log độ dài phản hồi
        global_logger.debug("Assistant reply generated, length: {}".format(len(assistant_reply)))

        # Lấy retrieved docs từ session_state và xóa nó khỏi session_state
        # pop() trả về giá trị và xóa key khỏi dict
        retrieved_docs = st.session_state.pop("last_retrieved_docs", None)
        
        # Ghi log retrieved docs (hoặc None nếu không có)
        # Ghi log retrieved docs (hoặc 'None')
        global_logger.debug("Retrieved docs: {}".format(retrieved_docs if retrieved_docs else 'None'))

        # Tạo chat message bubble cho assistant
        with st.chat_message("assistant"):
            # Hiển thị phản hồi của assistant
            st.markdown(assistant_reply)
            
            # Nếu có retrieved docs, hiển thị chúng
            if retrieved_docs:
                _render_retrieved_docs(retrieved_docs)

        # Thêm phản hồi của assistant vào chat history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        # Nếu có retrieved docs, lưu vào retrieved_docs_map với key là message index
        if retrieved_docs:
            # Tính index của message vừa thêm (length - 1)
            msg_index = len(st.session_state.chat_history) - 1
            # Lưu retrieved docs vào map với key là index
            st.session_state.retrieved_docs_map[msg_index] = retrieved_docs

        # Ghi log tổng số messages trong chat history
        # Ghi log tổng số messages trong chat history
        global_logger.debug("Updated chat history, total messages: {}".format(len(st.session_state.get("chat_history", []))))
        
        # Rerun app để cập nhật UI với messages mới
        st.rerun()
