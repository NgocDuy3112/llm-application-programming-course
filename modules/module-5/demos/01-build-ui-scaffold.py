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
# IMPORTS - KHAI BÁO THƯ VIỆN
# =============================================================================
import os  # Thư viện làm việc với hệ điều hành, biến môi trường
import sys  # Thư viện làm việc với hệ thống, đặc biệt là sys.path

from dotenv import load_dotenv  # Hàm load biến môi trường từ file .env
import streamlit as st  # Thư viện Streamlit để xây dựng giao diện web


# Thêm thư mục cha vào sys.path để có thể import các module con
# Điều này cần thiết vì Streamlit chạy từ thư mục gốc của project
# os.path.abspath(__file__): lấy đường dẫn tuyệt đối của file hiện tại
# os.path.dirname(...): lấy thư mục chứa file
# os.path.dirname(os.path.dirname(...)): lấy thư mục cha (module-5)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# IMPORTS INTERNAL MODULES - IMPORT CÁC MODULE NỘI BỘ
# =============================================================================
from ui.sidebar import render_sidebar  # Import hàm render sidebar từ module ui/sidebar.py
from ui.chat_interface import render_chat_interface  # Import hàm render giao diện chat từ module ui/chat_interface.py
from orchestrator.engine import FakeChatbotEngine  # Import engine giả để test UI từ module orchestrator/engine.py


# =============================================================================
# CONFIGURATION - CẤU HÌNH
# =============================================================================
# Load biến môi trường từ file .env
# override=True cho phép ghi đè biến môi trường đã tồn tại
# dotenv_path=".env": chỉ định đường dẫn file .env trong thư mục hiện tại
load_dotenv(dotenv_path=".env", override=True)


# =============================================================================
# MAIN APPLICATION - ỨNG DỤNG CHÍNH
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
    # Cấu hình layout của trang Streamlit
    # layout="wide": sử dụng toàn bộ chiều ngang của màn hình
    st.set_page_config(layout="wide")
    
    # Khởi tạo engine - sử dụng FakeChatbotEngine để test UI
    # Sau này sẽ thay bằng ChatbotEngine thật khi kết nối API
    # FakeChatbotEngine trả về phản hồi giả, không gọi API thật
    engine = FakeChatbotEngine()

    # Khởi tạo lịch sử chat nếu chưa tồn tại
    # st.session_state được Streamlit quản lý và tồn tại suốt phiên làm việc
    # Kiểm tra key "chat_history" có tồn tại chưa, nếu chưa thì khởi tạo list rỗng
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render các thành phần giao diện
    # render_sidebar(): hiển thị thanh sidebar bên trái với các cài đặt
    render_sidebar()
    # render_chat_interface(engine=engine): hiển thị giao diện chat chính với engine đã khởi tạo
    render_chat_interface(engine=engine)


# =============================================================================
# ENTRY POINT - ĐIỂM NHẬP
# =============================================================================
# Kiểm tra xem file có được chạy trực tiếp không (không phải import từ file khác)
# Nếu đúng, gọi hàm main() để khởi động ứng dụng
if __name__ == "__main__":
    main()