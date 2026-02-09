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


def _string_chunk_generator(text: str, words_per_chunk: int = 6):
    """Yield successive chunks of the given text split by words.

    This is used to provide a lightweight "typing" animation when
    we only have the final string (non-streaming responses).
    """
    if not text:
        return
    words = text.split()
    if not words:
        yield text
        return
    i = 0
    while i < len(words):
        chunk_words = words[i : i + words_per_chunk]
        chunk = " ".join(chunk_words)
        # Preserve spacing between chunks
        if i + words_per_chunk < len(words):
            chunk += " "
        yield chunk
        i += words_per_chunk


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


def stream_response(response: Generator | str, spinner_text: str) -> dict:
    """
    Stream and display response with reasoning support.

    Accepts either:
    - a generator yielding dicts like {'type': 'text'|'reasoning', 'content': '...'}
    - or a final string (non-streaming) which will be animated locally.

    Returns:
        Dict with keys: 'content' (full response text) and 'reasoning' (accumulated reasoning text)
    """
    # Use a placeholder for the loading state to avoid stacking multiple elements
    loading_ph = st.empty()
    loading_ph.markdown(f"*{spinner_text}*")

    # --- String (non-streaming) path: animate the final text locally ---
    if isinstance(response, str):
        loading_ph.empty()
        thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
        thinking_ph = thinking_expander.empty()

        full_parts: list[str] = []

        def gen_from_string():
            for part in _string_chunk_generator(response):
                full_parts.append(part)
                yield part

        st.write_stream(gen_from_string())
        full_text = "".join(full_parts) if full_parts else response
        return {"content": full_text, "reasoning": ""}

    # --- Generator path (streaming) ---
    response_iter = iter(response)

    try:
        first_chunk = next(response_iter)
    except StopIteration:
        first_chunk = None
    finally:
        # Clear loading indicator once we have the first chunk or stream ends
        loading_ph.empty()

    if first_chunk is None:
        st.markdown("")
        return {"content": "", "reasoning": ""}

    thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
    thinking_ph = thinking_expander.empty()

    full_parts: list[str] = []
    full_reasoning = ""

    def response_generator():
        nonlocal full_parts, full_reasoning
        for chunk in _chain_first(first_chunk, response_iter):
            ctype = chunk.get("type") if isinstance(chunk, dict) else "text"
            content = chunk.get("content") if isinstance(chunk, dict) else str(chunk)

            if ctype == "reasoning":
                full_reasoning += content
                thinking_ph.markdown(full_reasoning)
            else:
                full_parts.append(content)
                yield content

        # Ensure final reasoning is shown when stream completes
        if full_reasoning:
            thinking_ph.markdown(full_reasoning)

    # Stream main text to UI and return both text and reasoning for persistence
    st.write_stream(response_generator())
    full_text = "".join(full_parts)
    return {"content": full_text, "reasoning": full_reasoning}


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
        reasoning = msg.get("reasoning", "")

        with st.chat_message(role):
            if role == "assistant":
                # Show persisted reasoning (if any) in an expander so it survives reruns
                if reasoning:
                    thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
                    thinking_expander.markdown(reasoning)

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


# Streamlit-specific helpers for UI interactions
def enforce_mutual_exclusion(active_key: str, inactive_key: str) -> None:
    """When a widget with key `active_key` becomes True, ensure
    the widget with key `inactive_key` is set to False.

    This function uses `st.session_state` and is intended to be used
    as an `on_change` callback for checkboxes in the Streamlit UI.
    """
    try:
        if st.session_state.get(active_key, False):
            st.session_state[inactive_key] = False
    except Exception as e:
        logger.debug(f"Failed to enforce mutual exclusion: {e}")


def disable_streaming_when_structured() -> None:
    """Disable the streaming checkbox if structured output is enabled.

    Intended to be used as an `on_change` callback for the structured
    format checkbox in the Streamlit UI.
    """
    try:
        if st.session_state.get("structured_mode_widget", False):
            st.session_state["streaming_mode_widget"] = False
    except Exception as e:
        logger.debug(f"Failed to disable streaming widget: {e}")