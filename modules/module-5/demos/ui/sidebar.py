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
# IMPORTS
# =============================================================================
import streamlit as st


# =============================================================================
# FUNCTIONS
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
    st.sidebar.title("Cài đặt Chatbot")
    
    # ==========================================================================
    # TEMPERATURE SLIDER
    # ==========================================================================
    # Temperature kiểm soát độ "sáng tạo" của phản hồi:
    # - 0.0: Phản hồi xác định nhất, ít biến thiên
    # - 1.0: Phản hồi sáng tạo nhất, nhiều biến thiên
    # Giá trị mặc định 0.25 phù hợp cho các tác vụ cần tính chính xác cao
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        key="temperature"
    )
    
    # ==========================================================================
    # MAX OUTPUT TOKENS INPUT
    # ==========================================================================
    # Giới hạn số token trong phản hồi:
    # - Token là đơn vị cơ bản của text (khoảng 4 ký tự tiếng Anh)
    # - Giá trị cao hơn cho phép phản hồi dài hơn nhưng tốn nhiều token hơn
    # - Giới hạn: 2048 - 131072 (tùy model)
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=65536,
        step=256,
        key="max_tokens"
    )
    
    # ==========================================================================
    # SYSTEM PROMPT TEXT AREA
    # ==========================================================================
    # System prompt định hướng hành vi của AI:
    # - Được gửi đầu tiên trong danh sách messages
    # - Không hiển thị cho người dùng
    # - Có thể dùng để: định vai trò, giới hạn chủ đề, định dạng output
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Prompt)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        key="system_prompt"
    )
    
    # ==========================================================================
    # CONTEXT MANAGEMENT MODE RADIO
    # ==========================================================================
    # Chế độ quản lý ngữ cảnh hội thoại:
    # - Tắt: Không quản lý, gửi toàn bộ lịch sử
    # - Cửa sổ trượt: Giữ N tin nhắn gần nhất
    # - Tóm tắt: Tóm tắt lịch sử khi quá dài
    # (Sẽ được triển khai chi tiết trong các module sau)
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            "Tắt",
            "Cửa sổ trượt (sliding window)",
            "Tóm tắt (summarization)"
        ],
        index=0,
        key="context_management_mode"
    )
    
    # ==========================================================================
    # UPDATE BUTTON & CONFIGURATION DISPLAY
    # ==========================================================================
    # Nút cập nhật để người dùng xác nhận cấu hình
    # Hiển thị expander với chi tiết cấu hình hiện tại
    if st.sidebar.button("Cập nhật cài đặt"):
        st.sidebar.success("Đã cập nhật cấu hình!")
        
        # Expander hiển thị chi tiết cấu hình
        with st.sidebar.expander("Xem chi tiết cấu hình", expanded=True):
            st.markdown(f"**Độ sáng tạo (Temperature):** {st.session_state.temperature}")
            st.markdown(f"**Số lượng token tối đa (Max Output Tokens):** {st.session_state.max_tokens}")
            st.markdown(f"**Câu lệnh hệ thống (System Prompt):** {st.session_state.system_prompt}")
            st.markdown(f"**Chế độ quản lý ngữ cảnh (Context Management Mode):** {st.session_state.context_management_mode}")