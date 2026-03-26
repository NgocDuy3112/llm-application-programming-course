# Module 5
# Import thư viện streamlit để xây dựng giao diện web
import streamlit as st


def render_sidebar():
    """
    Render thanh sidebar với các cài đặt chatbot.
    
    Sidebar chứa:
    1. Temperature slider - Điều chỉnh độ sáng tạo
    2. Max Output Tokens input - Giới hạn độ dài phản hồi
    3. System Prompt text area - Định hướng hành vi AI
    4. Context Management radio - Chọn chế độ quản lý ngữ cảnh
    5. Nút cập nhật và hiển thị cấu hình hiện tại
    
    Session State được sử dụng:
    - st.session_state.temperature: float (0.0 - 1.0)
    - st.session_state.max_tokens: int (2048 - 131072)
    - st.session_state.system_prompt: str
    - st.session_state.context_management_mode: str
    """
    # Tiêu đề sidebar
    # st.sidebar.title(): tạo tiêu đề cho thanh sidebar bên trái
    st.sidebar.title("Cài đặt Chatbot")
    
    # Temperature slider - Điều chỉnh độ sáng tạo
    # Temperature kiểm soát độ "sáng tạo" của phản hồi:
    # - 0.0: Phản hồi xác định nhất, ít biến thiên
    # - 1.0: Phản hồi sáng tạo nhất, nhiều biến thiên
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",  # Nhãn hiển thị cho slider
        min_value=0.0,  # Giá trị nhỏ nhất có thể chọn
        max_value=1.0,  # Giá trị lớn nhất có thể chọn
        value=0.25,  # Giá trị mặc định khi khởi tạo
        step=0.05,  # Bước nhảy khi tăng/giảm (0.05, 0.10, 0.15, ...)
        key="temperature"  # Key để lưu giá trị vào session_state
    )
    
    # Max Output Tokens input - Giới hạn độ dài phản hồi
    # Giới hạn số token trong phản hồi:
    # - Token là đơn vị cơ bản của text (khoảng 4 ký tự tiếng Anh)
    # - Giá trị cao hơn cho phép phản hồi dài hơn nhưng tốn nhiều token hơn
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",  # Nhãn hiển thị
        min_value=2048,  # Giá trị nhỏ nhất có thể nhập
        max_value=131072,  # Giá trị lớn nhất có thể nhập
        value=65536,  # Giá trị mặc định khi khởi tạo
        step=256,  # Bước nhảy khi tăng/giảm bằng nút mũi tên
        key="max_tokens"  # Key để lưu giá trị vào session_state
    )
    
    # System Prompt text area - Định hướng hành vi AI
    # System prompt định hướng hành vi của AI:
    # - Được gửi đầu tiên trong danh sách messages
    # - Không hiển thị cho người dùng
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Prompt)",  # Nhãn hiển thị
        height=200,  # Chiều cao của text area (pixels)
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",  # Text hiển thị khi chưa nhập
        key="system_prompt"  # Key để lưu giá trị vào session_state
    )
    
    # Context Management Mode radio - Chọn chế độ quản lý ngữ cảnh
    # Chế độ quản lý ngữ cảnh hội thoại:
    # - Tắt: Không quản lý, gửi toàn bộ lịch sử
    # - Cửa sổ trượt: Giữ N tin nhắn gần nhất
    # - Tóm tắt: Tóm tắt lịch sử khi quá dài
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",  # Nhãn hiển thị
        options=[  # Danh sách các lựa chọn
            "Tắt",  # Tắt quản lý ngữ cảnh
            "Cửa sổ trượt (sliding window)",  # Sử dụng cửa sổ trượt
            "Tóm tắt (summarization)"  # Tóm tắt lịch sử
        ],
        index=0,  # Index của lựa chọn mặc định (0 = "Tắt")
        key="context_management_mode"  # Key để lưu giá trị vào session_state
    )
    
    # Nút cập nhật cài đặt
    # st.sidebar.button(): tạo nút bấm trong sidebar
    # Trả về True khi nút được nhấn
    if st.sidebar.button("Cập nhật cài đặt"):
        # st.sidebar.success(): hiển thị thông báo thành công với background xanh lá
        st.sidebar.success("Đã cập nhật cấu hình!")
        
        # Expander hiển thị chi tiết cấu hình
        # st.sidebar.expander(): tạo collapsible section trong sidebar
        # expanded=True: mở rộng mặc định
        with st.sidebar.expander("Xem chi tiết cấu hình", expanded=True):
            # Hiển thị các giá trị cấu hình hiện tại từ session_state
            # st.markdown(): hiển thị text với hỗ trợ Markdown
            # st.session_state.<key>: truy cập giá trị từ session_state
            st.markdown(f"**Độ sáng tạo (Temperature):** {st.session_state.temperature}")
            st.markdown(f"**Số lượng token tối đa (Max Output Tokens):** {st.session_state.max_tokens}")
            st.markdown(f"**Câu lệnh hệ thống (System Prompt):** {st.session_state.system_prompt}")
            st.markdown(f"**Chế độ quản lý ngữ cảnh (Context Management Mode):** {st.session_state.context_management_mode}")
