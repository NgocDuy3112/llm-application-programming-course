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
        structured_output_mode = st.toggle(
            "Chế độ định dạng theo cấu trúc",
            value=st.session_state.get("structured_mode_widget", False),
            key="structured_mode_widget",
            on_change=disable_streaming_when_structured,
        )
        enable_web_search = st.toggle(
            "Bật tìm kiếm web (web search)",
            value=st.session_state.get("enable_web_search", True),
            key="enable_web_search",
        )
        output_schema = ""
        if structured_output_mode:
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
        
    state = {
        "structured_output_mode": structured_output_mode,
        "output_schema": output_schema,
        "enable_web_search": enable_web_search,
        "model_provider": model_provider,
        "model": model,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "custom_instructions": custom_instructions
    }
    return state