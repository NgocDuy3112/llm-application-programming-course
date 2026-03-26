# Module 5
# Import thư viện os để làm việc với hệ điều hành và biến môi trường
import os
# Import thư viện sys để làm việc với hệ thống, đặc biệt là sys.path
import sys
# Import thư viện streamlit để xây dựng giao diện web
import streamlit as st
# Import hàm load_dotenv từ thư viện dotenv để load biến môi trường từ file .env
from dotenv import load_dotenv

# Thêm thư mục hiện tại vào sys.path để có thể import các module con
# os.path.abspath(__file__): lấy đường dẫn tuyệt đối của file hiện tại
# os.path.dirname(...): lấy thư mục chứa file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import hàm render_sidebar từ module ui/sidebar.py
from ui.sidebar import render_sidebar
# Import hàm render_chat_interface từ module ui/chat_interface.py
from ui.chat_interface import render_chat_interface
# Import class ChatbotEngine từ module orchestrator/engine.py
from orchestrator.engine import ChatbotEngine


# Load biến môi trường từ file .env
# override=True cho phép ghi đè biến môi trường đã tồn tại
load_dotenv(override=True)



def main():
    """
    Hàm chính của ứng dụng Streamlit cho bài tập Module 5.
    
    Quy trình:
    1. Cấu hình trang với tiêu đề và layout rộng
    2. Khởi tạo ChatbotEngine để kết nối API
    3. Khởi tạo lịch sử chat trong session_state
    4. Render sidebar và giao diện chat
    """
    # Cấu hình trang Streamlit với tiêu đề và layout
    # page_title="Bài tập Module 5": tiêu đề hiển thị trên tab trình duyệt
    # layout="wide": sử dụng toàn bộ chiều ngang màn hình
    st.set_page_config(page_title="Bài tập Module 5", layout="wide")
    
    # Khởi tạo engine
    # ChatbotEngine(): tạo instance của engine kết nối API thật
    # Engine này sẽ gọi Groq API để tạo phản hồi
    engine = ChatbotEngine()

    # Khởi tạo lịch sử chat trong session_state
    # Kiểm tra key "chat_history" có tồn tại chưa
    # Nếu chưa tồn tại, khởi tạo list rỗng
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render các thành phần UI
    # render_sidebar(): hiển thị thanh sidebar bên trái với các cài đặt
    render_sidebar()
    # render_chat_interface(engine=engine): hiển thị giao diện chat chính
    render_chat_interface(engine=engine)


# Kiểm tra xem file có được chạy trực tiếp không
# Nếu đúng, gọi hàm main() để khởi động ứng dụng
if __name__ == "__main__":
    main()
