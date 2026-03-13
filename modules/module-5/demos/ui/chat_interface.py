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
# IMPORTS
# =============================================================================
import streamlit as st


# =============================================================================
# FUNCTIONS
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
               Phải có method response(model, input, temperature, max_output_tokens)
    
    Session State được sử dụng:
    - chat_history: List[Dict] - Lịch sử tin nhắn
    - temperature: float - Từ sidebar
    - max_output_tokens: int - Từ sidebar
    
    Error Handling:
    - Bắt tất cả exceptions và hiển thị thông báo lỗi
    - Không crash ứng dụng khi có lỗi API
    """
    # Header của giao diện chat
    st.header("Xây dựng chatbot cơ bản")
    
    # ==========================================================================
    # HIỂN THỊ LỊCH SỬ TIN NHẮN
    # ==========================================================================
    # Duyệt qua tất cả tin nhắn trong lịch sử và hiển thị
    # st.chat_message tạo một container với avatar tương ứng
    for entry in st.session_state.chat_history:
        # entry["role"] = "user" hoặc "assistant"
        # entry["message"] = nội dung tin nhắn
        st.chat_message(entry["role"]).write(entry["message"])
    
    # ==========================================================================
    # INPUT BOX CHO NGƯỜI DÙNG
    # ==========================================================================
    # st.chat_input tạo input box ở cuối trang
    # Trả về None nếu người dùng chưa gửi tin nhắn
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...")
    
    # ==========================================================================
    # XỬ LÝ TIN NHẮN MỚI
    # ==========================================================================
    if user_input:
        # -------------------------------------------------------------------------
        # Bước 1: Hiển thị tin nhắn của người dùng
        # -------------------------------------------------------------------------
        # st.chat_message("user") tạo container với avatar user
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Lưu tin nhắn vào lịch sử
        st.session_state.chat_history.append({
            "role": "user", 
            "message": user_input
        })
        
        # -------------------------------------------------------------------------
        # Bước 2: Gọi API và hiển thị phản hồi
        # -------------------------------------------------------------------------
        # st.chat_message("assistant") tạo container với avatar assistant
        with st.chat_message("assistant"):
            # Hiển thị spinner trong khi chờ phản hồi
            with st.spinner("Đang suy nghĩ..."):
                try:
                    # Gọi engine để lấy phản hồi từ AI
                    # Model "openai/gpt-oss-20b" là model miễn phí trên Groq
                    assistant_reply = engine.response(
                        model="openai/gpt-oss-20b", 
                        input=user_input,
                        temperature=st.session_state.temperature,
                        max_output_tokens=st.session_state.max_output_tokens,
                    )
                    
                    # Hiển thị phản hồi
                    st.markdown(assistant_reply)
                    
                    # Lưu phản hồi vào lịch sử
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "message": assistant_reply
                    })
                    
                except Exception as e:
                    # Xử lý lỗi: hiển thị thông báo nhưng không crash app
                    st.error(f"Lỗi rồi: {e}")