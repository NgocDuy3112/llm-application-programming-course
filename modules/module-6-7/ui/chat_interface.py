import re
import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice


def render_chat_interface(engine: object):
    """
    Render the chat UI và forward user input đến engine.response().

    Function này:
    - Giữ UI state trong st.session_state.chat_history
    - Strip các internal <think>...</think> blocks khỏi UI view
    - Gửi cleaned input đến engine để xử lý
    - Engine's memory được dùng cho audit/logging và full context

    Args:
        engine (object): Object implementing `.response(...)` method
            để lấy assistant's reply

    Session State Used:
        - chat_history: List of {"role": str, "content": str} messages
        - selected_model: Model name/ID to use
        - temperature: Creativity level (0.0-1.0)
        - max_tokens: Maximum tokens in response
        - enable_tools: Whether to enable function calling
        - system_prompt: System system_prompt/prompt

    Note:
        - UI chỉ lưu cleaned content (không có reasoning blocks)
        - Engine.memory handles its own buffer cho full context
    """
    global_logger.debug("Render chat interface")
    st.title("Xây dựng chatbot cơ bản")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "tool_call_log" not in st.session_state:
        st.session_state.tool_call_log = []

    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).markdown(entry["content"])
        global_logger.debug(f"Hiển thị {len(st.session_state.chat_history)} messages từ chat history")

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        global_logger.debug(f"Xử lý user input: {user_input[:50]}...")
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Đang suy nghĩ..."):
            assistant_reply = engine.response(
                model=st.session_state.selected_model,
                user_prompt=user_input,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                system_prompt=st.session_state.system_prompt if st.session_state.system_prompt else None,
                tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
                tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            )

        # Hiển thị expander tool calls nếu có
        if hasattr(engine, 'tool_call_log') and engine.tool_call_log:
            with st.expander("🔧 Luồng Tool Calls", expanded=False):
                for i, call in enumerate(engine.tool_call_log, 1):
                    st.markdown(f"**{i}. {call['tool']}**")
                    st.markdown(f"   - Args: `{call['args']}`")
                    result = call['result']
                    if len(result) > 200:
                        result = result[:200] + "..."
                    st.markdown(f"   - Result: {result}")
                    st.markdown("---")

        assistant_reply_clean = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL | re.IGNORECASE).strip()

        global_logger.debug(f"Assistant reply được tạo, độ dài: {len(assistant_reply_clean)}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply_clean,
        })

        global_logger.debug(f"Cập nhật chat history, tổng messages: {len(st.session_state.chat_history)}")
        # Do not modify `st.session_state['chat_input']` (Streamlit forbids changing
        # a widget-backed key after the widget is created). We use `_last_handled_input`
        # to detect duplicates instead. Now re-run to refresh the UI.
        st.rerun()