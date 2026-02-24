import json
import streamlit as st

from settings import Settings
from logger import ChatbotLogger

from enum import Enum



logger = ChatbotLogger.get_logger("streamlit_handlers")



class OpenAIResponseAPIStreamingState(str, Enum):
    TEXT_STREAMING_IN_PROGRESS = "response.output_text.delta"
    TEXT_STREAMING_DONE = "response.output_text.done"
    REASONING_IN_PROGRESS = "response.reasoning_text.delta"
    REASONING_DONE = "response.reasoning_text.done"
    RESPONSE_COMPLETED = "response.completed"
    RESPONSE_INCOMPLETED = "response.incomplete"



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



def display_response(response) -> None:
    for block in response.output:
        content = block.content[0].text
        match block.type:
            case 'reasoning':
                if (summary := block.summary or content):
                    with st.expander("REASONING"):
                        st.markdown(summary)
            case 'message':
                if content.startswith("{") and content.endswith("}"):
                    json_data = json.loads(content)
                    st.json(json_data)
                else:
                    st.markdown(content)
            case _:
                st.error(f"❌ [ERROR] Unsupported block type: {block.type}")



def display_streaming_response(response_generator) -> dict | None:
    """Consume a streaming response and render it incrementally.

    Returns a dict suitable for appending to `chat_history` when the stream completes.
    """
    # Keep text streaming incrementally; reasoning will render once at the end.
    # Placeholder order controls visual order in Streamlit: reasoning above text.
    reasoning_placeholder = st.empty()
    content_placeholder = st.empty()
    reasoning_content_response = ""
    reasoning_final_response = ""
    content_response = ""

    for event in response_generator:
        # event.type can be one of our enum values
        etype = getattr(event, "type", None)

        if etype == OpenAIResponseAPIStreamingState.REASONING_IN_PROGRESS:
            delta = getattr(event, "delta", "")
            if delta:
                reasoning_content_response += delta

        elif etype == OpenAIResponseAPIStreamingState.REASONING_DONE:
            # Prefer final reasoning payload when available.
            done_text = getattr(event, "text", "")
            if done_text:
                reasoning_final_response = done_text

        elif etype == OpenAIResponseAPIStreamingState.TEXT_STREAMING_IN_PROGRESS:
            delta = getattr(event, "delta", "")
            if delta:
                content_response += delta
                content_placeholder.markdown(content_response)

        elif etype == OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED:
            break

    final_reasoning = (reasoning_final_response or reasoning_content_response).strip()
    if final_reasoning:
        with reasoning_placeholder.expander("REASONING"):
            st.markdown(final_reasoning)

    # Build assistant message dict to append to history
    message = {"role": "assistant"}
    if final_reasoning:
        message["reasoning_content"] = final_reasoning
    if content_response:
        message["content"] = content_response

    return message



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



def render_chat_history(chat_history: list[dict[str, str]]) -> None:
    """
    Render chat history in Streamlit
    
    Args:
        chat_history: List of chat messages
    """
    for msg in chat_history:
        role = msg.get("role", "user")
        reasoning = msg.get("reasoning_content", "")
        content = msg.get("content", "")
        
        with st.chat_message(role):
            if reasoning:
                with st.expander("REASONING"):
                    st.markdown(reasoning)
            if content.startswith("{") and content.endswith("}"):
                json_data = json.loads(content)
                st.json(json_data)
            else:
                st.markdown(content)