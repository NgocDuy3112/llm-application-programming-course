"""
Module 5 - Bước 2: Kết nối với Groq API

File này mở rộng từ bước 1 bằng cách:
1. Kết nối với Groq API thông qua OpenAI SDK
2. Sử dụng ChatbotEngine thật thay vì FakeChatbotEngine
3. Cache engine để tối ưu hiệu suất

Yêu cầu:
- File .env với biến GROQ_API_KEY
- Cài đặt openai package (pip install openai)

Lưu ý quan trọng:
- Groq sử dụng OpenAI SDK nên cần set base_url="https://api.groq.com/openai/v1"
- API key phải được bảo mật và không commit vào git
"""

# =============================================================================
# IMPORTS
# =============================================================================
import os
import sys

import streamlit as st

# Thêm thư mục cha vào sys.path để import các module con
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# IMPORTS INTERNAL MODULES
# =============================================================================
from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.engine import ChatbotEngine


# =============================================================================
# RESOURCE CACHING
# =============================================================================
@st.cache_resource()
def get_chatbot_engine():
    """
    Tạo và cache ChatbotEngine để tái sử dụng trong suốt phiên làm việc.
    
    @st.cache_resource():
    - Cache resource ở mức toàn bộ ứng dụng (không phải mỗi user session)
    - Chỉ tạo một instance duy nhất, tái sử dụng cho tất cả users
    - Phù hợp cho các đối tượng tốn tài nguyên để khởi tạo (như API clients)
    
    Returns:
        ChatbotEngine: Instance của chatbot engine đã được khởi tạo
    """
    return ChatbotEngine()


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """
    Hàm chính của ứng dụng Streamlit với kết nối API thật.
    
    Quy trình:
    1. Lấy engine từ cache (hoặc tạo mới nếu chưa có)
    2. Khởi tạo session state cho lịch sử chat
    3. Render giao diện người dùng
    
    Lưu ý về hiệu suất:
    - Engine được cache nên không cần khởi tạo lại mỗi lần rerun
    - Kết nối API được duy trì và tái sử dụng
    """
    # Lấy engine từ cache - chỉ khởi tạo một lần duy nhất
    engine = get_chatbot_engine()
    
    # Khởi tạo lịch sử chat trong session_state
    # Session state được Streamlit quản lý và tồn tại suốt phiên làm việc
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Render các thành phần giao diện
    render_sidebar()
    render_chat_interface(engine=engine)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()