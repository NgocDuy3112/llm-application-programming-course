# Module 5
# Import thư viện streamlit để xây dựng giao diện web
import streamlit as st



def render_chat_interface(engine: object):
    """
    Render giao diện chat chính.
    
    Giao diện bao gồm:
    1. Header với tiêu đề
    2. Lịch sử tin nhắn (scrollable)
    3. Input box để nhập tin nhắn mới
    
    Args:
        engine: ChatbotEngine hoặc FakeChatbotEngine
               Phải có method response(model, input, temperature, max_tokens)
    
    Session State được sử dụng:
    - chat_history: List[Dict] - Lịch sử tin nhắn
    - temperature: float - Từ sidebar
    - max_tokens: int - Từ sidebar
    """
    # Header của giao diện chat
    # st.header(): tạo tiêu đề cấp 1 cho phần giao diện
    st.header("Xây dựng chatbot cơ bản")
    
    # Duyệt qua tất cả tin nhắn trong lịch sử và hiển thị
    # st.session_state.chat_history: list chứa các tin nhắn đã lưu
    for entry in st.session_state.chat_history:
        # st.chat_message(role): tạo container cho tin nhắn với avatar tương ứng
        # entry["role"]: "user" hoặc "assistant"
        # entry["message"]: nội dung tin nhắn
        # .write(content): hiển thị nội dung tin nhắn
        st.chat_message(entry["role"]).write(entry["message"])
    
    # Input box cho người dùng
    # st.chat_input(): tạo input box ở cuối trang với placeholder text
    # Trả về None nếu người dùng chưa gửi tin nhắn
    # Trả về string nếu người dùng đã nhập và nhấn Enter
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...")
    
    # Xử lý tin nhắn mới
    # Kiểm tra nếu có input từ người dùng (không None và không rỗng)
    if user_input:
        # Hiển thị tin nhắn của người dùng
        # st.chat_message("user"): tạo container với avatar user
        with st.chat_message("user"):
            # st.markdown(): hiển thị text với hỗ trợ Markdown formatting
            st.markdown(user_input)
        
        # Lưu tin nhắn vào lịch sử
        # append(): thêm phần tử mới vào cuối list
        # Dict chứa role "user" và message là nội dung đã nhập
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        
        # Gọi API và hiển thị phản hồi
        # st.chat_message("assistant"): tạo container với avatar assistant
        with st.chat_message("assistant"):
            # Hiển thị spinner trong khi chờ phản hồi
            # st.spinner(): hiển thị animation loading với message
            with st.spinner("Đang suy nghĩ..."):
                try:
                    # Gọi engine để lấy phản hồi từ AI
                    # Các tham số lấy từ session_state (do sidebar set)
                    assistant_reply = engine.response(
                        model="openai/gpt-oss-20b",  # Model miễn phí trên Groq
                        input=user_input,  # Tin nhắn người dùng đã nhập
                        temperature=st.session_state.temperature,  # Độ sáng tạo từ sidebar
                        max_tokens=st.session_state.max_tokens,  # Số token tối đa từ sidebar
                    )
                    
                    # Hiển thị phản hồi
                    # st.markdown(): hiển thị text với hỗ trợ Markdown
                    st.markdown(assistant_reply)
                    
                    # Lưu phản hồi vào lịch sử
                    # append(): thêm phần tử mới vào cuối list
                    # Dict chứa role "assistant" và message là nội dung phản hồi
                    st.session_state.chat_history.append({"role": "assistant", "message": assistant_reply})
                    
                except Exception as e:
                    # Xử lý lỗi: hiển thị thông báo nhưng không crash app
                    # Exception: bắt tất cả các loại lỗi
                    # st.error(): hiển thị thông báo lỗi với background đỏ
                    st.error(f"Lỗi rồi: {e}")
