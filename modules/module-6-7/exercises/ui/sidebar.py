"""
Module 6-7 - Giao diện Sidebar

Mô tả: Component sidebar (Streamlit) cho demo chatbot. Sidebar cung cấp
các điều khiển để cấu hình:
- Nhà cung cấp LLM (Groq, Ollama)
- Chọn mô hình
- Độ sáng tạo (temperature)
- Số token tối đa trả về
- Câu lệnh hệ thống
- Chế độ quản lý ngữ cảnh (tắt, cửa sổ trượt)
- Bật/tắt sử dụng công cụ (function calling)

Kiến trúc / Phụ thuộc:
- Streamlit: Framework UI web
- custom_types: Enum Provider, ContextManagementMode
- constants: Bản đồ MODELS_BY_PROVIDER

Trạng thái phiên (session state) được quản lý:
    - selected_provider: Tên provider (groq, ollama)
    - selected_model: ID model được chọn
    - temperature: Float 0.0-1.0
    - max_tokens: Integer (số token tối đa)
    - instruction: Câu lệnh hệ thống (system prompt)
    - context_management_mode: Chế độ quản lý ngữ cảnh
    - sliding_window_turns: Số lượt trong cửa sổ trượt
    - enable_tools: Bool bật/tắt sử dụng công cụ
    - chat_history: Lịch sử chat (reset khi cập nhật cài đặt)

Cách sử dụng:
    from ui.sidebar import render_sidebar
    render_sidebar()
"""

import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode
from constants import MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar chứa các control để cấu hình chatbot.

    Các thành phần sidebar (theo thứ tự):
    1. Hộp chọn nhà cung cấp (Provider)
    2. Hộp chọn mô hình (dynamic theo provider)
    3. Thanh trượt cho temperature
    4. Input số cho max tokens
    5. Textarea cho câu lệnh hệ thống
    6. Radio cho chế độ quản lý ngữ cảnh
    7. Input số cho số lượt cửa sổ trượt (nếu áp dụng)
    8. Toggle bật/tắt sử dụng công cụ
    9. Nút cập nhật cài đặt

    Tác động phụ:
        - Cập nhật `st.session_state` với các giá trị từ controls
        - Tự động bật chế độ cửa sổ trượt khi bật công cụ
        - Reset `chat_history` khi nhấn nút "Cập nhật cài đặt"
    """
    global_logger.debug("Rendering sidebar")
    
    # Initialize default provider if not set
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]
    
    st.sidebar.title("Cài đặt Chatbot")
    
    # Hộp chọn nhà cung cấp mô hình, với các tùy chọn lấy từ enum Provider, bao gồm Groq và Ollama
    st.sidebar.selectbox(
        label="Chọn nhà cung cấp mô hình", # Nhãn cho hộp chọn
        # Các tùy chọn cho nhà cung cấp mô hình, lấy giá trị từ enum Provider
        options=[
            Provider.GROQ.value,
            Provider.OLLAMA.value
        ],
        index=0, # Mặc định chọn tùy chọn đầu tiên (Groq)
        key="selected_provider", # Key để lưu giá trị đã chọn trong session_state
        help="Chọn nhà cung cấp LLM mà bạn muốn sử dụng cho chatbot. Groq là một nền tảng LLM dựa trên đám mây, trong khi Ollama cho phép bạn chạy mô hình LLM cục bộ trên máy của mình." # Mô tả chức năng của hộp chọn
    )

    # Biến available_models được tính toán dựa trên provider đã chọn, lấy từ hằng số MODELS_BY_PROVIDER
    available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    # Hộp chọn mô hình
    st.sidebar.selectbox(
        label="Chọn mô hình", # Nhãn cho hộp chọn
        options=available_models, # Các tùy chọn mô hình dựa trên provider đã chọn
        index=0, # Mặc định chọn tùy chọn đầu tiên trong danh sách mô hình
        key="selected_model", # Key để lưu giá trị đã chọn trong session_state
        help="Chọn mô hình ngôn ngữ lớn (LLM) mà bạn muốn sử dụng cho chatbot. Các mô hình khác nhau có thể có khả năng và hiệu suất khác nhau, vì vậy hãy chọn mô hình phù hợp với nhu cầu của bạn." # Mô tả chức năng của hộp chọn
    )
    
    # Thanh trượt để chọn độ sáng tạo (temperature)
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)", # Nhãn cho thanh trượt
        min_value=0.0, # Giá trị tối thiểu là 0.0
        max_value=1.0, # Giá trị tối đa là 1.0
        value=0.25, # Giá trị mặc định
        step=0.05, # Bước tăng giảm
        help="Giá trị cao hơn sẽ làm cho phản hồi của mô hình sáng tạo hơn, trong khi giá trị thấp hơn sẽ làm cho phản hồi an toàn và tập trung hơn", # Mô tả chức năng của thanh trượt
        key="temperature" # Key để lưu giá trị trong session_state
    )
    
    # Khung number input để chọn độ dài tối đa của phản hồi (max output tokens)
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)", # Nhãn cho number input
        min_value=2048, # Giá trị tối thiểu (tùy theo yêu cầu của mô hình, thường là 2048)
        max_value=131072, # Giá trị tối đa (tùy theo khả năng của mô hình, có thể lên đến 131072 hoặc hơn)
        value=16384, # Giá trị mặc định (có thể điều chỉnh tùy theo nhu cầu, ví dụ 16384)
        step=256, # Bước tăng giảm (tùy theo nhu cầu, ví dụ 256)
        help="Giới hạn số token trong phản hồi của mô hình, bao gồm cả token suy luận nếu có", # Mô tả chức năng của number input
        key="max_tokens" # Key để lưu giá trị trong session_state
    )

    # Note: temperature and max_tokens are UI-configurable and should be
    # forwarded through `engine.response` -> `adapter.response` when calling the model.
    
    # Khung text_area để nhập câu lệnh hệ thống
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Instruction)", # Nhãn cho text area
        height=200, # Chiều cao của text area
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.", # Văn bản gợi ý khi chưa nhập gì
        help="Câu lệnh hệ thống là một phần của prompt được gửi đến mô hình để hướng dẫn cách thức phản hồi. Bạn có thể sử dụng nó để thiết lập bối cảnh, vai trò của chatbot, hoặc bất kỳ hướng dẫn đặc biệt nào mà bạn muốn mô hình tuân theo khi tạo phản hồi.", # Mô tả chức năng của text area
        key="instruction" # Key để lưu giá trị trong session_state
    )
    
    # Khung radio để chọn chế độ quản lý ngữ cảnh
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh", # Nhãn cho khung radio
        # Các tùy chọn cho chế độ quản lý ngữ cảnh, lấy giá trị từ enum ContextManagementMode
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0, # Mặc định chọn tùy chọn đầu tiên (OFF)
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại để tạo phản hồi. 'Tắt' sẽ không sử dụng lịch sử nào, 'Cửa sổ trượt' sẽ chỉ sử dụng một số lượng tin nhắn gần đây nhất dựa trên kích thước cửa sổ đã định.", # Mô tả chức năng của khung radio
        key="context_management_mode" # Key để lưu giá trị đã chọn trong session_state
    )
    
    # Nếu chọn chế độ sliding window, hiển thị input để chọn số tin nhắn trong cửa sổ trượt
    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        # Khởi tạo giá trị mặc định cho sliding_window_turns nếu chưa có trong session_state
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 2
        # Input để chọn số tin nhắn trong cửa sổ trượt
        st.sidebar.number_input(
            label="Số tin nhắn trong cửa sổ trượt", # Nhãn cho input
            min_value=1, # Giá trị tối thiểu là 1
            max_value=5, # Giá trị tối đa là 5 (có thể điều chỉnh tùy theo nhu cầu)
            value=st.session_state.sliding_window_turns, # Giá trị mặc định lấy từ session_state
            step=1, # Bước tăng giảm là 1
            key="sliding_window_turns", # Key để lưu giá trị trong session_state
            help="Số tin nhắn user-assistant được giữ lại trong cửa sổ trượt để cung cấp ngữ cảnh cho phản hồi. Ví dụ: nếu bạn đặt 3, chatbot sẽ sử dụng 3 tin nhắn gần nhất", # Mô tả chức năng của input
        )
    
    # Hàm callback để tự động bật chế độ quản lý ngữ cảnh khi bật công cụ
    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value
    
    # Nút gạc bật công cụ
    st.sidebar.toggle(
        label="Sử dụng công cụ", # Nhãn cho toggle
        value=False, # Mặc định là tắt
        key="enable_tools", # Key để lưu trạng thái toggle trong session_state
        help="Bật nếu bạn muốn cho phép chatbot sử dụng các công cụ đã tích hợp (ví dụ: truy vấn cơ sở dữ liệu, gọi API, v.v.) để trả lời câu hỏi của người dùng. Nếu tắt, chatbot sẽ chỉ dựa vào kiến thức đã được huấn luyện mà không sử dụng công cụ bên ngoài nào.", # Mô tả chức năng của toggle
        on_change=on_enable_tools_change, # Callback function để tự động bật chế độ quản lý ngữ cảnh khi bật công cụ
    )
    
    # Nút cập nhật cài đặt - khi click sẽ ghi log cấu hình mới và reset lịch sử chat
    if st.sidebar.button("Cập nhật cài đặt"):
        # Ghi log cấu hình mới
        selected_provider = st.session_state.get("selected_provider")
        selected_model = st.session_state.get("selected_model")
        temperature = st.session_state.get("temperature")
        max_tokens = st.session_state.get("max_tokens")
        context_mode = ContextManagementMode(st.session_state.get("context_management_mode"))
        tools_enabled = st.session_state.get("enable_tools")
    
        global_logger.info(f"Settings updated: Selected provider: {selected_provider}, model: {selected_model}, Temperature: {temperature}, Max tokens: {max_tokens}, Context Management Mode: {context_mode}, Tools enabled: {tools_enabled}")
        
        st.sidebar.success("Đã cập nhật cấu hình!")
        # Reset lịch sử chat
        st.session_state.chat_history = []
