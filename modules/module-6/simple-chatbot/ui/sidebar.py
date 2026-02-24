from ui.helpers import *
from settings import LLMProvider
from service.chat import *



logger = ChatbotLogger.get_logger("streamlit_handlers")
settings = Settings()



def sidebar():
    with st.sidebar:
        st.title("Cài đặt Chatbot")
        model_provider = st.selectbox(
            "Chọn nhà cung cấp mô hình",
            options=LLMProvider.all(),
            format_func=lambda p: p.value,
            index=0,
        )
        model = st.selectbox(
            "Chọn mô hình",
            options=model_provider.default_models,
            index=0,
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
        )
        max_output_tokens = st.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=65000,
            value=65000,
            step=1
        )
        custom_instructions = st.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)",
            value="",
            height=200,
        )
        
        with st.expander("Định dạng đầu ra", expanded=True):
            streaming_mode = st.toggle(
                "Chế độ Streaming",
                value=st.session_state.get("streaming_mode_widget", True),
                key="streaming_mode_widget",
                disabled=st.session_state.get("structured_mode_widget", False),
            )
            structured_output_mode = st.toggle(
                "Chế độ định dạng theo cấu trúc",
                value=st.session_state.get("structured_mode_widget", False),
                key="structured_mode_widget",
                on_change=disable_streaming_when_structured,
            )
            output_schema = ""
            if structured_output_mode:
                st.session_state["streaming_mode"] = False
                streaming_mode = False
                schema_from_file = load_json_schema()
                if schema_from_file:
                    output_schema = json.dumps(schema_from_file)
                else:
                    output_schema_text = st.text_area(
                        "Lược đồ Đầu ra (định dạng JSON)",
                        value='{"field_name": { "type": "str", "default": null, "description": "Description of the field" }}',
                        height=300,
                    )
                    output_schema = parse_json_schema_text(output_schema_text) or None
        with st.expander("Sử dụng công cụ", expanded=False):
            st.info("Tính năng này sẽ sớm được ra mắt! Hãy chờ đón các bản cập nhật tiếp theo.")
        
    state = {
        "streaming_mode": streaming_mode,
        "structured_output_mode": structured_output_mode,
        "output_schema": output_schema,
        "model_provider": model_provider,
        "model": model,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "custom_instructions": custom_instructions
    }
    return state