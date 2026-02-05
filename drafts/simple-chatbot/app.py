import streamlit as st
import json

from src.core.client import OpenAIStandardClient
from src.services.chat_service import ChatService
from src.ui.streamlit_handlers import (
    handle_response_error,
    stream_response,
    render_chat_history,
    load_json_schema,
    parse_json_schema_text,
    enforce_mutual_exclusion,
    disable_streaming_when_structured,
)
from src.utils.settings import *
from logger import ChatbotLogger

logger = ChatbotLogger.get_logger("app")


def sidebar():
    """Render sidebar and return client + state"""
    with st.sidebar:
        model_provider = st.selectbox(
            "Chọn nhà cung cấp mô hình",
            options=["Groq", "Gemini", "Ollama", "Huggingface"],
            index=0,
        )

        api_key = None
        if model_provider in NEED_API_KEY_PROVIDERS:
            api_key = st.text_input(
                "Nhập API Key",
                value=settings.API_KEY,
                type="password",
            )

        model = st.selectbox(
            "Chọn mô hình",
            options=MODELS_LIST.get(model_provider, []),
            placeholder="Không có mô hình nào khả dụng",
            index=0,
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
        )

        max_output_tokens = st.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=2048,
            value=512,
            step=1,
        )

        custom_instructions = st.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)",
            value="",
            height=200,
        )

        # Output format controls
        with st.expander("Định dạng output", expanded=True):
            streaming_mode = st.checkbox(
                "Chế độ Streaming",
                value=st.session_state.get("streaming_mode_widget", True),
                key="streaming_mode_widget",
                disabled=st.session_state.get("structured_mode_widget", False),
            )

            structured_output_mode = st.checkbox(
                "Chế độ định dạng theo cấu trúc",
                value=st.session_state.get("structured_mode_widget", False),
                key="structured_mode_widget",
                on_change=disable_streaming_when_structured,
            )

            output_schema = ""
            if structured_output_mode:
                # Ensure streaming is considered disabled when structured output is active
                st.session_state["streaming_mode"] = False
                streaming_mode = False

                # Try loading from file first
                schema_from_file = load_json_schema()

                if schema_from_file:
                    output_schema = schema_from_file
                else:
                    # Fallback to text input
                    output_schema_text = st.text_area(
                        "Lược đồ Đầu ra (định dạng JSON)",
                        value='{"field_name": { "type": "str", "default": null, "description": "Description of the field" }}',
                        height=300,
                    )
                    output_schema = parse_json_schema_text(output_schema_text) or ""

        # Context management controls
        with st.expander("Quản lý ngữ cảnh", expanded=True):
            sliding_window_mode = st.checkbox(
                "Sử dụng kỹ thuật Sliding Window",
                value=st.session_state.get("sliding_window_mode_widget", False),
                key="sliding_window_mode_widget",
                on_change=enforce_mutual_exclusion,
                args=("sliding_window_mode_widget", "summarization_mode_widget"),
            )

            summarization_mode = st.checkbox(
                "Sử dụng kỹ thuật Summarization",
                value=st.session_state.get("summarization_mode_widget", False),
                key="summarization_mode_widget",
                on_change=enforce_mutual_exclusion,
                args=("summarization_mode_widget", "sliding_window_mode_widget"),
            )

        # Create or reuse a client resource across Streamlit reruns
        @st.cache_resource
        def _get_client(model, model_provider, api_key):
            return OpenAIStandardClient(
                model=model,
                model_provider=model_provider,
                api_key=api_key,
            )

        client = _get_client(model, model_provider, api_key)

    state = {
        "streaming_mode": streaming_mode,
        "structured_output_mode": structured_output_mode,
        "sliding_window_mode": sliding_window_mode,
        "summarization_mode": summarization_mode,
        "output_schema": output_schema,
        "custom_instructions": custom_instructions,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
    }
    return client, state


def main():
    st.title("Simple Chatbot Application")
    
    # Widen sidebar
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { width: 420px; min-width: 420px; }
        .css-1d391kg { width: 420px; }
        main { margin-left: 440px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "streaming_mode" not in st.session_state:
        st.session_state["streaming_mode"] = True
    if "sliding_window_mode" not in st.session_state:
        st.session_state["sliding_window_mode"] = False
    if "summarization_mode" not in st.session_state:
        st.session_state["summarization_mode"] = False
    
    # Get client and settings from sidebar
    client, sidebar_state = sidebar()
    chat_service = ChatService(client)
    
    # Render chat history
    render_chat_history(st.session_state["chat_history"])
    
    # Handle user input
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...")
    
    if user_input:
        # Remove previous error if exists
        if (st.session_state["chat_history"] and 
            st.session_state["chat_history"][-1].get("role") == "assistant" and 
            st.session_state["chat_history"][-1].get("content", "").startswith("[ERROR]")):
            st.session_state["chat_history"].pop()
            logger.info("Removed previous error message")
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input
        })
        
        # Determine mode
        if sidebar_state["structured_output_mode"]:
            mode = "structured"
        elif sidebar_state["streaming_mode"]:
            mode = "streaming"
        else:
            mode = "non-streaming"
        
        # Create response
        with st.chat_message("assistant"):
            try:
                # Validate input
                chat_service.validate_input(user_input)
                
                # Validate schema if structured mode
                if mode == "structured":
                    chat_service.validate_schema(sidebar_state["output_schema"])
                
                # Get response
                response = chat_service.create_response(
                    mode=mode,
                    input_data=st.session_state["chat_history"],
                    instructions=sidebar_state["custom_instructions"],
                    max_output_tokens=sidebar_state["max_output_tokens"],
                    temperature=sidebar_state["temperature"],
                    schema=sidebar_state.get("output_schema") if mode == "structured" else None,
                    use_sliding_window=sidebar_state.get("sliding_window_mode", False),
                    use_summarization=sidebar_state.get("summarization_mode", False),
                    max_history_messages=None,
                )
                
                # Display response
                if mode == "streaming":
                    content = stream_response(response, "Đang phản hồi...")
                elif mode == "structured":
                    st.json(json.loads(response))
                    content = response
                else:
                    with st.spinner("Đang phản hồi..."):
                        content = response
                    st.markdown(content)
                
            except Exception as e:
                content = handle_response_error(e, mode=mode)
        
        # Save to history
        if content:
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": content
            })


if __name__ == "__main__":
    main()