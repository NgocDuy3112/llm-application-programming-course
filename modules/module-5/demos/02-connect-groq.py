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
# IMPORTS - KHAI BÁO THƯ VIỆN
# =============================================================================
import os  # Thư viện làm việc với hệ điều hành, biến môi trường
import sys  # Thư viện làm việc với hệ thống, đặc biệt là sys.path

import streamlit as st  # Thư viện Streamlit để xây dựng giao diện web


# Thêm thư mục cha vào sys.path để import các module con
# os.path.abspath(__file__): lấy đường dẫn tuyệt đối của file hiện tại
# os.path.dirname(...): lấy thư mục chứa file
# os.path.dirname(os.path.dirname(...)): lấy thư mục cha (module-5)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# IMPORTS INTERNAL MODULES - IMPORT CÁC MODULE NỘI BỘ
# =============================================================================
from ui.sidebar import render_sidebar  # Import hàm render sidebar từ module ui/sidebar.py
from ui.chat_interface import render_chat_interface  # Import hàm render giao diện chat từ module ui/chat_interface.py
from orchestrator.engine import ChatbotEngine  # Import engine thật kết nối API từ module orchestrator/engine.py


# =============================================================================
# RESOURCE CACHING - BỘ NHỚ ĐỆM TÀI NGUYÊN
# =============================================================================
@st.cache_resource()  # Decorator của Streamlit để cache resource ở mức toàn ứng dụng
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
    # Tạo và trả về instance mới của ChatbotEngine
    # Engine này sẽ được cache và tái sử dụng cho các lần gọi sau
    return ChatbotEngine()


# =============================================================================
# MAIN APPLICATION - ỨNG DỤNG CHÍNH
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
    # Lần đầu gọi: tạo mới engine và cache
    # Các lần sau: trả về engine đã cache, không tạo mới
    engine = get_chatbot_engine()

    # Khởi tạo lịch sử chat trong session_state
    # Session state được Streamlit quản lý và tồn tại suốt phiên làm việc
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