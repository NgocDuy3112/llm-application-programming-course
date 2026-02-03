import json
from collections.abc import Generator
import streamlit as st

from src.core.exceptions import ChatbotError, APIKeyError, ValidationError
from logger import ChatbotLogger



logger = ChatbotLogger.get_logger("streamlit_handlers")


THINKING_PROCESS_DISPLAY_STRING = "🧠 Quá trình suy luận"


def _chain_first(first_item, iterator):
    """Chain first item with iterator"""
    yield first_item
    yield from iterator


def handle_response_error(e: Exception, mode: str = "general") -> str:
    """
    Handle and display errors in Streamlit UI
    
    Args:
        e: Exception to handle
        mode: Mode of operation (for context in suggestions)
        
    Returns:
        Error message string to save in history
    """
    error_msg = ""
    
    if isinstance(e, APIKeyError):
        logger.error(f"API Key error in {mode}: {e}")
        st.error("❌ **Lỗi xác thực:** API Key không hợp lệ hoặc đã hết hạn.")
        st.info("💡 **Gợi ý:** Nhập lại API Key ở thanh sidebar bên trái.")
        error_msg = "[ERROR] API Key không hợp lệ"
        
    elif isinstance(e, ValidationError):
        logger.error(f"Validation error in {mode}: {e}")
        st.error(f"❌ **Lỗi dữ liệu:** {str(e)}")
        if "schema" in str(e).lower():
            st.info("💡 **Gợi ý:** Kiểm tra lại schema JSON hoặc nội dung tin nhắn.")
        error_msg = f"[ERROR] {str(e)}"
        
    elif isinstance(e, ChatbotError):
        logger.error(f"Chatbot error in {mode}: {e}")
        st.error(f"❌ **Lỗi:** {str(e)}")
        if mode == "streaming":
            st.info("💡 **Gợi ý:** Vui lòng thử lại hoặc tắt chế độ streaming.")
        else:
            st.info("💡 **Gợi ý:** Vui lòng thử lại sau vài giây hoặc thử với model khác.")
        error_msg = f"[ERROR] {str(e)}"
        
    else:
        logger.critical(f"Unexpected error in {mode}: {e}", exc_info=True)
        st.error("❌ **Lỗi không xác định:** Đã xảy ra lỗi trong quá trình xử lý.")
        with st.expander("🔍 Chi tiết kỹ thuật (cho developer)"):
            st.exception(e)
        error_msg = "[ERROR] Lỗi không xác định"
    
    return error_msg


def stream_response(response: Generator, spinner_text: str) -> str:
    """
    Stream and display response with reasoning support
    
    Args:
        response: Generator yielding response chunks
        spinner_text: Loading text for spinner
        
    Returns:
        Full response text
    """
    response_iter = iter(response)
    
    with st.spinner(spinner_text):
        try:
            first_chunk = next(response_iter)
        except StopIteration:
            first_chunk = None

    if first_chunk is None:
        st.markdown("")
        return ""

    thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
    thinking_ph = thinking_expander.empty()
    message_ph = st.empty()
    full_text = ""
    full_reasoning = ""

    for chunk in _chain_first(first_chunk, response_iter):
        ctype = chunk.get("type") if isinstance(chunk, dict) else "text"
        content = chunk.get("content") if isinstance(chunk, dict) else str(chunk)
        
        if ctype == "reasoning":
            full_reasoning += content
            thinking_ph.markdown(full_reasoning)
        else:
            full_text += content
            message_ph.markdown(full_text + "▌")

    if full_reasoning:
        thinking_ph.markdown(full_reasoning)
    
    message_ph.markdown(full_text)
    return full_text


def display_response(content: str, mode: str) -> None:
    """
    Display response based on mode
    
    Args:
        content: Response content
        mode: Display mode ('structured', 'streaming', 'non-streaming')
    """
    if content.startswith("[ERROR]"):
        st.error(content.replace("[ERROR] ", "❌ "))
    elif mode == "structured" and content.strip().startswith("{"):
        try:
            json_data = json.loads(content)
            st.json(json_data)
        except json.JSONDecodeError:
            st.markdown(content)
    else:
        st.markdown(content)


def render_chat_history(chat_history: list[dict[str, str]]) -> None:
    """
    Render chat history in Streamlit
    
    Args:
        chat_history: List of chat messages
    """
    for msg in chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        with st.chat_message(role):
            if role == "assistant":
                # Determine display mode based on content
                if content.strip().startswith("{"):
                    mode = "structured"
                else:
                    mode = "non-streaming"
                display_response(content, mode)
            else:
                st.markdown(content)


def load_json_schema() -> dict | None:
    """
    Handle JSON schema upload and parsing
    
    Returns:
        Parsed schema dict or None
    """
    json_file = st.file_uploader(
        "Tải lên file lược đồ (JSON)",
        type=["json"],
    )
    
    if json_file is not None:
        try:
            file_content = json_file.read().decode("utf-8")
            output_schema = json.loads(file_content)
            schema_display = json.dumps(output_schema, ensure_ascii=False, indent=2)
            st.success("Đọc lược đồ từ file JSON thành công!")
            st.code(schema_display, language="json")
            return output_schema
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse JSON file: {e}")
            st.error("Không đọc được file JSON. Vui lòng kiểm tra lại nội dung.")
            return None
    
    return None


def parse_json_schema_text(schema_text: str) -> dict | None:
    """
    Parse JSON schema from text input
    
    Args:
        schema_text: JSON string
        
    Returns:
        Parsed schema dict or None
    """
    try:
        output_schema = json.loads(schema_text)
        st.success("Lược đồ hợp lệ!")
        return output_schema
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON schema: {e}")
        st.error("Định dạng JSON không hợp lệ. Vui lòng kiểm tra lại.")
        return None