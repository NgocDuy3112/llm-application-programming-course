"""
Module 5 - UI Layer: Chat Interface Component

File này chứa giao diện chat chính của ứng dụng, bao gồm:
1. Hiển thị lịch sử tin nhắn
2. Input cho người dùng nhập tin nhắn mới
3. Xử lý gửi tin nhắn và hiển thị phản hồi

Kiến trúc UI:
┌─────────────────────────────────────┐
│          Header: Chatbot            │
├─────────────────────────────────────┤
│  [User Message]                     │
│  [Assistant Message]                │
│  [User Message]                     │
│  [Assistant Message]                │
│  ...                                │
├─────────────────────────────────────┤
│  [Chat Input Box]                   │
└─────────────────────────────────────┘

Session State:
- chat_history: List[Dict] - Lịch sử tin nhắn
  Format: [{"role": "user"|"assistant", "message": "..."}]
"""

# =============================================================================
# IMPORTS - KHAI BÁO THƯ VIỆN
# =============================================================================
import streamlit as st  # Thư viện Streamlit để xây dựng giao diện web


# =============================================================================
# FUNCTIONS - HÀM
# =============================================================================
def render_chat_interface(engine: object):
    """
    Render giao diện chat chính.

    Giao diện bao gồm:
    1. Header với tiêu đề
    2. Lịch sử tin nhắn (scrollable)
    3. Input box để nhập tin nhắn mới

    Quy trình xử lý tin nhắn:
    1. Người dùng nhập tin nhắn và nhấn Enter
    2. Tin nhắn được hiển thị ngay lập tức
    3. Lưu tin nhắn vào chat_history
    4. Gọi engine để lấy phản hồi
    5. Hiển thị phản hồi từ assistant
    6. Lưu phản hồi vào chat_history

    Args:
        engine: ChatbotEngine hoặc FakeChatbotEngine
               Phải có method response(model, input, temperature, max_tokens)

    Session State được sử dụng:
    - chat_history: List[Dict] - Lịch sử tin nhắn
    - temperature: float - Từ sidebar
    - max_tokens: int - Từ sidebar

    Error Handling:
    - Bắt tất cả exceptions và hiển thị thông báo lỗi
    - Không crash ứng dụng khi có lỗi API
    """
    # Header của giao diện chat
    # st.header(): tạo tiêu đề cấp 1 cho phần giao diện
    st.header("Xây dựng chatbot cơ bản")

    # ==========================================================================
    # HIỂN THỊ LỊCH SỬ TIN NHẮN
    # ==========================================================================
    # Duyệt qua tất cả tin nhắn trong lịch sử và hiển thị
    # Sử dụng setdefault để khởi tạo chat_history nếu chưa có
    # st.session_state.setdefault(key, default): đảm bảo key tồn tại trong session_state
    # Nếu chưa có, khởi tạo với giá trị default (list rỗng)
    st.session_state.setdefault("chat_history", [])  # đảm bảo key tồn tại
    
    # Duyệt qua từng entry trong lịch sử chat
    # entry là dict với keys: "role" (user/assistant) và "message" (nội dung)
    for entry in st.session_state["chat_history"]:
        # st.chat_message(role): tạo container cho tin nhắn với avatar tương ứng
        # .write(content): hiển thị nội dung tin nhắn
        st.chat_message(entry["role"]).write(entry["message"])

    # ==========================================================================
    # INPUT BOX CHO NGƯỜI DÙNG
    # ==========================================================================
    # st.chat_input(): tạo input box ở cuối trang với placeholder text
    # Trả về None nếu người dùng chưa gửi tin nhắn
    # Trả về string nếu người dùng đã nhập và nhấn Enter
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...")

    # ==========================================================================
    # XỬ LÝ TIN NHẮN MỚI
    # ==========================================================================
    # Kiểm tra nếu có input từ người dùng (không None và không rỗng)
    if user_input:
        # -------------------------------------------------------------------------
        # Bước 1: Hiển thị tin nhắn của người dùng
        # -------------------------------------------------------------------------
        # st.chat_message("user"): tạo container với avatar user
        # with: context manager để hiển thị nội dung trong container
        with st.chat_message("user"):
            # st.markdown(): hiển thị text với hỗ trợ Markdown formatting
            st.markdown(user_input)

        # Lưu tin nhắn vào lịch sử
        # append(): thêm phần tử mới vào cuối list
        # Dict chứa role "user" và message là nội dung đã nhập
        st.session_state["chat_history"].append({"role": "user", "message": user_input})

        # -------------------------------------------------------------------------
        # Bước 2: Gọi API và hiển thị phản hồi
        # -------------------------------------------------------------------------
        # st.chat_message("assistant"): tạo container với avatar assistant
        with st.chat_message("assistant"):
            # Hiển thị spinner trong khi chờ phản hồi
            # st.spinner(): hiển thị animation loading với message
            with st.spinner("Đang suy nghĩ..."):
                try:
                    # Gọi engine để lấy phản hồi từ AI
                    # engine.response(): method tạo phản hồi từ engine
                    # Các tham số:
                    # - model: "openai/gpt-oss-20b" là model miễn phí trên Groq
                    # - input: tin nhắn người dùng đã nhập
                    # - temperature: lấy từ session_state (do sidebar set)
                    # - max_tokens: lấy từ session_state (do sidebar set)
                    assistant_reply = engine.response(
                        model="openai/gpt-oss-20b",
                        input=user_input,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens,
                    )

                    # Hiển thị phản hồi
                    # st.markdown(): hiển thị text với hỗ trợ Markdown
                    st.markdown(assistant_reply)

                    # Lưu phản hồi vào lịch sử
                    # append(): thêm phần tử mới vào cuối list
                    # Dict chứa role "assistant" và message là nội dung phản hồi
                    st.session_state["chat_history"].append({"role": "assistant", "message": assistant_reply})

                except Exception as e:
                    # Xử lý lỗi: hiển thị thông báo nhưng không crash app
                    # Exception: bắt tất cả các loại lỗi
                    # st.error(): hiển thị thông báo lỗi với background đỏ
                    st.error(f"Lỗi rồi: {e}")
