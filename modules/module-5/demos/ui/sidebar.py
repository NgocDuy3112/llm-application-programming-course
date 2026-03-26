"""
Module 5 - UI Layer: Sidebar Component

File này chứa các thành phần giao diện sidebar cho phép người dùng
cấu hình các tham số của chatbot.

Các tham số có thể điều chỉnh:
1. Temperature: Độ sáng tạo của phản hồi (0.0 - 1.0)
2. Max Output Tokens: Độ dài tối đa của phản hồi
3. System Prompt: Câu lệnh hệ thống định hướng hành vi AI
4. Context Management Mode: Chế độ quản lý ngữ cảnh hội thoại

Session State Keys:
- temperature: Giá trị temperature hiện tại
- max_tokens: Giá trị max tokens hiện tại
- system_prompt: System prompt hiện tại
- context_management_mode: Chế độ quản lý ngữ cảnh
"""

# =============================================================================
# IMPORTS - KHAI BÁO THƯ VIỆN
# =============================================================================
import streamlit as st  # Thư viện Streamlit để xây dựng giao diện web


# =============================================================================
# FUNCTIONS - HÀM
# =============================================================================
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

    Lưu ý:
    - Các giá trị được lưu tự động vào session_state thông qua key parameter
    - Giá trị mặc định được set qua value parameter
    """
    # Tiêu đề sidebar
    # st.sidebar.title(): tạo tiêu đề cho thanh sidebar bên trái
    st.sidebar.title("Cài đặt Chatbot")

    # ==========================================================================
    # TEMPERATURE SLIDER - THANH TRƯỢT ĐỘ SÁNG TẠO
    # ==========================================================================
    # Temperature kiểm soát độ "sáng tạo" của phản hồi:
    # - 0.0: Phản hồi xác định nhất, ít biến thiên
    # - 1.0: Phản hồi sáng tạo nhất, nhiều biến thiên
    # Giá trị mặc định 0.25 phù hợp cho các tác vụ cần tính chính xác cao
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",  # Nhãn hiển thị cho slider
        min_value=0.0,  # Giá trị nhỏ nhất có thể chọn
        max_value=1.0,  # Giá trị lớn nhất có thể chọn
        value=0.25,  # Giá trị mặc định khi khởi tạo
        step=0.05,  # Bước nhảy khi tăng/giảm (0.05, 0.10, 0.15, ...)
        help="Giá trị cao hơn sẽ làm cho phản hồi của mô hình sáng tạo hơn, trong khi giá trị thấp hơn sẽ làm cho phản hồi an toàn và tập trung hơn",  # Tooltip khi hover
        key="temperature"  # Key để lưu giá trị vào session_state
    )

    # ==========================================================================
    # MAX OUTPUT TOKENS INPUT - ĐẦU VÀO SỐ TOKEN TỐI ĐA
    # ==========================================================================
    # Giới hạn số token trong phản hồi:
    # - Token là đơn vị cơ bản của text (khoảng 4 ký tự tiếng Anh)
    # - Giá trị cao hơn cho phép phản hồi dài hơn nhưng tốn nhiều token hơn
    # - Giới hạn: 2048 - 131072 (tùy model)
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",  # Nhãn hiển thị
        min_value=2048,  # Giá trị nhỏ nhất có thể nhập
        max_value=131072,  # Giá trị lớn nhất có thể nhập
        value=65536,  # Giá trị mặc định khi khởi tạo
        step=256,  # Bước nhảy khi tăng/giảm bằng nút mũi tên
        help="Giới hạn số token trong phản hồi của mô hình, bao gồm cả token suy luận nếu có",  # Tooltip khi hover
        key="max_tokens"  # Key để lưu giá trị vào session_state
    )

    # ==========================================================================
    # SYSTEM PROMPT TEXT AREA - VÙNG NHẬP CÂU LỆNH HỆ THỐNG
    # ==========================================================================
    # System prompt định hướng hành vi của AI:
    # - Được gửi đầu tiên trong danh sách messages
    # - Không hiển thị cho người dùng
    # - Có thể dùng để: định vai trò, giới hạn chủ đề, định dạng output
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Prompt)",  # Nhãn hiển thị
        height=200,  # Chiều cao của text area (pixels)
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",  # Text hiển thị khi chưa nhập
        key="system_prompt",  # Key để lưu giá trị vào session_state
        help="Câu lệnh hệ thống là một phần của prompt được gửi đến mô hình để hướng dẫn cách thức phản hồi. Bạn có thể sử dụng nó để thiết lập bối cảnh, vai trò của chatbot, hoặc bất kỳ hướng dẫn đặc biệt nào mà bạn muốn mô hình tuân theo khi tạo phản hồi."  # Tooltip khi hover
    )

    # ==========================================================================
    # CONTEXT MANAGEMENT MODE RADIO - CHỌN CHẾ ĐỘ QUẢN LÝ NGỮ CẢNH
    # ==========================================================================
    # Chế độ quản lý ngữ cảnh hội thoại:
    # - Tắt: Không quản lý, gửi toàn bộ lịch sử
    # - Cửa sổ trượt: Giữ N tin nhắn gần nhất
    # - Tóm tắt: Tóm tắt lịch sử khi quá dài
    # (Sẽ được triển khai chi tiết trong các module sau)
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",  # Nhãn hiển thị
        options=[  # Danh sách các lựa chọn
            "Tắt",  # Tắt quản lý ngữ cảnh
            "Cửa sổ trượt (sliding window)",  # Sử dụng cửa sổ trượt
        ],
        index=0,  # Index của lựa chọn mặc định (0 = "Tắt")
        key="context_management_mode",  # Key để lưu giá trị vào session_state
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại để tạo phản hồi. 'Tắt' sẽ không sử dụng lịch sử nào, 'Cửa sổ trượt' sẽ chỉ sử dụng một số lượng tin nhắn gần đây nhất dựa trên kích thước cửa sổ đã định."  # Tooltip khi hover
    )
    
    # Toggle để bật/tắt tính năng sử dụng công cụ
    st.sidebar.toggle(
        label="Sử dụng công cụ",  # Nhãn hiển thị
        value=False,  # Giá trị mặc định (False = tắt)
        key="enable_tools",  # Key để lưu giá trị vào session_state
        help="Bật nếu bạn muốn cho phép chatbot sử dụng các công cụ đã tích hợp (ví dụ: truy vấn cơ sở dữ liệu, gọi API, v.v.) để trả lời câu hỏi của người dùng. Nếu tắt, chatbot sẽ chỉ dựa vào kiến thức đã được huấn luyện mà không sử dụng công cụ bên ngoài nào.",  # Tooltip khi hover
        # on_change=on_enable_tools_change,  # Callback khi thay đổi giá trị (đã comment)
    )
    
    # ==========================================================================
    # UPDATE BUTTON & CONFIGURATION DISPLAY - NÚT CẬP NHẬT & HIỂN THỊ CẤU HÌNH
    # ==========================================================================
    # Nút cập nhật để người dùng xác nhận cấu hình
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
