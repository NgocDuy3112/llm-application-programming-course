import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode


MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b", 
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b"
    ],
    Provider.OLLAMA.value: [
        "qwen3.5:2b-q4_K_M",
        "qwen3.5:2b-q8_0",
        "qwen3.5:2b-bf16", 
    ],
}



def render_sidebar():
    global_logger.debug("Rendering sidebar")
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
    st.sidebar.title("Cài đặt Chatbot")
    st.sidebar.selectbox(
        label="Chọn nhà cung cấp mô hình",
        options=[
            Provider.GROQ.value,
            Provider.OLLAMA.value
        ],
        index=0,
        key="selected_provider"
    )
    
    available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    st.sidebar.selectbox(
        label="Chọn mô hình",
        options=available_models,
        index=0,
        key="selected_model"
    )
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Giá trị cao hơn sẽ làm cho phản hồi của mô hình sáng tạo hơn, trong khi giá trị thấp hơn sẽ làm cho phản hồi an toàn và tập trung hơn",
        key="temperature"
    )
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=16384,
        step=256,
        help="Giới hạn số token trong phản hồi của mô hình, bao gồm cả token suy luận nếu có",
        key="max_tokens"
    )
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Instruction)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        help="Câu lệnh hệ thống là một phần của prompt được gửi đến mô hình để hướng dẫn cách thức phản hồi. Bạn có thể sử dụng nó để thiết lập bối cảnh, vai trò của chatbot, hoặc bất kỳ hướng dẫn đặc biệt nào mà bạn muốn mô hình tuân theo khi tạo phản hồi.",
        key="instruction"
    )
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0,
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại để tạo phản hồi. 'Tắt' sẽ không sử dụng lịch sử nào, 'Cửa sổ trượt' sẽ chỉ sử dụng một số lượng tin nhắn gần đây nhất dựa trên kích thước cửa sổ đã định.",
        key="context_management_mode"
    )
    # Sliding window turns input
    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_turns" not in st.session_state:
            st.session_state.sliding_window_turns = 2
        st.sidebar.number_input(
            label="Số lượt hội thoại (sliding window)",
            min_value=1,
            max_value=50,
            value=st.session_state.sliding_window_turns,
            step=1,
            key="sliding_window_turns",
            help="Số cặp user-assistant được giữ lại trong sliding window",
        )
    def on_enable_tools_change():
        if st.session_state.enable_tools:
            st.session_state.context_management_mode = ContextManagementMode.SLIDING_WINDOW.value
    st.sidebar.toggle(
        label="Sử dụng công cụ",
        value=False,
        key="enable_tools",
        help="Bật nếu bạn muốn cho phép chatbot sử dụng các công cụ đã tích hợp (ví dụ: truy vấn cơ sở dữ liệu, gọi API, v.v.) để trả lời câu hỏi của người dùng. Nếu tắt, chatbot sẽ chỉ dựa vào kiến thức đã được huấn luyện mà không sử dụng công cụ bên ngoài nào.",
        on_change=on_enable_tools_change,
    )
    if st.sidebar.button("Cập nhật cài đặt"):
        global_logger.info(f"Settings updated: Selected provider: {st.session_state.selected_provider}, model: {st.session_state.selected_model}, Temperature: {st.session_state.temperature}, Max tokens: {st.session_state.max_tokens}, Context Management Mode: {ContextManagementMode(st.session_state.context_management_mode)}, Tools enabled: {st.session_state.enable_tools}")
        st.session_state.chat_history = []
        st.sidebar.success("Đã cập nhật cấu hình! Lịch sử chat đã được xóa.")