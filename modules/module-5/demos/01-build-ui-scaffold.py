"""
Module 5 - Bước 1: Xây dựng giao diện người dùng (UI Scaffold)

File này là bước đầu tiên trong việc xây dựng chatbot. Chúng ta sẽ:
1. Tạo giao diện Streamlit cơ bản
2. Thiết lập cấu trúc thư mục theo kiến trúc 3 tầng
3. Sử dụng FakeChatbotEngine để test UI mà chưa cần kết nối API thật

Kiến trúc ứng dụng:
├── ui/                    # Tầng giao diện (Presentation Layer)
│   ├── sidebar.py             # Thanh cài đặt bên trái
│   └── chat_interface.py      # Khu vực chat chính
├── orchestrator/          # Tầng điều phối (Business Logic Layer)
│   └── engine.py              # Xử lý logic gọi model
└── model/                 # Tầng dữ liệu (Data Access Layer)
    └── adapter.py             # Kết nối với API bên ngoài (Groq)
"""

# =============================================================================
# IMPORTS
# =============================================================================
import os
import sys

from dotenv import load_dotenv
import streamlit as st

# Thêm thư mục cha vào sys.path để có thể import các module con
# Điều này cần thiết vì Streamlit chạy từ thư mục gốc của project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# IMPORTS INTERNAL MODULES
# =============================================================================
from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.engine import FakeChatbotEngine


# =============================================================================
# CONFIGURATION
# =============================================================================
# Load biến môi trường từ file .env
# override=True cho phép ghi đè biến môi trường đã tồn tại
load_dotenv(dotenv_path=".env", override=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """
    Hàm chính của ứng dụng Streamlit.
    
    Quy trình khởi tạo:
    1. Tạo engine giả định (FakeChatbotEngine) để test UI
    2. Khởi tạo lịch sử chat trong session_state
    3. Render sidebar với các cài đặt
    4. Render giao diện chat chính
    
    Session State:
    - chat_history: Danh sách các tin nhắn trong cuộc hội thoại
      Format: [{"role": "user"|"assistant", "message": "..."}]
    """
    # Khởi tạo engine - sử dụng FakeChatbotEngine để test UI
    # Sau này sẽ thay bằng ChatbotEngine thật khi kết nối API
    engine = FakeChatbotEngine()
    
    # Khởi tạo lịch sử chat nếu chưa tồn tại
    # st.session_state được Streamlit quản lý và tồn tại suốt phiên làm việc
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