import streamlit as st
from logger import global_logger
from custom_types import Provider, ContextManagementMode
from custom_types import MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls để cấu hình chatbot.

    Sidebar components (theo thứ tự):
    1. Provider selection dropdown
    2. Model selection dropdown (dynamic based on provider)
    3. Temperature slider
    4. Max tokens number input
    5. System system_prompt textarea
    6. Context management mode radio
    7. Sliding window turns input (conditional)
    8. Tools toggle
    9. Update settings button

    Side Effects:
        - Updates st.session_state với các giá trị từ controls
        - Auto-toggles context mode when tools enabled
        - Resets chat_history when "Cập nhật cài đặt" pressed
    """
    global_logger.debug("Rendering sidebar")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    st.sidebar.title("Cài đặt Chatbot")

    st.sidebar.selectbox(
        label="Chọn nhà cung cấp mô hình",
        options=[
            Provider.GROQ.value,
            Provider.OLLAMA.value,
            Provider.CEREBRAS.value
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
        label="Độ dài tối đa của phản hồi (Max Completion Tokens)",
        min_value=2048,
        max_value=131072,
        value=5120,
        step=256,
        help="Giới hạn số token trong phản hồi của mô hình, bao gồm cả token suy luận nếu có",
        key="max_completion_tokens"
    )

    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System prompt)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        help="Câu lệnh hệ thống là một phần của prompt được gửi đến mô hình để hướng dẫn cách thức phản hồi. Bạn có thể sử dụng nó để thiết lập bối cảnh, vai trò của chatbot, hoặc bất kỳ hướng dẫn đặc biệt nào mà bạn muốn mô hình tuân theo khi tạo phản hồi.",
        key="system_prompt"
    )

    st.sidebar.radio(
        label="Chế độ quản lý ngữ cảnh",
        options=[
            ContextManagementMode.OFF.value,
            ContextManagementMode.SLIDING_WINDOW.value,
        ],
        index=0,
        help="Chế độ quản lý ngữ cảnh sẽ quyết định cách chatbot sử dụng lịch sử hội thoại để tạo phản hồi. 'Tắt' sẽ không sử dụng lịch sử nào, 'Cửa sổ trượt' sẽ chỉ sử dụng một số lượng tin nhắn gần đây nhất dựa trên kích thước cửa sổ đã định.",
        key="context_management_mode"
    )

    if st.session_state.get("context_management_mode") == ContextManagementMode.SLIDING_WINDOW.value:
        if "sliding_window_messages" not in st.session_state:
            st.session_state.sliding_window_messages = 5
        st.sidebar.number_input(
            label="Số tin nhắn trong cửa sổ trượt",
            min_value=1,
            max_value=50,
            value=st.session_state.sliding_window_messages,
            step=1,
            key="sliding_window_messages",
            help="Số tin nhắn user-assistant được giữ lại trong cửa sổ trượt để cung cấp ngữ cảnh cho phản hồi. Ví dụ: nếu bạn đặt 3, chatbot sẽ sử dụng 3 tin nhắn gần nhất",
        )

    st.sidebar.toggle(
        label="Sử dụng công cụ",
        value=False,
        key="enable_tools",
        help="Bật nếu bạn muốn cho phép chatbot sử dụng các công cụ đã tích hợp (ví dụ: truy vấn cơ sở dữ liệu, gọi API, v.v.) để trả lời câu hỏi của người dùng. Nếu tắt, chatbot sẽ chỉ dựa vào kiến thức đã được huấn luyện mà không sử dụng công cụ bên ngoài nào.",
    )

    if st.sidebar.button("Cập nhật cài đặt"):
        selected_provider = st.session_state.get("selected_provider")
        selected_model = st.session_state.get("selected_model")
        temperature = st.session_state.get("temperature")
        max_tokens = st.session_state.get("max_completion_tokens")
        context_mode = st.session_state.get("context_management_mode")
        try:
            context_mode_label = ContextManagementMode(context_mode).value
        except Exception:
            context_mode_label = str(context_mode)
        tools_enabled = st.session_state.get("enable_tools")

        global_logger.info(
            "Cập nhật cấu hình:\n"
            f"  - Nhà cung cấp: {selected_provider}\n"
            f"  - Mô hình: {selected_model}\n"
            f"  - Temperature: {temperature}\n"
            f"  - Max Completion Tokens: {max_tokens}\n"
            f"  - Chế độ quản lý ngữ cảnh: {context_mode_label}\n"
            f"  - Sử dụng công cụ: {tools_enabled}"
        )

        st.session_state.chat_history = []
        # Xoá engine cũ để app.py tạo lại engine với cài đặt mới (provider, memory mode...)
        if "chatbot_engine" in st.session_state:
            del st.session_state.chatbot_engine
        st.sidebar.success("Đã cập nhật cấu hình!")